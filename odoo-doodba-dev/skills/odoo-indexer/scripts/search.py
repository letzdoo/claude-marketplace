#!/usr/bin/env python3
"""Search for indexed Odoo elements."""

import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from tools import search_odoo_index


def main():
    parser = argparse.ArgumentParser(description='Search indexed Odoo elements')
    parser.add_argument('query', help='Search term (supports SQL LIKE patterns with %%)')
    parser.add_argument('--type', dest='item_type', help='Filter by item type')
    parser.add_argument('--module', help='Filter by module name')
    parser.add_argument('--parent', dest='parent_name', help='Filter by parent name')
    parser.add_argument('--limit', type=int, default=20, help='Maximum results')
    parser.add_argument('--offset', type=int, default=0, help='Pagination offset')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = search_odoo_index(
        query=args.query,
        item_type=args.item_type,
        module=args.module,
        parent_name=args.parent_name,
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
            print(f"[{item['type']}] {item['name']}")
            if 'parent' in item:
                print(f"  Parent: {item['parent']}")
            print(f"  Module: {item['module']}")
            if 'file' in item:
                print(f"  Location: {item['file']}:{item['line']}")
            if 'description' in item:
                print(f"  Description: {item['description']}")
            if 'field_type' in item:
                print(f"  Type: {item['field_type']}")
            print()


if __name__ == '__main__':
    main()
