#!/usr/bin/env python3
"""Search Odoo elements by their attributes."""

import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from tools import search_by_attribute


def main():
    parser = argparse.ArgumentParser(description='Search by attributes')
    parser.add_argument('item_type', help='Type of item to search')
    parser.add_argument('--filters', required=True, help='JSON dict of attribute filters')
    parser.add_argument('--module', help='Filter by module')
    parser.add_argument('--limit', type=int, default=20, help='Maximum results')
    parser.add_argument('--offset', type=int, default=0, help='Pagination offset')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    # Parse attribute filters
    try:
        attribute_filters = json.loads(args.filters)
    except json.JSONDecodeError as e:
        print(f"Error parsing filters JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = search_by_attribute(
        item_type=args.item_type,
        attribute_filters=attribute_filters,
        module=args.module,
        limit=args.limit,
        offset=args.offset
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"\n=== Search Results ===")
        print(f"Total: {result['total']} | Showing: {result['returned']} | Offset: {result['offset']}")
        if result['has_more']:
            print(f"More results available (use --offset {result['next_offset']})")
        print()

        for item in result['results']:
            print(f"[{item['item_type']}] {item['name']}")
            if item['parent_name']:
                print(f"  Parent: {item['parent_name']}")
            print(f"  Module: {item['module']}")

            # Show matching attributes
            if item.get('attributes'):
                print(f"  Attributes:")
                for key, value in item['attributes'].items():
                    if key in attribute_filters:
                        print(f"    {key}: {value}")

            print()


if __name__ == '__main__':
    main()
