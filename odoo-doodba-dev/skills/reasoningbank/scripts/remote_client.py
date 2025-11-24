"""
Remote Service API Client for Centralized Reasoning Bank.

Handles HTTP communication with the central knowledge base service.
"""

import aiohttp
import asyncio
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path


class RemoteServiceError(Exception):
    """Base exception for remote service errors."""
    pass


class AuthenticationError(RemoteServiceError):
    """Authentication failed."""
    pass


class RateLimitError(RemoteServiceError):
    """Rate limit exceeded."""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class NetworkError(RemoteServiceError):
    """Network/connection error."""
    pass


class RemoteServiceClient:
    """Client for interacting with centralized reasoning bank service."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.central_config = config.get('reasoningbank', {}).get('central', {})

        self.api_url = self.central_config.get('api_url', '')
        self.api_key = self._get_api_key()
        self.user_id = self.central_config.get('user_id', os.getenv('USER', 'anonymous'))
        self.org_id = self.central_config.get('org_id')

        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

        self.session: Optional[aiohttp.ClientSession] = None

    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        api_key = self.central_config.get('api_key', '')

        # Check if it's an environment variable reference
        if api_key.startswith('${') and api_key.endswith('}'):
            env_var = api_key[2:-1]
            api_key = os.getenv(env_var, '')

        return api_key

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _authenticate(self) -> str:
        """Authenticate and get access token."""
        await self._ensure_session()

        if not self.api_key:
            raise AuthenticationError("No API key configured. Set reasoningbank.central.api_key or REASONINGBANK_API_KEY environment variable.")

        url = f"{self.api_url}/auth/token"
        payload = {
            "api_key": self.api_key,
            "user_id": self.user_id,
            "org_id": self.org_id
        }

        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitError("Rate limit exceeded during authentication", retry_after)
                elif response.status != 200:
                    text = await response.text()
                    raise AuthenticationError(f"Authentication failed: {response.status} - {text}")

                data = await response.json()
                self.access_token = data['access_token']
                expires_in = data.get('expires_in', 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                return self.access_token

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error during authentication: {e}")

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers, refreshing token if needed."""
        # Check if token needs refresh
        if not self.access_token or not self.token_expires_at:
            await self._authenticate()
        elif datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5):
            # Refresh if expires in < 5 minutes
            await self._authenticate()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def upload_pattern(
        self,
        pattern: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Upload a pattern to the central service.

        Args:
            pattern: Pattern data (JSON-serializable dict)
            metadata: Optional metadata about the upload

        Returns:
            (remote_id, response_data)
        """
        await self._ensure_session()
        headers = await self._get_auth_headers()

        url = f"{self.api_url}/patterns"

        # Prepare payload
        payload = {
            "pattern": pattern,
            "metadata": metadata or {
                "created_at": datetime.utcnow().isoformat(),
                "source_version": "1.0.0",
                "anonymize": True
            }
        }

        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 401:
                    # Try re-authenticating once
                    self.access_token = None
                    headers = await self._get_auth_headers()
                    async with self.session.post(url, json=payload, headers=headers) as retry_response:
                        return await self._handle_upload_response(retry_response)

                return await self._handle_upload_response(response)

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error during upload: {e}")

    async def _handle_upload_response(self, response: aiohttp.ClientResponse) -> Tuple[str, Dict[str, Any]]:
        """Handle upload response."""
        if response.status == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            raise RateLimitError("Upload rate limit exceeded", retry_after)

        if response.status == 401:
            raise AuthenticationError("Authentication failed")

        if response.status not in (200, 201):
            text = await response.text()
            raise RemoteServiceError(f"Upload failed: {response.status} - {text}")

        data = await response.json()
        remote_id = data.get('remote_id', '')
        return remote_id, data

    async def search_patterns(
        self,
        query: str,
        embedding: Optional[List[float]] = None,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for patterns in the central service.

        Args:
            query: Text query
            embedding: Optional pre-computed embedding vector
            k: Number of results to return
            filters: Optional filters (domain, min_confidence, etc.)

        Returns:
            List of pattern dicts with scores
        """
        await self._ensure_session()
        headers = await self._get_auth_headers()

        url = f"{self.api_url}/patterns/search"

        payload = {
            "query": query,
            "k": k
        }

        if embedding:
            payload["embedding"] = embedding

        if filters:
            payload["filters"] = filters

        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 401:
                    # Try re-authenticating once
                    self.access_token = None
                    headers = await self._get_auth_headers()
                    async with self.session.post(url, json=payload, headers=headers) as retry_response:
                        if retry_response.status != 200:
                            text = await retry_response.text()
                            raise RemoteServiceError(f"Search failed: {retry_response.status} - {text}")
                        data = await retry_response.json()
                        return data.get('patterns', [])

                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitError("Search rate limit exceeded", retry_after)

                if response.status != 200:
                    text = await response.text()
                    raise RemoteServiceError(f"Search failed: {response.status} - {text}")

                data = await response.json()
                return data.get('patterns', [])

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error during search: {e}")

    async def submit_feedback(
        self,
        remote_id: str,
        feedback_type: str,
        comment: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit feedback on a community pattern.

        Args:
            remote_id: Remote pattern ID
            feedback_type: 'upvote', 'downvote', or 'report'
            comment: Optional comment
            context: Optional context (task_id, outcome, etc.)

        Returns:
            Response data
        """
        await self._ensure_session()
        headers = await self._get_auth_headers()

        url = f"{self.api_url}/patterns/{remote_id}/feedback"

        payload = {
            "feedback_type": feedback_type
        }

        if comment:
            payload["comment"] = comment

        if context:
            payload["context"] = context

        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 401:
                    # Try re-authenticating once
                    self.access_token = None
                    headers = await self._get_auth_headers()
                    async with self.session.post(url, json=payload, headers=headers) as retry_response:
                        if retry_response.status != 200:
                            text = await retry_response.text()
                            raise RemoteServiceError(f"Feedback failed: {retry_response.status} - {text}")
                        return await retry_response.json()

                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitError("Feedback rate limit exceeded", retry_after)

                if response.status != 200:
                    text = await response.text()
                    raise RemoteServiceError(f"Feedback failed: {response.status} - {text}")

                return await response.json()

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error during feedback submission: {e}")

    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics from central service."""
        await self._ensure_session()
        headers = await self._get_auth_headers()

        url = f"{self.api_url}/users/me/stats"

        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 401:
                    # Try re-authenticating once
                    self.access_token = None
                    headers = await self._get_auth_headers()
                    async with self.session.get(url, headers=headers) as retry_response:
                        if retry_response.status != 200:
                            return {}
                        return await retry_response.json()

                if response.status != 200:
                    return {}

                return await response.json()

        except aiohttp.ClientError:
            return {}

    async def health_check(self) -> bool:
        """Check if remote service is accessible."""
        await self._ensure_session()

        url = f"{self.api_url}/health"

        try:
            async with self.session.get(url) as response:
                return response.status == 200
        except:
            return False


async def test_client():
    """Test remote client (for development)."""
    from scripts.utils.config import load_config

    config = load_config()

    # Create mock config for testing
    config['reasoningbank']['central'] = {
        'enabled': True,
        'api_url': 'https://reasoningbank.example.com/api/v1',
        'api_key': 'test_key_123',
        'user_id': 'test_user',
        'org_id': 'test_org'
    }

    client = RemoteServiceClient(config)

    # Test health check
    print("Testing health check...")
    healthy = await client.health_check()
    print(f"  Service healthy: {healthy}")

    # Test pattern upload (will fail without real service)
    try:
        print("\nTesting pattern upload...")
        test_pattern = {
            'type': 'odoo_antipattern',
            'data': {
                'title': 'Test Pattern',
                'description': 'Test description',
                'domain': 'odoo.orm'
            },
            'confidence': 0.85
        }

        remote_id, response = await client.upload_pattern(test_pattern)
        print(f"  Uploaded: {remote_id}")
        print(f"  Response: {response}")
    except RemoteServiceError as e:
        print(f"  Expected error: {e}")

    # Test search
    try:
        print("\nTesting pattern search...")
        results = await client.search_patterns("N+1 query", k=5)
        print(f"  Found {len(results)} patterns")
    except RemoteServiceError as e:
        print(f"  Expected error: {e}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(test_client())
