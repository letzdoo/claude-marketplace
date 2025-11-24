"""
Sync Manager for Centralized Reasoning Bank.

Handles pattern upload/download queue, retry logic, and background synchronization.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from scripts.remote_client import (
    RemoteServiceClient,
    RemoteServiceError,
    NetworkError,
    RateLimitError,
    AuthenticationError
)
from scripts.utils.ulid_gen import generate_ulid
from scripts.utils.pii import redact_memory_item


class SyncManager:
    """Manages pattern synchronization with central service."""

    def __init__(self, db, config: Dict[str, Any], remote_client: Optional[RemoteServiceClient] = None):
        self.db = db
        self.config = config
        self.central_config = config.get('reasoningbank', {}).get('central', {})
        self.sync_config = self.central_config.get('sync', {})

        self.client = remote_client or RemoteServiceClient(config)

        self.upload_enabled = self.sync_config.get('upload_enabled', True)
        self.download_enabled = self.sync_config.get('download_enabled', True)
        self.batch_size = self.sync_config.get('batch_size', 10)
        self.retry_max = self.sync_config.get('retry_max', 5)
        self.retry_backoff_base = self.sync_config.get('retry_backoff_base', 2)

        self._is_syncing = False
        self._sync_task: Optional[asyncio.Task] = None

    async def queue_pattern_upload(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any],
        confidence: float
    ) -> str:
        """
        Add a pattern to the upload queue.

        Returns:
            Queue item ID
        """
        if not self.upload_enabled:
            return ""

        queue_id = generate_ulid()
        timestamp = datetime.utcnow().isoformat()

        async with await self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO sync_queue (id, pattern_id, operation, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (queue_id, pattern_id, 'upload', 'pending', timestamp))
            await conn.commit()

        # Log event
        await self._log_event('pattern_queued', pattern_id, {'queue_id': queue_id})

        return queue_id

    async def process_upload_queue(self, immediate: bool = False) -> Dict[str, int]:
        """
        Process pending uploads in the queue.

        Args:
            immediate: If True, skip retry backoff delays

        Returns:
            Dict with counts: {success, failed, skipped}
        """
        if not self.upload_enabled:
            return {'success': 0, 'failed': 0, 'skipped': 0}

        if self._is_syncing and not immediate:
            return {'success': 0, 'failed': 0, 'skipped': 0, 'message': 'Sync already in progress'}

        self._is_syncing = True
        stats = {'success': 0, 'failed': 0, 'skipped': 0}

        try:
            # Get pending items
            pending = await self._get_pending_uploads()

            for item in pending[:self.batch_size]:
                queue_id = item['id']
                pattern_id = item['pattern_id']
                retry_count = item['retry_count']

                # Check if we should retry
                if retry_count >= self.retry_max:
                    stats['failed'] += 1
                    await self._mark_failed(queue_id, "Max retries exceeded")
                    continue

                # Check retry backoff
                if item['last_retry_at'] and not immediate:
                    last_retry = datetime.fromisoformat(item['last_retry_at'])
                    wait_seconds = self.retry_backoff_base ** retry_count
                    next_retry = last_retry + timedelta(seconds=wait_seconds)

                    if datetime.utcnow() < next_retry:
                        stats['skipped'] += 1
                        continue

                # Mark as uploading
                await self._mark_uploading(queue_id)

                # Get pattern data
                pattern = await self._get_pattern(pattern_id)
                if not pattern:
                    stats['failed'] += 1
                    await self._mark_failed(queue_id, "Pattern not found")
                    continue

                # Upload pattern
                result = await self._upload_pattern(pattern)

                if result['success']:
                    stats['success'] += 1
                    await self._mark_uploaded(queue_id, pattern_id, result['remote_id'])
                else:
                    stats['failed'] += 1
                    await self._mark_retry(queue_id, result['error'])

        finally:
            self._is_syncing = False

        return stats

    async def _upload_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a single pattern."""
        try:
            # Prepare pattern data
            pattern_data = json.loads(pattern['pattern_data']) if isinstance(pattern['pattern_data'], str) else pattern['pattern_data']

            # Redact PII if configured
            privacy_config = self.central_config.get('privacy', {})
            if privacy_config.get('redact_file_paths', True):
                pattern_data = redact_memory_item(pattern_data)

            # Prepare upload payload
            upload_data = {
                'type': pattern['type'],
                'data': pattern_data,
                'confidence': pattern['confidence']
            }

            # Upload via remote client
            remote_id, response = await self.client.upload_pattern(
                upload_data,
                metadata={
                    'created_at': pattern['created_at'],
                    'usage_count': pattern.get('usage_count', 0),
                    'source_version': '1.0.0'
                }
            )

            return {
                'success': True,
                'remote_id': remote_id,
                'response': response
            }

        except AuthenticationError as e:
            return {'success': False, 'error': f"Authentication failed: {e}", 'retriable': False}

        except RateLimitError as e:
            return {'success': False, 'error': f"Rate limited: {e}", 'retriable': True}

        except NetworkError as e:
            return {'success': False, 'error': f"Network error: {e}", 'retriable': True}

        except RemoteServiceError as e:
            return {'success': False, 'error': f"Service error: {e}", 'retriable': False}

        except Exception as e:
            return {'success': False, 'error': f"Unexpected error: {e}", 'retriable': False}

    async def download_community_patterns(
        self,
        query: Optional[str] = None,
        domains: Optional[List[str]] = None,
        k: int = 100
    ) -> Dict[str, int]:
        """
        Download community patterns from central service.

        Args:
            query: Optional query string (if None, gets top patterns for domains)
            domains: Optional list of domains to filter
            k: Number of patterns to download

        Returns:
            Dict with counts: {downloaded, cached, skipped}
        """
        if not self.download_enabled:
            return {'downloaded': 0, 'cached': 0, 'skipped': 0}

        stats = {'downloaded': 0, 'cached': 0, 'skipped': 0}

        try:
            # Build filters
            filters = {}

            if domains:
                filters['domains'] = domains

            retrieval_config = self.central_config.get('retrieval', {})
            filters['min_confidence'] = retrieval_config.get('min_community_confidence', 0.65)
            filters['min_upvotes'] = retrieval_config.get('min_community_upvotes', 3)

            # Search patterns
            if query:
                patterns = await self.client.search_patterns(query, k=k, filters=filters)
            else:
                # Get top patterns for each domain
                patterns = []
                for domain in (domains or self._get_active_domains()):
                    domain_filters = {**filters, 'domain': domain}
                    domain_patterns = await self.client.search_patterns(
                        query=f"patterns for {domain}",
                        k=k // len(domains or self._get_active_domains()),
                        filters=domain_filters
                    )
                    patterns.extend(domain_patterns)

            # Cache patterns
            for pattern in patterns:
                cached = await self._cache_community_pattern(pattern)
                if cached:
                    stats['cached'] += 1
                else:
                    stats['skipped'] += 1

            stats['downloaded'] = len(patterns)

        except RemoteServiceError as e:
            print(f"⚠️  Failed to download community patterns: {e}")

        return stats

    async def _cache_community_pattern(self, pattern: Dict[str, Any]) -> bool:
        """Cache a community pattern locally."""
        try:
            remote_id = pattern.get('remote_id', '')
            if not remote_id:
                return False

            # Check if already cached
            async with await self.db.get_connection() as conn:
                async with conn.execute("""
                    SELECT id FROM community_patterns WHERE remote_id = ?
                """, (remote_id,)) as cursor:
                    existing = await cursor.fetchone()

                if existing:
                    # Update existing
                    await conn.execute("""
                        UPDATE community_patterns
                        SET pattern_data = ?,
                            confidence = ?,
                            usage_count = ?,
                            upvotes = ?,
                            downvotes = ?,
                            last_synced_at = ?
                        WHERE remote_id = ?
                    """, (
                        json.dumps(pattern.get('data', {})),
                        pattern.get('confidence', 0.7),
                        pattern.get('usage_count', 0),
                        pattern.get('upvotes', 0),
                        pattern.get('downvotes', 0),
                        datetime.utcnow().isoformat(),
                        remote_id
                    ))
                else:
                    # Insert new
                    local_id = generate_ulid()
                    timestamp = datetime.utcnow().isoformat()

                    await conn.execute("""
                        INSERT INTO community_patterns (
                            id, remote_id, pattern_type, pattern_data,
                            confidence, usage_count, upvotes, downvotes,
                            source_org, downloaded_at, last_synced_at, is_cached
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        local_id,
                        remote_id,
                        pattern.get('type', 'community_pattern'),
                        json.dumps(pattern.get('data', {})),
                        pattern.get('confidence', 0.7),
                        pattern.get('usage_count', 0),
                        pattern.get('upvotes', 0),
                        pattern.get('downvotes', 0),
                        pattern.get('source_org'),
                        timestamp,
                        timestamp,
                        True
                    ))

                await conn.commit()

            return True

        except Exception as e:
            print(f"⚠️  Failed to cache pattern {pattern.get('remote_id', 'unknown')}: {e}")
            return False

    async def periodic_sync(self, interval_seconds: int = 21600):
        """
        Run periodic sync in background.

        Args:
            interval_seconds: Sync interval (default 6 hours)
        """
        while True:
            try:
                await asyncio.sleep(interval_seconds)

                print(f"🔄 Running periodic sync...")

                # Upload pending patterns
                upload_stats = await self.process_upload_queue()
                print(f"   Uploaded: {upload_stats['success']}, Failed: {upload_stats['failed']}")

                # Download community patterns
                download_stats = await self.download_community_patterns()
                print(f"   Downloaded: {download_stats['downloaded']}, Cached: {download_stats['cached']}")

            except Exception as e:
                print(f"⚠️  Periodic sync error: {e}")

    async def get_sync_status(self) -> Dict[str, Any]:
        """Get sync status and statistics."""
        async with await self.db.get_connection() as conn:
            # Queue stats
            async with conn.execute("""
                SELECT status, COUNT(*) as count
                FROM sync_queue
                GROUP BY status
            """) as cursor:
                rows = await cursor.fetchall()
                queue_stats = {row[0]: row[1] for row in rows}

            # Last successful upload
            async with conn.execute("""
                SELECT MAX(uploaded_at) FROM patterns WHERE is_uploaded = 1
            """) as cursor:
                row = await cursor.fetchone()
                last_upload = row[0] if row and row[0] else None

            # Community pattern cache size
            async with conn.execute("""
                SELECT COUNT(*) FROM community_patterns
            """) as cursor:
                row = await cursor.fetchone()
                cache_size = row[0] if row else 0

            # Last download
            async with conn.execute("""
                SELECT MAX(last_synced_at) FROM community_patterns
            """) as cursor:
                row = await cursor.fetchone()
                last_download = row[0] if row and row[0] else None

        return {
            'is_syncing': self._is_syncing,
            'queue': queue_stats,
            'last_upload': last_upload,
            'last_download': last_download,
            'cache_size': cache_size,
            'upload_enabled': self.upload_enabled,
            'download_enabled': self.download_enabled
        }

    # Helper methods

    async def _get_pending_uploads(self) -> List[Dict[str, Any]]:
        """Get pending upload items."""
        async with await self.db.get_connection() as conn:
            async with conn.execute("""
                SELECT * FROM sync_queue
                WHERE status IN ('pending', 'failed')
                ORDER BY created_at ASC
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def _get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get pattern from database."""
        async with await self.db.get_connection() as conn:
            async with conn.execute("""
                SELECT * FROM patterns WHERE id = ?
            """, (pattern_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def _mark_uploading(self, queue_id: str):
        """Mark queue item as uploading."""
        async with await self.db.get_connection() as conn:
            await conn.execute("""
                UPDATE sync_queue
                SET status = 'uploading'
                WHERE id = ?
            """, (queue_id,))
            await conn.commit()

    async def _mark_uploaded(self, queue_id: str, pattern_id: str, remote_id: str):
        """Mark queue item and pattern as successfully uploaded."""
        timestamp = datetime.utcnow().isoformat()

        async with await self.db.get_connection() as conn:
            # Update queue
            await conn.execute("""
                UPDATE sync_queue
                SET status = 'success'
                WHERE id = ?
            """, (queue_id,))

            # Update pattern
            await conn.execute("""
                UPDATE patterns
                SET is_uploaded = 1, remote_id = ?, uploaded_at = ?
                WHERE id = ?
            """, (remote_id, timestamp, pattern_id))

            await conn.commit()

        await self._log_event('pattern_uploaded', pattern_id, {'remote_id': remote_id})

    async def _mark_retry(self, queue_id: str, error_message: str):
        """Mark queue item for retry."""
        timestamp = datetime.utcnow().isoformat()

        async with await self.db.get_connection() as conn:
            await conn.execute("""
                UPDATE sync_queue
                SET status = 'pending',
                    retry_count = retry_count + 1,
                    last_retry_at = ?,
                    error_message = ?
                WHERE id = ?
            """, (timestamp, error_message, queue_id))
            await conn.commit()

    async def _mark_failed(self, queue_id: str, error_message: str):
        """Mark queue item as permanently failed."""
        async with await self.db.get_connection() as conn:
            await conn.execute("""
                UPDATE sync_queue
                SET status = 'failed',
                    error_message = ?
                WHERE id = ?
            """, (error_message, queue_id))
            await conn.commit()

    async def _log_event(self, event_type: str, entity_id: str, data: Dict[str, Any]):
        """Log event to events table."""
        async with await self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO events (event_type, entity_id, entity_type, data)
                VALUES (?, ?, ?, ?)
            """, (event_type, entity_id, 'pattern', json.dumps(data)))
            await conn.commit()

    def _get_active_domains(self) -> List[str]:
        """Get list of active Odoo domains from config."""
        return self.config.get('reasoningbank', {}).get('odoo', {}).get('domains', [
            'odoo.orm', 'odoo.security', 'odoo.views', 'odoo.performance'
        ])


async def test_sync_manager():
    """Test sync manager (for development)."""
    from scripts.database import Database
    from scripts.utils.config import load_config

    config = load_config()
    db = Database()
    await db.init_schema()

    manager = SyncManager(db, config)

    # Get sync status
    status = await manager.get_sync_status()
    print(f"Sync status: {json.dumps(status, indent=2)}")

    # Test upload queue processing (will fail without real service)
    stats = await manager.process_upload_queue()
    print(f"Upload stats: {stats}")


if __name__ == "__main__":
    asyncio.run(test_sync_manager())
