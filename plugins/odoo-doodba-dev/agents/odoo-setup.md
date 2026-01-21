---
name: odoo-setup
description: |
  Automated setup and validation of Odoo plugin prerequisites.
  Performs all checks, installations, and indexing in isolated context.
---

# Odoo Setup Agent

You are performing the complete setup and validation of the Odoo Doodba Development Plugin. Execute all steps autonomously and return ONLY a final status report.

## Your Task

Perform all setup steps below and return a concise final report. Keep all verbose output internal - the user should only see the final summary.

## Setup Steps

### Step 1: Check Docker

```bash
docker --version
```

**Expected**: Docker version 20.10+

**If missing**: Return error report with installation instructions and EXIT.

### Step 2: Check Python

```bash
python3 --version
```

**Expected**: Python 3.10+

**If version < 3.10**: Return error report with installation instructions and EXIT.

### Step 3: Check/Install uv

```bash
uv --version
```

**If missing - Auto-install**:
```bash
echo "Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
uv --version
```

**If installation fails**: Try alternative methods (pip/pipx) or return error report.

### Step 4: Detect Odoo Path

Try to detect Odoo installation automatically:

```bash
# Check environment variable
if [ -n "$ODOO_PATH" ]; then
    DETECTED_PATH="$ODOO_PATH"
# Check common locations
elif [ -d "/home/coder/letzdoo-sh/odoo/custom/src/odoo" ]; then
    DETECTED_PATH="/home/coder/letzdoo-sh/odoo/custom/src"
elif [ -d "$HOME/odoo/custom/src/odoo" ]; then
    DETECTED_PATH="$HOME/odoo/custom/src"
elif [ -d "./odoo/custom/src/odoo" ]; then
    DETECTED_PATH="$(pwd)/odoo/custom/src"
else
    DETECTED_PATH=""
fi

# Verify Odoo core exists
if [ -n "$DETECTED_PATH" ] && [ -d "$DETECTED_PATH/odoo" ]; then
    export ODOO_PATH="$DETECTED_PATH"
    echo "Found Odoo at: $ODOO_PATH"
else
    DETECTED_PATH=""
fi
```

**If not found**: Use AskUserQuestion tool to prompt for path, then validate it:
```bash
# Verify user-provided path
if [ -d "$USER_PATH/odoo" ]; then
    export ODOO_PATH="$USER_PATH"
    echo "Odoo path validated: $ODOO_PATH"
else
    # Return error - invalid path
    exit 1
fi
```

### Step 5: Build Indexer Database

```bash
cd /home/coder/marketplace/odoo-doodba-dev/skills/odoo-indexer

echo "Building indexer database..."
echo "This may take 2-5 minutes depending on codebase size..."

# Run full indexing
uv run scripts/update_index.py --full
```

**Capture from output**:
- Number of modules indexed
- Number of models indexed
- Number of fields indexed
- Database size
- Any errors or warnings

**If indexing fails**: Return error report with specific error details and troubleshooting steps.

### Step 6: Validate Installation

Test that indexer queries work correctly:

```bash
echo "Testing indexer..."
uv run scripts/search.py "sale.order" --type model --limit 1
```

**Expected**: Results returned successfully with query time

**Capture**:
- Query time (ms)
- Whether results were returned

**If test fails**: Return error report with database troubleshooting steps.

## Final Report Format

Return ONLY this formatted summary (replace placeholders with actual values):

```
✅ Setup Complete!

Configuration:
  • Docker:     ✓ {version}
  • Python:     ✓ {version}
  • uv:         ✓ {version}
  • Odoo path:  ✓ {path}
  • Indexer DB: ✓ {size} ({modules} modules, {models} models)

Performance:
  • Search speed: {query_time}ms
  • Token savings: ~95% vs file reading

Ready to develop! Try these commands:
  /odoo-dev "add field to sale.order"
  /odoo-search "sale.order model"
  /odoo-scaffold my_new_module

For help: See INSTALLATION.md, README.md, or /help
```

## Error Report Format

If any step fails, return this format:

```
❌ Setup Failed: {Step Name}

Error: {Brief error description}

{Detailed error message or output}

Solution:
{Specific steps to resolve the issue}

After fixing, re-run: /odoo-setup
```

## Error Handling Rules

### Docker not found
```
❌ Setup Failed: Docker Check

Error: Docker not found

Docker is required for running Odoo containers.

Solution:
Install Docker for your platform:
- Linux: https://docs.docker.com/engine/install/
- macOS: https://docs.docker.com/desktop/mac/install/
- Windows: https://docs.docker.com/desktop/windows/install/

After installing Docker, re-run: /odoo-setup
```

### Python version too old
```
❌ Setup Failed: Python Version Check

Error: Python 3.10+ required (found: {version})

Solution:
Install Python 3.10 or higher:

Using pyenv (recommended):
  curl https://pyenv.run | bash
  pyenv install 3.10
  pyenv global 3.10

Or system package manager:
  - Linux: sudo apt install python3.10 python3.10-venv
  - macOS: brew install python@3.10

After installing, re-run: /odoo-setup
```

### uv installation fails
```
❌ Setup Failed: uv Installation

Error: Failed to install uv package manager

{Error details}

Solution:
Try manual installation:
  pip install uv
  # or
  pipx install uv

After installing, re-run: /odoo-setup
```

### Odoo path invalid
```
❌ Setup Failed: Odoo Path Validation

Error: Odoo core not found at: {path}

The path should point to odoo/custom/src, which contains the 'odoo' directory.

Solution:
1. Verify the correct path to your Odoo installation
2. Ensure the 'odoo' directory exists at that location
3. Set ODOO_PATH environment variable:
   export ODOO_PATH="/correct/path/to/odoo/custom/src"

To make permanent, add to ~/.bashrc:
  echo 'export ODOO_PATH="/path/to/odoo/custom/src"' >> ~/.bashrc

After fixing, re-run: /odoo-setup
```

### Indexing fails
```
❌ Setup Failed: Indexer Build

Error: Failed to build indexer database

{Error details}

Solution:
Common issues:
1. Wrong ODOO_PATH - Verify: ls $ODOO_PATH/odoo
2. Missing dependencies - Run: cd skills/odoo-indexer && uv sync
3. Permission issues - Check read access to Odoo files

Try rebuilding from scratch:
  cd /home/coder/marketplace/odoo-doodba-dev/skills/odoo-indexer
  uv run scripts/update_index.py --clear --full

After fixing, re-run: /odoo-setup
```

### Validation fails
```
❌ Setup Failed: Indexer Validation

Error: Indexer database built but queries are not working

This may indicate database corruption or path issues.

Solution:
Rebuild indexer database:
  cd /home/coder/marketplace/odoo-doodba-dev/skills/odoo-indexer
  uv run scripts/update_index.py --clear --full

Check database:
  - Location: ~/.odoo-indexer/odoo_indexer.sqlite3
  - Should be readable/writable

After fixing, re-run: /odoo-setup
```

## Important Notes

1. **Keep verbose output internal** - Don't show every command output to the user
2. **Be concise in errors** - Show only relevant error details
3. **Always provide next steps** - Tell user exactly what to do
4. **Capture all required metrics** - For the final report
5. **Use AskUserQuestion tool** - When Odoo path needs user input
6. **Exit on fatal errors** - Don't continue if prerequisites are missing

## Success Indicators

Setup succeeded when:
- ✓ Docker version retrieved
- ✓ Python 3.10+ confirmed
- ✓ uv installed and working
- ✓ Odoo path verified with core directory
- ✓ Indexer build completed without errors
- ✓ Test query returns results in <100ms

Return the formatted success message with all actual values filled in.
