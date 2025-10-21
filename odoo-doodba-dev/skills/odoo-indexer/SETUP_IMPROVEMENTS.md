# Odoo Indexer Setup Improvements - Summary

## Overview

This document summarizes the improvements made to make the Odoo Indexer plugin more robust and user-friendly.

## Issues Addressed

1. **No automatic environment setup** - Users had to manually create venv and install dependencies
2. **uv dependency with no fallback** - Plugin required uv but had no graceful fallback
3. **No first-run detection** - No guidance for initial setup
4. **Poor error messages** - Unclear what to do when things went wrong

## New Components

### 1. Setup Script (`scripts/setup.sh`)

**Purpose:** Automated environment configuration

**Features:**
- Detects if `uv` is available
- Attempts to install `uv` via Homebrew if available
- Falls back to Python venv if `uv` unavailable
- Installs all dependencies automatically
- Provides clear feedback and next steps

**Usage:**
```bash
./scripts/setup.sh
```

### 2. Wrapper Script (`scripts/run.sh`)

**Purpose:** Smart command wrapper with automatic setup

**Features:**
- Runs setup automatically on first use
- Detects best Python environment (uv vs venv)
- Auto-configures ODOO_PATH intelligently
- Provides clear error messages if setup needed
- Creates `.setup_complete` marker

**Usage:**
```bash
./scripts/run.sh scripts/search.py "sale.order" --type model
```

### 3. Environment Check Library (`scripts/env_check.py`)

**Purpose:** Reusable environment validation

**Features:**
- `check_environment()` - Validates dependencies are installed
- `get_runner()` - Determines which runner to use (uv/venv)
- `ensure_environment()` - Convenience function that exits if not ready
- Can be imported by other scripts for validation

**Usage:**
```python
from env_check import ensure_environment
ensure_environment()  # Exits if environment not ready
```

### 4. Requirements File (`requirements.txt`)

**Purpose:** Fallback dependencies for non-uv installations

**Contents:**
- lxml >= 4.9.0
- aiosqlite >= 0.19.0
- uvloop >= 0.21.0 (optional, non-Windows only)

### 5. Health Check Script (`scripts/health_check.py`)

**Purpose:** Comprehensive setup diagnostics

**Checks:**
- Python version
- uv availability
- Virtual environment existence
- Dependency installation (aiosqlite, lxml)
- Database location and size
- ODOO_PATH configuration
- Odoo directory structure
- Setup completion marker

**Usage:**
```bash
./scripts/health_check.py
```

**Example Output:**
```
Odoo Indexer Health Check
==================================================
✓ Python: 3.12.3
✓ uv: Available at /usr/local/bin/uv
✓ Virtual env: Exists
✓ aiosqlite: 0.19.0
✓ lxml: 5.1.0
✓ Database: /home/coder/.odoo-indexer/odoo_indexer.sqlite3
  Size: 2.3 MB
✓ ODOO_PATH: /home/coder/project/odoo/custom/src
  Found: addons/
✓ Setup marker: Present

==================================================
✓ Environment is ready!
```

### 6. Updated Documentation (`SKILL.md`)

**Changes:**
- Added "First-Time Setup" section at the top
- Updated frontmatter description to mention auto-configuration
- Added wrapper script examples alongside uv commands
- Added "Health Check" operation
- Added "Troubleshooting" section
- Included uv installation instructions

## User Experience Improvements

### Before
```bash
# User had to figure out:
cd skills/odoo-indexer
uv sync  # Or manually create venv and install deps
export ODOO_PATH=/path/to/odoo
uv run scripts/update_index.py --full
```

### After
```bash
# User can simply run:
./scripts/run.sh scripts/update_index.py --full
# Setup happens automatically on first run!

# Or check setup status:
./scripts/health_check.py
```

## Graceful Degradation Path

The setup now follows a graceful degradation strategy:

1. **Best case:** `uv` available → Use `uv sync` for fast, reliable setup
2. **Fallback:** No `uv`, but Homebrew available → Install `uv` via brew
3. **Fallback:** No `uv` or brew → Use Python venv + pip install
4. **Error case:** No Python or venv → Clear error message with instructions

## Benefits

1. **Zero-config first run** - Setup happens automatically
2. **Better error messages** - Clear guidance on what to do
3. **Cross-platform** - Works on macOS (brew), Linux (apt/dnf), and manual venv
4. **Maintains uv preference** - Still uses uv when available for speed
5. **Health checking** - Easy to diagnose issues
6. **Professional UX** - Clear feedback and progress indicators

## File Structure

```
skills/odoo-indexer/
├── scripts/
│   ├── setup.sh                 # NEW: Setup script
│   ├── run.sh                   # NEW: Wrapper script
│   ├── health_check.py          # NEW: Health diagnostics
│   ├── lib/
│   │   ├── __init__.py         # NEW: Library init
│   │   └── env_check.py        # NEW: Environment validation
│   ├── search.py
│   ├── update_index.py
│   └── ... (other scripts)
├── requirements.txt             # NEW: Fallback dependencies
├── SKILL.md                     # UPDATED: Documentation
├── SETUP_IMPROVEMENTS.md        # NEW: This file
├── pyproject.toml
└── uv.lock
```

## Testing the Setup

### Test Auto-Setup
```bash
# Remove markers to simulate first run
rm -f .setup_complete .venv
./scripts/run.sh scripts/index_status.py
# Should automatically run setup
```

### Test Health Check
```bash
./scripts/health_check.py
# Should show comprehensive status
```

### Test Manual Setup
```bash
./scripts/setup.sh
# Should set up environment with clear feedback
```

## Migration Notes

- Existing users with working setups won't be affected
- The `.setup_complete` marker prevents unnecessary re-setup
- All existing `uv run` commands continue to work
- New wrapper script is optional but recommended

## Future Enhancements (Optional)

1. **Auto-update detection** - Check for outdated dependencies
2. **Setup progress bar** - Visual feedback during long operations
3. **Configuration wizard** - Interactive ODOO_PATH setup
4. **Pre-commit hooks** - Validate environment before indexing
5. **Docker support** - Container-based setup option
