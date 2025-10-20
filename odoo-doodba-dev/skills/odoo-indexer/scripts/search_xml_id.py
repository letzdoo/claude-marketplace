#!/usr/bin/env python3
"""Search for XML IDs."""

import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from tools import search_xml_id


def main():
    parser = argparse.ArgumentParser(description='Search for XML IDs')
    parser.add_argument('query', help='Search term (supports %% wildcards)')
    parser.add_argument('--module', help='Filter by module')
    parser.add_argument('--limit', type=int, default=20, help='Maximum results')
    parser.add_argument('--offset', type=int, default=0, help='Pagination offset')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = search_xml_id(
        query=args.query,
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

        print(f"\n=== XML ID Search Results ===")
        print(f"Total: {result['total']} | Showing: {result['returned']} | Offset: {result['offset']}")
        if result['has_more']:
            print(f"More results available (use --offset {result['next_offset']})")
        print()

        for item in result['results']:
            print(f"[{item['item_type']}] {item['name']}")
            print(f"  Module: {item['module']}")

            attrs = item.get('attributes', {})
            if attrs.get('model'):
                print(f"  Model: {attrs['model']}")
            if attrs.get('res_model'):
                print(f"  Model: {attrs['res_model']}")
            if attrs.get('view_type'):
                print(f"  View Type: {attrs['view_type']}")

            if item.get('references'):
                ref = item['references'][0]
                print(f"  Location: {ref['file']}:{ref['line']}")

            print()


if __name__ == '__main__':
    main()
