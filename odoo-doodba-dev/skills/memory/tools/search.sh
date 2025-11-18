#!/bin/bash
# Wrapper for searching memory
# Usage: ./search.sh "query" [--category cat] [--tags tag1,tag2]

cd "$(dirname "$0")/.."
uv run scripts/search.py "$@"
