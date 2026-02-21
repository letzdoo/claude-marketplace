#!/bin/bash
# OTK gain wrapper - show token savings dashboard
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" && uv run otk gain "$@"
