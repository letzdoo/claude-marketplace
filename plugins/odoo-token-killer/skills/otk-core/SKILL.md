---
name: otk-core
description: |
  Core OTK engine: Rust CLI proxy, output filters, token tracking, and analytics.
  This skill provides the `otk` binary and all 12 filter strategies.
  AUTO-TRIGGER: Used automatically via PreToolUse hook - no manual invocation needed.
  Performance: <10ms startup, <5MB binary, <5MB memory. Written in Rust like RTK.
allowed-tools: Bash, Read
---

# OTK Core Engine

A high-performance Rust binary providing:
- `otk <command>` - Token-filtered command execution
- `otk gain` - Analytics dashboard
- `otk read <file>` - Filtered file reading with tee recovery
- 12 specialized output filters
- SQLite-based token tracking
- Tee system for full output recovery

## Quick Reference

```bash
# After cargo install:
otk git status                # Compact status
otk git log                   # One-line per commit
otk test invoke test module   # Failures only
otk logs docker compose logs  # Errors/warnings only
otk read models/sale.py       # Filtered Python source
otk read views/sale_view.xml  # XML structure only
otk gain                      # Token savings dashboard
otk gain --daily --json       # Export analytics
otk proxy <any command>       # Passthrough with tracking
```

## Tee: Full Output Recovery

When OTK filters output, the full raw version is saved to disk:
```
[full output: ~/.local/share/otk/tee/1234567890_git_log.log]
```
Read that file to access the complete unfiltered output.

## Build

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && cargo build --release
# Binary: target/release/otk (4.2MB)
```

## Install

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/otk-core && cargo install --path .
```
