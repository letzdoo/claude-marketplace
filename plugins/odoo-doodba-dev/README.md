# Odoo Doodba Dev Plugin

Doodba-specific tooling for Odoo development with fast code indexing, environment setup, and test execution.

## Features

### Odoo Indexer Skill

Fast SQLite-based code search for Odoo codebases:
- **<100ms queries** vs 2-5 seconds for file reading
- **95% more token-efficient** than reading files
- Indexes models, fields, views, actions, menus, XML IDs
- Auto-triggers on Odoo-related questions

**Example usage**:
```
"What is sale.order?"
"What fields does res.partner have?"
"Find all Many2one fields in sale module"
```

### Setup Command (`/odoo-setup`)

Validates and configures Doodba development environment:
- Checks Docker and Docker Compose
- Validates Python version
- Detects Doodba project
- Verifies invoke tasks
- Builds code indexer database

### Test Command (`/odoo-test`)

Runs Odoo tests using Doodba's `invoke test`:
- Module-specific testing
- Debug mode support
- Clear result reporting

## Quick Start

```bash
# Install plugin
/plugin install odoo-doodba-dev@letzdoo

# Run setup
/odoo-setup

# Start using the indexer (automatic)
"What is sale.order?"
```

## Requirements

- Doodba-based Odoo deployment
- Docker 20.10+
- Python 3.10+
- uv package manager (auto-installed)

## Commands

| Command | Purpose |
|---------|---------|
| `/odoo-setup` | Environment validation and indexer setup |
| `/odoo-test` | Run module tests with `invoke test` |

## Skills

| Skill | Purpose |
|-------|---------|
| `odoo-indexer` | Fast code search (<100ms queries) |

## Related Plugins

For complete Odoo development:

| Plugin | Purpose |
|--------|---------|
| **odoo-doodba-dev** | Doodba tooling: indexer, setup, testing (this plugin) |
| **odoo-development** | Odoo patterns, best practices, code generation |

## Documentation

- `INSTALLATION.md` - Detailed installation guide
- `CHANGELOG.md` - Version history
- `CLAUDE.md` - Plugin development guide
- `skills/odoo-indexer/SKILL.md` - Indexer usage documentation

## Version

- **Version**: 3.0.0
- **Author**: Letzdoo Team
- **License**: MIT

## Support

- **Issues**: https://github.com/letzdoo/claude-marketplace/issues
