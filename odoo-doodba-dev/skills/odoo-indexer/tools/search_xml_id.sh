#!/bin/bash
# Wrapper for XML ID search
# Usage: ./search_xml_id.sh "action_view_task" [module]

cd "$(dirname "$0")/.."
XMLID="$1"
MODULE="$2"

if [ -z "$XMLID" ]; then
    echo "Usage: $0 XMLID [MODULE]"
    echo "Example: $0 'action_view_task' 'project'"
    exit 1
fi

if [ -n "$MODULE" ]; then
    uv run scripts/search_xml_id.py "$XMLID" --module "$MODULE"
else
    uv run scripts/search_xml_id.py "$XMLID"
fi
