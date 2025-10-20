#!/usr/bin/env python3
"""List all indexed Odoo modules."""

import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from tools import list_modules


def main():
    parser = argparse.ArgumentParser(description='List indexed Odoo modules')
    parser.add_argument('--pattern', help='Filter by module name pattern')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = list_modules(pattern=args.pattern)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"\n=== Indexed Modules ({result['total_modules']}) ===\n")
        for module in result['modules']:
            print(f"{module['module']}: {module['total_items']} items")


if __name__ == '__main__':
    main()
