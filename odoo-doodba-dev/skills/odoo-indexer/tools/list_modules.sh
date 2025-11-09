#!/bin/bash
# Wrapper for listing modules
# Usage: ./list_modules.sh [pattern]

cd "$(dirname "$0")/.."
PATTERN="$1"

if [ -n "$PATTERN" ]; then
    uv run scripts/list_modules.py --pattern "$PATTERN"
else
    uv run scripts/list_modules.py
fi
