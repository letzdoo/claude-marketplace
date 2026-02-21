---
name: otk-core
description: |
  Core OTK engine: CLI proxy, output filters, token tracking, and analytics.
  This skill provides the `otk` command and all filter strategies.
  AUTO-TRIGGER: Used automatically via PreToolUse hook - no manual invocation needed.
allowed-tools: Bash, Read
---

# OTK Core Engine

The core Python package providing:
- `otk <command>` - Token-filtered command execution
- `otk gain` - Analytics dashboard
- `otk read <file>` - Filtered file reading
- 12 specialized output filters
- SQLite-based token tracking

## Quick Reference

```bash
# Run command with filtered output
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk <command> [args...]

# Analytics
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk gain
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk gain --daily
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk gain --json
```

## Shell Wrappers

For convenience, shell wrappers are available in `tools/`:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/otk-core/tools/otk.sh <command> [args...]
${CLAUDE_PLUGIN_ROOT}/skills/otk-core/tools/otk-gain.sh
```
