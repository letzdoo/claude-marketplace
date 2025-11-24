#!/usr/bin/env python3
"""
Initialize centralized reasoning bank infrastructure.

This script migrates the local-only reasoning bank database to support
centralized pattern sharing with user consent and remote synchronization.

Usage:
    rb-init-central [--db-path PATH] [--dry-run]
"""

import aiosqlite
import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime


DEFAULT_DB_PATH = "~/.reasoningbank/odoo_patterns.db"


async def check_existing_schema(db_path: str) -> dict:
    """Check if tables already exist."""
    async with aiosqlite.connect(db_path) as db:
        tables = {}

        # Check for existing central tables
        async with db.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('sync_queue', 'user_consent', 'community_patterns')
        """) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                tables[row[0]] = True

        # Check for new columns in patterns table
        async with db.execute("PRAGMA table_info(patterns)") as cursor:
            cols = await cursor.fetchall()
            col_names = [col[1] for col in cols]
            tables['patterns_migrated'] = all(c in col_names for c in [
                'is_uploaded', 'remote_id', 'uploaded_at', 'consent_required', 'is_local_only'
            ])

        return tables


async def migrate_database(db_path: str, dry_run: bool = False):
    """Add centralized sync infrastructure to existing database."""

    print(f"🔍 Checking database: {db_path}")

    if not Path(db_path).exists():
        print(f"❌ Database not found at {db_path}")
        print(f"   Run 'rb-init-db' first to create the base database.")
        sys.exit(1)

    existing = await check_existing_schema(db_path)

    if dry_run:
        print("\n📋 Dry run mode - no changes will be made\n")

    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys=ON")

        # Track if any changes were made
        changes_made = False

        # 1. Create sync_queue table
        if 'sync_queue' not in existing:
            print("📦 Creating sync_queue table...")
            if not dry_run:
                await db.execute("""
                    CREATE TABLE sync_queue (
                        id TEXT PRIMARY KEY,
                        pattern_id TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        status TEXT NOT NULL,
                        retry_count INTEGER DEFAULT 0,
                        last_retry_at TEXT,
                        error_message TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY(pattern_id) REFERENCES patterns(id) ON DELETE CASCADE
                    )
                """)
                await db.execute("""
                    CREATE INDEX idx_sync_queue_status ON sync_queue(status)
                """)
                await db.execute("""
                    CREATE INDEX idx_sync_queue_pattern ON sync_queue(pattern_id)
                """)
                changes_made = True
            print("   ✅ sync_queue table created")
        else:
            print("   ⏭️  sync_queue table already exists")

        # 2. Create user_consent table
        if 'user_consent' not in existing:
            print("📦 Creating user_consent table...")
            if not dry_run:
                await db.execute("""
                    CREATE TABLE user_consent (
                        id TEXT PRIMARY KEY,
                        pattern_id TEXT NOT NULL,
                        consent_given BOOLEAN NOT NULL,
                        consent_timestamp TEXT NOT NULL,
                        consent_mode TEXT,
                        notes TEXT,
                        FOREIGN KEY(pattern_id) REFERENCES patterns(id) ON DELETE CASCADE
                    )
                """)
                await db.execute("""
                    CREATE INDEX idx_consent_pattern ON user_consent(pattern_id)
                """)
                changes_made = True
            print("   ✅ user_consent table created")
        else:
            print("   ⏭️  user_consent table already exists")

        # 3. Create community_patterns table
        if 'community_patterns' not in existing:
            print("📦 Creating community_patterns table...")
            if not dry_run:
                await db.execute("""
                    CREATE TABLE community_patterns (
                        id TEXT PRIMARY KEY,
                        remote_id TEXT UNIQUE NOT NULL,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        upvotes INTEGER DEFAULT 0,
                        downvotes INTEGER DEFAULT 0,
                        source_org TEXT,
                        downloaded_at TEXT NOT NULL,
                        last_synced_at TEXT NOT NULL,
                        is_cached BOOLEAN DEFAULT 1
                    )
                """)
                await db.execute("""
                    CREATE INDEX idx_community_type ON community_patterns(pattern_type)
                """)
                await db.execute("""
                    CREATE INDEX idx_community_remote ON community_patterns(remote_id)
                """)
                changes_made = True
            print("   ✅ community_patterns table created")
        else:
            print("   ⏭️  community_patterns table already exists")

        # 4. Migrate patterns table
        if not existing.get('patterns_migrated', False):
            print("📦 Migrating patterns table (adding central sync columns)...")
            if not dry_run:
                # SQLite doesn't support multiple ALTER TABLE in one transaction easily
                # Add columns one by one
                try:
                    await db.execute("ALTER TABLE patterns ADD COLUMN is_uploaded BOOLEAN DEFAULT 0")
                except Exception:
                    pass  # Column might already exist

                try:
                    await db.execute("ALTER TABLE patterns ADD COLUMN remote_id TEXT UNIQUE")
                except Exception:
                    pass

                try:
                    await db.execute("ALTER TABLE patterns ADD COLUMN uploaded_at TEXT")
                except Exception:
                    pass

                try:
                    await db.execute("ALTER TABLE patterns ADD COLUMN consent_required BOOLEAN DEFAULT 1")
                except Exception:
                    pass

                try:
                    await db.execute("ALTER TABLE patterns ADD COLUMN is_local_only BOOLEAN DEFAULT 0")
                except Exception:
                    pass

                changes_made = True
            print("   ✅ patterns table migrated")
        else:
            print("   ⏭️  patterns table already migrated")

        # 5. Log migration event
        if changes_made and not dry_run:
            await db.execute("""
                INSERT INTO events (event_type, entity_type, data)
                VALUES (?, ?, ?)
            """, (
                'central_migration',
                'database',
                '{"version": "1.0.0", "timestamp": "' + datetime.utcnow().isoformat() + '"}'
            ))

        if not dry_run:
            await db.commit()

    if dry_run:
        print("\n✅ Dry run complete - no changes were made")
    elif changes_made:
        print("\n✅ Database migration complete!")
        print("\n📝 Next steps:")
        print("   1. Configure central service in config.yaml:")
        print("      reasoningbank.central.api_url = https://your-service.com/api/v1")
        print("      reasoningbank.central.api_key = YOUR_API_KEY")
        print("   2. Set consent mode:")
        print("      reasoningbank.central.consent.mode = ask_each_time")
        print("   3. Start using with: rb-sync --upload")
    else:
        print("\n✅ Database is already up to date!")


async def rollback_migration(db_path: str):
    """Rollback centralized migration (for testing)."""
    print(f"🔄 Rolling back central migration: {db_path}")

    if not Path(db_path).exists():
        print(f"❌ Database not found at {db_path}")
        sys.exit(1)

    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys=OFF")  # Disable to allow column drops

        # Drop central tables
        await db.execute("DROP TABLE IF EXISTS sync_queue")
        await db.execute("DROP TABLE IF EXISTS user_consent")
        await db.execute("DROP TABLE IF EXISTS community_patterns")

        # SQLite doesn't support DROP COLUMN easily, so we'd need to recreate table
        # For now, just clear the values
        try:
            await db.execute("UPDATE patterns SET is_uploaded = 0, remote_id = NULL, uploaded_at = NULL")
        except Exception:
            pass

        await db.commit()

    print("✅ Rollback complete")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize centralized reasoning bank infrastructure"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=DEFAULT_DB_PATH,
        help=f"Path to database (default: {DEFAULT_DB_PATH})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check what would be changed without making changes"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback central migration (WARNING: deletes central data)"
    )

    args = parser.parse_args()
    db_path = Path(args.db_path).expanduser()

    if args.rollback:
        if input("⚠️  Are you sure? This will delete all central sync data (y/N): ").lower() != 'y':
            print("Cancelled")
            sys.exit(0)
        asyncio.run(rollback_migration(str(db_path)))
    else:
        asyncio.run(migrate_database(str(db_path), args.dry_run))


if __name__ == "__main__":
    main()
