# Plugin Development Guide - odoo-doodba-dev

This file provides guidance for developing and contributing to the odoo-doodba-dev plugin.

## Plugin Purpose

This plugin provides Doodba-specific tooling for Odoo development:
- **odoo-indexer skill**: Fast SQLite-based code search for Odoo codebases
- **odoo-setup command/agent**: Doodba environment validation and setup
- **odoo-test command**: Run tests using Doodba's `invoke test`

## Directory Structure

```
odoo-doodba-dev/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, metadata)
├── agents/
│   └── odoo-setup.md        # Setup agent definition
├── commands/
│   ├── odoo-setup.md        # Setup command
│   └── odoo-test.md         # Test command
├── skills/
│   └── odoo-indexer/        # Code indexer skill
│       ├── SKILL.md         # Skill definition and usage
│       ├── scripts/         # Python indexer scripts
│       ├── tools/           # Shell wrapper scripts
│       └── pyproject.toml   # Python dependencies
├── CLAUDE.md                # This file - plugin development guide
├── README.md                # User-facing documentation
├── INSTALLATION.md          # Installation instructions
└── CHANGELOG.md             # Version history
```

## Component Guidelines

### Commands (`commands/`)

Commands are user-invokable slash commands. Each `.md` file becomes a `/command-name` command.

**Required frontmatter**:
```yaml
---
description: "Brief description for command discovery"
---
```

**Best practices**:
- Keep descriptions concise but include trigger keywords
- Use `**AUTO-USE**` prefix for commands Claude should use proactively
- Reference skills and agents by their paths

### Agents (`agents/`)

Agents are specialized subagents for complex tasks. Each `.md` file defines an agent.

**Required frontmatter**:
```yaml
---
name: agent-name
description: |
  Multi-line description of what the agent does
---
```

**Best practices**:
- Define clear success criteria
- Include error handling patterns
- Keep agents focused on single responsibilities

### Skills (`skills/`)

Skills are reusable capabilities with supporting scripts. Each skill lives in its own subdirectory with a `SKILL.md` file.

**Required structure**:
```
skill-name/
├── SKILL.md              # Required - skill definition
├── scripts/              # Supporting scripts
├── tools/                # Shell wrappers
└── pyproject.toml        # Dependencies (if Python)
```

**SKILL.md frontmatter**:
```yaml
---
name: Skill Name
description: When and how to use this skill (trigger keywords)
allowed-tools: Read, Bash, Grep, Glob
---
```

**Best practices**:
- Include auto-trigger keywords in description
- Provide concrete usage examples
- Document all available commands/scripts
- Include troubleshooting section

## Development Workflow

### Adding a New Command

1. Create `commands/new-command.md`
2. Add YAML frontmatter with description
3. Write implementation instructions
4. Test with `/new-command`

### Adding a New Skill

1. Create `skills/new-skill/` directory
2. Create `skills/new-skill/SKILL.md` with frontmatter
3. Add supporting scripts in `scripts/`
4. Document usage in SKILL.md

### Modifying Existing Components

1. Read the existing component file
2. Understand current behavior and triggers
3. Make focused changes
4. Test affected functionality

## Testing

### Manual Testing

```bash
# Test setup
/odoo-setup

# Test indexer skill (via natural language)
# "What is sale.order?"
# "List all modules"

# Test directly
cd skills/odoo-indexer
uv run scripts/search.py "sale.order" --type model
```

### Validation Checklist

- [ ] Plugin loads without errors
- [ ] Commands appear in `/help`
- [ ] Skills trigger on appropriate keywords
- [ ] Agents complete their tasks
- [ ] Error handling works correctly

## Path References

Always use `${CLAUDE_PLUGIN_ROOT}` for intra-plugin paths:

```bash
# In hook commands
"command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh"

# In skill documentation
cd ${CLAUDE_PLUGIN_ROOT}/skills/odoo-indexer
```

## Dependencies

### Python (for odoo-indexer)

Managed via `uv` and `pyproject.toml`:
```bash
cd skills/odoo-indexer
uv sync  # Install dependencies
```

### System Requirements

- Docker 20.10+ (for Doodba)
- Python 3.10+
- uv package manager

## Contributing

1. Follow existing code style and patterns
2. Update CHANGELOG.md for user-visible changes
3. Test all modified components
4. Update documentation as needed

## Related Plugins

- **odoo-development**: Odoo patterns, best practices, and code generation
- Use both plugins together for complete Odoo development workflow
