# Letzdoo Claude Marketplace

A curated collection of Claude Code plugins for professional Odoo ERP development — fast code indexing, intelligent patterns, token optimization, and live instance querying.

## Available Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [odoo-doodba-dev](#odoo-doodba-dev) | 2.0.0 | Doodba development toolkit with fast SQLite-based code indexer |
| [odoo-development](#odoo-development) | 3.0.0 | 123 skill files covering Odoo 14-19 patterns, OWL, security, migrations |
| [odoo-query](#odoo-query) | 1.0.0 | Read-only XML-RPC queries against live Odoo instances |
| [odoo-token-killer](#odoo-token-killer) | 1.0.0 | Rust CLI proxy that cuts token usage 60-90% via smart output filtering |

## Quick Start

```bash
# Add the marketplace
/plugin marketplace add https://github.com/letzdoo/claude-marketplace.git

# Install the plugins you need
/plugin install odoo-doodba-dev@letzdoo-marketplace
/plugin install odoo-development@letzdoo-marketplace
/plugin install odoo-token-killer@letzdoo-marketplace

# Run setup
/odoo-setup    # Environment + code indexer
/otk-setup     # Token optimization hook
```

## Plugin Compatibility

| Plugin | Requires Doodba | Works with any Odoo | Standalone |
|--------|:---:|:---:|:---:|
| odoo-development | | | Yes |
| odoo-doodba-dev | Yes | | |
| odoo-query | | Yes | Yes |
| odoo-token-killer | | | Yes |

**Recommended stack for Doodba projects:** install all four plugins together.

---

## Plugin Details

### odoo-doodba-dev

Professional Odoo development toolkit for Doodba containers with a SQLite-based code indexer that delivers sub-100ms queries and 95% token savings compared to reading full source files.

**Commands:**
| Command | Description |
|---------|-------------|
| `/odoo-setup` | Validate environment, install dependencies, build index |
| `/odoo-dev` | Auto-detect task complexity (Quick / Full / Search modes) |
| `/odoo-search` | Natural language code search across indexed codebase |
| `/odoo-scaffold` | Generate properly structured Odoo modules |
| `/odoo-test` | Run and manage tests via Doodba's `invoke test` |

**Indexer capabilities:** models, fields, views, actions, menus, XML IDs, module dependencies, cross-references — all queryable in <100ms.

**Requirements:** Doodba deployment, Docker 20.10+, Python 3.10+, uv (auto-installed)

[Full documentation](plugins/odoo-doodba-dev/README.md)

---

### odoo-development

123 progressively-loaded skill files covering Odoo versions 14 through 19: ORM patterns, view types, OWL components (v1/v2/v3), security, accounting, and version migration guides.

**Commands:**
| Command | Description |
|---------|-------------|
| `/odoo-module` | Scaffold a new Odoo module with best practices |
| `/odoo-owl` | Generate OWL components (version-aware) |
| `/odoo-review` | Review module against Odoo best practices |
| `/odoo-security` | Generate or audit access rights and record rules |
| `/odoo-test` | Generate test cases |
| `/odoo-upgrade` | Analyze version upgrade compatibility |

**Agents:**
- `odoo-context-gatherer` — compiles relevant patterns before code generation (auto-invoked)
- `odoo-code-reviewer` — deep review against Odoo conventions
- `odoo-upgrade-analyzer` — version compatibility analysis
- `odoo-skill-finder` — locates relevant skill files on demand

**Skill categories:** core ORM, views (form/tree/kanban/search), actions & menus, security, OWL (v1.x/v2.x/v3.x), business modules (accounting, sales, HR, stock, purchase, project), portal, external APIs, webhooks, dashboards, performance, and version-specific breaking changes.

---

### odoo-query

Connect to any Odoo instance via XML-RPC for safe, read-only investigation.

**Command:** `/odoo-query`

**Allowed operations:** `search`, `read`, `search_read`, `fields_get` — nothing else.

**Security model:**
- Write operations are blocked at the protocol level
- API key authentication preferred over passwords
- Credentials are session-scoped, never persisted

**Use cases:** investigate production data issues, explore model structures, debug domain filters, verify record states.

---

### odoo-token-killer

Rust CLI proxy inspired by [RTK](https://github.com/rtk-ai/rtk) that intercepts Claude Code tool calls via a PreToolUse hook and returns intelligently filtered output. Claude sees concise summaries; full output is preserved in tee files for recovery.

**Commands:**
| Command | Description |
|---------|-------------|
| `/otk-setup` | Build binary, register hook, validate installation |
| `/otk-gain` | Analytics dashboard showing token savings |

**How it works:**

```
Claude runs:    invoke test sale_module
Hook rewrites:  otk invoke test sale_module
OTK executes:   run command -> filter output -> save full to tee file
Claude sees:    "Tests: 142 passed, 1 failed\nFAILED: AssertionError..."
Instead of:     3,000 lines of Odoo logs
```

**12 filter strategies:**

| Filter | Target | Savings |
|--------|--------|---------|
| Test | pytest / invoke test output | 90-95% |
| Log | Docker / Odoo logs | 85-95% |
| Python | .py source files | 40-70% |
| XML | .xml views and data | 60-80% |
| Git status | Status output | ~80% |
| Git diff | Diff output | 70-80% |
| Git log | Log output | ~80% |
| Grep | Search results | 70-85% |
| LS/Tree | Directory listings | 50-70% |
| Docker | Container commands | 60-80% |
| Pip | Package manager output | 80-90% |
| SQL | Query results | 60-80% |

**Typical session savings (~30 min):**

| Operation | Without OTK | With OTK | Savings |
|-----------|:-----------:|:--------:|:-------:|
| `invoke test` (5x) | 50,000 | 5,000 | 90% |
| `docker compose logs` (10x) | 30,000 | 3,000 | 90% |
| Reading .py files (20x) | 40,000 | 12,000 | 70% |
| Reading .xml views (15x) | 30,000 | 9,000 | 70% |
| Git commands (10x) | 15,000 | 3,000 | 80% |
| Grep searches (8x) | 16,000 | 3,200 | 80% |
| **Total tokens** | **181,000** | **35,200** | **81%** |

**Specs:** <10ms startup, 4.2MB binary, <5MB memory footprint. Falls back to raw output on filter failure.

[Full documentation](plugins/odoo-token-killer/README.md)

---

## Marketplace Structure

```
claude-marketplace/
├── .claude-plugin/
│   └── marketplace.json        # Marketplace manifest
├── plugins/
│   ├── odoo-doodba-dev/        # Doodba toolkit + SQLite indexer
│   │   ├── skills/
│   │   │   └── odoo-indexer/   # Python indexer + parsers
│   │   └── agents/
│   ├── odoo-development/       # 123 skill files + agents
│   │   ├── skills/             # Progressive loading
│   │   ├── agents/             # Context gatherer, reviewer, etc.
│   │   └── commands/           # 6 slash commands
│   ├── odoo-query/             # XML-RPC client
│   │   ├── commands/
│   │   └── scripts/
│   └── odoo-token-killer/      # Rust CLI proxy
│       ├── skills/
│       │   └── otk-core/       # Rust source (2,345 lines)
│       ├── hooks/              # PreToolUse hook
│       └── commands/
├── LICENSE
└── README.md
```

## Contributing

1. Create a directory under `plugins/`
2. Add `.claude-plugin/plugin.json` manifest
3. Add `SKILL.md` with proper frontmatter
4. Update `.claude-plugin/marketplace.json`
5. Submit a pull request

```bash
# Validate marketplace structure
claude plugin validate .
```

## License

MIT — see [LICENSE](LICENSE).

## Support

- [Open an issue](https://github.com/letzdoo/claude-marketplace/issues)
- Contact the [Letzdoo](https://letzdoo.com) development team

## Links

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Plugin Marketplaces Guide](https://docs.anthropic.com/en/docs/claude-code/plugins)
