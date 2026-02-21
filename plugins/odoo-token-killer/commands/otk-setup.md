---
name: otk-setup
description: |
  **AUTO-USE** on first use or when user reports OTK not working.
  Sets up OTK (Odoo Token Killer) - installs the CLI proxy, registers the
  PreToolUse hook for transparent command rewriting, and validates the setup.
  Use when: 'setup otk', 'install otk', 'configure token killer', 'otk not working'.
---

# /otk-setup Command

Set up OTK (Odoo Token Killer) for transparent token optimization.

## What This Does

1. Installs the OTK Python package via `uv`
2. Registers the PreToolUse hook in Claude Code settings
3. Validates the installation
4. Shows first token savings estimate

## Steps

### Step 1: Install OTK Core

Run in the plugin's skill directory:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv sync
```

### Step 2: Register PreToolUse Hook

Check if `~/.claude/settings.json` exists and add the OTK hook.

**Read** `~/.claude/settings.json` first. If it exists, parse it and add the hook entry.
If it doesn't exist, create it.

The hook entry to add under `hooks.PreToolUse`:

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/otk-rewrite.sh"
}
```

**IMPORTANT**: Back up the settings file first:
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak 2>/dev/null || true
```

### Step 3: Validate Installation

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk --version
```

Expected output: `otk 1.0.0 (Odoo Token Killer)`

### Step 4: Show Setup Summary

Report to the user:

```
OTK Setup Complete

  CLI:   otk 1.0.0 installed
  Hook:  PreToolUse registered (transparent command rewriting)
  DB:    ~/.local/share/otk/tracking.db

Commands now automatically optimized:
  invoke test    → failures only (90% token reduction)
  docker logs    → errors/warnings only (90% reduction)
  git status     → compact stats (80% reduction)
  cat *.py       → signatures only (60% reduction)
  cat *.xml      → structure only (70% reduction)

Run /otk-gain to see your token savings dashboard.
```
