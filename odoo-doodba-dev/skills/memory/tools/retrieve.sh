#!/bin/bash
# Wrapper for retrieving memory
# Usage: ./retrieve.sh "key"

cd "$(dirname "$0")/.."
uv run scripts/retrieve.py "$@"
