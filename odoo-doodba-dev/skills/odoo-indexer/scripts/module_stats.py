#!/usr/bin/env python3
"""Get statistics for a specific module."""

import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from tools import get_module_stats


def main():
    parser = argparse.ArgumentParser(description='Get module statistics')
    parser.add_argument('module', help='Module name')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = get_module_stats(module=args.module)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"\n=== Module: {result['module']} ===\n")
        counts = result.get('counts_by_type', {})
        total = sum(counts.values())
        print(f"Total items: {total}\n")
        print("Breakdown by type:")
        for item_type, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {item_type}: {count}")


if __name__ == '__main__':
    main()
