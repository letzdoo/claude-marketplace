#!/bin/bash
# Get Odoo project context summary
# Usage: ./get_context.sh [--format text|markdown|json] [--section section_name]

cd "$(dirname "$0")/.."
uv run scripts/get_context.py "$@"
