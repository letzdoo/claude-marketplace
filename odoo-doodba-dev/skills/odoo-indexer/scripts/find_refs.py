#!/usr/bin/env python3
"""Find all references to a specific Odoo element."""

import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from tools import find_references


def main():
    parser = argparse.ArgumentParser(description='Find references to an Odoo element')
    parser.add_argument('item_type', help='Type of item')
    parser.add_argument('name', help='Item name')
    parser.add_argument('--ref-type', dest='reference_type', help='Filter by reference type')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = find_references(
        item_type=args.item_type,
        name=args.name,
        reference_type=args.reference_type
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"\n=== References to {result['item_type']}: {result['item']} ===")
        print(f"Total: {result['total_references']}\n")

        for ref in result['references']:
            print(f"{ref['file']}:{ref['line']} ({ref['type']})")


if __name__ == '__main__':
    main()
