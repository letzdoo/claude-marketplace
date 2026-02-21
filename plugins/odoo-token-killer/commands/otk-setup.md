---
name: otk-setup
description: |
  **AUTO-USE** on first use or when user reports OTK not working.
  Sets up OTK (Odoo Token Killer) - builds the Rust binary, installs it,
  registers the PreToolUse hook for transparent command rewriting.
  Use when: 'setup otk', 'install otk', 'configure token killer', 'otk not working'.
---

# /otk-setup Command

Set up OTK (Odoo Token Killer) for transparent token optimization.

## Steps

### Step 1: Check Prerequisites

Verify Rust toolchain is available:

```bash
which cargo && cargo --version
```

If cargo is missing, install Rust:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
```

Also check for `jq` (needed by the hook):
```bash
which jq && jq --version
```

### Step 2: Build and Install OTK

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && cargo install --path .
```

Verify:
```bash
otk --version
```

Expected: `otk 1.0.0`

### Step 3: Register PreToolUse Hook

Read `~/.claude/settings.json`. Add the OTK hook under `hooks.PreToolUse`.

**Back up first:**
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak 2>/dev/null || true
```

The hook entry to add:
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

### Step 4: Report

```
OTK Setup Complete

  Binary:  otk 1.0.0 (Rust, 4.2MB, <10ms startup)
  Hook:    PreToolUse registered (transparent command rewriting)
  DB:      ~/.local/share/otk/tracking.db
  Tee:     ~/.local/share/otk/tee/ (full output recovery)

Commands now automatically optimized:
  invoke test    → failures only (90% token reduction)
  docker logs    → errors/warnings only (90% reduction)
  git status     → compact stats (80% reduction)
  cat *.py       → signatures + fields (60% reduction)
  cat *.xml      → structure only (70% reduction)

Tee: full unfiltered output always available at the path shown in [full output: ...]

Run /otk-gain to see your token savings dashboard.
```
