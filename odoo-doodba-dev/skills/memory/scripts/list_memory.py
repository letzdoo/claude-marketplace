#!/usr/bin/env python3
"""List all memory items in the project memory database."""

import argparse
import json
import sys
from pathlib import Path

from config import DEFAULT_PROJECT_PATH, SESSION_ID
from database import MemoryDatabase


def main():
    """Main entry point for the list script."""
    parser = argparse.ArgumentParser(
        description='List all memory items in the project memory database'
    )
    parser.add_argument(
        '--category',
        help='Filter by category',
        default=None
    )
    parser.add_argument(
        '--limit',
        help='Maximum number of results (default: 100)',
        type=int,
        default=100
    )
    parser.add_argument(
        '--project',
        help='Project path (defaults to current directory)',
        default=DEFAULT_PROJECT_PATH
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics only'
    )

    args = parser.parse_args()

    # Normalize project path
    project_path = str(Path(args.project).resolve())

    # List memory
    try:
        db = MemoryDatabase()

        # Record session if available
        if SESSION_ID:
            db.record_session(SESSION_ID, project_path)

        if args.stats:
            # Show statistics
            stats = db.get_stats(project_path)
            if args.json:
                print(json.dumps(stats, indent=2))
            else:
                print("Memory Statistics")
                print("=" * 50)
                print(f"Total items: {stats['total_items']}")
                print(f"Database: {stats['database_path']}")
                if stats['last_update']:
                    print(f"Last update: {stats['last_update']}")
                print("\nItems by category:")
                for category, count in stats['by_category'].items():
                    print(f"  {category}: {count}")
        else:
            # List items
            results = db.list_all_memory(
                project_path=project_path,
                category=args.category,
                limit=args.limit
            )

            if args.json:
                output = {
                    'success': True,
                    'count': len(results),
                    'results': results
                }
                print(json.dumps(output, indent=2))
            else:
                if results:
                    print(f"Memory items ({len(results)}):\n")
                    for i, item in enumerate(results, 1):
                        print(f"{i}. {item['key']}")
                        print(f"   Value: {item['value'][:100]}{'...' if len(item['value']) > 100 else ''}")
                        if item['category']:
                            print(f"   Category: {item['category']}")
                        if item['tags']:
                            print(f"   Tags: {', '.join(item['tags'])}")
                        print(f"   Updated: {item['updated_at']}")
                        print()
                else:
                    print("No memory items found.")

    except Exception as e:
        if args.json:
            result = {
                'success': False,
                'error': str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Error listing memory: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
