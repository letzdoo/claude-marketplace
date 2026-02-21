# OTK - Odoo Token Killer (Development Guide)

## Overview

OTK is a high-performance Rust CLI proxy for Odoo development with Claude Code.
Inspired by RTK (rtk-ai/rtk). Reduces token consumption by 60-90%.

Written in Rust for <10ms startup, 4.2MB binary, <5MB memory.

## Architecture

```
hooks/otk-rewrite.sh        PreToolUse hook (transparent command rewriting)
skills/otk-core/
  Cargo.toml                 Rust project manifest
  src/
    main.rs                  CLI entry point (clap derive) + command routing
    filters.rs               12 filter strategies (test, log, python, xml, git, etc.)
    tracking.rs              SQLite token tracking (TimedExecution, Tracker)
    tee.rs                   Full output recovery (save raw, print hint)
    gain.rs                  Analytics dashboard (summary, daily, JSON export)
commands/
  otk-setup.md              /otk-setup command
  otk-gain.md               /otk-gain command
agents/
  otk-setup.md              Setup automation agent
```

## Development Commands

```bash
cd plugins/odoo-token-killer/skills/otk-core

# Build
cargo build --release

# Test
cargo test

# Install globally
cargo install --path .

# Check binary size
ls -lh target/release/otk    # Should be <5MB

# Benchmark
hyperfine 'otk git status' 'git status' --warmup 3
```

## Adding a New Filter

1. Add a `pub fn my_filter(output: &str) -> String` in `src/filters.rs`
2. Add `lazy_static!` regex patterns at the top of the file
3. Add a new `Commands` variant in `src/main.rs`
4. Wire it in the `match` statement in `main()`
5. Add the command pattern to `hooks/otk-rewrite.sh`
6. Add unit tests in `#[cfg(test)] mod tests`
7. Update README.md filter table

## Design Principles (from RTK)

- **<10ms startup**: No async runtime, lazy regex, minimal allocations
- **Graceful degradation**: Falls back to raw output if filter fails
- **Exit code preservation**: Critical for CI/CD
- **Tee recovery**: Full output saved to disk, hint printed for LLM re-read
- **Measurable**: SQLite tracking + `otk gain` proves the value
- **Zero context overhead**: Hook-based rewriting is invisible to Claude
