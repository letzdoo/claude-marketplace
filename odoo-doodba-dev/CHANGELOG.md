# Changelog

All notable changes to the Odoo Doodba Dev Plugin.

## [2.0.0] - Current Version

### Overview

Professional Odoo development toolkit with intelligent workflows, fast code indexing, and deep Doodba integration.

**Key Metrics:**
- Setup time: 2-5 minutes (automated)
- Simple tasks: 5-7 minutes
- Complex features: 20-25 minutes
- Code search: <100ms
- User approvals: 1 per task (architecture only)

---

## Core Commands

### `/odoo-setup`
Automated one-command setup with prerequisite checking, auto-installation, and indexer database building.

**Features:**
- Automatic prerequisite detection
- Auto-installs missing dependencies (uv)
- Detects Odoo directory automatically
- Builds indexer database (2-5 minutes)
- Interactive troubleshooting

### `/odoo-dev`
Primary development command with automatic mode detection.

**Modes:**
- **Quick Mode**: Simple tasks (1-2 fields) - 5-7 minutes
- **Full Mode**: Complex features (new modules) - 20-25 minutes
- **Search Mode**: Questions about code - <2 seconds

**Features:**
- Auto-detects complexity
- Inline architecture proposals
- Single approval point (architecture)
- Automatic validation with indexer
- Automatic testing
- Auto-proceeds on success

### `/odoo-search`
Fast codebase search with natural language queries.

**Features:**
- Sub-100ms query performance
- 10+ query pattern recognitions
- Natural language interface
- Comprehensive results
- Powered by SQLite indexer

### `/odoo-scaffold`
Generate properly structured Odoo modules.

**Creates:**
- Complete module structure
- Proper manifest
- Model templates
- View templates
- Security files
- Test framework

### `/odoo-test`
Run Odoo tests with Doodba integration.

**Features:**
- Module-specific testing
- Debug mode support
- Proper Doodba invoke integration
- Comprehensive reporting

---

## Agents

### `odoo-developer`
Unified development agent handling analysis + implementation.

**Capabilities:**
- Requirements analysis
- Codebase research with indexer
- Architecture proposal (inline)
- Code implementation
- Auto-validation
- Test stub creation

**Triggers:** "create", "add", "implement", "develop", "build", "make"

### `odoo-verifier`
Unified validation + testing agent.

**Capabilities:**
- Structure validation
- Model/field/view validation with indexer
- Security validation
- Test execution
- Inline reporting (no files unless failures)
- Auto-proceed on success

**Triggers:** Automatic after implementation

### `odoo-documenter`
Documentation generation agent.

**Capabilities:**
- README.md generation
- USER-GUIDE.md creation
- DEVELOPER-GUIDE.md creation
- API documentation
- Extension examples

**Triggers:** "document", "create docs", "write README"

### `odoo-setup`
Automated setup agent.

**Capabilities:**
- Prerequisite checking
- Dependency installation
- Odoo path detection
- Indexer database building
- Installation validation

**Triggers:** `/odoo-setup` command

---

## Skills

### `odoo-indexer`
SQLite-based code indexer for 95% faster searches.

**Indexed Data:**
- All models with fields and methods
- All views (form, list, kanban, search, etc.)
- All XML IDs
- All actions and menus
- Module dependencies
- Field relationships

**Performance:**
- Query time: <100ms
- Token savings: 95% vs file reading
- Supports wildcards and filters

**Auto-Triggers:**
- "what is {model}"
- "what fields does {model} have"
- "find {element}"
- "where is {element}"
- "search for {element}"

---

## Documentation

### START_HERE.md
5-minute quick start guide with installation, setup, and first steps.

### INSTALLATION.md
Comprehensive installation guide with prerequisites, platform-specific instructions, and troubleshooting.

### USAGE_GUIDE.md
Practical usage examples covering all modes, common workflows, and best practices.

### CLAUDE.md
Complete instructions for Claude Code on how to use the plugin automatically for ALL Odoo development tasks.

### TEST_CHECKLIST.md
Quality assurance checklist for plugin validation.

---

## Architecture Decisions

### Single Command Philosophy
**Decision:** Use `/odoo-dev` for 95% of development tasks.

**Rationale:**
- Reduces cognitive load
- Auto-detects complexity
- Single entry point
- Consistent experience

### Inline Proposals
**Decision:** Architecture proposals presented inline in chat, not in spec files.

**Rationale:**
- 60-80% faster
- Reduces file clutter
- Better conversation flow
- Easier to iterate

### Auto-Proceed on Success
**Decision:** No approval needed if validation/testing passes.

**Rationale:**
- Reduces friction (5 approvals → 1)
- Faster workflows
- Trust automation
- User notified of issues only

### Unified Agents
**Decision:** Merge analyst+implementer and validator+tester.

**Rationale:**
- Fewer context switches
- More coherent workflow
- Better error handling
- Simpler mental model

---

## Performance Metrics

| Operation | Time | Details |
|-----------|------|---------|
| Setup | 2-5 min | Automated, one-command |
| Simple field addition | 5-7 min | Quick Mode |
| Complex module | 20-25 min | Full Mode |
| Code search | <100ms | Indexer-powered |
| Validation | Automatic | Inline reporting |
| Testing | Automatic | Part of workflow |

---

## Technology Stack

- **Indexer**: SQLite 3 database
- **Parser**: Python AST + lxml for XML
- **Package Manager**: uv (auto-installed)
- **Container**: Doodba (Docker Compose)
- **Testing**: Odoo test framework
- **Version Control**: Git integration

---

## Best Practices

### For Claude Code
1. **Always use plugin** for ANY Odoo development
2. **Use `/odoo-dev`** as primary command (95% of tasks)
3. **Use `/odoo-search`** for questions about code
4. **Trust validation** - indexer validates everything
5. **One approval** - architecture only, rest automatic
6. **Never manually implement** - always use plugin

### For Users
1. **Run `/odoo-setup`** once after installation
2. **Use `/odoo-dev`** for all development
3. **Keep indexer updated** - rebuild after major changes
4. **Trust the automation** - validation and testing are automatic
5. **Review architecture** - only approval point needed

---

## Support

- **Documentation**: See README.md, START_HERE.md, USAGE_GUIDE.md
- **Issues**: https://github.com/letzdoo/claude-marketplace/issues
- **Indexer Help**: See skills/odoo-indexer/SKILL.md

---

## License

LGPL-3

---

## Authors

- Letzdoo (Jerome Sonnet)
- Built for Claude Code
- Optimized for Doodba containers

---

**🎉 Welcome to professional Odoo development with 60-80% time savings and 90% automation!**
