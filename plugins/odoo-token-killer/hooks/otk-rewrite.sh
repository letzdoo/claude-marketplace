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
else
    # Try plugin-local installation via uv
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills/otk-core" 2>/dev/null && pwd)"
    if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR" ]; then
        OTK_CMD="cd $SCRIPT_DIR && uv run otk"
    else
        exit 0  # No otk available, skip silently
    fi
fi

# Pattern matching: command → otk rewrite
REWRITTEN=""

case "$FIRST_CMD" in
    # -- Odoo Tests --
    "invoke test"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    pytest*|"python -m pytest"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    *"odoo-bin --test"*|*"odoo-bin -t"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;

    # -- Docker/Logs --
    "docker compose logs"*|"docker-compose logs"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    "docker logs"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    "docker ps"*|"docker images"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;

    # -- Git --
    "git status"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    "git diff"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    "git log"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    "git add"*|"git commit"*|"git push"*|"git pull"*|"git fetch"*|"git stash"*|"git checkout"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;

    # -- File Reading (Python/XML) --
    "cat "*.py|"cat "*.xml|"cat "*.csv)
        FILE=$(echo "$FIRST_CMD" | awk '{print $NF}')
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} read ${FILE}"
        ;;

    # -- Search --
    "grep "*|"rg "*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;

    # -- Directory Listing --
    "ls "*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    "tree "*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;
    "find "*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;

    # -- Python Packages --
    "pip list"*|"pip install"*|"pip freeze"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} ${FIRST_CMD}"
        ;;

    # -- SQL --
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
