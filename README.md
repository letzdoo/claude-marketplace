# Letzdoo Claude Plugins Marketplace

Welcome to the Letzdoo Claude Plugins Marketplace - a collection of professional development plugins for Claude Code.

## Available Plugins

### 🔧 odoo-doodba-dev

Professional Odoo development toolkit for Doodba containers with deep knowledge of Odoo structure, testing, and best practices.

#### Features

- **Module Scaffolding**: Generate properly structured Odoo modules
- **Testing Framework**: Run and manage Odoo tests effectively
- **Addon Management**: Manage addons.yaml configuration
- **Interactive Shell**: Quick access to Odoo shell for debugging
- **Logging**: View and analyze Odoo logs
- **System Info**: Get detailed information about modules and structure
- **Code Indexing**: Fast code navigation with odoo-indexer MCP server
- **Multi-stage Development Workflow**: Orchestrated development with validation checkpoints
- **Specialized Agents**: Expert agents for analysis, implementation, testing, validation, and documentation

#### Key Capabilities

- Deep knowledge of Doodba directory structure
- Odoo development patterns and best practices
- Security considerations and access rights management
- Performance optimization techniques
- Comprehensive testing strategies
- Fast AST and XML parsing with incremental code indexing
- Pure SQLite database for quick searches (<50ms)

#### Requirements

- Doodba-based Odoo deployment
- Docker and Docker Compose
- Python 3.8.1+ with pyinvoke installed
- Python 3.10+ with uv (for MCP server)
- Claude Code installed

---

## Installation

### Add the Marketplace

From a remote repository:

```shell
/plugin marketplace add letzdoo/claude-marketplace
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
