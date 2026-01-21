#!/usr/bin/env python3
"""Retrieve a memory item from the project memory database."""

import argparse
import json
import sys
from pathlib import Path

from config import DEFAULT_PROJECT_PATH, SESSION_ID
from database import MemoryDatabase


def main():
    """Main entry point for the retrieve script."""
    parser = argparse.ArgumentParser(
        description='Retrieve a memory item from the project memory database'
    )
    parser.add_argument(
        'key',
        help='Key of the memory item to retrieve'
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

    # Normalize project path
    project_path = str(Path(args.project).resolve())

    # Retrieve memory
    try:
        db = MemoryDatabase()
        memory = db.retrieve_memory(args.key, project_path)

        # Record session if available
        if SESSION_ID:
            db.record_session(SESSION_ID, project_path)

        if memory:
            if args.json:
                print(json.dumps(memory, indent=2))
            else:
                print(f"Key: {memory['key']}")
                print(f"Value: {memory['value']}")
                if memory['context']:
                    print(f"Context: {memory['context']}")
                if memory['category']:
                    print(f"Category: {memory['category']}")
                if memory['tags']:
                    print(f"Tags: {', '.join(memory['tags'])}")
                print(f"Created: {memory['created_at']}")
                print(f"Updated: {memory['updated_at']}")
        else:
            if args.json:
                result = {
                    'success': False,
                    'error': 'Memory item not found'
                }
                print(json.dumps(result, indent=2))
            else:
                print(f"Memory item not found: {args.key}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        if args.json:
            result = {
                'success': False,
                'error': str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Error retrieving memory: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
