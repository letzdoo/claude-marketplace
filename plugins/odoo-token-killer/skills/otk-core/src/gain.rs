// OTK Gain - Token savings analytics dashboard.
// Modeled after RTK's gain.rs (rtk-ai/rtk).

use crate::tracking::Tracker;
use anyhow::{Context, Result};
use colored::*;
use std::io::IsTerminal;

pub fn run(daily: bool, json: bool, reset: bool) -> Result<()> {
    let tracker = Tracker::new().context("Failed to open tracking database")?;

    if reset {
        tracker.reset()?;
        println!("Tracking database reset.");
        return Ok(());
    }

    let summary = tracker.summary()?;

    if json {
        return run_json(&tracker, &summary, daily);
    }

    if summary.total_commands == 0 {
        println!("No commands tracked yet. Use otk to run commands and track savings.");
        return Ok(());
    }

    // Pretty dashboard
    let is_tty = std::io::stdout().is_terminal();

    let title = "OTK Token Savings (Odoo Development)";
    if is_tty {
        println!("{}", title.bold());
    } else {
        println!("{}", title);
    }
    println!("{}", "=".repeat(50));
    println!("{:<22} {:>10}", "Total commands:", format!("{}", summary.total_commands));
    println!("{:<22} {:>10}", "Input tokens:", fmt_tokens(summary.input_tokens));
    println!("{:<22} {:>10}", "Output tokens:", fmt_tokens(summary.output_tokens));
    println!(
        "{:<22} {:>10}",
        "Tokens saved:",
        format!("{} ({:.1}%)", fmt_tokens(summary.saved_tokens), summary.avg_savings_pct)
    );
    println!("{:<22} {:>10}", "Exec time:", format!("{}ms", summary.total_exec_time_ms));

    // By command breakdown
    let by_cmd = tracker.by_command(15)?;
    if !by_cmd.is_empty() {
        println!();

        let cmd_w = by_cmd
            .iter()
            .map(|c| c.command.len())
            .max()
            .unwrap_or(20)
            .max(20);

        println!(
            "{:<cmd_w$}  {:>6}  {:>8}  {:>6}",
            "Command", "Count", "Saved", "Avg%",
            cmd_w = cmd_w
        );
        println!("{}", "-".repeat(cmd_w + 26));

        for c in &by_cmd {
            let pct_str = format!("{:.1}%", c.avg_pct);
            let pct_display = if is_tty {
                colorize_pct(c.avg_pct, &pct_str)
            } else {
                pct_str
            };
            println!(
                "{:<cmd_w$}  {:>6}  {:>8}  {:>6}",
                c.command,
                c.count,
                fmt_tokens(c.saved),
                pct_display,
                cmd_w = cmd_w
            );
        }
    }

    // Daily breakdown
    if daily {
        let days = tracker.daily(30)?;
        if !days.is_empty() {
            println!();
            if is_tty {
                println!("{}", "Daily Breakdown".bold());
            } else {
                println!("Daily Breakdown");
            }
            println!("{}", "-".repeat(50));
            println!("{:<12}  {:>6}  {:>8}  {:>6}", "Date", "Cmds", "Saved", "Avg%");

            for d in &days {
                let pct_str = format!("{:.1}%", d.avg_pct);
                let pct_display = if is_tty {
                    colorize_pct(d.avg_pct, &pct_str)
                } else {
                    pct_str
                };
                println!(
                    "{:<12}  {:>6}  {:>8}  {:>6}",
                    d.date,
                    d.commands,
                    fmt_tokens(d.saved),
                    pct_display
                );
            }
        }
    }

    Ok(())
}

fn run_json(
    tracker: &Tracker,
    summary: &crate::tracking::GainSummary,
    daily: bool,
) -> Result<()> {
    let mut data = serde_json::json!({
        "summary": summary,
        "by_command": tracker.by_command(15)?,
    });

    if daily {
        data["daily"] = serde_json::to_value(tracker.daily(30)?)?;
    }

    println!("{}", serde_json::to_string_pretty(&data)?);
    Ok(())
}

fn fmt_tokens(n: i64) -> String {
    if n >= 1_000_000 {
        format!("{:.1}M", n as f64 / 1_000_000.0)
    } else if n >= 1_000 {
        format!("{:.1}K", n as f64 / 1_000.0)
    } else {
        n.to_string()
    }
}

fn colorize_pct(pct: f64, text: &str) -> String {
    if pct >= 70.0 {
        text.green().bold().to_string()
    } else if pct >= 40.0 {
        text.yellow().bold().to_string()
    } else {
        text.red().bold().to_string()
    }
}
