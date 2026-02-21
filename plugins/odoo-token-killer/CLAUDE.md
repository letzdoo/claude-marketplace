# OTK - Odoo Token Killer (Development Guide)

## Overview

OTK is a token-optimized CLI proxy for Odoo development with Claude Code.
Inspired by RTK (rtk-ai/rtk). Reduces token consumption by 60-90%.

## Architecture

```
hooks/otk-rewrite.sh        PreToolUse hook (transparent command rewriting)
skills/otk-core/
  scripts/
    cli.py                   CLI entry point (otk command + gain dashboard)
    filters.py               12 filter strategies (test, log, python, xml, git, etc.)
    tracking.py              SQLite token tracking (record, query, aggregate)
  tools/
    otk.sh                   Shell wrapper for uv run otk
    otk-gain.sh              Shell wrapper for gain command
commands/
  otk-setup.md              /otk-setup command
  otk-gain.md               /otk-gain command
agents/
  otk-setup.md              Setup automation agent
```

## Development Commands

```bash
# Install/sync dependencies
cd plugins/odoo-token-killer/skills/otk-core && uv sync

# Run otk directly
cd plugins/odoo-token-killer/skills/otk-core && uv run otk --version

# Test a filter manually
cd plugins/odoo-token-killer/skills/otk-core && echo "test output" | uv run python -c "
from scripts.filters import test_filter
import sys
print(test_filter(sys.stdin.read()))
"

# Check tracking database
cd plugins/odoo-token-killer/skills/otk-core && uv run otk gain --json
```

## Adding a New Filter

1. Add the filter function in `scripts/filters.py`
2. Add the command pattern to `FILTER_MAP` dict
3. Add the pattern to `hooks/otk-rewrite.sh` case statement
4. Update the README.md filter table
5. Test with real Odoo output

## Design Principles

- Pure Python stdlib: no runtime dependencies beyond Python 3.10+
- Graceful degradation: never break the underlying command
- Exit code preservation: critical for CI/CD
- Lazy patterns: compile regex once, reuse
- Measurable: track every command in SQLite
