"""Environment checker for Odoo Indexer"""
import sys
import subprocess
from pathlib import Path


def check_environment():
    """Check if environment is properly set up

    Returns:
        bool: True if environment is ready, False otherwise
    """
    plugin_dir = Path(__file__).parent.parent

    # Check for required Python modules
    try:
        import aiosqlite
        import lxml
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print(f"\nPlease run setup:")
        print(f"  cd {plugin_dir}")
        print(f"  ./scripts/setup.sh")
        print(f"\nOr install dependencies manually:")
        print(f"  uv sync")
        print(f"  # OR")
        print(f"  pip install lxml aiosqlite")
        return False


def get_runner():
    """Determine which Python runner to use

    Returns:
        str: 'uv', 'venv', or None if neither is available
    """
    # Check for uv
    try:
        result = subprocess.run(['which', 'uv'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'uv'
    except Exception:
        pass

    # Check for venv
    plugin_dir = Path(__file__).parent.parent
    venv_path = plugin_dir / '.venv'
    if venv_path.exists():
        return 'venv'

    return None


def ensure_environment():
    """Ensure environment is set up, exit if not

    This is a convenience function that checks the environment
    and exits with code 1 if it's not properly configured.
    """
    if not check_environment():
        sys.exit(1)


if __name__ == '__main__':
    # Allow running as standalone check
    if check_environment():
        print("✓ Environment is properly configured")
        runner = get_runner()
        if runner:
            print(f"✓ Using runner: {runner}")
    else:
        sys.exit(1)
