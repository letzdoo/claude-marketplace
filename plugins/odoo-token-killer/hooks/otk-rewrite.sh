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

# Skip heredocs and multi-line commands. Multi-line input would break the
# FIRST_CMD/REST reconstruction below, and substring patterns like
# *"odoo-bin --test"* would match text inside strings (e.g. commit messages).
if echo "$CMD" | grep -q '<<'; then
    exit 0
fi
case "$CMD" in
    *$'\n'*) exit 0 ;;
esac

# Extract first command (before pipes/&&)
# POSIX character classes: BSD sed (macOS) treats \s as a literal "s",
# silently truncating commands whose first segment ends in "s"
# ("src/main.rs" -> "src/main.r"). [[:space:]] works on GNU and BSD sed.
FIRST_CMD=$(echo "$CMD" | sed 's/[|&;].*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')

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

# Pattern matching: command → otk rewrite
REWRITTEN=""

case "$FIRST_CMD" in
    # -- Odoo Tests -- (otk subcommand "test" expects the full command in args)
    "invoke test"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} test ${FIRST_CMD}"
        ;;
    pytest*|"python -m pytest"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} test ${FIRST_CMD}"
        ;;
    *"odoo-bin --test"*|*"odoo-bin -t"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} test ${FIRST_CMD}"
        ;;

    # -- Docker/Logs -- (otk subcommand "logs" expects the full command in args)
    "docker compose logs"*|"docker-compose logs"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} logs ${FIRST_CMD}"
        ;;
    "docker logs"*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} logs ${FIRST_CMD}"
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

    # -- Search -- (do not rewrite rg: otk has no rg subcommand)
    "grep "*)
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

    # -- SQL -- (the otk subcommand is named "sql", not "psql"; the binary re-prepends "psql")
    "psql "*)
        REWRITTEN="${ENV_PREFIX}${OTK_CMD} sql ${FIRST_CMD#psql }"
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
