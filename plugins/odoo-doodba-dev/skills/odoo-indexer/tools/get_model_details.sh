#!/bin/bash
# Wrapper for model details
# Usage: ./get_model_details.sh "sale.order"

cd "$(dirname "$0")/.."
uv run scripts/get_details.py model "$1"
