#!/usr/bin/env python3
"""Check Odoo Indexer health and configuration"""

import sys
import subprocess
from pathlib import Path
import os


def check_health():
    """Run comprehensive health check on Odoo Indexer setup"""
    plugin_dir = Path(__file__).parent.parent

    print("Odoo Indexer Health Check")
    print("=" * 50)

    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✓ Python: {python_version}")

    # Check for uv
    try:
        result = subprocess.run(['which', 'uv'], capture_output=True, text=True)
        uv_available = result.returncode == 0
        if uv_available:
            uv_path = result.stdout.strip()
            print(f"✓ uv: Available at {uv_path}")
        else:
            print("✗ uv: Not installed (will use venv fallback)")
    except Exception:
        uv_available = False
        print("✗ uv: Not installed (will use venv fallback)")

    # Check venv
    venv_exists = (plugin_dir / '.venv').exists()
    status = "✓" if venv_exists else "✗"
    print(f"{status} Virtual env: {'Exists' if venv_exists else 'Not created'}")

    # Check dependencies
    deps_ok = True
    try:
        import aiosqlite
        print(f"✓ aiosqlite: {aiosqlite.version}")
    except ImportError:
        print("✗ aiosqlite: Not installed")
        deps_ok = False

    try:
        import lxml
        from lxml import etree
        print(f"✓ lxml: {etree.__version__}")
    except ImportError:
        print("✗ lxml: Not installed")
        deps_ok = False

    # Check database
    db_path = Path.home() / '.odoo-indexer' / 'odoo_indexer.sqlite3'
    db_exists = db_path.exists()
    status = "✓" if db_exists else "✗"
    print(f"{status} Database: {db_path}")
    if db_exists:
        size_kb = db_path.stat().st_size / 1024
        size_mb = size_kb / 1024
        if size_mb > 1:
            print(f"  Size: {size_mb:.2f} MB")
        else:
            print(f"  Size: {size_kb:.1f} KB")

    # Check ODOO_PATH
    odoo_path = os.getenv('ODOO_PATH', os.getcwd())
    odoo_path_exists = Path(odoo_path).exists()
    status = "✓" if odoo_path_exists else "⚠"
    print(f"{status} ODOO_PATH: {odoo_path}")
    if not odoo_path_exists:
        print("  Warning: Path does not exist")

    # Check for common Odoo directories
    odoo_dirs = ['addons', 'odoo/addons', 'src', 'custom/src']
    found_odoo_structure = False
    for dir_name in odoo_dirs:
        dir_path = Path(odoo_path) / dir_name
        if dir_path.exists():
            print(f"  Found: {dir_name}/")
            found_odoo_structure = True

    if not found_odoo_structure:
        print("  ⚠ No typical Odoo directory structure found")

    # Check setup completion marker
    setup_complete = (plugin_dir / '.setup_complete').exists()
    if setup_complete:
        print("✓ Setup marker: Present")
    else:
        print("✗ Setup marker: Not found (setup may not have run)")

    print()
    print("=" * 50)

    # Summary and recommendations
    if not (venv_exists or uv_available):
        print("⚠  ISSUE: No Python environment detected")
        print("   Run: ./scripts/setup.sh")
    elif not deps_ok:
        print("⚠  ISSUE: Missing dependencies")
        print("   Run: ./scripts/setup.sh")
    elif not db_exists:
        print("⚠  Database not initialized")
        print("   Run: uv run scripts/update_index.py --full")
        print("   Or:  ./scripts/run.sh scripts/update_index.py --full")
    else:
        print("✓ Environment is ready!")
        if not found_odoo_structure:
            print()
            print("Note: Verify ODOO_PATH points to your Odoo source:")
            print(f"  export ODOO_PATH=/path/to/odoo/source")

    print()
    return deps_ok and (venv_exists or uv_available)


if __name__ == '__main__':
    success = check_health()
    sys.exit(0 if success else 1)
