#!/usr/bin/env python3
"""Get complete details for a specific Odoo element."""

import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from tools import get_item_details


def main():
    parser = argparse.ArgumentParser(description='Get complete details for an Odoo element')
    parser.add_argument('item_type', help='Type of item (model/field/function/view/etc)')
    parser.add_argument('name', help='Item name')
    parser.add_argument('--parent', dest='parent_name', help='Parent name (for fields/methods)')
    parser.add_argument('--module', help='Module name (optional)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = get_item_details(
        item_type=args.item_type,
        name=args.name,
        parent_name=args.parent_name,
        module=args.module
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"\n=== {result['item_type'].upper()}: {result['name']} ===\n")
        print(f"Module: {result['module']}")
        if result['parent_name']:
            print(f"Parent: {result['parent_name']}")
        print(f"Dependency Depth: {result['dependency_depth']}")

        if result['attributes']:
            print(f"\nAttributes:")
            for key, value in result['attributes'].items():
                print(f"  {key}: {value}")

        print(f"\nReferences ({len(result['references'])}):")
        for ref in result['references']:
            print(f"  {ref['file']}:{ref['line']} ({ref['type']})")

        # Show related items for models
        if 'related_items' in result:
            related = result['related_items']
            if related.get('fields'):
                print(f"\nFields ({len(related['fields'])}):")
                for field in related['fields'][:10]:
                    attrs = field.get('attributes', {})
                    field_type = attrs.get('field_type', '?')
                    print(f"  - {field['name']} ({field_type})")
                if len(related['fields']) > 10:
                    print(f"  ... and {len(related['fields']) - 10} more")

            if related.get('methods'):
                print(f"\nMethods ({len(related['methods'])}):")
                for method in related['methods'][:10]:
                    print(f"  - {method['name']}")
                if len(related['methods']) > 10:
                    print(f"  ... and {len(related['methods']) - 10} more")

            if related.get('views'):
                print(f"\nViews ({len(related['views'])}):")
                for view in related['views'][:5]:
                    attrs = view.get('attributes', {})
                    view_type = attrs.get('view_type', '?')
                    print(f"  - {view['name']} ({view_type})")

            if related.get('actions'):
                print(f"\nActions ({len(related['actions'])}):")
                for action in related['actions'][:5]:
                    print(f"  - {action['name']}")


if __name__ == '__main__':
    main()
