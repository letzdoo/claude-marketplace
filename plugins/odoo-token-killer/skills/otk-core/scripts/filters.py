#!/usr/bin/env python3
"""
OTK Output Filters - Specialized compression strategies for Odoo development.

Inspired by RTK's 12 filtering strategies (rtk-ai/rtk).
Each filter targets a specific output type and reduces tokens 60-95%.

Filter taxonomy:
  1. test_filter      - Odoo/pytest test output → failures only (90-95%)
  2. log_filter       - Docker/Odoo logs → errors + warnings only (85-95%)
  3. python_filter    - Python files → signatures + docstrings (40-70%)
  4. xml_filter       - XML views → structure only (60-80%)
  5. git_status       - git status → compact stats (80%)
  6. git_diff         - git diff → stats + key changes (70-80%)
  7. git_log          - git log → one-line format (80%)
  8. grep_filter      - grep/rg output → grouped + deduplicated (70-85%)
  9. ls_filter        - ls/tree → compact tree with counts (50-70%)
  10. docker_filter   - docker ps/images → compact table (60-80%)
  11. pip_filter      - pip list/install → summary (80-90%)
  12. sql_filter      - psql output → compact + truncated (60-80%)
"""

import re
import sys
from collections import Counter, defaultdict

# -- Compiled patterns (equivalent to RTK's lazy_static!) --

RE_ANSI = re.compile(r"\x1b\[[0-9;]*m")
RE_ODOO_LOG_PREFIX = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \d+ (INFO|DEBUG|WARNING|ERROR|CRITICAL) "
)
RE_PYTEST_PASS = re.compile(r"^(PASSED|.*\.\.\. PASSED|.*::.*PASSED)", re.IGNORECASE)
RE_PYTEST_FAIL = re.compile(r"(FAILED|ERROR|ERRORS|assert|AssertionError|Traceback)", re.IGNORECASE)
RE_PYTEST_SUMMARY = re.compile(r"^=+ .*(passed|failed|error|warning).* =+$", re.IGNORECASE)
RE_TEST_SEPARATOR = re.compile(r"^[-=]{40,}$")
RE_PYTHON_FUNC = re.compile(r"^(\s*)(def |class |async def )")
RE_PYTHON_DECORATOR = re.compile(r"^(\s*)@")
RE_PYTHON_COMMENT = re.compile(r"^\s*#")
RE_XML_COMMENT = re.compile(r"^\s*<!--.*-->$")
RE_GIT_DIFF_FILE = re.compile(r"^diff --git a/(.*) b/(.*)")
RE_GIT_DIFF_HUNK = re.compile(r"^@@ .* @@(.*)")
RE_GIT_STAT = re.compile(r"(\d+) files? changed")
RE_BLANK_LINES = re.compile(r"\n{3,}")
RE_DOCKER_PROGRESS = re.compile(r"^(Pulling|Extracting|Downloading|Waiting|Verifying)")
RE_ODOO_MODULE_LOAD = re.compile(r"^odoo\.(modules|addons)\.")
RE_ODOO_WERKZEUG = re.compile(r'^\d+\.\d+\.\d+\.\d+ - - \[')
RE_SQL_BORDER = re.compile(r"^[-+]+$")


def strip_ansi(text: str) -> str:
    return RE_ANSI.sub("", text)


def normalize_blanks(text: str) -> str:
    return RE_BLANK_LINES.sub("\n\n", text)


# =============================================================================
# 1. TEST FILTER (Odoo tests via pytest / invoke test)
# Target: 90-95% reduction
# =============================================================================

def test_filter(output: str) -> str:
    """Extract only failures, errors, and summary from test output.

    Drops all PASSED tests, module loading logs, and XML-RPC noise.
    Keeps: FAILED tests with tracebacks, assertion messages, summary line.
    """
    lines = strip_ansi(output).splitlines()
    result = []
    in_failure = False
    in_traceback = False
    passed = 0
    failed = 0
    errors = 0

    for line in lines:
        stripped = line.strip()

        # Count results without outputting passes
        if RE_PYTEST_PASS.match(stripped):
            passed += 1
            in_failure = False
            in_traceback = False
            continue

        # Keep failure blocks
        if RE_PYTEST_FAIL.search(stripped) or "FAIL" in stripped.upper():
            in_failure = True
            failed += 1

        if "Traceback (most recent call last)" in stripped:
            in_traceback = True

        # Keep summary lines
        if RE_PYTEST_SUMMARY.match(stripped):
            result.append(line)
            continue

        if in_failure or in_traceback:
            result.append(line)
            # End traceback on next test or separator
            if in_traceback and (stripped.startswith("FAILED") or
                                 stripped.startswith("ERROR") or
                                 RE_TEST_SEPARATOR.match(stripped)):
                in_traceback = False

        # Skip Odoo module loading noise
        if RE_ODOO_MODULE_LOAD.match(stripped):
            continue
        if RE_ODOO_WERKZEUG.match(stripped):
            continue

    # Prepend compact summary
    header = f"Tests: {passed} passed, {failed} failed, {errors} errors"
    if not result:
        return f"{header}\nAll tests passed."

    return f"{header}\n" + "\n".join(result)


# =============================================================================
# 2. LOG FILTER (Docker Compose / Odoo server logs)
# Target: 85-95% reduction
# =============================================================================

def log_filter(output: str) -> str:
    """Keep only ERROR/WARNING/CRITICAL lines + context from Odoo logs.

    Drops: INFO, DEBUG, module loading, werkzeug access logs, SQL queries.
    Keeps: Errors with 2 lines of context, warnings, critical messages.
    """
    lines = strip_ansi(output).splitlines()
    result = []
    context_buffer = []
    error_count = 0
    warning_count = 0
    total_lines = len(lines)

    for line in lines:
        # Skip werkzeug access logs
        if RE_ODOO_WERKZEUG.match(line):
            continue
        # Skip docker progress
        if RE_DOCKER_PROGRESS.match(line.strip()):
            continue

        m = RE_ODOO_LOG_PREFIX.match(line)
        if m:
            level = m.group(1)
            if level in ("ERROR", "CRITICAL"):
                error_count += 1
                # Include 2 lines of context before the error
                for ctx in context_buffer[-2:]:
                    result.append(f"  | {ctx}")
                result.append(line)
                context_buffer = []
                continue
            elif level == "WARNING":
                warning_count += 1
                result.append(line)
                continue
            else:
                # Buffer INFO/DEBUG for context
                context_buffer.append(line)
                if len(context_buffer) > 3:
                    context_buffer.pop(0)
                continue

        # Non-Odoo lines: keep if they look like errors
        if any(kw in line.lower() for kw in ("error", "traceback", "exception", "critical")):
            error_count += 1
            result.append(line)
        else:
            context_buffer.append(line)
            if len(context_buffer) > 3:
                context_buffer.pop(0)

    header = f"Logs: {total_lines} lines filtered → {error_count} errors, {warning_count} warnings"
    if not result:
        return f"{header}\nNo errors or warnings found."

    return f"{header}\n" + "\n".join(result)


# =============================================================================
# 3. PYTHON FILTER (Odoo model files)
# Target: 40-70% reduction
# =============================================================================

def python_filter(output: str, aggressive: bool = False) -> str:
    """Filter Python source to signatures + docstrings.

    Minimal mode: strips comments, normalizes blanks (40% reduction).
    Aggressive mode: keeps only class/function signatures, decorators,
    field definitions, and docstrings (60-70% reduction).
    """
    lines = output.splitlines()
    result = []
    in_docstring = False
    in_body = False
    body_indent = 0
    docstring_delim = None

    for line in lines:
        stripped = line.strip()

        # Always keep empty lines (normalized later)
        if not stripped:
            if not aggressive:
                result.append("")
            continue

        # Skip standalone comments
        if RE_PYTHON_COMMENT.match(line) and not stripped.startswith("#!"):
            continue

        # Track docstrings
        if '"""' in stripped or "'''" in stripped:
            delim = '"""' if '"""' in stripped else "'''"
            count = stripped.count(delim)
            if count == 1:
                in_docstring = not in_docstring
            # Keep docstrings (they're useful context)
            result.append(line)
            continue

        if in_docstring:
            result.append(line)
            continue

        # Always keep decorators, class/def lines, imports
        if RE_PYTHON_DECORATOR.match(line):
            result.append(line)
            continue

        if RE_PYTHON_FUNC.match(line):
            result.append(line)
            in_body = True
            body_indent = len(line) - len(line.lstrip()) + 4
            continue

        # Keep field definitions (Odoo-specific: fields.Xxx)
        if "fields." in stripped and "=" in stripped:
            result.append(line)
            continue

        # Keep _name, _inherit, _description, _order, _sql_constraints
        if stripped.startswith("_") and "=" in stripped:
            result.append(line)
            continue

        # Keep import lines
        if stripped.startswith(("import ", "from ")):
            result.append(line)
            continue

        if aggressive and in_body:
            current_indent = len(line) - len(line.lstrip())
            if current_indent >= body_indent:
                continue  # Skip function body
            else:
                in_body = False
                result.append(line)
        else:
            result.append(line)

    return normalize_blanks("\n".join(result))


# =============================================================================
# 4. XML FILTER (Odoo views, data files)
# Target: 60-80% reduction
# =============================================================================

def xml_filter(output: str) -> str:
    """Extract XML structure: tags, attributes, field names. Strip values.

    Keeps: record ids, field names, view types, widget attrs.
    Drops: long string values, translation terms, inline content.
    """
    lines = output.splitlines()
    result = []
    depth = 0

    for line in lines:
        stripped = line.strip()

        # Skip XML comments
        if RE_XML_COMMENT.match(stripped):
            continue
        if stripped.startswith("<!--"):
            continue
        if stripped.endswith("-->"):
            continue

        # Skip empty lines
        if not stripped:
            continue

        # Keep structural tags, truncate long attribute values
        if "<" in stripped:
            # Truncate long string content between tags
            # e.g., <field name="arch" type="xml">..long xml..</field>
            truncated = re.sub(
                r">((?!<).{80,})<",
                lambda m: f">[...{len(m.group(1))} chars]<",
                stripped
            )
            result.append(line.replace(stripped, truncated) if truncated != stripped else line)
        else:
            # Non-XML content lines - truncate if long
            if len(stripped) > 100:
                result.append(f"{line[:100]}... [{len(stripped)} chars]")
            else:
                result.append(line)

    return "\n".join(result)


# =============================================================================
# 5-7. GIT FILTERS
# =============================================================================

def git_status_filter(output: str) -> str:
    """Compact git status → file counts by category (80% reduction)."""
    lines = strip_ansi(output).splitlines()
    modified = []
    added = []
    deleted = []
    untracked = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("M ") or stripped.startswith("modified:"):
            modified.append(stripped.split()[-1])
        elif stripped.startswith("A ") or stripped.startswith("new file:"):
            added.append(stripped.split()[-1])
        elif stripped.startswith("D ") or stripped.startswith("deleted:"):
            deleted.append(stripped.split()[-1])
        elif stripped.startswith("??") or stripped.startswith("Untracked"):
            untracked.append(stripped.split()[-1])

    parts = []
    if modified:
        parts.append(f"{len(modified)} modified")
    if added:
        parts.append(f"{len(added)} added")
    if deleted:
        parts.append(f"{len(deleted)} deleted")
    if untracked:
        parts.append(f"{len(untracked)} untracked")

    if not parts:
        return "Clean working tree."

    summary = ", ".join(parts)
    # List files compactly
    all_files = modified + added + deleted + untracked
    file_list = "\n".join(f"  {f}" for f in all_files[:30])
    if len(all_files) > 30:
        file_list += f"\n  ... and {len(all_files) - 30} more"

    return f"{summary}\n{file_list}"


def git_diff_filter(output: str) -> str:
    """Compact git diff → stats + key hunks (70-80% reduction)."""
    lines = strip_ansi(output).splitlines()
    files = []
    current_file = None
    hunks = []
    additions = 0
    deletions = 0

    for line in lines:
        m = RE_GIT_DIFF_FILE.match(line)
        if m:
            current_file = m.group(2)
            files.append(current_file)
            continue

        if line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1

        # Keep hunk headers
        m = RE_GIT_DIFF_HUNK.match(line)
        if m:
            hunks.append(f"  {current_file}: {m.group(1).strip()}" if current_file else line)

    header = f"{len(files)} files, +{additions}/-{deletions} lines"
    if not files:
        return "No changes."

    result = [header]
    for f in files[:20]:
        result.append(f"  {f}")
    if len(files) > 20:
        result.append(f"  ... and {len(files) - 20} more")
    if hunks:
        result.append("")
        result.append("Key changes:")
        result.extend(hunks[:15])
        if len(hunks) > 15:
            result.append(f"  ... and {len(hunks) - 15} more hunks")

    return "\n".join(result)


def git_log_filter(output: str) -> str:
    """Compact git log → one line per commit (80% reduction)."""
    lines = strip_ansi(output).splitlines()
    commits = []
    current_hash = None
    current_msg = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("commit "):
            if current_hash and current_msg:
                commits.append(f"{current_hash[:7]} {current_msg}")
            current_hash = stripped.split()[1]
            current_msg = None
        elif stripped and not stripped.startswith(("Author:", "Date:", "Merge:")):
            if current_msg is None:
                current_msg = stripped

    if current_hash and current_msg:
        commits.append(f"{current_hash[:7]} {current_msg}")

    if not commits:
        return output  # Fallback: already compact or empty

    return "\n".join(commits)


# =============================================================================
# 8. GREP FILTER
# Target: 70-85% reduction
# =============================================================================

def grep_filter(output: str) -> str:
    """Group grep results by file, deduplicate patterns (70-85% reduction)."""
    lines = strip_ansi(output).splitlines()
    by_file = defaultdict(list)

    for line in lines:
        if ":" in line:
            parts = line.split(":", 2)
            if len(parts) >= 3:
                filename = parts[0]
                by_file[filename].append(parts[2].strip()[:100])
            elif len(parts) >= 2:
                filename = parts[0]
                by_file[filename].append(parts[1].strip()[:100])
        else:
            by_file["(no file)"].append(line.strip()[:100])

    result = [f"{len(by_file)} files, {len(lines)} matches"]
    for fname, matches in sorted(by_file.items(), key=lambda x: -len(x[1])):
        unique = list(dict.fromkeys(matches))  # Deduplicate preserving order
        result.append(f"\n{fname} ({len(matches)} matches):")
        for m in unique[:5]:
            result.append(f"  {m}")
        if len(unique) > 5:
            result.append(f"  ... +{len(unique) - 5} more")

    return "\n".join(result)


# =============================================================================
# 9. LS/TREE FILTER
# Target: 50-70% reduction
# =============================================================================

def ls_filter(output: str) -> str:
    """Compact directory listing with file counts (50-70% reduction)."""
    lines = strip_ansi(output).splitlines()
    dirs = []
    files = []
    total = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        total += 1
        # Detect directories (common patterns)
        if stripped.endswith("/") or stripped.startswith("d"):
            dirs.append(stripped)
        else:
            files.append(stripped)

    if total <= 30:
        return output  # Small enough, keep as-is

    # Group files by extension
    ext_counts = Counter()
    for f in files:
        ext = f.rsplit(".", 1)[-1] if "." in f else "(no ext)"
        ext_counts[ext] += 1

    result = [f"{len(dirs)} directories, {len(files)} files"]
    if dirs:
        result.append("\nDirectories:")
        for d in dirs[:15]:
            result.append(f"  {d}")
        if len(dirs) > 15:
            result.append(f"  ... +{len(dirs) - 15} more")
    if ext_counts:
        result.append("\nFiles by type:")
        for ext, cnt in ext_counts.most_common(10):
            result.append(f"  .{ext}: {cnt}")

    return "\n".join(result)


# =============================================================================
# 10. DOCKER FILTER
# Target: 60-80% reduction
# =============================================================================

def docker_filter(output: str) -> str:
    """Compact docker output: strip IDs, truncate columns (60-80% reduction)."""
    lines = strip_ansi(output).splitlines()
    if not lines:
        return output

    # For docker ps: keep name, status, ports only
    result = []
    for line in lines:
        # Truncate long image digests and container IDs
        line = re.sub(r"[a-f0-9]{12,64}", lambda m: m.group(0)[:12], line)
        # Truncate long lines
        if len(line) > 120:
            result.append(line[:120] + "...")
        else:
            result.append(line)

    return "\n".join(result)


# =============================================================================
# 11. PIP FILTER
# Target: 80-90% reduction
# =============================================================================

def pip_filter(output: str) -> str:
    """Compact pip output: summary of installed/listed packages."""
    lines = strip_ansi(output).splitlines()

    # pip install: keep only final status
    if any("Successfully installed" in l for l in lines):
        for line in reversed(lines):
            if "Successfully installed" in line:
                pkgs = line.replace("Successfully installed ", "").split()
                return f"Installed {len(pkgs)} packages: {', '.join(pkgs[:10])}" + (
                    f" +{len(pkgs) - 10} more" if len(pkgs) > 10 else "")
        return "Installation complete."

    # pip list: count packages
    pkg_lines = [l for l in lines if l.strip() and not l.startswith("-") and "Package" not in l]
    if len(pkg_lines) > 20:
        return f"{len(pkg_lines)} packages installed.\nTop packages:\n" + \
               "\n".join(f"  {l.strip()}" for l in pkg_lines[:15]) + \
               f"\n  ... +{len(pkg_lines) - 15} more"

    return output  # Small enough


# =============================================================================
# 12. SQL FILTER
# Target: 60-80% reduction
# =============================================================================

def sql_filter(output: str) -> str:
    """Compact SQL/psql output: truncate wide columns, limit rows."""
    lines = strip_ansi(output).splitlines()
    result = []
    row_count = 0

    for line in lines:
        if RE_SQL_BORDER.match(line.strip()):
            result.append(line)
            continue
        # Truncate wide columns
        if len(line) > 150:
            result.append(line[:150] + "...")
        else:
            result.append(line)
        row_count += 1
        if row_count > 50:
            remaining = len(lines) - 50
            result.append(f"... {remaining} more rows (truncated)")
            break

    return "\n".join(result)


# =============================================================================
# PASSTHROUGH (for commands we don't filter)
# =============================================================================

def passthrough(output: str) -> str:
    """Pass output through with minimal cleanup: strip ANSI, normalize blanks."""
    return normalize_blanks(strip_ansi(output))


# =============================================================================
# SUCCESS / OK FILTER (for write commands: git add, git commit, git push)
# Target: 90%+ reduction
# =============================================================================

def ok_filter(output: str) -> str:
    """For commands where only success/failure matters."""
    clean = strip_ansi(output).strip()
    if not clean:
        return "ok"

    # Extract key info from common success patterns
    lines = clean.splitlines()

    # git commit: extract hash
    for line in lines:
        if line.strip().startswith("[") and "]" in line:
            return f"ok {line.strip()}"

    # git push: extract branch info
    for line in lines:
        if "->" in line:
            return f"ok {line.strip()}"

    # Default: first meaningful line
    for line in lines:
        if line.strip():
            return f"ok {line.strip()[:80]}"

    return "ok"


# =============================================================================
# COMMAND → FILTER ROUTING
# =============================================================================

FILTER_MAP = {
    # Odoo tests
    "invoke test": test_filter,
    "pytest": test_filter,
    "python -m pytest": test_filter,
    "odoo-bin --test-tags": test_filter,
    "odoo-bin -t": test_filter,
    # Logs
    "docker compose logs": log_filter,
    "docker-compose logs": log_filter,
    "docker logs": log_filter,
    # Python source
    "cat": python_filter,
    "read": python_filter,
    # XML views
    "xml": xml_filter,
    # Git
    "git status": git_status_filter,
    "git diff": git_diff_filter,
    "git log": git_log_filter,
    "git add": ok_filter,
    "git commit": ok_filter,
    "git push": ok_filter,
    "git pull": ok_filter,
    "git fetch": ok_filter,
    "git checkout": ok_filter,
    "git stash": ok_filter,
    # Search
    "grep": grep_filter,
    "rg": grep_filter,
    # Files
    "ls": ls_filter,
    "tree": ls_filter,
    "find": ls_filter,
    # Docker
    "docker ps": docker_filter,
    "docker images": docker_filter,
    # Python packages
    "pip list": pip_filter,
    "pip install": pip_filter,
    "pip freeze": pip_filter,
    # SQL
    "psql": sql_filter,
}


def route_filter(command: str, output: str) -> tuple[str, str]:
    """Route a command to the appropriate filter. Returns (filter_name, filtered_output)."""
    cmd_lower = command.lower().strip()

    # Check for exact prefix matches (longest first for specificity)
    for pattern in sorted(FILTER_MAP.keys(), key=len, reverse=True):
        if cmd_lower.startswith(pattern) or pattern in cmd_lower:
            filter_fn = FILTER_MAP[pattern]
            return (filter_fn.__name__, filter_fn(output))

    # File extension-based routing for cat/read commands
    if any(cmd_lower.endswith(ext) for ext in (".xml", ".html")):
        return ("xml_filter", xml_filter(output))
    if any(cmd_lower.endswith(ext) for ext in (".py",)):
        return ("python_filter", python_filter(output))

    return ("passthrough", passthrough(output))
