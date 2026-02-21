#!/usr/bin/env python3
"""
OTK Token Tracking - SQLite-based metrics storage.

Modeled after RTK's tracking.rs (rtk-ai/rtk).
Records every filtered command with input/output token counts,
savings percentage, and execution time for analytics.
"""

import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

HISTORY_DAYS = 90
DB_DIR = Path(os.environ.get("OTK_DATA_DIR", Path.home() / ".local" / "share" / "otk"))
DB_PATH = DB_DIR / "tracking.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    original_cmd TEXT NOT NULL,
    otk_cmd TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    saved_tokens INTEGER NOT NULL,
    savings_pct REAL NOT NULL,
    exec_time_ms INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_commands_timestamp ON commands(timestamp);
CREATE INDEX IF NOT EXISTS idx_commands_otk_cmd ON commands(otk_cmd);
"""


def estimate_tokens(text: str) -> int:
    """Estimate token count. ~4 chars per token (GPT-style heuristic)."""
    if not text:
        return 0
    return max(1, -(-len(text) // 4))  # ceil division


class TimedExecution:
    """Context manager for timing command execution and recording metrics."""

    def __init__(self):
        self._start = time.monotonic()

    @property
    def elapsed_ms(self) -> int:
        return int((time.monotonic() - self._start) * 1000)

    def track(self, original_cmd: str, otk_cmd: str, raw_output: str, filtered_output: str):
        input_tokens = estimate_tokens(raw_output)
        output_tokens = estimate_tokens(filtered_output)
        try:
            tracker = Tracker()
            tracker.record(original_cmd, otk_cmd, input_tokens, output_tokens, self.elapsed_ms)
        except Exception:
            pass  # Never break the command for tracking failures


class Tracker:
    """SQLite-backed token tracking database."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.executescript(SCHEMA)
        self._cleanup_old()

    def record(self, original_cmd: str, otk_cmd: str,
               input_tokens: int, output_tokens: int, exec_time_ms: int = 0):
        saved = max(0, input_tokens - output_tokens)
        pct = (saved / input_tokens * 100) if input_tokens > 0 else 0.0
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT INTO commands (timestamp, original_cmd, otk_cmd, "
            "input_tokens, output_tokens, saved_tokens, savings_pct, exec_time_ms) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (now, original_cmd, otk_cmd, input_tokens, output_tokens, saved, pct, exec_time_ms)
        )
        self._conn.commit()

    def summary(self) -> dict:
        """Overall summary statistics."""
        row = self._conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(input_tokens),0), "
            "COALESCE(SUM(output_tokens),0), COALESCE(SUM(saved_tokens),0), "
            "COALESCE(AVG(savings_pct),0), COALESCE(SUM(exec_time_ms),0) "
            "FROM commands"
        ).fetchone()
        return {
            "total_commands": row[0],
            "input_tokens": row[1],
            "output_tokens": row[2],
            "saved_tokens": row[3],
            "avg_savings_pct": round(row[4], 1),
            "total_exec_time_ms": row[5],
        }

    def by_command(self, limit: int = 15) -> list[dict]:
        """Top commands by tokens saved."""
        rows = self._conn.execute(
            "SELECT otk_cmd, COUNT(*) as cnt, SUM(saved_tokens) as saved, "
            "AVG(savings_pct) as avg_pct, SUM(exec_time_ms) as total_ms "
            "FROM commands GROUP BY otk_cmd "
            "ORDER BY saved DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [
            {"command": r[0], "count": r[1], "saved": r[2],
             "avg_pct": round(r[3], 1), "exec_time_ms": r[4]}
            for r in rows
        ]

    def daily(self, days: int = 30) -> list[dict]:
        """Daily breakdown for the last N days."""
        rows = self._conn.execute(
            "SELECT DATE(timestamp) as day, COUNT(*), SUM(saved_tokens), "
            "AVG(savings_pct), SUM(exec_time_ms) "
            "FROM commands WHERE timestamp >= DATE('now', ?) "
            "GROUP BY day ORDER BY day DESC",
            (f"-{days} days",)
        ).fetchall()
        return [
            {"date": r[0], "commands": r[1], "saved": r[2],
             "avg_pct": round(r[3], 1), "exec_time_ms": r[4]}
            for r in rows
        ]

    def _cleanup_old(self):
        try:
            self._conn.execute(
                "DELETE FROM commands WHERE timestamp < DATE('now', ?)",
                (f"-{HISTORY_DAYS} days",)
            )
            self._conn.commit()
        except Exception:
            pass

    def close(self):
        self._conn.close()
