---
description: Automated setup and validation of Odoo plugin prerequisites
---

# Odoo Plugin Setup

Run comprehensive setup with automatic dependency installation and validation.

## Your Role

You are setting up the Odoo Doodba Development Plugin. Follow these steps to ensure all prerequisites are met and the plugin is ready to use.

## Setup Process

### Step 1: Check Docker

```bash
docker --version
```

**Expected**: Docker version 20.10+ installed

**If missing**:
```
❌ Docker not found!

Please install Docker:
- Linux: https://docs.docker.com/engine/install/
- macOS: https://docs.docker.com/desktop/mac/install/
- Windows: https://docs.docker.com/desktop/windows/install/

After installing Docker, re-run: /odoo-setup
```

### Step 2: Check Python Version

```bash
python3 --version
```

**Required**: Python 3.10 or higher

**If version < 3.10**:
```
❌ Python 3.10+ required (found: {version})

Please install Python 3.10 or higher:
- Linux: sudo apt install python3.10 python3.10-venv
- macOS: brew install python@3.10
- Or use pyenv: pyenv install 3.10

After installing, re-run: /odoo-setup
```

### Step 3: Check/Install uv

```bash
uv --version
```

**Required**: uv package manager

**If missing - Auto-install**:
```bash
echo "📦 Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Source the new PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Verify installation
uv --version
```

**Output**:
```
✓ uv installed successfully (version {version})
```

### Step 4: Detect Odoo Path

Try to detect Odoo installation automatically:

```bash
# Check environment variable
if [ -n "$ODOO_PATH" ]; then
    echo "Found ODOO_PATH: $ODOO_PATH"
    DETECTED_PATH="$ODOO_PATH"
# Check common locations
elif [ -d "/home/coder/letzdoo-sh/odoo/custom/src" ]; then
    DETECTED_PATH="/home/coder/letzdoo-sh/odoo/custom/src"
    echo "Found Odoo at: $DETECTED_PATH"
elif [ -d "$HOME/odoo/custom/src" ]; then
    DETECTED_PATH="$HOME/odoo/custom/src"
    echo "Found Odoo at: $DETECTED_PATH"
elif [ -d "./odoo/custom/src" ]; then
    DETECTED_PATH="$(pwd)/odoo/custom/src"
    echo "Found Odoo at: $DETECTED_PATH"
else
    DETECTED_PATH=""
fi

# Verify Odoo path
if [ -n "$DETECTED_PATH" ] && [ -d "$DETECTED_PATH/odoo" ]; then
    echo "✓ Verified: Odoo core found at $DETECTED_PATH/odoo"
    export ODOO_PATH="$DETECTED_PATH"
else
    echo "❌ Odoo not found in common locations"
fi
```

**If not found - Prompt user**:
```
❌ Odoo path not detected automatically

Please provide the path to your Odoo installation:
(This should be the path to odoo/custom/src, containing the 'odoo' directory)

Example: /home/coder/letzdoo-sh/odoo/custom/src

Enter path: [wait for user input]
```

**After user provides path**:
```bash
# Verify the path
if [ -d "$USER_PATH/odoo" ]; then
    export ODOO_PATH="$USER_PATH"
    echo "✓ Odoo path set to: $ODOO_PATH"
else
    echo "❌ Invalid path: 'odoo' directory not found at $USER_PATH"
    echo "Please check the path and try again"
    exit 1
fi
```

### Step 5: Build Indexer Database

```bash
cd odoo-doodba-dev/skills/odoo-indexer

echo "🔍 Building indexer database..."
echo "This will scan your Odoo codebase and may take 2-5 minutes..."
echo ""

# Run full indexing
uv run scripts/update_index.py --full
```

**Expected output**:
```
Starting full index rebuild...
Scanning modules...
Found 156 modules

Indexing: odoo (core)                    ████████████ 100%
Indexing: sale                           ████████████ 100%
Indexing: account                        ████████████ 100%
...

✓ Indexing complete!

Summary:
- Modules indexed: 156
- Models indexed: 1,247
- Fields indexed: 15,832
- Views indexed: 3,421
- Actions indexed: 892
- Menus indexed: 765

Database size: 42.3 MB
Average query time: <50ms
```

**If indexing fails**:
```
❌ Indexing failed!

Common issues:
1. Wrong ODOO_PATH - Verify with: ls $ODOO_PATH/odoo
2. Missing dependencies - Run: uv sync
3. Permission issues - Check read access to Odoo files

Error details:
{error_message}

After fixing, re-run: /odoo-setup
```

### Step 6: Validate Installation

Run a test search to verify everything works:

```bash
echo "🧪 Testing indexer..."

# Test search for a common model
uv run scripts/search.py "sale.order" --type model --limit 1
```

**Expected output**:
```
Results for "sale.order":

1. sale.order
   Module: sale
   Type: model
   Description: Sales Order
   Fields: 127
   Views: 8

Query time: 23ms
```

**If test fails**:
```
❌ Validation test failed!

The indexer database was built but queries are not working.
This may indicate a database corruption or path issue.

Try rebuilding:
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py --clear --full

If issues persist, check:
- Database file: ~/.odoo-indexer/odoo_indexer.sqlite3
- Permissions: Should be readable/writable
```

### Step 7: Report Success

```
✅ Setup Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Odoo Doodba Dev Plugin is ready to use!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Configuration:
  • Docker:     ✓ {version}
  • Python:     ✓ {version}
  • uv:         ✓ {version}
  • Odoo path:  ✓ {path}
  • Indexer DB: ✓ {size} ({modules} modules)

Performance:
  • Search speed: <50ms
  • Token savings: 95% vs file reading

Ready to develop! Try these commands:

  /odoo-dev "add field to sale.order"
  /odoo-search "sale.order model"
  /odoo-scaffold my_new_module

For help:
  - Quick start: See INSTALLATION.md
  - Full docs: See README.md
  - Command list: /help

Happy coding! 🚀
```

## Troubleshooting

### Docker not found
Install Docker for your platform:
- https://docs.docker.com/get-docker/

### Python version too old
Use pyenv to install Python 3.10+:
```bash
curl https://pyenv.run | bash
pyenv install 3.10
pyenv global 3.10
```

### uv installation fails
Try manual installation:
```bash
pip install uv
# or
pipx install uv
```

### Odoo path detection fails
Set manually:
```bash
export ODOO_PATH="/your/path/to/odoo/custom/src"
/odoo-setup
```

To make permanent, add to ~/.bashrc or ~/.zshrc:
```bash
echo 'export ODOO_PATH="/your/path"' >> ~/.bashrc
```

### Indexer build takes too long
This is normal for large codebases (200+ modules).
- Average: 2-5 minutes
- Large installations: up to 10 minutes
- Subsequent updates are much faster (incremental)

### Indexer test fails
Rebuild from scratch:
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py --clear --full
```

## Re-running Setup

You can safely re-run setup anytime:
```bash
/odoo-setup
```

Setup is idempotent - it will:
- Skip already installed dependencies
- Detect existing configuration
- Only rebuild indexer if needed

## Manual Setup (Advanced)

If automated setup fails, you can set up manually:

1. Install prerequisites:
   ```bash
   # Docker (platform-specific)
   # Python 3.10+ (via pyenv or system)
   pip install uv
   ```

2. Set Odoo path:
   ```bash
   export ODOO_PATH="/path/to/odoo/custom/src"
   ```

3. Build indexer:
   ```bash
   cd odoo-doodba-dev/skills/odoo-indexer
   uv run scripts/update_index.py --full
   ```

4. Test:
   ```bash
   uv run scripts/search.py "sale.order" --type model
   ```

## Next Steps

After successful setup:

1. **Try a simple task**:
   ```bash
   /odoo-dev "add description field to res.partner"
   ```

2. **Search the codebase**:
   ```bash
   /odoo-search "what fields does sale.order have?"
   ```

3. **Create a new module**:
   ```bash
   /odoo-scaffold my_custom_module
   ```

4. **Read the docs**:
   - INSTALLATION.md - Complete installation guide
   - USAGE_GUIDE.md - How to use all features
   - README.md - Overview and best practices

## Keeping Index Fresh

The indexer tracks file changes, but you should rebuild after:
- Installing new modules
- Major code changes
- Git pulls with many changes

Quick incremental update:
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py
```

Full rebuild (slower):
```bash
uv run scripts/update_index.py --full
```

Check index status:
```bash
uv run scripts/index_status.py
```

## Success Indicators

You'll know setup worked when:
- ✓ All checks pass (Docker, Python, uv, Odoo path)
- ✓ Indexer builds without errors
- ✓ Test search returns results in <100ms
- ✓ Success message displays

If any step fails, read the error message carefully - it will guide you to the solution.

---

**Note**: This is a one-time setup. Once complete, you can immediately start developing with `/odoo-dev`, `/odoo-search`, and other commands!
