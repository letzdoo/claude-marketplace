#!/usr/bin/env python3
"""Store a memory item in the project memory database."""

import argparse
import json
import sys
from pathlib import Path

from config import DEFAULT_PROJECT_PATH, SESSION_ID
from database import MemoryDatabase


def main():
    """Main entry point for the store script."""
    parser = argparse.ArgumentParser(
        description='Store a memory item in the project memory database'
    )
    parser.add_argument(
        'key',
        help='Unique key for the memory item'
    )
    parser.add_argument(
        'value',
        help='The memory content to store'
    )
    parser.add_argument(
        '--context',
        help='Additional context about the memory',
        default=None
    )
    parser.add_argument(
        '--category',
        help='Category of the memory (e.g., decision, requirement, context, finding)',
        default=None
    )
    parser.add_argument(
        '--tags',
        help='Comma-separated list of tags',
        default=None
    )
    parser.add_argument(
        '--project',
        help='Project path (defaults to current directory)',
        default=DEFAULT_PROJECT_PATH
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result as JSON'
    )

    args = parser.parse_args()

    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]

    # Normalize project path
    project_path = str(Path(args.project).resolve())

    # Store memory
    try:
        db = MemoryDatabase()
        memory_id = db.store_memory(
            key=args.key,
            value=args.value,
            project_path=project_path,
            context=args.context,
            category=args.category,
            tags=tags
        )

        # Record session if available
        if SESSION_ID:
            db.record_session(SESSION_ID, project_path)

        if args.json:
            result = {
                'success': True,
                'id': memory_id,
                'key': args.key,
                'project': project_path
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"✓ Stored memory item: {args.key}")
            print(f"  Project: {project_path}")
            if args.category:
                print(f"  Category: {args.category}")
            if tags:
                print(f"  Tags: {', '.join(tags)}")

    except Exception as e:
        if args.json:
            result = {
                'success': False,
                'error': str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Error storing memory: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
