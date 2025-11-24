#!/usr/bin/env python3
"""
Central Sync Status CLI - Display synchronization status and statistics.

Usage:
    rb-sync-status [--json]
"""

import asyncio
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.sync_manager import SyncManager
from scripts.consent_manager import ConsentManager
from scripts.remote_client import RemoteServiceClient
from scripts.database import get_database
from scripts.utils.config import load_config


def format_timestamp(ts: str) -> str:
    """Format ISO timestamp to readable string."""
    if not ts:
        return "Never"
    try:
        dt = datetime.fromisoformat(ts)
        now = datetime.utcnow()
        delta = now - dt

        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60} minutes ago"
        else:
            return "Just now"
    except:
        return ts


async def status_command(args):
    """Display central sync status."""
    config = load_config()

    # Check if central sync is enabled
    central_config = config.reasoningbank.get('central', {})
    enabled = central_config.get('enabled', False)

    if args.json:
        # JSON output
        status_data = await get_full_status(config, enabled)
        print(json.dumps(status_data, indent=2, default=str))
        return 0

    # Human-readable output
    print("="*60)
    print("Central Reasoning Bank - Sync Status")
    print("="*60)

    # Configuration
    print(f"\n📋 Configuration:")
    print(f"   Status: {'✅ Enabled' if enabled else '❌ Disabled'}")

    if not enabled:
        print("\n   To enable central sync:")
        print("   1. Set reasoningbank.central.enabled = true in config.yaml")
        print("   2. Configure API URL and key")
        print("   3. Run 'rb-init-central' to initialize database")
        return 0

    print(f"   API URL: {central_config.get('api_url', 'not configured')}")
    print(f"   User ID: {central_config.get('user_id', 'anonymous')}")

    consent_mode = central_config.get('consent', {}).get('mode', 'ask_each_time')
    print(f"   Consent Mode: {consent_mode}")

    # Get database
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    # Sync Manager status
    sync_mgr = SyncManager(db, config.reasoningbank)
    sync_status = await sync_mgr.get_sync_status()

    print(f"\n📤 Upload Status:")
    print(f"   Upload Enabled: {'✅ Yes' if sync_status['upload_enabled'] else '❌ No'}")
    print(f"   Last Upload: {format_timestamp(sync_status.get('last_upload', ''))}")

    queue_stats = sync_status.get('queue', {})
    if queue_stats:
        print(f"   Queue:")
        print(f"      Pending: {queue_stats.get('pending', 0)}")
        print(f"      Uploading: {queue_stats.get('uploading', 0)}")
        print(f"      Success: {queue_stats.get('success', 0)}")
        print(f"      Failed: {queue_stats.get('failed', 0)}")
    else:
        print(f"   Queue: Empty")

    print(f"\n📥 Download Status:")
    print(f"   Download Enabled: {'✅ Yes' if sync_status['download_enabled'] else '❌ No'}")
    print(f"   Last Download: {format_timestamp(sync_status.get('last_download', ''))}")
    print(f"   Cached Patterns: {sync_status.get('cache_size', 0)}")

    # Consent statistics
    consent_mgr = ConsentManager(db, config)
    consent_stats = await consent_mgr.get_consent_statistics()

    print(f"\n🔐 Consent Statistics:")
    print(f"   Total Requests: {consent_stats['total']}")
    print(f"   Approved: {consent_stats['approved']} ({consent_stats['approval_rate']:.1%})")
    print(f"   Denied: {consent_stats['denied']}")

    if consent_stats.get('by_mode'):
        print(f"   By Mode:")
        for mode, count in consent_stats['by_mode'].items():
            print(f"      {mode}: {count}")

    # Remote service health
    print(f"\n🌐 Remote Service:")
    try:
        client = RemoteServiceClient(config.reasoningbank)
        healthy = await client.health_check()
        print(f"   Status: {'✅ Reachable' if healthy else '❌ Unreachable'}")

        if healthy:
            user_stats = await client.get_user_stats()
            if user_stats:
                print(f"   Your Statistics:")
                print(f"      Patterns Contributed: {user_stats.get('patterns_contributed', 0)}")
                print(f"      Patterns Downloaded: {user_stats.get('patterns_downloaded', 0)}")
                print(f"      Upvotes Received: {user_stats.get('upvotes_received', 0)}")
                print(f"      Reputation: {user_stats.get('reputation_score', 0)}")

        await client.close()
    except Exception as e:
        print(f"   Status: ❌ Error checking service: {e}")

    print("\n" + "="*60)
    print("\n💡 Commands:")
    print("   rb-sync --upload      # Upload pending patterns")
    print("   rb-sync --download    # Download community patterns")
    print("   rb-sync --full        # Bidirectional sync")

    return 0


async def get_full_status(config, enabled: bool) -> dict:
    """Get full status as dict (for JSON output)."""
    if not enabled:
        return {
            "enabled": False,
            "message": "Central sync is not enabled"
        }

    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    sync_mgr = SyncManager(db, config.reasoningbank)
    consent_mgr = ConsentManager(db, config)

    sync_status = await sync_mgr.get_sync_status()
    consent_stats = await consent_mgr.get_consent_statistics()

    # Remote service health
    remote_status = {"reachable": False}
    try:
        client = RemoteServiceClient(config.reasoningbank)
        healthy = await client.health_check()
        remote_status["reachable"] = healthy

        if healthy:
            user_stats = await client.get_user_stats()
            remote_status["user_stats"] = user_stats

        await client.close()
    except Exception as e:
        remote_status["error"] = str(e)

    return {
        "enabled": True,
        "config": {
            "api_url": config.reasoningbank.get('central', {}).get('api_url'),
            "consent_mode": config.reasoningbank.get('central', {}).get('consent', {}).get('mode')
        },
        "sync": sync_status,
        "consent": consent_stats,
        "remote": remote_status
    }


async def main():
    parser = argparse.ArgumentParser(
        description="Display central sync status and statistics"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()
    return await status_command(args)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
