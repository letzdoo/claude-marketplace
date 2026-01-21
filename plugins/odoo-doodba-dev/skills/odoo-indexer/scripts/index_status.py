#!/usr/bin/env python3
"""Get index status and statistics."""

import json
import sys

from query_shared import Database, get_config

config = get_config()
SQLITE_DB_PATH = config['SQLITE_DB_PATH']
ODOO_PATH = config['ODOO_PATH']


def main():
    db = Database(SQLITE_DB_PATH)

    # Check if database exists and has data
    if not SQLITE_DB_PATH.exists():
        print("\nIndex Status: NOT INITIALIZED")
        print(f"Database path: {SQLITE_DB_PATH}")
        print("\nRun 'python scripts/update_index.py --full' to create the index.")
        sys.exit(0)

    # Get module stats
    stats = db.get_module_stats()

    print(f"\n=== Odoo Index Status ===")
    print(f"Database: {SQLITE_DB_PATH}")
    print(f"Odoo Path: {ODOO_PATH}")
    print(f"Total Modules: {stats['total_modules']}")

    total_items = sum(m['total_items'] for m in stats['modules'])
    print(f"Total Items: {total_items}")

    # Get breakdown by counting all item types
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_type, COUNT(*) as count
            FROM indexed_items
            GROUP BY item_type
            ORDER BY count DESC
        """)
        counts = {row['item_type']: row['count'] for row in cursor.fetchall()}

    if counts:
        print(f"\nBreakdown by type:")
        for item_type, count in counts.items():
            print(f"  {item_type}: {count}")

    # Show top modules
    print(f"\nTop 10 modules by item count:")
    for module in stats['modules'][:10]:
        print(f"  {module['module']}: {module['total_items']} items")

    if len(stats['modules']) > 10:
        print(f"  ... and {len(stats['modules']) - 10} more modules")

    print()


if __name__ == '__main__':
    main()
