#!/usr/bin/env python3
"""Update the Odoo index."""

import argparse
import asyncio
import logging
import sys

from indexer import index_odoo_codebase
from config import ODOO_PATH, SQLITE_DB_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Update Odoo index')
    parser.add_argument('--full', action='store_true', help='Force full re-indexing')
    parser.add_argument('--modules', help='Comma-separated list of modules to index')
    parser.add_argument('--clear', action='store_true', help='Clear database before indexing')

    args = parser.parse_args()

    incremental = not args.full
    module_filter = None
    if args.modules:
        module_filter = [m.strip() for m in args.modules.split(',')]

    print(f"\nOdoo Index Update")
    print(f"=================")
    print(f"Odoo Path: {ODOO_PATH}")
    print(f"Database: {SQLITE_DB_PATH}")
    print(f"Mode: {'Incremental' if incremental else 'Full'}")
    if module_filter:
        print(f"Modules: {', '.join(module_filter)}")
    if args.clear:
        print(f"Clear DB: Yes")
    print()

    try:
        asyncio.run(
            index_odoo_codebase(
                incremental=incremental,
                module_filter=module_filter,
                clear_db=args.clear
            )
        )
        print("\nIndexing completed successfully!")
    except Exception as e:
        logger.error(f"Indexing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
