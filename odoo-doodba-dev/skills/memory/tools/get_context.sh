#!/bin/bash
# Wrapper for getting context summary
# Usage: ./get_context.sh [--format text|markdown|json] [--days N] [--category cat]

cd "$(dirname "$0")/.."
uv run scripts/get_context.py "$@"
