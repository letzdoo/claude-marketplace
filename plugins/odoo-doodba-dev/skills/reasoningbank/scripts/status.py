#!/usr/bin/env python3
"""Check ReasoningBank status and statistics."""

import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database import get_database
from scripts.utils.config import load_config


async def main():
    """Show ReasoningBank status."""
    config = load_config()

    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())

    # Check if DB exists
    if not Path(db_path).exists():
        print(f"❌ Database not found at {db_path}")
        print(f"\nRun: uv run scripts/init_db.py")
        return 1

    db = get_database(db_path)

    # Get statistics
    stats = await db.get_statistics()

    # Display
    print("ReasoningBank Status")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")
    print(f"Size: {Path(db_path).stat().st_size / 1024 / 1024:.2f} MB")
    print(f"\nMemories: {stats['total_memories']}")
    print(f"Trajectories: {stats['total_trajectories']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    print(f"Average Confidence: {stats['avg_confidence']:.2f}")

    print(f"\nTop Memories (by usage):")
    for i, mem in enumerate(stats['top_memories'], 1):
        print(f"  {i}. {mem['title']}")
        print(f"     Used: {mem['usage_count']} times")

    print(f"\nConfiguration:")
    print(f"  Retrieve k: {config.retrieve.k}")
    print(f"  Consolidate every: {config.consolidate.run_every_new_items} new items")
    print(f"  MaTTS enabled: {config.matts.enabled}")
    if config.matts.enabled:
        print(f"    Parallel k: {config.matts.parallel_k}")
        print(f"    Sequential r: {config.matts.sequential_r}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
