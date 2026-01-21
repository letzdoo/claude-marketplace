#!/usr/bin/env python3
"""Import memory items into the project memory database."""

import argparse
import json
import sys
from pathlib import Path

from config import DEFAULT_PROJECT_PATH
from database import MemoryDatabase


def main():
    """Main entry point for the import script."""
    parser = argparse.ArgumentParser(
        description='Import memory items into the project memory database'
    )
    parser.add_argument(
        'input_file',
        help='Input JSON file containing memory items'
    )
    parser.add_argument(
        '--project',
        help='Project path (defaults to current directory)',
        default=DEFAULT_PROJECT_PATH
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing items with same key'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result as JSON'
    )

    args = parser.parse_args()

    # Normalize project path
    project_path = str(Path(args.project).resolve())

    # Import memory
    try:
        # Read input file
        input_path = Path(args.input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        data = json.loads(input_path.read_text())

        # Validate data structure
        if 'items' not in data:
            raise ValueError("Invalid import file: missing 'items' field")

        items = data['items']

        # Import items
        db = MemoryDatabase()
        count = db.import_memory(items, project_path, overwrite=args.overwrite)

        if args.json:
            result = {
                'success': True,
                'imported': count,
                'total': len(items)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"✓ Imported {count} out of {len(items)} memory item(s)")
            if count < len(items):
                print(f"  ({len(items) - count} items already existed and were skipped)")

    except Exception as e:
        if args.json:
            result = {
                'success': False,
                'error': str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Error importing memory: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
