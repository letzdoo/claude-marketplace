#!/bin/bash
# Wrapper for importing memory
# Usage: ./import.sh file.json [--overwrite]

cd "$(dirname "$0")/.."
uv run scripts/import_memory.py "$@"
