---
name: otk-gain
description: |
  Show OTK token savings analytics dashboard.
  Use when: 'otk gain', 'token savings', 'how many tokens saved', 'otk stats',
  'show savings', 'token analytics', 'otk dashboard'.
arguments:
  - name: format
    description: "Output format: text (default), json, csv"
    required: false
  - name: period
    description: "Time period: summary (default), daily, weekly"
    required: false
input_examples:
  - description: "Show summary dashboard"
    arguments: {}
  - description: "Show daily breakdown as JSON"
    arguments:
      format: "json"
      period: "daily"
  - description: "Reset tracking data"
    arguments:
      format: "reset"
---

# /otk-gain Command

Display the OTK token savings analytics dashboard.

## Execution

Run the gain command with appropriate flags:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk gain
```

For daily breakdown:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk gain --daily
```

For JSON export:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk gain --json
```

For daily JSON:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk gain --daily --json
```

To reset tracking:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && uv run otk gain --reset
```

## Output

The dashboard shows:
- Total commands tracked
- Input/output token counts
- Tokens saved with percentage
- Execution time total
- Breakdown by command (top 15 by savings)
- Optional daily breakdown

## Interpreting Results

- **70%+ savings**: Excellent - tests, logs, git write operations
- **40-70% savings**: Good - file reading, grep, status
- **<40% savings**: Moderate - small files, simple commands
- **0% savings**: Passthrough - command not matched to a filter

Report these results to the user clearly, highlighting the most impactful commands.
