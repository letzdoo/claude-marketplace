#!/bin/bash
# Wrapper for clearing memory
# Usage: ./clear.sh [--key key] [--category cat] [--all] [--yes]

cd "$(dirname "$0")/.."
uv run scripts/clear.py "$@"
