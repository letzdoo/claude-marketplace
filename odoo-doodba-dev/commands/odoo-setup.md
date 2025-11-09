---
description: Automated setup and validation of Odoo plugin prerequisites
---

# Odoo Plugin Setup

You will launch a specialized setup agent to perform the complete plugin installation and configuration. The agent will handle all verification, installation, and validation steps autonomously.

## Your Role

1. Launch the `odoo-setup` agent to perform the complete plugin installation
2. The agent will autonomously:
   - Check all prerequisites (Docker, Python, uv)
   - Auto-install missing dependencies (uv)
   - Detect or prompt for Odoo path
   - Build the indexer database
   - Validate the installation
   - Return a concise status report

3. After the agent completes:
   - Display ONLY the agent's final report in main context
   - All verbose setup output stays in agent context
   - If setup failed, guide user with troubleshooting steps below

## Launch Agent

Use the Task tool to launch the odoo-setup agent:

```
subagent_type: odoo-doodba-dev:odoo-setup
prompt: "Perform complete Odoo plugin setup and return final status report"
```

The agent has detailed instructions and will handle all steps autonomously.

## Troubleshooting Guide

If the agent reports setup failures, guide the user:

### Docker not found
```
Install Docker: https://docs.docker.com/get-docker/
After installing, re-run: /odoo-setup
```

### Python version too old
```
Install Python 3.10+ via pyenv:
curl https://pyenv.run | bash
pyenv install 3.10
pyenv global 3.10

Then re-run: /odoo-setup
```

### uv installation fails
```
Try manual installation:
pip install uv
# or
pipx install uv

Then re-run: /odoo-setup
```

### Odoo path not detected
```
Set ODOO_PATH manually:
export ODOO_PATH="/path/to/odoo/custom/src"

To make permanent, add to ~/.bashrc:
echo 'export ODOO_PATH="/path/to/odoo/custom/src"' >> ~/.bashrc

Then re-run: /odoo-setup
```

### Indexing fails
```
Check:
1. Verify ODOO_PATH: ls $ODOO_PATH/odoo
2. Install dependencies: cd skills/odoo-indexer && uv sync
3. Check permissions: Ensure read access to Odoo files

Rebuild from scratch:
cd skills/odoo-indexer
uv run scripts/update_index.py --clear --full
```

### Validation fails
```
Rebuild indexer database:
cd skills/odoo-indexer
uv run scripts/update_index.py --clear --full

Check database:
- Location: ~/.odoo-indexer/odoo_indexer.sqlite3
- Should be readable/writable
```

## Re-running Setup

Setup is idempotent and can be re-run anytime:
- Skips already installed dependencies
- Detects existing configuration
- Only rebuilds indexer if needed

## Manual Setup (Advanced)

If automated setup fails completely:

1. Install prerequisites manually:
   ```bash
   # Docker (platform-specific)
   # Python 3.10+ via pyenv or system
   pip install uv
   ```

2. Set Odoo path:
   ```bash
   export ODOO_PATH="/path/to/odoo/custom/src"
   ```

3. Build indexer:
   ```bash
   cd /home/coder/marketplace/odoo-doodba-dev/skills/odoo-indexer
   uv run scripts/update_index.py --full
   ```

4. Test:
   ```bash
   uv run scripts/search.py "sale.order" --type model
   ```

---

**Note**: This setup runs once. After completion, you can immediately use `/odoo-dev`, `/odoo-search`, `/odoo-scaffold`, and all other plugin features!
