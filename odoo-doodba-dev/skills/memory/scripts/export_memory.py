#!/usr/bin/env python3
"""Export memory items from the project memory database."""

import argparse
import json
import sys
from pathlib import Path

from config import DEFAULT_PROJECT_PATH
from database import MemoryDatabase


def main():
    """Main entry point for the export script."""
    parser = argparse.ArgumentParser(
        description='Export memory items from the project memory database'
    )
    parser.add_argument(
        '--output',
        help='Output file path (defaults to stdout)',
        default=None
    )
    parser.add_argument(
        '--project',
        help='Project path (defaults to current directory)',
        default=DEFAULT_PROJECT_PATH
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )

    args = parser.parse_args()

    # Normalize project path
    project_path = str(Path(args.project).resolve())

    # Export memory
    try:
        db = MemoryDatabase()
        items = db.export_memory(project_path)

        # Prepare output
        output = {
            'project_path': project_path,
            'export_date': str(Path.ctime(Path(__file__))),
            'count': len(items),
            'items': items
        }

        # Write output
        indent = 2 if args.pretty else None
        json_output = json.dumps(output, indent=indent)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json_output)
            print(f"✓ Exported {len(items)} memory item(s) to {output_path}")
        else:
            print(json_output)

    except Exception as e:
        print(f"Error exporting memory: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
