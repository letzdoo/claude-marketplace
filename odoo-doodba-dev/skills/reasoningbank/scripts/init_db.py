#!/usr/bin/env python3
"""Initialize ReasoningBank database."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database import get_database
from scripts.utils.config import load_config


async def main():
    """Initialize the database."""
    print("Initializing ReasoningBank database...")

    # Load configuration
    config = load_config()

    # Get database
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())

    db = get_database(db_path)

    # Initialize schema
    await db.init_schema()

    # Get statistics
    stats = await db.get_statistics()

    print(f"\n✓ Database initialized successfully!")
    print(f"  Location: {db_path}")
    print(f"  Total memories: {stats['total_memories']}")
    print(f"  Total trajectories: {stats['total_trajectories']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Average confidence: {stats['avg_confidence']:.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
