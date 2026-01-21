#!/usr/bin/env python3
"""Search memory items in the project memory database."""

import argparse
import json
import sys
from pathlib import Path

from config import DEFAULT_PROJECT_PATH, MAX_SEARCH_RESULTS, SESSION_ID
from database import MemoryDatabase


def main():
    """Main entry point for the search script."""
    parser = argparse.ArgumentParser(
        description='Search memory items in the project memory database'
    )
    parser.add_argument(
        'query',
        nargs='?',
        help='Search query (searches in key, value, and context)',
        default=None
    )
    parser.add_argument(
        '--category',
        help='Filter by category',
        default=None
    )
    parser.add_argument(
        '--tags',
        help='Comma-separated list of tags to filter by',
        default=None
    )
    parser.add_argument(
        '--limit',
        help=f'Maximum number of results (default: {MAX_SEARCH_RESULTS})',
        type=int,
        default=MAX_SEARCH_RESULTS
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

    args = parser.parse_args()

    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]

    # Normalize project path
    project_path = str(Path(args.project).resolve())

    # Search memory
    try:
        db = MemoryDatabase()
        results = db.search_memory(
            project_path=project_path,
            query=args.query,
            category=args.category,
            tags=tags,
            limit=args.limit
        )

        # Record session if available
        if SESSION_ID:
            db.record_session(SESSION_ID, project_path)

        if args.json:
            output = {
                'success': True,
                'count': len(results),
                'results': results
            }
            print(json.dumps(output, indent=2))
        else:
            if results:
                print(f"Found {len(results)} memory item(s):\n")
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
                print("No memory items found matching the search criteria.")

    except Exception as e:
        if args.json:
            result = {
                'success': False,
                'error': str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Error searching memory: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
