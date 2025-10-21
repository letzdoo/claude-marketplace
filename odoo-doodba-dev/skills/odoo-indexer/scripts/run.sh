#!/bin/bash
# Smart wrapper that handles environment automatically
# Usage: ./scripts/run.sh scripts/search.py "sale.order" --type model

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

# Auto-setup if not already done
if [ ! -f "$PLUGIN_DIR/.setup_complete" ]; then
    echo "First run detected. Running setup..."
    echo ""
    "$SCRIPT_DIR/setup.sh"
    touch "$PLUGIN_DIR/.setup_complete"
    echo ""
fi

# Determine ODOO_PATH if not set
if [ -z "$ODOO_PATH" ]; then
    # Try to find Odoo path intelligently
    if [ -d "/home/coder/project/odoo/custom/src" ]; then
        export ODOO_PATH="/home/coder/project/odoo/custom/src"
    elif [ -d "$(pwd)/odoo" ]; then
        export ODOO_PATH="$(pwd)/odoo"
    else
        export ODOO_PATH="$(pwd)"
    fi
fi

# Run command with appropriate environment
if command -v uv &> /dev/null; then
    cd "$PLUGIN_DIR"
    uv run "$@"
elif [ -d "$PLUGIN_DIR/.venv" ]; then
    source "$PLUGIN_DIR/.venv/bin/activate"
    cd "$PLUGIN_DIR"
    python3 "$@"
else
    echo "Error: Environment not set up. Run setup.sh first."
    echo "  cd $PLUGIN_DIR"
    echo "  ./scripts/setup.sh"
    exit 1
fi
