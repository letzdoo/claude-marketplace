# Letzdoo Claude Plugins Marketplace

Welcome to the Letzdoo Claude Plugins Marketplace - a collection of professional development plugins for Claude Code.

## Available Plugins

### 🔧 odoo-doodba-dev

**Version:** 1.0.0
**Author:** Letzdoo (Jerome Sonnet)

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
/plugin marketplace add letzdoo/claude-plugins
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

## Using the Plugins

### Odoo Doodba Development Plugin

#### Available Commands

- `/odoo-scaffold` - Create a new Odoo module with proper structure
- `/odoo-test` - Run tests for specific modules
- `/odoo-addons` - Manage addons.yaml configuration and module installation
- `/odoo-shell` - Launch interactive Odoo shell for debugging
- `/odoo-logs` - View and analyze Odoo logs
- `/odoo-info` - Get detailed information about modules and system structure
- `/odoo-validate` - Validate Odoo module before installation using indexer
- `/odoo-workflow` - Orchestrate multi-stage Odoo development with validation checkpoints

#### Available Agents

- **odoo-analyst**: Analyze Odoo requirements and create detailed specifications
- **odoo-implementer**: Implement Odoo modules from approved specifications
- **odoo-tester**: Create and run comprehensive tests for Odoo modules
- **odoo-validator**: Validate Odoo module code quality, correctness, and installability
- **odoo-documenter**: Generate comprehensive documentation for Odoo modules

#### Available Skills

- **odoo-indexer**: Index and search Odoo codebase elements (models, fields, functions, views, actions, menus)

#### Quick Start

1. **Scaffold a new module:**
   ```shell
   /odoo-scaffold
   ```

2. **Use the multi-stage workflow for comprehensive development:**
   ```shell
   /odoo-workflow
   ```

   This will guide you through:
   - Requirements analysis and specification
   - Implementation with validation
   - Comprehensive testing
   - Code quality validation
   - Documentation generation

3. **Or develop iteratively with specialized agents:**
   ```shell
   /agents switch odoo-implementer
   ```

4. **Test your changes:**
   ```shell
   /odoo-test
   ```

5. **Validate before deployment:**
   ```shell
   /odoo-validate
   ```

## Plugin Development

Want to contribute a plugin to the marketplace? Check out the [Claude Code Plugin Documentation](https://docs.claude.com/claude-code) for guidelines on creating plugins.

### Marketplace Structure

```
marketplace/
├── README.md
├── LICENSE
├── .gitignore
├── .claude-plugin/
│   └── marketplace.json
└── [plugin-name]/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── commands/
    │   └── *.md
    ├── agents/
    │   └── *.md
    ├── skills/
    │   └── [skill-name]/
    ├── workflows/
    │   └── *.md
    └── README.md
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
