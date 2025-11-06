#!/bin/bash
# Wrapper for field validation
# Usage: ./validate_field.sh "sale.order" "partner_id"

cd "$(dirname "$0")/.."
MODEL="$1"
FIELD="$2"

if [ -z "$MODEL" ] || [ -z "$FIELD" ]; then
    echo "Usage: $0 MODEL FIELD"
    echo "Example: $0 'sale.order' 'partner_id'"
    exit 1
fi

uv run scripts/search.py "$FIELD" --type field --parent "$MODEL" --limit 1
