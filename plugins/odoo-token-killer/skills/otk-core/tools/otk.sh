#!/bin/bash
# OTK shell wrapper - runs otk via uv from the correct directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" && uv run otk "$@"
