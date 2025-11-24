"""
User Consent Manager for Centralized Reasoning Bank.

Handles user acknowledgment and consent before sharing patterns
with the central knowledge base.
"""

import json
import sys
from datetime import datetime
from typing import Dict, Optional, Any, Tuple
from pathlib import Path

from scripts.utils.ulid_gen import generate_ulid
from scripts.utils.config import Config
from scripts.utils.pii import redact_memory_item


class ConsentManager:
    """Manages user consent for pattern sharing."""

    def __init__(self, db, config: Config):
        self.db = db
        self.config = config
        self.central_config = config.reasoningbank.get('central', {})
        self.consent_config = self.central_config.get('consent', {})

    async def check_consent_required(self, pattern: Dict[str, Any]) -> bool:
        """Check if consent is required for this pattern."""

        # If central sync is disabled, no consent needed
        if not self.central_config.get('enabled', False):
            return False

        # Check if pattern is marked as local-only
        if pattern.get('is_local_only', False):
            return False

        # Check if already uploaded
        if pattern.get('is_uploaded', False):
            return False

        # Check consent mode
        mode = self.consent_config.get('mode', 'ask_each_time')

        if mode == 'always_deny':
            return False  # Don't even ask

        if mode == 'always_allow':
            # Check domain-specific blocks
            pattern_data = json.loads(pattern['pattern_data']) if isinstance(pattern['pattern_data'], str) else pattern['pattern_data']
            domain = pattern_data.get('domain', '')
            blocked_domains = self.consent_config.get('block_domains', [])

            if domain in blocked_domains:
                return True  # Ask even in always_allow mode

            # Auto-approve based on confidence threshold
            if self.consent_config.get('auto_approve_high_confidence', False):
                min_conf = self.consent_config.get('min_confidence_auto', 0.90)
                if pattern.get('confidence', 0) >= min_conf:
                    return False  # Auto-approve

        return True

    async def request_consent(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any],
        confidence: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Request user consent to share a pattern.

        Returns:
            (consent_given: bool, consent_mode: str)
        """

        # Get existing consent if any
        existing = await self._get_existing_consent(pattern_id)
        if existing:
            return existing['consent_given'], existing['consent_mode']

        # Check global mode
        mode = self.consent_config.get('mode', 'ask_each_time')

        if mode == 'always_deny':
            await self._record_consent(pattern_id, False, 'global_deny')
            return False, 'global_deny'

        if mode == 'always_allow':
            # Check domain-specific rules
            domain = pattern_data.get('domain', '')
            blocked_domains = self.consent_config.get('block_domains', [])

            if domain in blocked_domains:
                # Domain is blocked, ask user
                pass  # Fall through to prompt
            else:
                # Auto-approve
                await self._record_consent(pattern_id, True, 'global_allow')
                return True, 'global_allow'

        if mode == 'domain_specific':
            domain = pattern_data.get('domain', '')
            share_domains = self.consent_config.get('share_domains', [])
            blocked_domains = self.consent_config.get('block_domains', [])

            if domain in blocked_domains:
                await self._record_consent(pattern_id, False, 'domain_block')
                return False, 'domain_block'

            if domain in share_domains:
                await self._record_consent(pattern_id, True, 'domain_allow')
                return True, 'domain_allow'

            # Domain not in either list, ask user
            pass  # Fall through to prompt

        # mode == 'ask_each_time' or need explicit consent
        return await self._prompt_user_consent(pattern_id, pattern_data, confidence)

    async def _prompt_user_consent(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any],
        confidence: float
    ) -> Tuple[bool, Optional[str]]:
        """Prompt user via CLI for consent."""

        # Redact sensitive info for display
        display_data = self._prepare_display_data(pattern_data)

        # Build consent prompt
        print("\n" + "="*60)
        print("🌐 New Pattern Ready to Share with Community")
        print("="*60)
        print(f"\n📋 Pattern: {display_data.get('title', 'Untitled')}")
        print(f"🏷️  Domain: {display_data.get('domain', 'general')}")
        print(f"📊 Confidence: {confidence:.2f}")
        print(f"🔖 Tags: {', '.join(display_data.get('tags', []))}")

        # Show preview
        if self.consent_config.get('show_preview', True):
            print("\n📄 Preview:")
            print("─" * 60)
            description = display_data.get('description', '')
            if len(description) > 200:
                description = description[:197] + "..."
            print(description)
            print("─" * 60)

        print("\nThis pattern will be anonymized and shared with the community")
        print("to help other developers avoid similar issues.")

        # Prompt for decision
        print("\nOptions:")
        print("  [s] Share with Community (recommended)")
        print("  [l] Keep Local Only")
        print("  [v] View Full Pattern")
        if self.consent_config.get('remember_choice', True):
            domain = display_data.get('domain', '')
            print(f"  [a] Always share {domain} patterns")
            print(f"  [n] Never share {domain} patterns")

        # Get user input
        while True:
            try:
                choice = input("\nYour choice [s/l/v/a/n]: ").lower().strip()

                if choice == 's':
                    await self._record_consent(pattern_id, True, 'explicit')
                    print("✅ Pattern will be shared. Thank you for contributing!")
                    return True, 'explicit'

                elif choice == 'l':
                    await self._record_consent(pattern_id, False, 'explicit')
                    print("✅ Pattern will remain local only.")
                    return False, 'explicit'

                elif choice == 'v':
                    self._display_full_pattern(pattern_data)
                    continue

                elif choice == 'a':
                    if not self.consent_config.get('remember_choice', True):
                        print("❌ Remember choice is disabled in config")
                        continue

                    domain = display_data.get('domain', '')
                    await self._save_domain_preference(domain, True)
                    await self._record_consent(pattern_id, True, 'domain_allow')
                    print(f"✅ All {domain} patterns will be auto-shared going forward.")
                    return True, 'domain_allow'

                elif choice == 'n':
                    if not self.consent_config.get('remember_choice', True):
                        print("❌ Remember choice is disabled in config")
                        continue

                    domain = display_data.get('domain', '')
                    await self._save_domain_preference(domain, False)
                    await self._record_consent(pattern_id, False, 'domain_block')
                    print(f"✅ {domain} patterns will not be shared going forward.")
                    return False, 'domain_block'

                else:
                    print("❌ Invalid choice. Please enter s, l, v, a, or n.")

            except (KeyboardInterrupt, EOFError):
                print("\n\n⚠️  Consent cancelled. Pattern will remain local only.")
                await self._record_consent(pattern_id, False, 'cancelled')
                return False, 'cancelled'

    def _prepare_display_data(self, pattern_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare pattern data for display (redact sensitive info)."""

        # Make a copy
        display = pattern_data.copy()

        # Redact PII if configured
        if self.consent_config.get('anonymize_paths', True):
            display = self._redact_paths(display)

        if self.consent_config.get('anonymize_org', True):
            display = self._redact_org_info(display)

        return display

    def _redact_paths(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact file paths from pattern data."""
        # Use existing PII redaction utility
        if self.config.reasoningbank.get('distill', {}).get('redact_pii', False):
            data = redact_memory_item(data)

        return data

    def _redact_org_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact organization-specific information."""
        # Remove source if present
        if 'source' in data:
            if 'org_id' in data['source']:
                data['source']['org_id'] = '<redacted>'
            if 'user_id' in data['source']:
                data['source']['user_id'] = '<anonymous>'

        return data

    def _display_full_pattern(self, pattern_data: Dict[str, Any]):
        """Display the full pattern content."""
        print("\n" + "="*60)
        print("Full Pattern Content")
        print("="*60)
        print(json.dumps(pattern_data, indent=2))
        print("="*60)

    async def _record_consent(
        self,
        pattern_id: str,
        consent_given: bool,
        consent_mode: str,
        notes: Optional[str] = None
    ) -> None:
        """Record consent decision in database."""

        consent_id = generate_ulid()
        timestamp = datetime.utcnow().isoformat()

        async with await self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO user_consent (id, pattern_id, consent_given, consent_timestamp, consent_mode, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (consent_id, pattern_id, consent_given, timestamp, consent_mode, notes))

            # Update pattern record
            await conn.execute("""
                UPDATE patterns
                SET is_local_only = ?
                WHERE id = ?
            """, (not consent_given, pattern_id))

            await conn.commit()

    async def _get_existing_consent(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get existing consent record for pattern."""

        async with await self.db.get_connection() as conn:
            async with conn.execute("""
                SELECT * FROM user_consent
                WHERE pattern_id = ?
                ORDER BY consent_timestamp DESC
                LIMIT 1
            """, (pattern_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)

        return None

    async def _save_domain_preference(self, domain: str, allow: bool) -> None:
        """Save domain-specific preference to config."""
        # NOTE: This modifies runtime config, not the config file
        # In production, you'd want to persist this to config.yaml or a separate preferences file

        if allow:
            if 'share_domains' not in self.consent_config:
                self.consent_config['share_domains'] = []
            if domain not in self.consent_config['share_domains']:
                self.consent_config['share_domains'].append(domain)

            # Remove from block list if present
            if 'block_domains' in self.consent_config:
                if domain in self.consent_config['block_domains']:
                    self.consent_config['block_domains'].remove(domain)
        else:
            if 'block_domains' not in self.consent_config:
                self.consent_config['block_domains'] = []
            if domain not in self.consent_config['block_domains']:
                self.consent_config['block_domains'].append(domain)

            # Remove from share list if present
            if 'share_domains' in self.consent_config:
                if domain in self.consent_config['share_domains']:
                    self.consent_config['share_domains'].remove(domain)

        # TODO: Persist to config file
        # For now, just update runtime config

    async def get_consent_statistics(self) -> Dict[str, Any]:
        """Get statistics about consent decisions."""

        async with await self.db.get_connection() as conn:
            # Total consents
            async with conn.execute("SELECT COUNT(*) FROM user_consent") as cursor:
                row = await cursor.fetchone()
                total = row[0] if row else 0

            # Approved vs denied
            async with conn.execute("""
                SELECT consent_given, COUNT(*) as count
                FROM user_consent
                GROUP BY consent_given
            """) as cursor:
                rows = await cursor.fetchall()
                approved = 0
                denied = 0
                for row in rows:
                    if row[0]:
                        approved = row[1]
                    else:
                        denied = row[1]

            # By mode
            async with conn.execute("""
                SELECT consent_mode, COUNT(*) as count
                FROM user_consent
                GROUP BY consent_mode
            """) as cursor:
                rows = await cursor.fetchall()
                by_mode = {row[0]: row[1] for row in rows}

        return {
            'total': total,
            'approved': approved,
            'denied': denied,
            'approval_rate': approved / total if total > 0 else 0,
            'by_mode': by_mode
        }


async def test_consent_flow():
    """Test consent manager (for development)."""
    from scripts.database import Database
    from scripts.utils.config import load_config

    config = load_config()
    db = Database()
    await db.init_schema()

    manager = ConsentManager(db, config)

    # Test pattern
    test_pattern = {
        'id': 'test_001',
        'title': 'N+1 Query in Computed Field',
        'description': 'Using search() in loop within computed field causes N+1 queries. Fix: Use read_group().',
        'domain': 'odoo.orm',
        'tags': ['performance', 'orm'],
        'confidence': 0.85,
        'is_uploaded': False,
        'is_local_only': False
    }

    consent, mode = await manager.request_consent('test_001', test_pattern, 0.85)
    print(f"\nResult: consent={consent}, mode={mode}")

    stats = await manager.get_consent_statistics()
    print(f"\nStats: {stats}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_consent_flow())
