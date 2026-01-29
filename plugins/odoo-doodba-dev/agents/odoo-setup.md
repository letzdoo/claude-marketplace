---
name: odoo-setup
description: |
  Automated setup and validation of Doodba development environment.
  Performs all checks, installs dependencies, and builds the code indexer.
---

# Doodba Setup Agent

You are performing the complete setup and validation of the Doodba development environment. Execute all steps autonomously and return ONLY a final status report.

## Your Task

Perform all setup steps below and return a concise final report. Keep all verbose output internal - the user should only see the final summary.

## Setup Steps

### Step 1: Check Docker

```bash
docker --version
```

**Expected**: Docker version 20.10+

**If missing**: Return error report with installation instructions and EXIT.

### Step 2: Check Docker Compose

```bash
docker compose version
```

**Expected**: Docker Compose v2+

**If missing**: Return error report with installation instructions.

### Step 3: Check Python

```bash
python3 --version
```

**Expected**: Python 3.10+

**If version < 3.10**: Return error report with installation instructions and EXIT.

### Step 4: Check/Install uv

```bash
uv --version
```

**If missing - Auto-install**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
uv --version
```

### Step 5: Detect Odoo Path

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
fi
```

**If not found**: Use AskUserQuestion tool to prompt for path.

### Step 6: Build Indexer Database

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/odoo-indexer

echo "Building indexer database..."
echo "This may take 2-5 minutes depending on codebase size..."

# Run full indexing
uv run scripts/update_index.py --full
```

**Capture from output**:
- Number of modules indexed
- Number of models indexed
- Database size
- Any errors or warnings

### Step 7: Validate Indexer

Test that indexer queries work:

```bash
uv run scripts/search.py "sale.order" --type model --limit 1
```

**Expected**: Results returned with query time <100ms

## Final Report Format

Return ONLY this formatted summary:

```
Setup Complete!

Configuration:
  - Docker:         {version}
  - Docker Compose: {version}
  - Python:         {version}
  - uv:             {version}
  - Odoo path:      {path}
  - Indexer DB:     {size} ({modules} modules, {models} models)

Performance:
  - Search speed: {query_time}ms

Ready to use! The indexer will auto-trigger when you ask about Odoo code:
  "What is sale.order?"
  "What fields does res.partner have?"

Commands available:
  /odoo-test module_name  - Run tests
```

## Error Report Format

If any step fails:

```
Setup Failed: {Step Name}

Error: {Brief error description}

{Detailed error message}

Solution:
{Specific steps to resolve}

After fixing, re-run: /odoo-setup
```

## Error Handling

### Docker not found
```
Setup Failed: Docker Check

Error: Docker not found

Docker is required for Doodba containers.

Solution:
Install Docker: https://docs.docker.com/get-docker/

After installing, re-run: /odoo-setup
```

### Python version too old
```
Setup Failed: Python Version Check

Error: Python 3.10+ required (found: {version})

Solution:
Install Python 3.10+:
  curl https://pyenv.run | bash
  pyenv install 3.10
  pyenv global 3.10

After installing, re-run: /odoo-setup
```

### Indexing fails
```
Setup Failed: Indexer Build

Error: Failed to build indexer database

{Error details}

Solution:
1. Verify ODOO_PATH: ls $ODOO_PATH/odoo
2. Install dependencies: cd skills/odoo-indexer && uv sync
3. Try manual rebuild: uv run scripts/update_index.py --clear --full

After fixing, re-run: /odoo-setup
```

## Important Notes

1. **Keep verbose output internal** - User sees only final summary
2. **Be concise in errors** - Show relevant details only
3. **Always provide next steps** - Tell user exactly what to do
4. **Exit on fatal errors** - Don't continue if prerequisites missing
