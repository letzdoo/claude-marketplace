# Installation Guide - Odoo Doodba Dev Plugin v2.0

Complete installation and setup guide for the Odoo Doodba Development Plugin.

---

## Quick Start (5 Minutes)

```bash
# 1. Install the plugin
/plugin install odoo-doodba-dev@letzdoo

# 2. Run automated setup
/odoo-setup
```

**That's it!** The setup will automatically:
- ✓ Check all prerequisites
- ✓ Install missing dependencies
- ✓ Detect your Odoo installation
- ✓ Build the code indexer
- ✓ Validate everything works

---

## Prerequisites

The following are required and will be checked by `/odoo-setup`:

### Required

1. **Doodba-based Odoo Deployment**
   - Your Odoo must be running in Doodba containers
   - Standard directory structure expected
   - Docker Compose setup

2. **Docker & Docker Compose**
   - Docker 20.10 or higher
   - Docker Compose v2 recommended
   - Check: `docker --version`

3. **Python 3.10 or Higher**
   - Required for indexer performance features
   - Check: `python3 --version`
   - Install: `sudo apt install python3.10` (Linux) or `brew install python@3.10` (macOS)

4. **uv Package Manager**
   - Modern Python package manager
   - Auto-installed by setup if missing
   - Manual install: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Optional

- **pyinvoke** - For Doodba invoke tasks (most users already have this)
- Check: `python3 -c "import invoke" && echo "OK"`

---

## Installation Steps

### Step 1: Add Plugin Marketplace

If you haven't already, add the Letzdoo marketplace:

```bash
# From GitHub (recommended)
/plugin marketplace add https://github.com/letzdoo/claude-marketplace.git

# Or from local directory (for development)
/plugin marketplace add /path/to/claude-marketplace
```

### Step 2: Install Plugin

```bash
/plugin install odoo-doodba-dev@letzdoo
```

**Output**:
```
✓ Fetching plugin odoo-doodba-dev from letzdoo marketplace...
✓ Installing plugin...
✓ Plugin installed successfully!

Next step: Run /odoo-setup to complete setup
```

### Step 3: Run Automated Setup

```bash
/odoo-setup
```

The setup wizard will:

1. **Check Docker**
   ```
   Checking Docker...
   ✓ Docker version 24.0.6 found
   ```

2. **Check Python**
   ```
   Checking Python...
   ✓ Python 3.11.5 found
   ```

3. **Install uv** (if needed)
   ```
   Checking uv...
   ✗ uv not found
   📦 Installing uv package manager...
   ✓ uv 0.1.11 installed successfully
   ```

4. **Detect Odoo Path**
   ```
   Detecting Odoo installation...
   ✓ Found Odoo at: /home/coder/letzdoo-sh/odoo/custom/src
   ```

5. **Build Indexer**
   ```
   🔍 Building indexer database...
   This will scan your Odoo codebase (2-5 minutes)...

   Scanning modules... Found 156 modules
   Indexing modules...  ████████████ 100%

   ✓ Indexing complete!
   - Modules: 156
   - Models: 1,247
   - Fields: 15,832
   - Database size: 42.3 MB
   ```

6. **Validate**
   ```
   🧪 Testing indexer...
   ✓ Test search successful (23ms)
   ```

7. **Success!**
   ```
   ✅ Setup Complete!

   🎉 Odoo Doodba Dev Plugin is ready to use!

   Try: /odoo-dev "add field to sale.order"
   ```

---

## Verifying Installation

### Quick Test

Try a search query:

```bash
/odoo-search "sale.order model"
```

**Expected**: Information about the sale.order model in <1 second

### Full Test

Try a development task:

```bash
/odoo-dev "add a notes field to res.partner"
```

**Expected**: Claude will propose architecture and implement the change

---

## Configuration

### Setting Odoo Path Manually

If auto-detection fails, set the path manually:

```bash
export ODOO_PATH="/path/to/your/odoo/custom/src"
/odoo-setup
```

**To make permanent**, add to your shell profile:

```bash
# For bash
echo 'export ODOO_PATH="/your/path"' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export ODOO_PATH="/your/path"' >> ~/.zshrc
source ~/.zshrc
```

### Custom Database Location

By default, the indexer database is stored at:
```
~/.odoo-indexer/odoo_indexer.sqlite3
```

To use a different location:

```bash
export SQLITE_DB_PATH="/your/custom/path/odoo_indexer.sqlite3"
```

---

## Troubleshooting

### Docker Not Found

**Error**: `docker: command not found`

**Solution**: Install Docker for your platform
- Linux: https://docs.docker.com/engine/install/
- macOS: https://docs.docker.com/desktop/mac/install/
- Windows: https://docs.docker.com/desktop/windows/install/

### Python Version Too Old

**Error**: `Python 3.10+ required (found: 3.8.10)`

**Solution**: Install Python 3.10+

**Option 1 - System Package Manager**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv

# macOS
brew install python@3.10
```

**Option 2 - pyenv (Recommended)**:
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.10
pyenv install 3.10
pyenv global 3.10

# Verify
python3 --version
```

### uv Installation Fails

**Error**: `Failed to install uv`

**Solution**: Try manual installation

```bash
# Method 1: Direct download
curl -LsSf https://astral.sh/uv/install.sh | sh

# Method 2: Via pip
pip install uv

# Method 3: Via pipx
pipx install uv

# Verify
uv --version
```

### Odoo Path Not Detected

**Error**: `Odoo path not detected automatically`

**Solution**: Provide the path manually

1. Find your Odoo installation:
   ```bash
   # Look for odoo/custom/src directory
   find ~ -name "custom" -path "*/odoo/custom" 2>/dev/null
   ```

2. Set the path (should end with `/custom/src`):
   ```bash
   export ODOO_PATH="/home/coder/letzdoo-sh/odoo/custom/src"
   ```

3. Verify it's correct:
   ```bash
   ls $ODOO_PATH/odoo  # Should show Odoo core files
   ```

4. Re-run setup:
   ```bash
   /odoo-setup
   ```

### Indexer Build Fails

**Error**: `Indexing failed` or `Permission denied`

**Possible Causes**:

1. **Wrong path**: Verify Odoo path
   ```bash
   ls $ODOO_PATH/odoo  # Should work
   ```

2. **Permission issues**: Check read access
   ```bash
   cd $ODOO_PATH && ls -la
   ```

3. **Missing dependencies**: Reinstall
   ```bash
   cd odoo-doodba-dev/skills/odoo-indexer
   uv sync
   ```

4. **Corrupted database**: Clear and rebuild
   ```bash
   rm ~/.odoo-indexer/odoo_indexer.sqlite3
   uv run scripts/update_index.py --full
   ```

### Indexer Build Takes Too Long

**Issue**: Indexing has been running for >10 minutes

**This is normal for**:
- Very large codebases (200+ modules)
- Slow disk I/O
- Network-mounted filesystems

**Typical times**:
- Small (50 modules): 1-2 minutes
- Medium (100-150 modules): 2-5 minutes
- Large (200+ modules): 5-10 minutes

**If it seems stuck**:
1. Check it's actually running (look for CPU/disk activity)
2. Check the output - it should show progress
3. Let it complete - interrupting may corrupt the database

### Test Search Fails

**Error**: Test search returns no results or errors

**Solution**: Rebuild the index

```bash
cd odoo-doodba-dev/skills/odoo-indexer

# Clear and rebuild
uv run scripts/update_index.py --clear --full

# Test again
uv run scripts/search.py "sale.order" --type model
```

---

## Updating

### Plugin Updates

Check for plugin updates:

```bash
/plugin list
```

Update to latest version:

```bash
/plugin update odoo-doodba-dev@letzdoo
```

### Refreshing Index

Update the index after code changes:

**Incremental update** (fast - only changed files):
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py
```

**Full rebuild** (slow - all files):
```bash
uv run scripts/update_index.py --full
```

**When to update**:
- After installing new Odoo modules
- After major code changes
- After git pulls with many updates
- Weekly (recommended for active development)

**Check index status**:
```bash
uv run scripts/index_status.py
```

---

## Uninstalling

### Remove Plugin

```bash
/plugin uninstall odoo-doodba-dev
```

### Clean Up Data

Remove indexer database:
```bash
rm -rf ~/.odoo-indexer
```

Remove cached data:
```bash
rm -rf ~/.cache/odoo-doodba-dev
```

---

## Advanced Setup

### Multiple Odoo Installations

If you work with multiple Odoo installations, set the path per session:

```bash
# Project 1
export ODOO_PATH="/path/to/project1/odoo/custom/src"
/odoo-dev "task for project 1"

# Project 2
export ODOO_PATH="/path/to/project2/odoo/custom/src"
/odoo-dev "task for project 2"
```

Or use separate indexer databases:

```bash
# Project 1
export ODOO_PATH="/path/to/project1/odoo/custom/src"
export SQLITE_DB_PATH="~/.odoo-indexer/project1.sqlite3"
uv run scripts/update_index.py --full

# Project 2
export ODOO_PATH="/path/to/project2/odoo/custom/src"
export SQLITE_DB_PATH="~/.odoo-indexer/project2.sqlite3"
uv run scripts/update_index.py --full
```

### Docker-Only Setup

If you're running Claude Code inside Docker:

1. Ensure Odoo files are mounted and accessible
2. Set ODOO_PATH to the mounted location
3. Run setup as normal

### CI/CD Integration

To use in CI/CD pipelines:

```bash
# Install plugin
claude-code plugin install odoo-doodba-dev@letzdoo

# Setup with environment variables
export ODOO_PATH="/workspace/odoo/custom/src"
export SQLITE_DB_PATH="/workspace/.odoo-indexer/db.sqlite3"

# Run non-interactive setup
claude-code /odoo-setup --non-interactive
```

---

## Getting Help

### Check Plugin Status

```bash
/plugin list
```

Shows installed plugins and versions.

### View Logs

If something goes wrong:

```bash
# Plugin logs
cat ~/.claude-code/logs/plugins/odoo-doodba-dev.log

# Indexer logs (if available)
cat ~/.odoo-indexer/indexer.log
```

### Support Channels

- **GitHub Issues**: https://github.com/letzdoo/claude-marketplace/issues
- **Documentation**: See README.md and USAGE_GUIDE.md
- **Community**: [Your community channel if applicable]

---

## Next Steps

After successful installation:

1. **Read the Usage Guide**
   ```bash
   cat odoo-doodba-dev/USAGE_GUIDE.md
   ```

2. **Try Your First Task**
   ```bash
   /odoo-dev "add a color field to res.partner"
   ```

3. **Explore Commands**
   ```bash
   /help  # Show all available commands
   ```

4. **Learn Best Practices**
   ```bash
   cat odoo-doodba-dev/README.md
   ```

---

## FAQ

### Do I need to run setup every time?

No. Setup is a one-time process. The configuration persists between sessions.

### Can I skip the indexer?

No. The indexer is essential for the plugin's core functionality. It provides:
- 95% faster code searches
- Reference validation
- Accurate code generation

### How much disk space does it use?

- Plugin files: ~5 MB
- Indexer database: 10-50 MB (depends on codebase size)
- Total: ~15-55 MB

### Does it modify my Odoo code?

No. The indexer only reads files. It never modifies existing code. Code changes only happen when you explicitly request development tasks.

### Can I use it offline?

Yes, once setup is complete. The plugin works entirely offline. Only the initial installation requires internet access.

### Is my code sent to external servers?

No. The indexer runs locally. Code searches happen in your local SQLite database. Only Claude AI interactions go through Anthropic's API (as part of Claude Code's normal operation).

---

**Installation complete!** You're ready to start developing with Claude! 🚀

For usage examples, see: `USAGE_GUIDE.md`
For full documentation, see: `README.md`
