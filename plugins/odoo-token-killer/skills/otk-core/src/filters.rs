// OTK Output Filters - Specialized compression strategies for Odoo development.
// Inspired by RTK's filtering strategies (rtk-ai/rtk).
//
// 12 filters, each targeting a specific output type:
//   1. test_filter       - Odoo/pytest → failures only (90-95%)
//   2. log_filter        - Docker/Odoo logs → errors + warnings (85-95%)
//   3. python_filter     - .py files → signatures + fields (40-70%)
//   4. xml_filter        - .xml views → structure only (60-80%)
//   5. git_status_filter - compact stats (80%)
//   6. git_diff_filter   - stats + key hunks (70-80%)
//   7. git_log_filter    - one-line per commit (80%)
//   8. grep_filter       - grouped by file (70-85%)
//   9. ls_filter         - compact tree (50-70%)
//  10. docker_filter     - truncated IDs (60-80%)
//  11. pip_filter        - package summaries (80-90%)
//  12. sql_filter        - truncated rows/columns (60-80%)

use lazy_static::lazy_static;
use regex::Regex;
use std::collections::HashMap;

lazy_static! {
    static ref RE_ANSI: Regex = Regex::new(r"\x1b\[[0-9;]*m").unwrap();
    static ref RE_ODOO_LOG_PREFIX: Regex = Regex::new(
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \d+ (INFO|DEBUG|WARNING|ERROR|CRITICAL) "
    ).unwrap();
    static ref RE_PYTEST_PASS: Regex = Regex::new(r"(?i)^(PASSED|.*\.\.\. PASSED|.*::.*PASSED)").unwrap();
    static ref RE_PYTEST_FAIL: Regex = Regex::new(r"(?i)(FAILED|ERROR|ERRORS|assert|AssertionError|Traceback)").unwrap();
    static ref RE_PYTEST_SUMMARY: Regex = Regex::new(r"(?i)^=+ .*(passed|failed|error|warning).* =+$").unwrap();
    static ref RE_TEST_SEPARATOR: Regex = Regex::new(r"^[-=]{40,}$").unwrap();
    static ref RE_PYTHON_FUNC: Regex = Regex::new(r"^(\s*)(def |class |async def )").unwrap();
    static ref RE_PYTHON_DECORATOR: Regex = Regex::new(r"^(\s*)@").unwrap();
    static ref RE_PYTHON_COMMENT: Regex = Regex::new(r"^\s*#").unwrap();
    static ref RE_XML_COMMENT: Regex = Regex::new(r"^\s*<!--.*-->$").unwrap();
    static ref RE_GIT_DIFF_FILE: Regex = Regex::new(r"^diff --git a/(.*) b/(.*)").unwrap();
    static ref RE_GIT_DIFF_HUNK: Regex = Regex::new(r"^@@ .* @@(.*)").unwrap();
    static ref RE_ODOO_MODULE_LOAD: Regex = Regex::new(r"^odoo\.(modules|addons)\.").unwrap();
    static ref RE_WERKZEUG: Regex = Regex::new(r"^\d+\.\d+\.\d+\.\d+ - - \[").unwrap();
    static ref RE_DOCKER_PROGRESS: Regex = Regex::new(r"^(Pulling|Extracting|Downloading|Waiting|Verifying)").unwrap();
    static ref RE_SQL_BORDER: Regex = Regex::new(r"^[-+]+$").unwrap();
    static ref RE_BLANK_LINES: Regex = Regex::new(r"\n{3,}").unwrap();
    static ref RE_LONG_CONTENT: Regex = Regex::new(r">((?:(?!<).){80,})<").unwrap();
}

fn strip_ansi(text: &str) -> String {
    RE_ANSI.replace_all(text, "").to_string()
}

fn normalize_blanks(text: &str) -> String {
    RE_BLANK_LINES.replace_all(text, "\n\n").to_string()
}

// =============================================================================
// 1. TEST FILTER (invoke test / pytest / odoo-bin --test-tags)
// Target: 90-95% reduction
// =============================================================================

pub fn test_filter(output: &str) -> String {
    let lines = strip_ansi(output);
    let mut result: Vec<&str> = Vec::new();
    let mut in_failure = false;
    let mut in_traceback = false;
    let mut passed: u32 = 0;
    let mut failed: u32 = 0;

    for line in lines.lines() {
        let trimmed = line.trim();

        // Skip Odoo noise
        if RE_ODOO_MODULE_LOAD.is_match(trimmed) || RE_WERKZEUG.is_match(trimmed) {
            continue;
        }

        // Count passes silently
        if RE_PYTEST_PASS.is_match(trimmed) {
            passed += 1;
            in_failure = false;
            in_traceback = false;
            continue;
        }

        // Keep summary lines
        if RE_PYTEST_SUMMARY.is_match(trimmed) {
            result.push(line);
            continue;
        }

        // Detect failures
        if RE_PYTEST_FAIL.is_match(trimmed) || trimmed.contains("FAIL") {
            in_failure = true;
            failed += 1;
        }

        if trimmed.contains("Traceback (most recent call last)") {
            in_traceback = true;
        }

        if in_failure || in_traceback {
            result.push(line);
            if in_traceback
                && (trimmed.starts_with("FAILED")
                    || trimmed.starts_with("ERROR")
                    || RE_TEST_SEPARATOR.is_match(trimmed))
            {
                in_traceback = false;
            }
        }
    }

    let header = format!("Tests: {} passed, {} failed", passed, failed);
    if failed == 0 {
        if result.is_empty() {
            return format!("{}\nAll tests passed.", header);
        }
        // Only summary lines, no actual failures
        return format!("{}\nAll tests passed.\n{}", header, result.join("\n"));
    }
    format!("{}\n{}", header, result.join("\n"))
}

// =============================================================================
// 2. LOG FILTER (Docker Compose / Odoo server logs)
// Target: 85-95% reduction
// =============================================================================

pub fn log_filter(output: &str) -> String {
    let lines = strip_ansi(output);
    let mut result: Vec<String> = Vec::new();
    let mut context_buffer: Vec<&str> = Vec::new();
    let mut error_count: u32 = 0;
    let mut warning_count: u32 = 0;
    let total_lines = lines.lines().count();

    for line in lines.lines() {
        // Skip werkzeug access logs and docker progress
        if RE_WERKZEUG.is_match(line) || RE_DOCKER_PROGRESS.is_match(line.trim()) {
            continue;
        }

        if let Some(caps) = RE_ODOO_LOG_PREFIX.captures(line) {
            let level = caps.get(1).map(|m| m.as_str()).unwrap_or("");
            match level {
                "ERROR" | "CRITICAL" => {
                    error_count += 1;
                    // Include 2 lines of context
                    let start = context_buffer.len().saturating_sub(2);
                    for ctx in &context_buffer[start..] {
                        result.push(format!("  | {}", ctx));
                    }
                    result.push(line.to_string());
                    context_buffer.clear();
                }
                "WARNING" => {
                    warning_count += 1;
                    result.push(line.to_string());
                }
                _ => {
                    context_buffer.push(line);
                    if context_buffer.len() > 3 {
                        context_buffer.remove(0);
                    }
                }
            }
            continue;
        }

        // Non-Odoo lines: keep if they look like errors
        let lower = line.to_lowercase();
        if lower.contains("error")
            || lower.contains("traceback")
            || lower.contains("exception")
            || lower.contains("critical")
        {
            error_count += 1;
            result.push(line.to_string());
        } else {
            context_buffer.push(line);
            if context_buffer.len() > 3 {
                context_buffer.remove(0);
            }
        }
    }

    let header = format!(
        "Logs: {} lines filtered -> {} errors, {} warnings",
        total_lines, error_count, warning_count
    );
    if result.is_empty() {
        return format!("{}\nNo errors or warnings found.", header);
    }
    format!("{}\n{}", header, result.join("\n"))
}

// =============================================================================
// 3. PYTHON FILTER (.py source files - Odoo models)
// Target: 40-70% reduction
// =============================================================================

pub fn python_filter(output: &str) -> String {
    let mut result: Vec<&str> = Vec::new();
    let mut in_docstring = false;

    for line in output.lines() {
        let trimmed = line.trim();

        // Keep empty lines (normalized later)
        if trimmed.is_empty() {
            result.push("");
            continue;
        }

        // Skip standalone comments (keep shebangs)
        if RE_PYTHON_COMMENT.is_match(line) && !trimmed.starts_with("#!") {
            continue;
        }

        // Track docstrings
        if trimmed.contains("\"\"\"") || trimmed.contains("'''") {
            let delim = if trimmed.contains("\"\"\"") { "\"\"\"" } else { "'''" };
            let count = trimmed.matches(delim).count();
            if count == 1 {
                in_docstring = !in_docstring;
            }
            result.push(line);
            continue;
        }

        if in_docstring {
            result.push(line);
            continue;
        }

        // Always keep: decorators, class/def, imports
        if RE_PYTHON_DECORATOR.is_match(line)
            || RE_PYTHON_FUNC.is_match(line)
            || trimmed.starts_with("import ")
            || trimmed.starts_with("from ")
        {
            result.push(line);
            continue;
        }

        // Keep Odoo field definitions
        if trimmed.contains("fields.") && trimmed.contains('=') {
            result.push(line);
            continue;
        }

        // Keep _name, _inherit, _description, _order, _sql_constraints, etc.
        if trimmed.starts_with('_') && trimmed.contains('=') {
            result.push(line);
            continue;
        }

        // Keep everything else in minimal mode
        result.push(line);
    }

    normalize_blanks(&result.join("\n"))
}

pub fn python_filter_aggressive(output: &str) -> String {
    let mut result: Vec<String> = Vec::new();
    let mut in_docstring = false;
    let mut in_body = false;
    let mut body_indent: usize = 0;

    for line in output.lines() {
        let trimmed = line.trim();
        let indent = line.len() - line.trim_start().len();

        if trimmed.is_empty() {
            continue;
        }

        // Skip comments
        if RE_PYTHON_COMMENT.is_match(line) && !trimmed.starts_with("#!") {
            continue;
        }

        // Track docstrings
        if trimmed.contains("\"\"\"") || trimmed.contains("'''") {
            let delim = if trimmed.contains("\"\"\"") { "\"\"\"" } else { "'''" };
            let count = trimmed.matches(delim).count();
            if count == 1 {
                in_docstring = !in_docstring;
            }
            result.push(line.to_string());
            continue;
        }

        if in_docstring {
            result.push(line.to_string());
            continue;
        }

        // Keep decorators
        if RE_PYTHON_DECORATOR.is_match(line) {
            result.push(line.to_string());
            continue;
        }

        // Keep class/def signatures, enter body-skip mode
        if RE_PYTHON_FUNC.is_match(line) {
            result.push(line.to_string());
            in_body = true;
            body_indent = indent + 4;
            continue;
        }

        // Skip function bodies in aggressive mode
        if in_body {
            if indent >= body_indent {
                continue; // Skip body line
            }
            in_body = false;
        }

        // Keep Odoo-specific attributes and fields
        if (trimmed.contains("fields.") && trimmed.contains('='))
            || (trimmed.starts_with('_') && trimmed.contains('='))
            || trimmed.starts_with("import ")
            || trimmed.starts_with("from ")
        {
            result.push(line.to_string());
            continue;
        }

        result.push(line.to_string());
    }

    normalize_blanks(&result.join("\n"))
}

// =============================================================================
// 4. XML FILTER (Odoo views, data files)
// Target: 60-80% reduction
// =============================================================================

pub fn xml_filter(output: &str) -> String {
    let mut result: Vec<String> = Vec::new();

    for line in output.lines() {
        let trimmed = line.trim();

        // Skip XML comments
        if RE_XML_COMMENT.is_match(trimmed) || trimmed.starts_with("<!--") || trimmed.ends_with("-->") {
            continue;
        }

        if trimmed.is_empty() {
            continue;
        }

        // Truncate long inline content between tags
        if trimmed.contains('<') {
            let truncated = RE_LONG_CONTENT.replace_all(trimmed, |caps: &regex::Captures| {
                format!(">[...{} chars]<", caps[1].len())
            });
            if truncated != trimmed {
                let indent = &line[..line.len() - line.trim_start().len()];
                result.push(format!("{}{}", indent, truncated));
            } else {
                result.push(line.to_string());
            }
        } else if trimmed.len() > 100 {
            result.push(format!("{}... [{} chars]", &line[..100.min(line.len())], trimmed.len()));
        } else {
            result.push(line.to_string());
        }
    }

    result.join("\n")
}

// =============================================================================
// 5-7. GIT FILTERS
// =============================================================================

pub fn git_status_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let mut modified: Vec<String> = Vec::new();
    let mut added: Vec<String> = Vec::new();
    let mut deleted: Vec<String> = Vec::new();
    let mut untracked: Vec<String> = Vec::new();

    for line in clean.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("M ") || trimmed.contains("modified:") {
            if let Some(f) = trimmed.split_whitespace().last() {
                modified.push(f.to_string());
            }
        } else if trimmed.starts_with("A ") || trimmed.contains("new file:") {
            if let Some(f) = trimmed.split_whitespace().last() {
                added.push(f.to_string());
            }
        } else if trimmed.starts_with("D ") || trimmed.contains("deleted:") {
            if let Some(f) = trimmed.split_whitespace().last() {
                deleted.push(f.to_string());
            }
        } else if trimmed.starts_with("??") || trimmed.starts_with("Untracked") {
            if let Some(f) = trimmed.split_whitespace().last() {
                untracked.push(f.to_string());
            }
        }
    }

    let mut parts: Vec<String> = Vec::new();
    if !modified.is_empty() {
        parts.push(format!("{} modified", modified.len()));
    }
    if !added.is_empty() {
        parts.push(format!("{} added", added.len()));
    }
    if !deleted.is_empty() {
        parts.push(format!("{} deleted", deleted.len()));
    }
    if !untracked.is_empty() {
        parts.push(format!("{} untracked", untracked.len()));
    }

    if parts.is_empty() {
        return "Clean working tree.".to_string();
    }

    let summary = parts.join(", ");
    let all_files: Vec<&str> = modified
        .iter()
        .chain(added.iter())
        .chain(deleted.iter())
        .chain(untracked.iter())
        .map(|s| s.as_str())
        .collect();

    let mut result = summary;
    for (i, f) in all_files.iter().enumerate() {
        if i >= 30 {
            result.push_str(&format!("\n  ... and {} more", all_files.len() - 30));
            break;
        }
        result.push_str(&format!("\n  {}", f));
    }

    result
}

pub fn git_diff_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let mut files: Vec<String> = Vec::new();
    let mut hunks: Vec<String> = Vec::new();
    let mut current_file: Option<String> = None;
    let mut additions: u32 = 0;
    let mut deletions: u32 = 0;

    for line in clean.lines() {
        if let Some(caps) = RE_GIT_DIFF_FILE.captures(line) {
            let f = caps.get(2).map(|m| m.as_str().to_string()).unwrap_or_default();
            current_file = Some(f.clone());
            files.push(f);
            continue;
        }

        if line.starts_with('+') && !line.starts_with("+++") {
            additions += 1;
        } else if line.starts_with('-') && !line.starts_with("---") {
            deletions += 1;
        }

        if let Some(caps) = RE_GIT_DIFF_HUNK.captures(line) {
            let context = caps.get(1).map(|m| m.as_str().trim()).unwrap_or("");
            if let Some(ref f) = current_file {
                hunks.push(format!("  {}: {}", f, context));
            }
        }
    }

    if files.is_empty() {
        return "No changes.".to_string();
    }

    let mut result = format!("{} files, +{}/-{} lines", files.len(), additions, deletions);
    for (i, f) in files.iter().enumerate() {
        if i >= 20 {
            result.push_str(&format!("\n  ... and {} more", files.len() - 20));
            break;
        }
        result.push_str(&format!("\n  {}", f));
    }
    if !hunks.is_empty() {
        result.push_str("\n\nKey changes:");
        for (i, h) in hunks.iter().enumerate() {
            if i >= 15 {
                result.push_str(&format!("\n  ... and {} more hunks", hunks.len() - 15));
                break;
            }
            result.push_str(&format!("\n{}", h));
        }
    }

    result
}

pub fn git_log_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let mut commits: Vec<String> = Vec::new();
    let mut current_hash: Option<String> = None;
    let mut current_msg: Option<String> = None;

    for line in clean.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("commit ") {
            if let (Some(hash), Some(msg)) = (&current_hash, &current_msg) {
                commits.push(format!("{} {}", &hash[..7.min(hash.len())], msg));
            }
            current_hash = trimmed.split_whitespace().nth(1).map(|s| s.to_string());
            current_msg = None;
        } else if !trimmed.is_empty()
            && !trimmed.starts_with("Author:")
            && !trimmed.starts_with("Date:")
            && !trimmed.starts_with("Merge:")
        {
            if current_msg.is_none() {
                current_msg = Some(trimmed.to_string());
            }
        }
    }

    if let (Some(hash), Some(msg)) = (&current_hash, &current_msg) {
        commits.push(format!("{} {}", &hash[..7.min(hash.len())], msg));
    }

    if commits.is_empty() {
        return output.to_string(); // Already compact or empty
    }

    commits.join("\n")
}

// =============================================================================
// 8. GREP FILTER
// Target: 70-85% reduction
// =============================================================================

pub fn grep_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let mut by_file: HashMap<String, Vec<String>> = HashMap::new();
    let total_matches = clean.lines().count();

    for line in clean.lines() {
        if let Some(pos) = line.find(':') {
            let filename = &line[..pos];
            let rest = &line[pos + 1..];
            let content = if rest.len() > 100 { &rest[..100] } else { rest };
            by_file
                .entry(filename.to_string())
                .or_default()
                .push(content.to_string());
        } else {
            by_file
                .entry("(no file)".to_string())
                .or_default()
                .push(if line.len() > 100 {
                    line[..100].to_string()
                } else {
                    line.to_string()
                });
        }
    }

    let mut result = format!("{} files, {} matches", by_file.len(), total_matches);

    let mut sorted: Vec<_> = by_file.iter().collect();
    sorted.sort_by(|a, b| b.1.len().cmp(&a.1.len()));

    for (fname, matches) in &sorted {
        result.push_str(&format!("\n\n{} ({} matches):", fname, matches.len()));
        // Deduplicate
        let mut seen = Vec::new();
        for m in matches.iter() {
            if !seen.contains(m) {
                seen.push(m.clone());
            }
        }
        for (i, m) in seen.iter().enumerate() {
            if i >= 5 {
                result.push_str(&format!("\n  ... +{} more", seen.len() - 5));
                break;
            }
            result.push_str(&format!("\n  {}", m));
        }
    }

    result
}

// =============================================================================
// 9. LS / TREE FILTER
// Target: 50-70% reduction
// =============================================================================

pub fn ls_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let lines: Vec<&str> = clean.lines().filter(|l| !l.trim().is_empty()).collect();

    if lines.len() <= 30 {
        return output.to_string(); // Small enough
    }

    let mut dirs: Vec<&str> = Vec::new();
    let mut ext_counts: HashMap<String, u32> = HashMap::new();
    let mut file_count: u32 = 0;

    for line in &lines {
        let trimmed = line.trim();
        if trimmed.ends_with('/') || trimmed.starts_with('d') {
            dirs.push(trimmed);
        } else {
            file_count += 1;
            let ext = if let Some(pos) = trimmed.rfind('.') {
                &trimmed[pos + 1..]
            } else {
                "(no ext)"
            };
            *ext_counts.entry(ext.to_string()).or_insert(0) += 1;
        }
    }

    let mut result = format!("{} directories, {} files", dirs.len(), file_count);

    if !dirs.is_empty() {
        result.push_str("\n\nDirectories:");
        for (i, d) in dirs.iter().enumerate() {
            if i >= 15 {
                result.push_str(&format!("\n  ... +{} more", dirs.len() - 15));
                break;
            }
            result.push_str(&format!("\n  {}", d));
        }
    }

    if !ext_counts.is_empty() {
        result.push_str("\n\nFiles by type:");
        let mut sorted: Vec<_> = ext_counts.iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(a.1));
        for (ext, count) in sorted.iter().take(10) {
            result.push_str(&format!("\n  .{}: {}", ext, count));
        }
    }

    result
}

// =============================================================================
// 10. DOCKER FILTER
// Target: 60-80% reduction
// =============================================================================

pub fn docker_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let mut result: Vec<String> = Vec::new();

    for line in clean.lines() {
        // Truncate long container/image IDs
        let truncated = regex::Regex::new(r"[a-f0-9]{12,64}")
            .unwrap()
            .replace_all(line, |caps: &regex::Captures| {
                let s = &caps[0];
                if s.len() > 12 {
                    s[..12].to_string()
                } else {
                    s.to_string()
                }
            })
            .to_string();

        if truncated.len() > 120 {
            result.push(format!("{}...", &truncated[..120]));
        } else {
            result.push(truncated);
        }
    }

    result.join("\n")
}

// =============================================================================
// 11. PIP FILTER
// Target: 80-90% reduction
// =============================================================================

pub fn pip_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let lines: Vec<&str> = clean.lines().collect();

    // pip install: show only final status
    for line in lines.iter().rev() {
        if line.contains("Successfully installed") {
            let pkgs: Vec<&str> = line
                .trim_start_matches("Successfully installed ")
                .split_whitespace()
                .collect();
            let shown: Vec<&str> = pkgs.iter().take(10).copied().collect();
            let mut result = format!("Installed {} packages: {}", pkgs.len(), shown.join(", "));
            if pkgs.len() > 10 {
                result.push_str(&format!(" +{} more", pkgs.len() - 10));
            }
            return result;
        }
    }

    // pip list: count packages
    let pkg_lines: Vec<&str> = lines
        .iter()
        .filter(|l| {
            !l.trim().is_empty() && !l.starts_with('-') && !l.contains("Package")
        })
        .copied()
        .collect();

    if pkg_lines.len() > 20 {
        let mut result = format!("{} packages installed.\nTop packages:", pkg_lines.len());
        for line in pkg_lines.iter().take(15) {
            result.push_str(&format!("\n  {}", line.trim()));
        }
        result.push_str(&format!("\n  ... +{} more", pkg_lines.len() - 15));
        return result;
    }

    output.to_string()
}

// =============================================================================
// 12. SQL FILTER
// Target: 60-80% reduction
// =============================================================================

pub fn sql_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let mut result: Vec<String> = Vec::new();
    let mut row_count: u32 = 0;
    let lines: Vec<&str> = clean.lines().collect();

    for line in &lines {
        if RE_SQL_BORDER.is_match(line.trim()) {
            result.push(line.to_string());
            continue;
        }
        if line.len() > 150 {
            result.push(format!("{}...", &line[..150]));
        } else {
            result.push(line.to_string());
        }
        row_count += 1;
        if row_count > 50 {
            let remaining = lines.len().saturating_sub(50);
            result.push(format!("... {} more rows (truncated)", remaining));
            break;
        }
    }

    result.join("\n")
}

// =============================================================================
// ERROR FILTER (generic error-only filtering)
// =============================================================================

pub fn error_filter(output: &str) -> String {
    let clean = strip_ansi(output);
    let mut result: Vec<&str> = Vec::new();

    for line in clean.lines() {
        let lower = line.to_lowercase();
        if lower.contains("error")
            || lower.contains("warning")
            || lower.contains("traceback")
            || lower.contains("exception")
            || lower.contains("failed")
            || lower.contains("fatal")
        {
            result.push(line);
        }
    }

    if result.is_empty() {
        "ok".to_string()
    } else {
        result.join("\n")
    }
}

// =============================================================================
// OK FILTER (for write commands: git add/commit/push)
// Target: 90%+ reduction
// =============================================================================

pub fn ok_filter(output: &str) -> String {
    let clean = strip_ansi(output).trim().to_string();
    if clean.is_empty() {
        return "ok".to_string();
    }

    for line in clean.lines() {
        let trimmed = line.trim();
        // git commit: extract hash
        if trimmed.starts_with('[') && trimmed.contains(']') {
            return format!("ok {}", trimmed);
        }
        // git push: extract branch info
        if trimmed.contains("->") {
            return format!("ok {}", trimmed);
        }
    }

    // Default: first meaningful line
    for line in clean.lines() {
        let trimmed = line.trim();
        if !trimmed.is_empty() {
            let display = if trimmed.len() > 80 {
                &trimmed[..80]
            } else {
                trimmed
            };
            return format!("ok {}", display);
        }
    }

    "ok".to_string()
}

// =============================================================================
// PASSTHROUGH
// =============================================================================

pub fn passthrough(output: &str) -> String {
    normalize_blanks(&strip_ansi(output))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_strip_ansi() {
        assert_eq!(strip_ansi("\x1b[32mgreen\x1b[0m"), "green");
    }

    #[test]
    fn test_ok_filter_empty() {
        assert_eq!(ok_filter(""), "ok");
    }

    #[test]
    fn test_ok_filter_commit() {
        let output = "[master abc1234] Fix bug\n 1 file changed";
        assert!(ok_filter(output).starts_with("ok [master abc1234]"));
    }

    #[test]
    fn test_git_log_compact() {
        let input = "commit abc1234567890\nAuthor: test\nDate: 2025\n\n    Fix bug\n\ncommit def4567890123\nAuthor: test\nDate: 2025\n\n    Add feature\n";
        let output = git_log_filter(input);
        assert!(output.contains("abc1234"));
        assert!(output.contains("Fix bug"));
        assert!(output.contains("def4567"));
        assert!(!output.contains("Author:"));
    }

    #[test]
    fn test_git_status_clean() {
        assert_eq!(
            git_status_filter("On branch master\nnothing to commit"),
            "Clean working tree."
        );
    }

    #[test]
    fn test_test_filter_all_pass() {
        let input = "test_foo ... PASSED\ntest_bar ... PASSED\n===== 2 passed =====";
        let output = test_filter(input);
        assert!(output.contains("2 passed, 0 failed"));
        assert!(output.contains("All tests passed."));
    }

    #[test]
    fn test_python_filter_keeps_fields() {
        let input = "# Comment\nclass SaleOrder(models.Model):\n    _name = 'sale.order'\n    partner_id = fields.Many2one('res.partner')\n";
        let output = python_filter(input);
        assert!(!output.contains("# Comment"));
        assert!(output.contains("class SaleOrder"));
        assert!(output.contains("_name = 'sale.order'"));
        assert!(output.contains("fields.Many2one"));
    }

    #[test]
    fn test_error_filter_no_errors() {
        assert_eq!(error_filter("all good\nnothing wrong"), "ok");
    }

    #[test]
    fn test_error_filter_with_errors() {
        let input = "line 1\nERROR: something broke\nline 3";
        let output = error_filter(input);
        assert!(output.contains("ERROR: something broke"));
        assert!(!output.contains("line 1"));
    }
}
