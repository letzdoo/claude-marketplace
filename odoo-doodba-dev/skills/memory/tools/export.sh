#!/bin/bash
# Wrapper for exporting memory
# Usage: ./export.sh [--output file.json] [--pretty]

cd "$(dirname "$0")/.."
uv run scripts/export_memory.py "$@"
