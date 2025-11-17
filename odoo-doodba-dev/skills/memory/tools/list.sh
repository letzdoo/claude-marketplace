#!/bin/bash
# Wrapper for listing memory
# Usage: ./list.sh [--category cat] [--stats]

cd "$(dirname "$0")/.."
uv run scripts/list_memory.py "$@"
