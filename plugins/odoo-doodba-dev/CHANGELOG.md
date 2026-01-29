# Changelog

All notable changes to the Odoo Doodba Dev Plugin.

## [3.0.0] - Current Version

### Focus: Doodba-Specific Tooling

Plugin refocused on Doodba-specific functionality. General Odoo development patterns moved to `odoo-development` plugin.

### Components

**Skills**:
- `odoo-indexer` - Fast SQLite-based code search (<100ms queries, 95% token savings)

**Commands**:
- `/odoo-setup` - Environment validation and indexer setup
- `/odoo-test` - Run tests using `invoke test`

**Agents**:
- `odoo-setup` - Automated environment validation

### What's Changed from v2.0

**Removed** (moved to odoo-development plugin):
- `/odoo-dev` command
- `/odoo-search` command
- `/odoo-scaffold` command
- `/reasoningbank` command
- `odoo-developer` agent
- `odoo-verifier` agent
- `odoo-documenter` agent
- `memory` skill
- `reasoningbank` skill

**Kept**:
- `odoo-indexer` skill (core functionality)
- `odoo-setup` command/agent
- `odoo-test` command

### Migration

If you used removed components, install `odoo-development` plugin:
```bash
/plugin install odoo-development@letzdoo
```

---

## [2.0.0] - Previous Version

Full-featured Odoo development toolkit with:
- Intelligent workflows
- Fast code indexing
- Multiple specialized agents
- Pattern learning system

See git history for full v2.0.0 details.

---

## License

LGPL-3.0

## Authors

Letzdoo Team
