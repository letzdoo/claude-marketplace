#!/bin/bash
# Wrapper for module statistics
# Usage: ./module_stats.sh "sale"

cd "$(dirname "$0")/.."
MODULE="$1"

if [ -z "$MODULE" ]; then
    echo "Usage: $0 MODULE"
    echo "Example: $0 'sale'"
    exit 1
fi

uv run scripts/module_stats.py "$MODULE"
