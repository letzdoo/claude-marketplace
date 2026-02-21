// OTK - Odoo Token Killer
// High-performance CLI proxy to minimize LLM token consumption for Odoo development.
// Inspired by RTK (Rust Token Killer) - https://github.com/rtk-ai/rtk

mod filters;
mod gain;
mod tee;
mod tracking;

use anyhow::Result;
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    name = "otk",
    version,
    about = "Odoo Token Killer - minimize LLM token consumption for Odoo development",
    long_about = "OTK filters and compresses command outputs before they reach your LLM context,\n\
                  saving 60-90% of tokens on common Odoo development operations.\n\n\
                  Inspired by RTK (rtk-ai/rtk). Thanks to the RTK team for pioneering this approach."
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    /// Increase verbosity (-v, -vv)
    #[arg(short, long, action = clap::ArgAction::Count, global = true)]
    verbose: u8,
}

#[derive(Subcommand)]
enum Commands {
    /// Show token savings analytics dashboard
    Gain {
        /// Show daily breakdown
        #[arg(long)]
        daily: bool,

        /// Export as JSON
        #[arg(long)]
        json: bool,

        /// Reset tracking database
        #[arg(long)]
        reset: bool,
    },

    /// Run Odoo tests (invoke test / pytest) - show failures only
    Test {
        /// Arguments passed to the test runner
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Filter Docker/Odoo logs - errors and warnings only
    Logs {
        /// Arguments passed to docker compose logs
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Read a file with token-optimized filtering
    Read {
        /// File path to read
        path: String,

        /// Filter level: none, minimal, aggressive
        #[arg(short, long, default_value = "minimal")]
        level: String,
    },

    /// Git operations with compact output
    Git {
        /// Git subcommand and arguments
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Grep/search with grouped, deduplicated output
    Grep {
        /// Arguments passed to grep/rg
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Directory listing with compact tree view
    Ls {
        /// Arguments passed to ls
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Docker commands with compact output
    Docker {
        /// Arguments passed to docker
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// pip/uv commands with summary output
    Pip {
        /// Arguments passed to pip
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// SQL queries with compact output
    Sql {
        /// Arguments passed to psql
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Tree directory listing
    Tree {
        /// Arguments passed to tree
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Find files
    Find {
        /// Arguments passed to find
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Run any command with error-only filtering
    Err {
        /// Command and arguments
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },

    /// Run any command with passthrough (track but don't filter)
    Proxy {
        /// Command and arguments
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Gain { daily, json, reset } => {
            gain::run(daily, json, reset)?;
        }
        Commands::Test { args } => {
            run_filtered("test", &args, cli.verbose, filters::test_filter)?;
        }
        Commands::Logs { args } => {
            run_filtered("logs", &args, cli.verbose, filters::log_filter)?;
        }
        Commands::Read { path, level } => {
            run_read(&path, &level, cli.verbose)?;
        }
        Commands::Git { args } => {
            run_git(&args, cli.verbose)?;
        }
        Commands::Grep { args } => {
            run_filtered("grep", &args, cli.verbose, filters::grep_filter)?;
        }
        Commands::Ls { args } => {
            run_filtered("ls", &args, cli.verbose, filters::ls_filter)?;
        }
        Commands::Docker { args } => {
            run_filtered("docker", &args, cli.verbose, filters::docker_filter)?;
        }
        Commands::Pip { args } => {
            run_filtered("pip", &args, cli.verbose, filters::pip_filter)?;
        }
        Commands::Sql { args } => {
            run_filtered("psql", &args, cli.verbose, filters::sql_filter)?;
        }
        Commands::Tree { args } => {
            run_filtered("tree", &args, cli.verbose, filters::ls_filter)?;
        }
        Commands::Find { args } => {
            run_filtered("find", &args, cli.verbose, filters::ls_filter)?;
        }
        Commands::Err { args } => {
            run_filtered("err", &args, cli.verbose, filters::error_filter)?;
        }
        Commands::Proxy { args } => {
            run_proxy(&args, cli.verbose)?;
        }
    }

    Ok(())
}

/// Execute a command, apply a filter function, track metrics, and print result.
fn run_filtered(
    cmd_name: &str,
    args: &[String],
    verbose: u8,
    filter_fn: fn(&str) -> String,
) -> Result<()> {
    let command = args.join(" ");
    let timer = tracking::TimedExecution::start();

    if verbose > 0 {
        eprintln!("[otk] Running: {}", command);
    }

    let output = std::process::Command::new("sh")
        .args(["-c", &command])
        .output()
        .map_err(|e| anyhow::anyhow!("Failed to execute '{}': {}", command, e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    let raw = if stderr.is_empty() {
        stdout.to_string()
    } else {
        format!("{}\n{}", stdout, stderr)
    };

    let exit_code = output.status.code().unwrap_or(1);
    let filtered = filter_fn(&raw);

    // Graceful fallback
    let final_output = if filtered.trim().is_empty() {
        if exit_code == 0 {
            "ok".to_string()
        } else {
            let lines: Vec<&str> = raw.lines().collect();
            let tail: Vec<&str> = lines.iter().rev().take(15).copied().collect();
            format!(
                "Command failed (exit code {}):\n{}",
                exit_code,
                tail.into_iter().rev().collect::<Vec<&str>>().join("\n")
            )
        }
    } else {
        filtered
    };

    // Tee: save full output for recovery
    if let Some(hint) = tee::tee_and_hint(&raw, cmd_name, exit_code) {
        println!("{}\n{}", final_output, hint);
    } else {
        println!("{}", final_output);
    }

    timer.track(&command, &format!("otk {}", cmd_name), &raw, &final_output);

    // Preserve exit code
    if exit_code != 0 {
        std::process::exit(exit_code);
    }

    Ok(())
}

/// Read a file with language-aware filtering.
fn run_read(path: &str, level: &str, verbose: u8) -> Result<()> {
    let timer = tracking::TimedExecution::start();

    if verbose > 0 {
        eprintln!("[otk] Reading: {} (level: {})", path, level);
    }

    let raw = std::fs::read_to_string(path)
        .map_err(|e| anyhow::anyhow!("Failed to read '{}': {}", path, e))?;

    let filtered = if path.ends_with(".xml") || path.ends_with(".html") {
        filters::xml_filter(&raw)
    } else if path.ends_with(".py") {
        match level {
            "aggressive" => filters::python_filter_aggressive(&raw),
            "none" => raw.clone(),
            _ => filters::python_filter(&raw),
        }
    } else {
        raw.clone()
    };

    // Always tee file reads (agent may need full source)
    if let Some(hint) = tee::tee_always(&raw, &format!("read_{}", path.rsplit('/').next().unwrap_or("file"))) {
        println!("{}\n{}", filtered, hint);
    } else {
        println!("{}", filtered);
    }

    timer.track(
        &format!("cat {}", path),
        &format!("otk read {}", path),
        &raw,
        &filtered,
    );

    Ok(())
}

/// Git commands with subcommand-aware filtering.
fn run_git(args: &[String], verbose: u8) -> Result<()> {
    if args.is_empty() {
        anyhow::bail!("No git subcommand provided");
    }

    let subcmd = &args[0];
    let full_args = std::iter::once("git".to_string())
        .chain(args.iter().cloned())
        .collect::<Vec<_>>();
    let command = full_args.join(" ");

    let filter_fn: fn(&str) -> String = match subcmd.as_str() {
        "status" => filters::git_status_filter,
        "diff" => filters::git_diff_filter,
        "log" => filters::git_log_filter,
        "add" | "commit" | "push" | "pull" | "fetch" | "checkout" | "stash" | "merge" | "rebase" => {
            filters::ok_filter
        }
        _ => filters::passthrough,
    };

    let timer = tracking::TimedExecution::start();

    if verbose > 0 {
        eprintln!("[otk] Running: {}", command);
    }

    let output = std::process::Command::new("sh")
        .args(["-c", &command])
        .output()
        .map_err(|e| anyhow::anyhow!("Failed to execute '{}': {}", command, e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    let raw = if stderr.is_empty() {
        stdout.to_string()
    } else {
        format!("{}\n{}", stdout, stderr)
    };

    let exit_code = output.status.code().unwrap_or(1);
    let filtered = filter_fn(&raw);

    let final_output = if filtered.trim().is_empty() && exit_code == 0 {
        "ok".to_string()
    } else if filtered.trim().is_empty() {
        let lines: Vec<&str> = raw.lines().collect();
        let n = lines.len().min(15);
        lines[lines.len() - n..].join("\n")
    } else {
        filtered
    };

    if let Some(hint) = tee::tee_and_hint(&raw, &format!("git_{}", subcmd), exit_code) {
        println!("{}\n{}", final_output, hint);
    } else {
        println!("{}", final_output);
    }

    timer.track(&command, &format!("otk git {}", subcmd), &raw, &final_output);

    if exit_code != 0 {
        std::process::exit(exit_code);
    }

    Ok(())
}

/// Proxy: run command without filtering, track for metrics only.
fn run_proxy(args: &[String], verbose: u8) -> Result<()> {
    let command = args.join(" ");
    let timer = tracking::TimedExecution::start();

    if verbose > 0 {
        eprintln!("[otk] Proxy: {}", command);
    }

    let output = std::process::Command::new("sh")
        .args(["-c", &command])
        .output()
        .map_err(|e| anyhow::anyhow!("Failed to execute '{}': {}", command, e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    print!("{}", stdout);
    if !stderr.is_empty() {
        eprint!("{}", stderr);
    }

    // Track with 0% savings (passthrough)
    timer.track_passthrough(&command, &format!("otk proxy {}", command));

    let exit_code = output.status.code().unwrap_or(1);
    if exit_code != 0 {
        std::process::exit(exit_code);
    }

    Ok(())
}
