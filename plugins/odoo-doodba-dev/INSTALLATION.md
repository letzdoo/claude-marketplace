# Odoo Doodba Dev Plugin - Installation Guide

## Prerequisites

- **Doodba-based Odoo deployment** with `tasks.py`
- **Docker 20.10+** and Docker Compose
- **Python 3.10+**

## Quick Install

```bash
# 1. Add marketplace (if not already added)
/plugin marketplace add https://github.com/letzdoo/claude-marketplace.git

# 2. Install plugin
/plugin install odoo-doodba-dev@letzdoo

# 3. Run setup (validates environment and builds indexer)
/odoo-setup
```

## What Setup Does

The `/odoo-setup` command:

1. **Checks Docker** - Verifies Docker 20.10+
2. **Checks Python** - Verifies Python 3.10+
3. **Installs uv** - Auto-installs if missing
4. **Detects Odoo path** - Finds your Doodba installation
5. **Builds indexer** - Creates SQLite database (2-5 minutes)
6. **Validates** - Tests indexer queries work

## Troubleshooting

### Docker not found

```bash
# Install Docker for your platform
# https://docs.docker.com/get-docker/
```

### Python version too old

```bash
# Using pyenv (recommended)
curl https://pyenv.run | bash
pyenv install 3.10
pyenv global 3.10
```

### Odoo path not detected

```bash
# Set manually
export ODOO_PATH="/path/to/odoo/custom/src"

# Re-run setup
/odoo-setup
```

### Indexer build fails

```bash
# Manual rebuild
cd skills/odoo-indexer
uv sync
uv run scripts/update_index.py --full
```

## Plugin Ecosystem

| Plugin | Purpose |
|--------|---------|
| **odoo-doodba-dev** | Doodba tooling: indexer, setup, testing |
| **odoo-development** | Odoo patterns and code generation |

Install both for complete Odoo development:
```bash
/plugin install odoo-doodba-dev@letzdoo
/plugin install odoo-development@letzdoo
```

## Uninstall

```bash
/plugin remove odoo-doodba-dev
```
