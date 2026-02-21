---
name: odoo-token-killer
description: |
  OTK (Odoo Token Killer) - Reduce token consumption by 60-90% on Odoo development operations.
  Inspired by RTK (Rust Token Killer) by the rtk-ai team.

  AUTO-USE when running Bash commands during Odoo development.
  The PreToolUse hook handles transparent rewriting automatically.

  For manual use, prefix commands with `otk`:
    otk invoke test my_module    → test failures only (90% savings)
    otk docker compose logs odoo → errors/warnings only (90% savings)
    otk git status               → compact stats (80% savings)
    otk read models/sale.py      → signatures + fields only (60% savings)
    otk read views/sale_view.xml → structure only (70% savings)
    otk gain                     → token savings dashboard

  Compatible with: odoo-doodba-dev, odoo-development, odoo-query plugins.
allowed-tools: Bash, Read, Glob, Grep
---

# OTK - Odoo Token Killer

**Reduce Claude Code token consumption by 60-90% on Odoo development.**

Inspired by [RTK (Rust Token Killer)](https://github.com/rtk-ai/rtk) by the rtk-ai team.
We thank the RTK team for pioneering the token-optimized CLI proxy pattern.

## How It Works

OTK sits between Claude Code and your terminal. When Claude runs commands,
OTK's PreToolUse hook transparently intercepts and filters the output:

```
Claude runs: git status
Hook rewrites: otk git status
Output: "3 modified, 1 added" instead of 50 lines of verbose status
Tokens saved: ~80%
```

## Token Savings (Typical Odoo Session)

| Operation | Frequency | Without OTK | With OTK | Savings |
|-----------|-----------|-------------|----------|---------|
| `invoke test` | 5x | 50,000 | 5,000 | -90% |
| `docker compose logs` | 10x | 30,000 | 3,000 | -90% |
| Reading .py files | 20x | 40,000 | 12,000 | -70% |
| Reading .xml views | 15x | 30,000 | 9,000 | -70% |
| `git status/diff/log` | 10x | 15,000 | 3,000 | -80% |
| `grep/rg` searches | 8x | 16,000 | 3,200 | -80% |
| **Total** | | **~181,000** | **~35,200** | **-81%** |

## Commands

| Command | Description |
|---------|-------------|
| `/otk-setup` | Install OTK and register the PreToolUse hook |
| `/otk-gain` | Show token savings analytics dashboard |

## Filter Strategies

12 specialized filters, each targeting a specific output type:

1. **Test Filter** (90-95%): pytest/invoke test → failures only
2. **Log Filter** (85-95%): Docker/Odoo logs → errors + warnings
3. **Python Filter** (40-70%): .py files → signatures + fields + docstrings
4. **XML Filter** (60-80%): .xml views → structure, tag names, attributes
5. **Git Status** (80%): Compact file counts
6. **Git Diff** (70-80%): Stats + key hunk headers
7. **Git Log** (80%): One-line per commit
8. **Grep Filter** (70-85%): Grouped by file, deduplicated
9. **LS Filter** (50-70%): Compact tree with extension counts
10. **Docker Filter** (60-80%): Truncated IDs, compact tables
11. **Pip Filter** (80-90%): Package count summaries
12. **SQL Filter** (60-80%): Truncated columns, row limits

## Compatibility

OTK works alongside all other Letzdoo plugins:
- **odoo-doodba-dev**: OTK filters test output from `invoke test`
- **odoo-development**: OTK reduces context before code generation
- **odoo-query**: XML-RPC results pass through (already compact JSON)
