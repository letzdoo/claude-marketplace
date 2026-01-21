#!/bin/bash
# Wrapper for model search
# Usage: ./search_model.sh "sale.order"

cd "$(dirname "$0")/.."
uv run scripts/search.py "$1" --type model --limit "${2:-20}"
