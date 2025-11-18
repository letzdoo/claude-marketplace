#!/usr/bin/env python3
"""Clear memory items from the project memory database."""

import argparse
import json
import sys
from pathlib import Path

from config import DEFAULT_PROJECT_PATH
from database import MemoryDatabase


def main():
    """Main entry point for the clear script."""
    parser = argparse.ArgumentParser(
        description='Clear memory items from the project memory database'
    )
    parser.add_argument(
        '--key',
        help='Delete a specific memory item by key',
        default=None
    )
    parser.add_argument(
        '--category',
        help='Clear all items in a specific category',
        default=None
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clear all memory items for the project'
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
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )

    args = parser.parse_args()

    # Normalize project path
    project_path = str(Path(args.project).resolve())

    # Validate arguments
    if not args.key and not args.category and not args.all:
        parser.error('Must specify --key, --category, or --all')

    # Clear memory
    try:
        db = MemoryDatabase()

        if args.key:
            # Delete specific key
            if not args.yes and not args.json:
                response = input(f"Delete memory item '{args.key}'? [y/N] ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return

            success = db.delete_memory(args.key, project_path)
            if args.json:
                result = {
                    'success': success,
                    'deleted': 1 if success else 0
                }
                print(json.dumps(result, indent=2))
            else:
                if success:
                    print(f"✓ Deleted memory item: {args.key}")
                else:
                    print(f"Memory item not found: {args.key}", file=sys.stderr)
                    sys.exit(1)

        elif args.category:
            # Clear by category
            if not args.yes and not args.json:
                response = input(f"Delete all memory items in category '{args.category}'? [y/N] ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return

            count = db.clear_memory(project_path, category=args.category)
            if args.json:
                result = {
                    'success': True,
                    'deleted': count
                }
                print(json.dumps(result, indent=2))
            else:
                print(f"✓ Deleted {count} memory item(s) from category: {args.category}")

        elif args.all:
            # Clear all
            if not args.yes and not args.json:
                response = input("Delete ALL memory items for this project? [y/N] ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return

            count = db.clear_memory(project_path)
            if args.json:
                result = {
                    'success': True,
                    'deleted': count
                }
                print(json.dumps(result, indent=2))
            else:
                print(f"✓ Deleted {count} memory item(s)")

    except Exception as e:
        if args.json:
            result = {
                'success': False,
                'error': str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Error clearing memory: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
