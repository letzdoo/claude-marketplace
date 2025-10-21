"""Configuration management for Odoo Indexer."""

import os
from pathlib import Path

# Required settings
ODOO_PATH = Path(os.getenv('ODOO_PATH', '/home/coder/letzdoo-sh/odoo/custom/src'))
if not ODOO_PATH.exists():
    # Fallback to common locations
    possible_paths = [
        Path('/home/coder/letzdoo-sh/odoo/custom/src'),
        Path.home() / 'odoo' / 'custom' / 'src',
        Path.cwd() / 'odoo' / 'custom' / 'src',
    ]
    for path in possible_paths:
        if path.exists():
            ODOO_PATH = path
            break

# Optional settings
SQLITE_DB_PATH = Path(os.getenv('SQLITE_DB_PATH', str(Path.home() / '.odoo-indexer' / 'odoo_indexer.sqlite3')))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_CONCURRENT_MODULES = int(os.getenv('MAX_CONCURRENT_MODULES', '4'))
MAX_WORKER_PROCESSES = int(os.getenv('MAX_WORKER_PROCESSES', '0'))  # 0 = use CPU count
