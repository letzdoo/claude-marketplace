#!/usr/bin/env python3
"""
Central Sync CLI - Manual synchronization with central reasoning bank service.

Usage:
    rb-sync --upload           # Upload pending patterns
    rb-sync --download         # Download community patterns
    rb-sync --full             # Bidirectional sync
"""

import asyncio
import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.sync_manager import SyncManager
from scripts.database import get_database
from scripts.utils.config import load_config


async def sync_command(args):
    """Execute sync command."""
    config = load_config()

    # Check if central sync is enabled
    central_config = config.reasoningbank.get('central', {})
    if not central_config.get('enabled', False):
        print("❌ Central sync is not enabled.")
        print("   Enable it in config.yaml: reasoningbank.central.enabled = true")
        return 1

    # Get database
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    # Create sync manager
    sync_mgr = SyncManager(db, config.reasoningbank)

    # Determine operation
    if args.full:
        upload_enabled = True
        download_enabled = True
    else:
        upload_enabled = args.upload
        download_enabled = args.download

    # Upload patterns
    if upload_enabled:
        print("📤 Uploading pending patterns...")
        upload_stats = await sync_mgr.process_upload_queue(immediate=True)

        print(f"   ✅ Success: {upload_stats['success']}")
        print(f"   ❌ Failed: {upload_stats['failed']}")
        print(f"   ⏭️  Skipped: {upload_stats['skipped']}")

        if args.json:
            print(json.dumps({"upload": upload_stats}, indent=2))

    # Download patterns
    if download_enabled:
        print("\n📥 Downloading community patterns...")

        # Get domains from config or use defaults
        domains = args.domains if args.domains else None
        k = args.limit if args.limit else 100

        download_stats = await sync_mgr.download_community_patterns(
            query=args.query,
            domains=domains,
            k=k
        )

        print(f"   📦 Downloaded: {download_stats['downloaded']}")
        print(f"   💾 Cached: {download_stats['cached']}")
        print(f"   ⏭️  Skipped: {download_stats['skipped']}")

        if args.json:
            print(json.dumps({"download": download_stats}, indent=2))

    print("\n✅ Sync complete!")
    return 0


async def main():
    parser = argparse.ArgumentParser(
        description="Manual synchronization with central reasoning bank"
    )

    # Sync operations
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload pending patterns to central service"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download community patterns from central service"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Perform full bidirectional sync (upload + download)"
    )

    # Download options
    parser.add_argument(
        "--query",
        type=str,
        help="Query string for downloading specific patterns"
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        help="Filter download by domains (e.g., odoo.orm odoo.security)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum patterns to download (default: 100)"
    )

    # Output format
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Default to full sync if no operation specified
    if not args.upload and not args.download and not args.full:
        args.full = True

    return await sync_command(args)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
