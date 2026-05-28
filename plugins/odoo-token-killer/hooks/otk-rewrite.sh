#!/bin/bash
# =============================================================================
# OTK PreToolUse Hook - Transparent command rewriting for Claude Code
#
# Inspired by RTK's hook-first architecture (rtk-ai/rtk).
# Intercepts Bash commands and rewrites them to use otk filters.
# Zero token overhead: Claude never sees the rewrite.
#
# Installation: Registered automatically by /otk-setup command
# Manual: Add to ~/.claude/settings.json under hooks.PreToolUse
# =============================================================================

set -euo pipefail

# Graceful degradation: skip silently if dependencies missing
if ! command -v jq &>/dev/null; then
    exit 0
fi

# Only handle Bash tool calls
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
if [ "$TOOL" != "Bash" ]; then
    exit 0
fi

CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
if [ -z "$CMD" ]; then
    exit 0
fi

# Skip heredocs and multi-line commands
if echo "$CMD" | grep -q '<<'; then
    exit 0
fi

# Extract first command (before pipes/&&)
FIRST_CMD=$(echo "$CMD" | sed 's/[|&;].*//' | sed 's/^\s*//' | sed 's/\s*$//')

# Preserve environment variable prefixes (e.g., ODOO_RC=/etc/odoo.conf invoke test)
ENV_PREFIX=$(echo "$FIRST_CMD" | grep -oE '^([A-Za-z_][A-Za-z0-9_]*=[^ ]* +)+' || echo "")
if [ -n "$ENV_PREFIX" ]; then
    FIRST_CMD="${FIRST_CMD#$ENV_PREFIX}"
fi

# Determine the OTK command path
OTK_CMD=""
if command -v otk &>/dev/null; then
    OTK_CMD="otk"
elif [ -x "$HOME/.cargo/bin/otk" ]; then
    OTK_CMD="$HOME/.cargo/bin/otk"
else
    # Try plugin-local release binary
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills/otk-core" 2>/dev/null && pwd)"
    if [ -n "$SCRIPT_DIR" ] && [ -x "$SCRIPT_DIR/target/release/otk" ]; then
        OTK_CMD="$SCRIPT_DIR/target/release/otk"
    else
        exit 0  # No otk available, skip silently
    fi
fi

# Pattern matching: command → otk rewrite.
#
# OTK only rewrites commands that are specifically Odoo-, doodba- or
# Odoo-DB-centric. Generic dev commands (git, grep, find, ls, cat, pytest,
# pip, plain docker logs / ps / images) are intentionally left untouched —
# they are handled by general-purpose token-savers like RTK (rtk-ai/rtk),
# and rewriting them here caused two real-world problems:
#
#   1. Stacked PreToolUse hooks (OTK + RTK both enabled) made OTK rewrite
#      first → RTK then sees `otk git status` (not `git status`), doesn't
#      match, output stays uncompressed. Net negative.
#   2. When Claude was working on a non-Odoo Python project, OTK still
#      rewrote pytest / pip / find / grep / cat etc. — the otk filters
#      produced output the LLM couldn't interpret in that non-Odoo context,
#      so Claude resorted to creative workarounds that burned more tokens
#      than the filter ever saved.
#
# Recommended usage: install OTK *alongside* RTK. RTK handles the generic
# dev firehose; OTK handles the Odoo-specific verbose offenders below.
REWRITTEN=""

case "$FIRST_CMD" in
    # -- Odoo test runners --
    "invoke test"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    *"odoo-bin --test"*|*"odoo-bin -t"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;

    # -- Doodba / Odoo Docker stack (large structured log volume) --
    "docker compose logs"*|"docker-compose logs"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;

    # -- Odoo Database queries (psql often dumps wide ir_*/mail_*/stock_* rows) --
    "psql "*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
esac

# If no rewrite matched, exit silently (allow original command)
if [ -z "$REWRITTEN" ]; then
    exit 0
fi

# Reconstruct full command (preserve pipes/&& after first command)
REST=$(echo "$CMD" | sed "s|^[^|&;]*||")
FINAL_CMD="${REWRITTEN}${REST}"

# Output JSON hook response (same format as RTK)
cat <<HOOK_JSON
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "OTK auto-rewrite: token-optimized output",
    "updatedInput": {
      "command": $(echo "$FINAL_CMD" | jq -Rs .)
    }
  }
}
HOOK_JSON
