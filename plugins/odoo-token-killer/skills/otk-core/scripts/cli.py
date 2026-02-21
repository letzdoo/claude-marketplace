#!/usr/bin/env python3
"""
OTK CLI - Odoo Token Killer

A CLI proxy that filters command outputs before they reach your LLM context.
Inspired by RTK (Rust Token Killer) - https://github.com/rtk-ai/rtk

Usage:
    otk <command> [args...]     Execute command with token-optimized output
    otk gain                    Show token savings analytics
    otk gain --daily            Daily breakdown
    otk gain --json             Export as JSON
    otk gain --reset            Reset tracking database

Examples:
    otk invoke test my_module           Run Odoo tests, show failures only
    otk docker compose logs odoo        Show errors/warnings only
    otk git status                      Compact status
    otk read models/sale.py             Filtered Python source
    otk read views/sale_view.xml        XML structure only
"""

import json
import os
import subprocess
import sys

from .filters import route_filter, python_filter, xml_filter, passthrough
from .tracking import TimedExecution, Tracker, estimate_tokens


def run_gain(args: list[str]):
    """Display token savings analytics dashboard."""
    try:
        tracker = Tracker()
    except Exception as e:
        print(f"Error opening tracking database: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle flags
    as_json = "--json" in args
    daily = "--daily" in args
    reset = "--reset" in args

    if reset:
        import shutil
        from .tracking import DB_PATH
        if DB_PATH.exists():
            DB_PATH.unlink()
            print("Tracking database reset.")
        return

    summary = tracker.summary()

    if as_json:
        data = {"summary": summary}
        if daily:
            data["daily"] = tracker.daily()
        data["by_command"] = tracker.by_command()
        print(json.dumps(data, indent=2))
        return

    # Pretty dashboard (inspired by rtk gain)
    total = summary["total_commands"]
    if total == 0:
        print("No commands tracked yet. Use otk to run commands and track savings.")
        return

    input_t = summary["input_tokens"]
    output_t = summary["output_tokens"]
    saved_t = summary["saved_tokens"]
    pct = summary["avg_savings_pct"]

    print("OTK Token Savings (Odoo Development)")
    print("=" * 50)
    print(f"{'Total commands:':<22} {total:,}")
    print(f"{'Input tokens:':<22} {_fmt_tokens(input_t)}")
    print(f"{'Output tokens:':<22} {_fmt_tokens(output_t)}")
    print(f"{'Tokens saved:':<22} {_fmt_tokens(saved_t)} ({pct:.1f}%)")
    print(f"{'Exec time:':<22} {summary['total_exec_time_ms']:,}ms")

    # By command breakdown
    by_cmd = tracker.by_command()
    if by_cmd:
        print()
        # Dynamic column width
        cmd_w = max(len(c["command"]) for c in by_cmd)
        cmd_w = max(cmd_w, 20)
        print(f"{'Command':<{cmd_w}}  {'Count':>6}  {'Saved':>8}  {'Avg%':>6}")
        print("-" * (cmd_w + 26))
        for c in by_cmd:
            print(f"{c['command']:<{cmd_w}}  {c['count']:>6}  "
                  f"{_fmt_tokens(c['saved']):>8}  {c['avg_pct']:>5.1f}%")

    # Daily breakdown
    if daily:
        days = tracker.daily()
        if days:
            print()
            print("Daily Breakdown")
            print("-" * 50)
            print(f"{'Date':<12}  {'Cmds':>6}  {'Saved':>8}  {'Avg%':>6}")
            for d in days:
                print(f"{d['date']:<12}  {d['commands']:>6}  "
                      f"{_fmt_tokens(d['saved']):>8}  {d['avg_pct']:>5.1f}%")

    tracker.close()


def _fmt_tokens(n: int) -> str:
    """Format token count: 1234 → '1.2K', 1234567 → '1.2M'."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def run_command(cmd_args: list[str]):
    """Execute a command and filter its output."""
    if not cmd_args:
        print(__doc__)
        sys.exit(0)

    command = " ".join(cmd_args)
    timer = TimedExecution()

    # Determine if we're reading a file (cat/read equivalent)
    is_file_read = False
    file_path = None
    if cmd_args[0] in ("read", "cat", "head"):
        is_file_read = True
        file_path = cmd_args[-1] if len(cmd_args) > 1 else None

    # For file reads, read directly instead of subprocess
    if is_file_read and file_path and os.path.isfile(file_path):
        try:
            with open(file_path, "r", errors="replace") as f:
                raw_output = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

        # Route filter based on extension
        if file_path.endswith((".xml", ".html")):
            filter_name, filtered = "xml_filter", xml_filter(raw_output)
        elif file_path.endswith(".py"):
            filter_name, filtered = "python_filter", python_filter(raw_output)
        else:
            filter_name, filtered = "passthrough", passthrough(raw_output)

        print(filtered)
        timer.track(f"cat {file_path}", f"otk read {file_path}", raw_output, filtered)
        return

    # Execute command via subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min timeout
        )
    except subprocess.TimeoutExpired:
        print(f"Command timed out after 300s: {command}", file=sys.stderr)
        sys.exit(124)
    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        sys.exit(1)

    raw_output = result.stdout + ("\n" + result.stderr if result.stderr else "")

    # Route to appropriate filter
    filter_name, filtered = route_filter(command, raw_output)

    # Graceful fallback: if filter returned empty but command succeeded, show minimal output
    if not filtered.strip() and result.returncode == 0:
        filtered = "ok"
    elif not filtered.strip() and result.returncode != 0:
        # On failure with empty filter result, show last 15 lines
        lines = raw_output.strip().splitlines()
        filtered = f"Command failed (exit code {result.returncode}):\n"
        filtered += "\n".join(lines[-15:])

    print(filtered)

    # Track metrics
    timer.track(command, f"otk {command}", raw_output, filtered)

    # Preserve exit code (critical for CI/CD, same as RTK)
    sys.exit(result.returncode)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)

    if args[0] == "--version":
        print("otk 1.0.0 (Odoo Token Killer)")
        sys.exit(0)

    if args[0] == "gain":
        run_gain(args[1:])
        sys.exit(0)

    # Everything else: execute + filter
    run_command(args)


if __name__ == "__main__":
    main()
