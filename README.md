# Letzdoo Claude Plugins Marketplace

A curated collection of Claude Code plugins for Odoo ERP and business application development.

## Available Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [odoo-doodba-dev](./plugins/odoo-doodba-dev/) | Professional Odoo development toolkit for Doodba containers | 2.0.0 |
| [odoo-development](./plugins/odoo-development/) | Odoo module generation, review, and patterns for versions 14-19 | 3.0.0 |
| [odoo-query](./plugins/odoo-query/) | Read-only XML-RPC queries to investigate Odoo instances | 1.0.0 |

---

## Plugin Details

### odoo-doodba-dev v2.0

Professional Odoo development toolkit for Claude Code with intelligent workflows, fast code indexing, and deep Doodba integration.

**Features:**
- **One-Command Setup** (`/odoo-setup`): Automated installation with prerequisite checks
- **Smart Development** (`/odoo-dev`): Auto-detects task complexity (Quick/Full/Search modes)
- **Fast Code Search** (`/odoo-search`): Sub-100ms queries with natural language patterns
- **Module Scaffolding** (`/odoo-scaffold`): Generate properly structured Odoo modules
- **Testing Framework** (`/odoo-test`): Run and manage Odoo tests with Doodba integration
- **Proactive Tools**: 90% automated with AUTO-TRIGGER keywords

**Requirements:**
- Doodba-based Odoo deployment
- Docker & Docker Compose
- Python 3.10+
- uv package manager (auto-installed if missing)

**Quick Start:**
```bash
/odoo-setup
/odoo-dev "add notes field to res.partner"
```

**[Full Documentation](plugins/odoo-doodba-dev/README.md)**

---

### odoo-development v3.0

Comprehensive Odoo development patterns and module generation for versions 14-19 with progressive skill loading.

**Features:**
- Module scaffolding with best practices
- ORM patterns and field references
- View patterns (form, tree, kanban, search)
- Security configuration guides
- OWL component patterns (v1.x, v2.x, v3.x)
- Version-specific knowledge and migration guides

**Commands:**
- `/odoo-module` - Generate new Odoo module
- `/odoo-owl` - Generate OWL components
- `/odoo-review` - Review module for best practices
- `/odoo-security` - Generate/audit security configuration
- `/odoo-test` - Generate test cases
- `/odoo-upgrade` - Analyze upgrade compatibility

---

### odoo-query v1.0

Connect to Odoo instances via XML-RPC for read-only queries to investigate issues and explore data.

**Features:**
- Safe read-only operations (search, read, search_read, fields_get)
- Connect using API keys (recommended) or passwords
- Investigate data issues directly from Claude Code

**Commands:**
- `/odoo-query` - Connect and query Odoo instance

**Security:**
- Only READ operations are allowed
- API keys preferred over passwords
- Credentials only used for current session

---

## Installation

### Add the Marketplace

```bash
# From remote repository
/plugin marketplace add https://github.com/letzdoo/claude-marketplace.git

# Or clone locally
git clone https://github.com/letzdoo/claude-marketplace.git
/plugin marketplace add ./claude-marketplace
```

### Install a Plugin

```bash
# Install odoo-doodba-dev (for Doodba container development)
/plugin install odoo-doodba-dev@letzdoo-marketplace

# Install odoo-development (for general Odoo development)
/plugin install odoo-development@letzdoo-marketplace

# Install odoo-query (for querying Odoo instances)
/plugin install odoo-query@letzdoo-marketplace
```

### Complete Setup (for odoo-doodba-dev)

After installation, run the automated setup:
```bash
/odoo-setup
```

---

## Marketplace Structure

```
.
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
├── plugins/
│   ├── odoo-doodba-dev/      # Doodba development toolkit
│   │   ├── skills/
│   │   │   ├── odoo-indexer/ # Fast code indexer
│   │   │   └── reasoningbank/# Pattern learning system
│   │   └── README.md
│   ├── odoo-development/     # Odoo patterns & generation
│   │   ├── skills/           # On-demand skill files
│   │   ├── agents/           # Subagents
│   │   └── commands/         # Slash commands
│   └── odoo-query/           # XML-RPC query tool
│       ├── commands/
│       └── scripts/
├── LICENSE
└── README.md
```

---

## Contributing

To add a new plugin:

1. Create a directory under `plugins/` or at root level
2. Add `.claude-plugin/plugin.json` manifest
3. Add `SKILL.md` with proper frontmatter
4. Update `.claude-plugin/marketplace.json` to include your plugin
5. Submit a pull request

## Validation

```bash
# Validate marketplace structure
claude plugin validate .
```

## License

LGPL-3.0 - See [LICENSE](LICENSE) file for details.

## Support

For issues or questions:
- Open an issue in the [repository](https://github.com/letzdoo/claude-marketplace/issues)
- Contact the Letzdoo development team

## Links

- [Claude Code Documentation](https://code.claude.com/docs)
- [Plugin Marketplaces Guide](https://code.claude.com/docs/en/plugin-marketplaces)

---

Created and maintained by [Letzdoo](https://letzdoo.com) for professional Odoo development with Claude Code.
