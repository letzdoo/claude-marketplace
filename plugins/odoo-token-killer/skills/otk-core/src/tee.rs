// OTK Tee - Full output recovery system.
// Modeled after RTK's tee.rs (rtk-ai/rtk).
//
// Saves raw unfiltered output to disk so Claude can access it
// when the filtered version isn't enough.
//
// Filtered output includes a hint:
//   [full output: ~/.local/share/otk/tee/1234567890_invoke_test.log]

use std::path::{Path, PathBuf};

const MIN_TEE_SIZE: usize = 500;
const DEFAULT_MAX_FILES: usize = 200;
const DEFAULT_MAX_FILE_SIZE: usize = 1_048_576; // 1MB

fn sanitize_slug(slug: &str) -> String {
    let sanitized: String = slug
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '_' || c == '-' {
                c
            } else {
                '_'
            }
        })
        .collect();
    if sanitized.len() > 40 {
        sanitized[..40].to_string()
    } else {
        sanitized
    }
}

fn get_tee_dir() -> Option<PathBuf> {
    if let Ok(dir) = std::env::var("OTK_TEE_DIR") {
        return Some(PathBuf::from(dir));
    }
    dirs::data_local_dir().map(|d| d.join("otk").join("tee"))
}

fn get_mode() -> String {
    std::env::var("OTK_TEE_MODE")
        .unwrap_or_else(|_| "failures".to_string())
        .to_lowercase()
}

fn get_max_files() -> usize {
    std::env::var("OTK_TEE_MAX_FILES")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(DEFAULT_MAX_FILES)
}

fn get_max_size() -> usize {
    std::env::var("OTK_TEE_MAX_SIZE")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(DEFAULT_MAX_FILE_SIZE)
}

fn cleanup_old_files(dir: &Path, max_files: usize) {
    let mut entries: Vec<_> = std::fs::read_dir(dir)
        .ok()
        .into_iter()
        .flatten()
        .filter_map(|e| e.ok())
        .filter(|e| {
            e.path()
                .extension()
                .is_some_and(|ext| ext == "log")
        })
        .collect();

    if entries.len() <= max_files {
        return;
    }

    entries.sort_by_key(|e| e.file_name());
    let to_remove = entries.len() - max_files;
    for entry in entries.iter().take(to_remove) {
        let _ = std::fs::remove_file(entry.path());
    }
}

fn write_tee_file(
    raw: &str,
    command_slug: &str,
    tee_dir: &Path,
    max_file_size: usize,
    max_files: usize,
) -> Option<PathBuf> {
    std::fs::create_dir_all(tee_dir).ok()?;

    let slug = sanitize_slug(command_slug);
    let epoch = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .ok()?
        .as_secs();
    let filename = format!("{}_{}.log", epoch, slug);
    let filepath = tee_dir.join(filename);

    let content = if raw.len() > max_file_size {
        format!(
            "{}\n\n--- truncated at {} bytes ---",
            &raw[..max_file_size],
            max_file_size
        )
    } else {
        raw.to_string()
    };

    std::fs::write(&filepath, content).ok()?;
    cleanup_old_files(tee_dir, max_files);

    Some(filepath)
}

fn format_hint(path: &Path) -> String {
    let display = if let Some(home) = dirs::home_dir() {
        if let Ok(relative) = path.strip_prefix(&home) {
            format!("~/{}", relative.display())
        } else {
            path.display().to_string()
        }
    } else {
        path.display().to_string()
    };

    format!("[full output: {}]", display)
}

/// Save raw output to tee file if conditions are met.
/// Returns file path on success, None if skipped.
pub fn tee_raw(raw: &str, command_slug: &str, exit_code: i32) -> Option<PathBuf> {
    if std::env::var("OTK_TEE").ok().as_deref() == Some("0") {
        return None;
    }

    let mode = get_mode();

    match mode.as_str() {
        "never" => return None,
        "failures" => {
            if exit_code == 0 {
                return None;
            }
        }
        "always" => {}
        _ => {
            if exit_code == 0 {
                return None;
            }
        }
    }

    if raw.len() < MIN_TEE_SIZE {
        return None;
    }

    let tee_dir = get_tee_dir()?;

    write_tee_file(raw, command_slug, &tee_dir, get_max_size(), get_max_files())
}

/// Tee + format hint in one call.
pub fn tee_and_hint(raw: &str, command_slug: &str, exit_code: i32) -> Option<String> {
    let path = tee_raw(raw, command_slug, exit_code)?;
    Some(format_hint(&path))
}

/// Force-tee regardless of mode/exit code. For file reads where
/// the agent may need the full unfiltered source code.
pub fn tee_always(raw: &str, command_slug: &str) -> Option<String> {
    if std::env::var("OTK_TEE").ok().as_deref() == Some("0") {
        return None;
    }
    if raw.len() < MIN_TEE_SIZE {
        return None;
    }

    let tee_dir = get_tee_dir()?;
    let path = write_tee_file(raw, command_slug, &tee_dir, get_max_size(), get_max_files())?;
    Some(format_hint(&path))
}
