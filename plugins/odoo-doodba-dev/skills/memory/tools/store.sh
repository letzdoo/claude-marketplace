#!/bin/bash
# Wrapper for storing memory
# Usage: ./store.sh "key" "value" [--category cat] [--tags tag1,tag2] [--context "context"]

cd "$(dirname "$0")/.."
uv run scripts/store.py "$@"
