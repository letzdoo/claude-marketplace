---
name: otk-setup
description: |
  Automated OTK setup agent. Validates environment, installs dependencies,
  registers the PreToolUse hook, and confirms token tracking is working.

  Invoke when: user runs /otk-setup or asks to install/configure OTK.

tools:
  - Bash
  - Read
  - Glob
  - Grep
model: inherit
color: green
---

# OTK Setup Agent

## Task

Install and configure OTK (Odoo Token Killer) for the current environment.

## Steps

### 1. Check Prerequisites

Verify that `uv` and `jq` are available:

```bash
command -v uv && uv --version
command -v jq && jq --version
```

If `uv` is missing, install it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If `jq` is missing, inform user they need to install it (`apt install jq` or `brew install jq`).

### 2. Install OTK Python Package

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv sync
```

Verify:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk --version
```

### 3. Register PreToolUse Hook

Read `~/.claude/settings.json`. Add the OTK hook under `hooks.PreToolUse`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash PLUGIN_ROOT/hooks/otk-rewrite.sh"
          }
        ]
      }
    ]
  }
}
```

Replace `PLUGIN_ROOT` with the actual `${CLAUDE_PLUGIN_ROOT}` path.

**IMPORTANT**: Merge with existing hooks, don't overwrite.

### 4. Validate

Run a test command:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && echo "test line 1\ntest line 2\ntest line 3" | uv run otk gain
```

### 5. Report

Tell the user setup is complete with the summary from /otk-setup command.
