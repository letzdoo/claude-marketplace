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
- **Streamlined Workflow**: 3 stages, 1-2 approvals
- **Unified Agents**: 3 intelligent agents (developer, verifier, documenter)

#### Key Capabilities

- **Performance**: 60-80% faster development workflows
- **Automation**: Proactive tool usage without manual commands
- **Intelligence**: Auto-detects simple vs complex tasks
- **Speed**: SQLite-based indexer with <100ms search queries
- **Quality**: 100% validation and testing coverage maintained
- **Knowledge**: Deep Doodba structure and Odoo best practices
- **Validation**: Real-time validation with indexer integration

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

**For detailed guide, see [odoo-doodba-dev/README.md](odoo-doodba-dev/README.md)**

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

- **[README.md](odoo-doodba-dev/README.md)** - Plugin overview, features, and quick start
- **[INSTALLATION.md](odoo-doodba-dev/INSTALLATION.md)** - Complete installation guide
- **[USAGE.md](odoo-doodba-dev/USAGE.md)** - Practical examples and workflows
- **[CHANGELOG.md](odoo-doodba-dev/CHANGELOG.md)** - What's new in v2.0
- **[CLAUDE.md](odoo-doodba-dev/CLAUDE.md)** - Instructions for Claude Code AI

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
