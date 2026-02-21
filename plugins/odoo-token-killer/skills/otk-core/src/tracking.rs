// OTK Token Tracking - SQLite-based metrics storage.
// Modeled after RTK's tracking.rs (rtk-ai/rtk).

use anyhow::{Context, Result};
use rusqlite::Connection;
use std::path::PathBuf;
use std::time::Instant;

const HISTORY_DAYS: i64 = 90;

fn db_path() -> PathBuf {
    if let Ok(path) = std::env::var("OTK_DB_PATH") {
        return PathBuf::from(path);
    }
    let data_dir = dirs::data_local_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("otk");
    data_dir.join("tracking.db")
}

pub fn estimate_tokens(text: &str) -> usize {
    if text.is_empty() {
        return 0;
    }
    ((text.len() as f64) / 4.0).ceil() as usize
}

pub struct Tracker {
    conn: Connection,
}

impl Tracker {
    pub fn new() -> Result<Self> {
        let path = db_path();
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)
                .context("Failed to create OTK data directory")?;
        }

        let conn = Connection::open(&path)
            .context("Failed to open tracking database")?;

        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY,
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
            CREATE INDEX IF NOT EXISTS idx_commands_otk_cmd ON commands(otk_cmd);",
        )
        .context("Failed to initialize database schema")?;

        let tracker = Self { conn };
        tracker.cleanup_old();
        Ok(tracker)
    }

    pub fn record(
        &self,
        original_cmd: &str,
        otk_cmd: &str,
        input_tokens: usize,
        output_tokens: usize,
        exec_time_ms: u64,
    ) -> Result<()> {
        let saved = input_tokens.saturating_sub(output_tokens);
        let pct = if input_tokens > 0 {
            (saved as f64 / input_tokens as f64) * 100.0
        } else {
            0.0
        };
        let now = chrono::Utc::now().to_rfc3339();

        self.conn
            .execute(
                "INSERT INTO commands (timestamp, original_cmd, otk_cmd, \
                 input_tokens, output_tokens, saved_tokens, savings_pct, exec_time_ms) \
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
                rusqlite::params![
                    now,
                    original_cmd,
                    otk_cmd,
                    input_tokens as i64,
                    output_tokens as i64,
                    saved as i64,
                    pct,
                    exec_time_ms as i64,
                ],
            )
            .context("Failed to record command")?;

        Ok(())
    }

    pub fn summary(&self) -> Result<GainSummary> {
        let mut stmt = self.conn.prepare(
            "SELECT COUNT(*), COALESCE(SUM(input_tokens),0), \
             COALESCE(SUM(output_tokens),0), COALESCE(SUM(saved_tokens),0), \
             COALESCE(AVG(savings_pct),0), COALESCE(SUM(exec_time_ms),0) \
             FROM commands",
        )?;

        let row = stmt.query_row([], |row| {
            Ok(GainSummary {
                total_commands: row.get(0)?,
                input_tokens: row.get(1)?,
                output_tokens: row.get(2)?,
                saved_tokens: row.get(3)?,
                avg_savings_pct: row.get(4)?,
                total_exec_time_ms: row.get(5)?,
            })
        })?;

        Ok(row)
    }

    pub fn by_command(&self, limit: usize) -> Result<Vec<CommandStats>> {
        let mut stmt = self.conn.prepare(
            "SELECT otk_cmd, COUNT(*) as cnt, SUM(saved_tokens) as saved, \
             AVG(savings_pct) as avg_pct, SUM(exec_time_ms) as total_ms \
             FROM commands GROUP BY otk_cmd \
             ORDER BY saved DESC LIMIT ?1",
        )?;

        let rows = stmt
            .query_map([limit as i64], |row| {
                Ok(CommandStats {
                    command: row.get(0)?,
                    count: row.get(1)?,
                    saved: row.get(2)?,
                    avg_pct: row.get(3)?,
                    exec_time_ms: row.get(4)?,
                })
            })?
            .collect::<Result<Vec<_>, _>>()
            .context("Failed to query command stats")?;

        Ok(rows)
    }

    pub fn daily(&self, days: i64) -> Result<Vec<DayStats>> {
        let mut stmt = self.conn.prepare(
            "SELECT DATE(timestamp) as day, COUNT(*), SUM(saved_tokens), \
             AVG(savings_pct), SUM(exec_time_ms) \
             FROM commands WHERE timestamp >= DATE('now', ?1) \
             GROUP BY day ORDER BY day DESC",
        )?;

        let offset = format!("-{} days", days);
        let rows = stmt
            .query_map([&offset], |row| {
                Ok(DayStats {
                    date: row.get(0)?,
                    commands: row.get(1)?,
                    saved: row.get(2)?,
                    avg_pct: row.get(3)?,
                    exec_time_ms: row.get(4)?,
                })
            })?
            .collect::<Result<Vec<_>, _>>()
            .context("Failed to query daily stats")?;

        Ok(rows)
    }

    fn cleanup_old(&self) {
        let offset = format!("-{} days", HISTORY_DAYS);
        let _ = self.conn.execute(
            "DELETE FROM commands WHERE timestamp < DATE('now', ?1)",
            [&offset],
        );
    }

    pub fn reset(&self) -> Result<()> {
        self.conn
            .execute("DELETE FROM commands", [])
            .context("Failed to reset tracking")?;
        Ok(())
    }
}

#[derive(Debug, serde::Serialize)]
pub struct GainSummary {
    pub total_commands: i64,
    pub input_tokens: i64,
    pub output_tokens: i64,
    pub saved_tokens: i64,
    pub avg_savings_pct: f64,
    pub total_exec_time_ms: i64,
}

#[derive(Debug, serde::Serialize)]
pub struct CommandStats {
    pub command: String,
    pub count: i64,
    pub saved: i64,
    pub avg_pct: f64,
    pub exec_time_ms: i64,
}

#[derive(Debug, serde::Serialize)]
pub struct DayStats {
    pub date: String,
    pub commands: i64,
    pub saved: i64,
    pub avg_pct: f64,
    pub exec_time_ms: i64,
}

pub struct TimedExecution {
    start: Instant,
}

impl TimedExecution {
    pub fn start() -> Self {
        Self {
            start: Instant::now(),
        }
    }

    pub fn track(&self, original_cmd: &str, otk_cmd: &str, input: &str, output: &str) {
        let elapsed_ms = self.start.elapsed().as_millis() as u64;
        let input_tokens = estimate_tokens(input);
        let output_tokens = estimate_tokens(output);

        if let Ok(tracker) = Tracker::new() {
            let _ = tracker.record(original_cmd, otk_cmd, input_tokens, output_tokens, elapsed_ms);
        }
    }

    pub fn track_passthrough(&self, original_cmd: &str, otk_cmd: &str) {
        let elapsed_ms = self.start.elapsed().as_millis() as u64;
        if let Ok(tracker) = Tracker::new() {
            let _ = tracker.record(original_cmd, otk_cmd, 0, 0, elapsed_ms);
        }
    }
}
