# OTK - Odoo Token Killer

**Reduce Claude Code token consumption by 60-90% on Odoo development operations.**

Inspired by and built upon the ideas of [RTK (Rust Token Killer)](https://github.com/rtk-ai/rtk)
by the [rtk-ai team](https://github.com/rtk-ai). We are grateful for their pioneering work on
token-optimized CLI proxies for LLM development workflows. OTK applies the same principles
-- transparent output filtering, hook-based command rewriting, and data-driven analytics --
to the Odoo ERP development ecosystem.

## How It Works

OTK is a CLI proxy that filters command outputs before they reach Claude's context window.
A PreToolUse hook transparently rewrites commands so Claude never sees the overhead:

```
Claude runs:    invoke test sale_module
Hook rewrites:  otk invoke test sale_module
Claude sees:    "Tests: 142 passed, 1 failed\nFAILED test_sale_discount: AssertionError..."
Instead of:     3,000 lines of Odoo logs, module loading, SQL queries, and XML-RPC traces
```

## Token Savings (Typical 30-min Odoo Session)

| Operation | Freq | Without OTK | With OTK | Savings |
|-----------|------|-------------|----------|---------|
| `invoke test` | 5x | 50,000 | 5,000 | **-90%** |
| `docker compose logs` | 10x | 30,000 | 3,000 | **-90%** |
| Reading `.py` files | 20x | 40,000 | 12,000 | **-70%** |
| Reading `.xml` views | 15x | 30,000 | 9,000 | **-70%** |
| `git status/diff/log` | 10x | 15,000 | 3,000 | **-80%** |
| `grep/rg` searches | 8x | 16,000 | 3,200 | **-80%** |
| **Total** | | **~181,000** | **~35,200** | **-81%** |

## Quick Start

```bash
/otk-setup    # Install, register hook, validate
```

That's it. Commands are now transparently optimized.

## Commands

| Command | Description |
|---------|-------------|
| `/otk-setup` | Install OTK and register the PreToolUse hook |
| `/otk-gain` | Show token savings analytics dashboard |

## The `/otk-gain` Dashboard

See exactly what OTK saves you:

```
OTK Token Savings (Odoo Development)
==================================================
Total commands:        89
Input tokens:          181.0K
Output tokens:         35.2K
Tokens saved:          145.8K (81.0%)
Exec time:             12,340ms

Command                 Count    Saved     Avg%
------------------------------------------------
otk invoke test            12    45.0K    90.0%
otk docker compose logs    18    27.0K    90.0%
otk read *.py              25    28.0K    70.0%
otk git status             15    12.0K    80.0%
otk grep                    8    12.8K    80.0%
otk read *.xml             11    21.0K    70.0%
```

## 12 Filter Strategies

| # | Filter | Target | Savings | What It Does |
|---|--------|--------|---------|-------------|
| 1 | Test | pytest, invoke test | 90-95% | Failures + summary only |
| 2 | Log | Docker, Odoo logs | 85-95% | Errors + warnings + context |
| 3 | Python | .py source files | 40-70% | Signatures, fields, docstrings |
| 4 | XML | .xml views/data | 60-80% | Tags, attributes, structure |
| 5 | Git Status | git status | 80% | File counts by category |
| 6 | Git Diff | git diff | 70-80% | Stats + key hunk headers |
| 7 | Git Log | git log | 80% | One-line per commit |
| 8 | Grep | grep, rg | 70-85% | Grouped by file, deduped |
| 9 | LS/Tree | ls, tree, find | 50-70% | Compact tree + extension counts |
| 10 | Docker | docker ps/images | 60-80% | Truncated IDs, compact tables |
| 11 | Pip | pip list/install | 80-90% | Package count summaries |
| 12 | SQL | psql queries | 60-80% | Truncated columns, row limits |

## Architecture

```
Claude Code runs a command
         |
    PreToolUse Hook (hooks/otk-rewrite.sh)
         |
    Pattern match → rewrite to otk prefix
         |
    OTK CLI (scripts/cli.py)
         |
    Route to filter (src/filters.rs)
         |
    Execute command → capture raw output
         |
    Apply filter strategy → compressed output
         |
    Save full output to tee file (src/tee.rs)
         |
    Track metrics (src/tracking.rs → SQLite)
         |
    Return filtered output + [full output: ~/.local/share/otk/tee/...] hint
```

## Full Output Recovery (Tee)

When OTK filters output, the complete raw version is saved to disk.
The filtered output includes a hint line that Claude can use to access the full content:

```
Tests: 142 passed, 1 failed
FAILED test_sale_discount: AssertionError: expected 10.0, got 9.5
[full output: ~/.local/share/otk/tee/1234567890_invoke_test.log]
```

If the agent needs the full unfiltered output, it reads the tee file.
Tee modes: `failures` (default), `always`, `never` — via `OTK_TEE_MODE` env var.

## Key Design Principles (Learned from RTK)

1. **Rust**: <10ms startup, 4.2MB binary, same language as RTK
2. **Transparent**: Hook-based rewriting means zero context overhead
3. **Measurable**: SQLite tracking + `/otk-gain` proves the value
4. **Recoverable**: Tee system saves full output for when the agent needs it
5. **Graceful**: Falls back to raw output if filter fails
6. **Preserves exit codes**: Critical for CI/CD and test workflows

## Compatibility

OTK works alongside all Letzdoo marketplace plugins:

| Plugin | Integration |
|--------|-------------|
| **odoo-doodba-dev** | OTK filters `invoke test` output from Doodba |
| **odoo-development** | OTK reduces context before code generation agents |
| **odoo-query** | XML-RPC results pass through (already compact JSON) |

## Acknowledgments

This project would not exist without [RTK (Rust Token Killer)](https://github.com/rtk-ai/rtk)
by [pszymkowiak](https://github.com/pszymkowiak) and the rtk-ai team.

RTK demonstrated that:
- **60-90% token savings** are achievable through intelligent output filtering
- **Hook-first architecture** provides zero-overhead integration with Claude Code
- **Data-driven analytics** (`rtk gain`) make savings visible and compelling
- **Graceful degradation** ensures reliability in production workflows

OTK adapts these insights for the Odoo ecosystem, written in Rust like RTK,
with filters tuned for Odoo's specific output patterns (test runners, ORM logs,
XML views, Docker containers) and a tee system for full output recovery.

## License

LGPL-3.0 - Same as Odoo Community Edition.
