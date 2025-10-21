#!/bin/bash
# Auto-setup script for Odoo Indexer
# This script automatically configures the Python environment and dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

echo "Odoo Indexer Setup"
echo "=================="
echo ""

# Check for uv
if command -v uv &> /dev/null; then
    echo "✓ uv found: $(which uv)"
    USE_UV=true
elif command -v brew &> /dev/null; then
    echo "⚠ uv not found. Installing via Homebrew..."
    brew install uv
    USE_UV=true
else
    echo "⚠ uv not found. Falling back to Python venv..."
    USE_UV=false
fi

echo ""

# Setup environment
if [ "$USE_UV" = true ]; then
    echo "Setting up environment with uv..."
    cd "$PLUGIN_DIR"
    uv sync
    echo "✓ Environment ready (uv)"
else
    if [ ! -d "$PLUGIN_DIR/.venv" ]; then
        echo "Creating Python virtual environment..."
        cd "$PLUGIN_DIR"
        python3 -m venv .venv
    fi

    echo "Activating virtual environment..."
    source "$PLUGIN_DIR/.venv/bin/activate"

    echo "Installing dependencies..."
    if [ -f "$PLUGIN_DIR/requirements.txt" ]; then
        pip install -q -r "$PLUGIN_DIR/requirements.txt"
    else
        pip install -q lxml aiosqlite
    fi
    echo "✓ Environment ready (venv)"
fi

echo ""
echo "=" * 50
echo "Setup complete! You can now use the indexer."
echo ""
echo "Next steps:"
echo "  1. Run 'uv run scripts/update_index.py --full' to index your codebase"
echo "  2. Or use './scripts/run.sh scripts/update_index.py --full'"
echo "  3. Check status with 'uv run scripts/index_status.py'"
echo ""
echo "For health check, run: ./scripts/health_check.py"
