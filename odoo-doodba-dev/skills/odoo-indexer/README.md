# Odoo Indexer Skill

A Claude Code Skill for indexing and searching Odoo codebases.

## Overview

This Skill provides fast indexing and search capabilities for Odoo codebases, allowing Claude to quickly find:
- Models, fields, and methods
- XML views, actions, and menus
- Module dependencies and structure
- Element references and usage

## Features

- **Fast search**: Sub-100ms queries on indexed codebases
- **Incremental indexing**: Only re-parse changed files
- **Comprehensive**: Indexes Python, XML, and CSV files
- **Dependency-aware**: Tracks module dependencies
- **Reference tracking**: Find all usages of any element

## Installation

Dependencies are managed with `uv` and automatically installed when you run scripts.

1. **Set environment variables** (optional):
   ```bash
   export ODOO_PATH="/path/to/odoo/custom/src"
   export SQLITE_DB_PATH="$HOME/.odoo-indexer/odoo_indexer.sqlite3"
   ```

2. **Initial indexing**:
   ```bash
   uv run scripts/update_index.py --full
   ```

## Usage

Claude will automatically use this Skill when you ask questions about Odoo code. For example:

- "Where is the sale.order model defined?"
- "Find all Many2one fields in the sale module"
- "Show me all views for res.partner"
- "What modules depend on account?"

You can also call scripts directly:

```bash
# Search for a model
uv run scripts/search.py "sale.order" --type model

# Get complete details
uv run scripts/get_details.py model "sale.order"

# Find all Many2one fields
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one"}'

# Check index status
uv run scripts/index_status.py
```

## Architecture

```
skills/odoo-indexer/
├── SKILL.md              # Skill definition for Claude
├── README.md             # This file
├── pyproject.toml        # Python dependencies (uv project)
├── lib/                  # Shared library code
│   ├── config.py         # Configuration
│   ├── database.py       # SQLite operations
│   ├── indexer.py        # Main indexing logic
│   ├── tools.py          # MCP tool implementations
│   ├── dependency_tree.py # Module dependency tracking
│   └── parsers/          # File parsers
│       ├── python_parser.py
│       ├── xml_parser.py
│       ├── csv_parser.py
│       └── manifest_parser.py
└── scripts/              # Standalone CLI scripts
    ├── search.py
    ├── get_details.py
    ├── list_modules.py
    ├── module_stats.py
    ├── find_refs.py
    ├── search_by_attr.py
    ├── search_xml_id.py
    ├── update_index.py
    └── index_status.py
```

## Configuration

Environment variables:

- `ODOO_PATH`: Path to Odoo source (default: `/home/coder/letzdoo-sh/odoo/custom/src`)
- `SQLITE_DB_PATH`: Database location (default: `~/.odoo-indexer/odoo_indexer.sqlite3`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `MAX_CONCURRENT_MODULES`: Parallel indexing limit (default: `4`)

## Performance

- **Initial indexing**: 2-5 minutes for ~100 modules
- **Incremental updates**: < 30 seconds
- **Search queries**: < 100ms
- **Database size**: ~10-50MB for typical Odoo installation

## Differences from MCP Version

This Skill-based implementation differs from the MCP server version:

1. **No persistent server**: Scripts connect to DB each time
2. **Simpler deployment**: No MCP protocol overhead
3. **Better portability**: Works anywhere Claude Code runs
4. **Team sharing**: Can be distributed via plugin or git

Trade-offs:
- Slightly higher latency per query (DB connection overhead)
- No session state between calls
- Similar performance for typical workloads

## Maintenance

Update the index periodically to keep it fresh:

```bash
# Incremental update (recommended)
uv run scripts/update_index.py

# Full re-index (if needed)
uv run scripts/update_index.py --full

# Index specific modules
uv run scripts/update_index.py --modules "sale,account,stock"
```

## Troubleshooting

**Database not found**:
```bash
uv run scripts/index_status.py
# If empty, run initial indexing
uv run scripts/update_index.py --full
```

**ODOO_PATH not found**:
```bash
export ODOO_PATH="/correct/path/to/odoo/custom/src"
```

**Dependency errors**:
```bash
# Dependencies are automatically installed by uv
# If issues persist, try:
uv sync
```

## License

MIT License - Same as the original odoo-indexer-mcp project
