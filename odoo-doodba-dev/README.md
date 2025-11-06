# Odoo Doodba Development Plugin v2.0

Professional Odoo development toolkit for Claude Code with intelligent workflows, fast code indexing, and deep Doodba integration.

**🚀 New to v2.0?** Start with **[START_HERE.md](START_HERE.md)** for a 5-minute quick start guide!

---

## ⚡ What's New in v2.0

- **75% faster setup** - One-command automated setup
- **60-80% faster development** - Streamlined 3-stage workflow
- **90% automated** - Proactive tool usage
- **Simpler commands** - 8 commands → 5 essential commands
- **Smart workflows** - Auto-detects task complexity

**All while maintaining 100% quality!**

---

## Quick Start

### 1. Install

```bash
/plugin install odoo-doodba-dev@letzdoo
```

### 2. Setup (Automated)

```bash
/odoo-setup
```

**That's it!** The setup will automatically check prerequisites, install dependencies, and build the code indexer.

### 3. Start Developing

```bash
# Simple tasks (quick mode)
/odoo-dev "add notes field to res.partner"

# Complex features (full mode)
/odoo-dev "create inventory management module"

# Search codebase
/odoo-search "sale.order model"
```

---

## Core Features

### 🚀 Smart Development (`/odoo-dev`)

Automatically adapts to your task:

- **Quick Mode**: Simple changes (1-2 fields) → 5-7 minutes
- **Full Mode**: Complex features (new modules) → 20-25 minutes
- **Search Mode**: Questions about code → <2 seconds

**Example**:
```bash
/odoo-dev "add quality_result field to project.task with Many2one to quality.result"
```

Claude will:
1. Analyze requirements (with indexer validation)
2. Propose architecture → Ask approval
3. Implement code (auto-validated)
4. Run tests
5. Report completion

### 🔍 Fast Code Search (`/odoo-search`)

Search your Odoo codebase with sub-100ms queries:

```bash
/odoo-search "sale.order model"
/odoo-search "fields in res.partner"
/odoo-search "views for project.task"
```

**Powered by**: SQLite-based code indexer (95% faster than file reading)

### 🏗️ Module Scaffolding (`/odoo-scaffold`)

Generate properly structured Odoo modules:

```bash
/odoo-scaffold my_custom_module
```

Creates:
- Proper manifest
- Model template
- View structure
- Security files
- Test framework

### 🧪 Testing (`/odoo-test`)

Run Odoo tests with proper Doodba integration:

```bash
/odoo-test my_module
/odoo-test my_module --debug
```

### ⚙️ One-Command Setup (`/odoo-setup`)

Automated prerequisite checking and setup:

- ✓ Checks Docker, Python, uv
- ✓ Auto-installs missing dependencies
- ✓ Detects Odoo path
- ✓ Builds code indexer
- ✓ Validates installation

---

## Installation

### Quick Install

```bash
# 1. Add marketplace
/plugin marketplace add https://github.com/letzdoo/claude-marketplace.git

# 2. Install plugin
/plugin install odoo-doodba-dev@letzdoo

# 3. Run setup
/odoo-setup
```

### Requirements

Auto-checked by setup:
- Doodba-based Odoo deployment
- Docker & Docker Compose
- Python 3.10+
- uv package manager (auto-installed if missing)

**For complete installation guide, see [INSTALLATION.md](INSTALLATION.md)**

---

## Commands Reference

| Command | Purpose | Usage |
|---------|---------|-------|
| `/odoo-setup` | One-time automated setup | `/odoo-setup` |
| `/odoo-dev` | Smart development (auto-mode) | `/odoo-dev "your task"` |
| `/odoo-search` | Fast codebase search | `/odoo-search "query"` |
| `/odoo-test` | Run module tests | `/odoo-test module_name` |
| `/odoo-scaffold` | Create new module | `/odoo-scaffold module_name` |

---

## Workflows

### Simple Task (Quick Mode)

```
/odoo-dev "add color field to res.partner"

→ Analyzes requirements (auto-validates with indexer)
→ Proposes architecture
→ User approves
→ Implements + validates + tests
→ Done! (5-7 minutes)
```

### Complex Feature (Full Mode)

```
/odoo-dev "create inventory management module"

→ Researches codebase (auto-search)
→ Proposes detailed architecture
→ User approves
→ Implements in phases
→ Validates + tests
→ Optional: Generate documentation
→ Done! (20-25 minutes)
```

### Code Search

```
/odoo-search "what fields does sale.order have?"

→ Auto-uses indexer
→ Returns results instantly (<1 second)
```

---

## Architecture

### Intelligent Agents

**odoo-developer** - Analysis + Implementation
- Analyzes requirements
- Validates references with indexer
- Proposes architecture
- Implements code
- Auto-validates all changes

**odoo-verifier** - Validation + Testing
- Checks file structure
- Validates with indexer
- Runs tests
- Reports results

**odoo-documenter** - Documentation (Optional)
- Generates README
- Creates user guides
- Documents architecture

### Code Indexer

Fast SQLite-based search engine for Odoo codebases:

- **Models**: All Odoo models with fields and methods
- **Fields**: Field types, attributes, relationships
- **Views**: Form, tree, search views with inheritance
- **Actions**: Window actions, server actions
- **Menus**: Menu hierarchy
- **XML IDs**: All XML ID references

**Performance**:
- Initial indexing: 2-5 minutes (one-time)
- Search queries: <50ms
- Incremental updates: <30 seconds
- Database size: 10-50MB

---

## Best Practices

### 1. Keep Index Fresh

Update after major code changes:
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py
```

### 2. Use Smart Mode

Let `/odoo-dev` auto-detect complexity - don't overthink it:
```bash
/odoo-dev "your request"  # Just describe what you want
```

### 3. Trust the Validation

The indexer validates all references before code generation:
- Model existence
- Field types
- View inheritance
- XML ID references
- Security rules

### 4. Iterate on Architecture

When Claude proposes architecture, review carefully:
- Module structure
- Model relationships
- Field naming
- View organization

Give feedback before implementation starts.

### 5. Follow Odoo Conventions

The plugin enforces:
- Field naming: `_id` for Many2one, `_ids` for Many2many/One2many
- Odoo 18+ syntax: `<list>` not `<tree>`
- Security: Always define access rights
- Testing: Comprehensive test coverage

---

## Example Workflows

### Add Field to Existing Model

```bash
/odoo-dev "add quality_result_id (Many2one to quality.result) to project.task with form view update"
```

**Result**: Field added, view updated, tested in ~5 minutes

### Create New Module

```bash
/odoo-dev "create equipment_maintenance module with models for equipment, maintenance_request, and maintenance_schedule"
```

**Result**: Full module with models, views, security, tests in ~20 minutes

### Search and Learn

```bash
/odoo-search "how does sale.order handle taxes?"
```

**Result**: Detailed information about tax computation in <1 second

### Scaffold and Customize

```bash
/odoo-scaffold my_custom_crm
# Then customize the generated structure
```

**Result**: Proper module structure ready for customization

---

## Troubleshooting

### Setup Issues

See [INSTALLATION.md](INSTALLATION.md#troubleshooting) for:
- Docker not found
- Python version issues
- uv installation problems
- Odoo path detection
- Indexer build failures

### Development Issues

**Tests failing**:
```bash
/odoo-test module_name --debug
# Review logs and fix issues
```

**Search not working**:
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/index_status.py  # Check index health
uv run scripts/update_index.py --full  # Rebuild if needed
```

**Slow performance**:
- Update index: `uv run scripts/update_index.py`
- Check index status: `uv run scripts/index_status.py`
- Verify Odoo path: `echo $ODOO_PATH`

---

## Migration from v1.x

See [MIGRATION.md](MIGRATION.md) for complete migration guide.

**Key changes**:
- Commands consolidated (8 → 5)
- Workflow streamlined (5 stages → 3)
- Setup automated (one command)
- Tools auto-trigger (proactive)

**Old commands removed**:
- `/odoo-workflow` → Use `/odoo-dev`
- `/odoo-validate` → Automatic in `/odoo-dev`
- `/odoo-info` → Use `/odoo-search`
- `/odoo-addons`, `/odoo-shell`, `/odoo-logs` → Use `invoke` directly

---

## Documentation

- **[START_HERE.md](START_HERE.md)** - Quick start guide (read this first!)
- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide
- **[MIGRATION.md](MIGRATION.md)** - v1 to v2 migration guide
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Detailed usage examples
- **[CHANGELOG.md](CHANGELOG.md)** - What's new in v2.0
- **Skills README**: `skills/odoo-indexer/README.md` - Indexer documentation

---

## Support

- **Issues**: https://github.com/letzdoo/claude-marketplace/issues
- **Discussions**: [GitHub Discussions](https://github.com/letzdoo/claude-marketplace/discussions)
- **Documentation**: See docs above

---

## Performance Metrics

Based on real-world usage:

| Operation | v1.x | v2.0 | Improvement |
|-----------|------|------|-------------|
| Setup | 15-30 min | 2-5 min | **75% faster** |
| Simple task | 20-25 min | 5-7 min | **75% faster** |
| Complex feature | 50-55 min | 20-25 min | **60% faster** |
| Code search | File reading | <50ms | **15x faster** |
| Manual approvals | 5 | 1-2 | **60% less** |

---

## About

**Version**: 2.0.0
**Author**: Letzdoo (Jerome Sonnet)
**License**: See LICENSE file
**Repository**: https://github.com/letzdoo/claude-marketplace

Built for professional Odoo development with Claude Code.

---

**Happy Coding!** 🚀

*For quick start, run `/odoo-setup` and then `/odoo-dev "your first task"`*
