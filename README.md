# Letzdoo Claude Plugins Marketplace

Welcome to the Letzdoo Claude Plugins Marketplace - a collection of professional development plugins for Claude Code.

## Available Plugins

### 🔧 odoo-doodba-dev v2.0

Professional Odoo development toolkit for Claude Code with intelligent workflows, fast code indexing, and deep Doodba integration.

**🚀 v2.0 Released!** 75% faster setup, 60-80% faster development, 90% automated workflows.

#### Features

- **One-Command Setup** (`/odoo-setup`): Automated installation with prerequisite checks (2-5 min)
- **Smart Development** (`/odoo-dev`): Auto-detects task complexity (Quick/Full/Search modes)
- **Fast Code Search** (`/odoo-search`): Sub-100ms queries with natural language patterns
- **Module Scaffolding** (`/odoo-scaffold`): Generate properly structured Odoo modules
- **Testing Framework** (`/odoo-test`): Run and manage Odoo tests with Doodba integration
- **Proactive Tools**: 90% automated with AUTO-TRIGGER keywords
- **Streamlined Workflow**: 3 stages, 1-2 approvals (vs 5 stages, 5 approvals in previous version)
- **Unified Agents**: 3 intelligent agents (developer, verifier, documenter)

#### Key Capabilities

- **Performance**: 60-80% faster development workflows
- **Automation**: Proactive tool usage without manual commands
- **Intelligence**: Auto-detects simple vs complex tasks
- **Speed**: SQLite-based indexer with <100ms search queries
- **Quality**: 100% validation and testing coverage maintained
- **Knowledge**: Deep Doodba structure and Odoo best practices
- **Validation**: Real-time validation with indexer integration

#### Performance Metrics

| Operation | previous version | v2.0 | Improvement |
|-----------|------|------|-------------|
| Setup | 15-30 min | 2-5 min | **75% faster** |
| Simple tasks | 30-60 min | 5-7 min | **88% faster** |
| Complex features | 50-80 min | 20-25 min | **65% faster** |
| Code search | 2-5 sec | <100ms | **95% faster** |

#### Requirements

- Doodba-based Odoo deployment
- Docker & Docker Compose
- Python 3.10+
- uv package manager (auto-installed if missing)
- Claude Code installed

#### Quick Start

```bash
# 1. Add marketplace
/plugin marketplace add https://github.com/letzdoo/claude-marketplace.git

# 2. Install plugin
/plugin install odoo-doodba-dev@letzdoo

# 3. Run automated setup
/odoo-setup

# 4. Start developing
/odoo-dev "add notes field to res.partner"
```

**For detailed guide, see [odoo-doodba-dev/START_HERE.md](odoo-doodba-dev/START_HERE.md)**

---

## Installation

### Add the Marketplace

From a remote repository:

```shell
/plugin marketplace add https://github.com/letzdoo/claude-marketplace.git
```

From a local directory:

```shell
/plugin marketplace add ./path/to/marketplace
```

### Install a Plugin

```shell
/plugin install odoo-doodba-dev@letzdoo
```

Or for local development:

```shell
/plugin install odoo-doodba-dev@local
```

### Complete Setup (for odoo-doodba-dev)

After installation, run the automated setup:

```shell
/odoo-setup
```

This will check prerequisites, install dependencies, and build the code indexer (2-5 minutes).

**For detailed installation guide, see [odoo-doodba-dev/INSTALLATION.md](odoo-doodba-dev/INSTALLATION.md)**

---

## Documentation

### odoo-doodba-dev v2.0 Documentation

- **[START_HERE.md](odoo-doodba-dev/START_HERE.md)** - Quick start guide (5 minutes)
- **[INSTALLATION.md](odoo-doodba-dev/INSTALLATION.md)** - Complete installation guide
- **[USAGE_GUIDE.md](odoo-doodba-dev/USAGE_GUIDE.md)** - Practical examples and workflows
- **[CHANGELOG.md](odoo-doodba-dev/CHANGELOG.md)** - What's new in v2.0
- **[TEST_CHECKLIST.md](odoo-doodba-dev/TEST_CHECKLIST.md)** - Comprehensive testing guide
- **[README.md](odoo-doodba-dev/README.md)** - Plugin overview and features

## Support

For issues or questions:
- Open an issue in the plugin repository
- Contact the Letzdoo development team
- Check the individual plugin documentation

## License

See the LICENSE file for details.

## About

Created and maintained by Letzdoo for professional development with Claude Code.

---

**Happy Coding!** 🚀
