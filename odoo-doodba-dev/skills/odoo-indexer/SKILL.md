---
name: Odoo Indexer
description: |
  PROACTIVELY index and search Odoo codebase when user asks about code structure.

  AUTO-TRIGGER for these queries:
  - "what is {model}" - Get model details
  - "what fields does {model} have" - List model fields
  - "find {element}" - Search for elements
  - "search for {element}" - Search codebase
  - "show me {element}" - Display element info
  - "where is {element}" - Find definition location
  - "does {model} have {field}" - Check field existence
  - "list {type}" - List elements of type
  - "tell me about {module}" - Module information

  This skill provides 95% faster responses than file reading.
  ALWAYS prefer indexer over Read tool for Odoo code exploration.

allowed-tools: Read, Bash, Grep, Glob
---

# Odoo Indexer Skill

**⚡ PROACTIVE USAGE**: This skill should be used automatically when user asks questions about Odoo code structure, models, fields, views, or modules.

Fast indexing and search for Odoo codebase elements with sub-100ms query performance.

---

## When to Auto-Use This Skill

✅ **User asks**: "What is sale.order?"
→ **AUTO-USE**: `uv run scripts/get_details.py model "sale.order"`

✅ **User asks**: "What fields does res.partner have?"
→ **AUTO-USE**: `uv run scripts/get_details.py model "res.partner"`

✅ **User asks**: "Find all Many2one fields in sale module"
→ **AUTO-USE**: `uv run scripts/search_by_attr.py field --filters '{"field_type":"Many2one"}' --module sale`

✅ **User asks**: "Where is project.task defined?"
→ **AUTO-USE**: `uv run scripts/search.py "project.task" --type model`

✅ **User asks**: "Does sale.order have partner_id field?"
→ **AUTO-USE**: `uv run scripts/search.py "partner_id" --type field --parent "sale.order"`

✅ **User asks**: "Search for task views"
→ **AUTO-USE**: `uv run scripts/search.py "%task%" --type view`

✅ **User asks**: "List all modules"
→ **AUTO-USE**: `uv run scripts/list_modules.py`

✅ **User asks**: "Tell me about the sale module"
→ **AUTO-USE**: `uv run scripts/module_stats.py sale`

---

## Trigger Keywords

**Automatically use this skill when user query contains**:

- **"what is"** + model/field/view name
- **"what fields"** + model name
- **"find"** / **"search"** / **"search for"** + element type
- **"show me"** + element name
- **"where is"** + element name
- **"does...have"** + model + field
- **"list"** + element type
- **"tell me about"** + module name
- **"how does"** + model/method name
- **"get"** / **"display"** + element info

---

## Prerequisites

This skill requires `uv` (Python package manager). Usually auto-installed by `/odoo-setup`.

**Manual install** (if needed):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew (macOS)
brew install uv
```

---

## Configuration

Environment variables (optional - auto-detected by skill):

```bash
export ODOO_PATH="$HOME/letzdoo-sh/odoo/custom/src"  # Auto-detected if not set
export SQLITE_DB_PATH="$HOME/.odoo-indexer/odoo_indexer.sqlite3"  # Default location
```

The skill auto-detects common Odoo locations:
1. `$ODOO_PATH` (if set)
2. `/home/coder/letzdoo-sh/odoo/custom/src`
3. `$HOME/odoo/custom/src`
4. `./odoo/custom/src`

---

## Initial Setup

**Automatic** (via `/odoo-setup` command):
- Index is built automatically during plugin setup
- No manual steps needed

**Manual** (if index not built):
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py --full
```

**Expected output**:
```
Starting full index rebuild...
Scanning modules... Found 156 modules
Indexing: odoo (core) ████████████ 100%
Indexing: sale ████████████ 100%
...
✓ Indexing complete!
Summary:
- Modules: 156
- Models: 1,247
- Fields: 15,832
Database size: 42.3 MB
```

**Indexing time**:
- Small (50 modules): 1-2 minutes
- Medium (100-150 modules): 2-5 minutes
- Large (200+ modules): 5-10 minutes

---

## Core Commands

All commands use `uv run` from the `skills/odoo-indexer/` directory:

### 1. Search for Elements

```bash
# Search models
uv run scripts/search.py "sale.order" --type model

# Search fields in a module
uv run scripts/search.py "partner_id" --type field --module sale

# Search with wildcards (supports SQL LIKE patterns)
uv run scripts/search.py "action_view_%" --type action

# Limit results for performance
uv run scripts/search.py "sale%" --type model --limit 10
```

**Parameters**:
- `query`: Search term (supports `%` wildcards)
- `--type`: Element type (model/field/function/view/action/menu)
- `--module`: Filter by module name
- `--parent`: Filter by parent (e.g., model name for fields)
- `--limit`: Max results (default: 20)
- `--offset`: Pagination offset (default: 0)
- `--json`: Output as JSON

**Performance**: <50ms for exact match, <100ms for wildcard search

---

### 2. Get Element Details

Get complete information about a specific element:

```bash
# Model details (all fields, methods, views, actions)
uv run scripts/get_details.py model "sale.order"

# Field details (type, attributes, usage)
uv run scripts/get_details.py field "partner_id" --parent "sale.order"

# View details (structure, inheritance)
uv run scripts/get_details.py view "sale_order_form_view" --module sale
```

**Returns**:
- Full element definition
- All attributes and properties
- Related elements (views, actions, menus)
- File location and line numbers
- Usage statistics

**Performance**: <30ms

---

### 3. List Modules

```bash
# List all indexed modules
uv run scripts/list_modules.py

# Filter by pattern
uv run scripts/list_modules.py --pattern "sale*"
```

**Returns**:
- Module name
- Number of models, fields, views
- Installation status
- Location

---

### 4. Module Statistics

```bash
# Detailed module info
uv run scripts/module_stats.py sale
```

**Returns**:
- Total elements (models, fields, views, actions, menus)
- Main models with field counts
- Dependencies and dependents
- Installation path
- Index status

---

### 5. Find References

Find all locations where an element is used:

```bash
# Find all references to a model
uv run scripts/find_refs.py model "sale.order"

# Find field references
uv run scripts/find_refs.py field "partner_id" --ref-type definition
```

**Reference types**:
- `definition` - Where element is defined
- `inheritance` - Where element is inherited
- `override` - Where element is overridden
- `reference` - Where element is referenced

---

### 6. Search by Attribute

Advanced search using element attributes:

```bash
# Find all Many2one fields
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one"}'

# Find transient models
uv run scripts/search_by_attr.py model --filters '{"model_type": "transient"}' --module sale

# Find form views
uv run scripts/search_by_attr.py view --filters '{"view_type": "form"}'

# Combine filters
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one", "required": true}' --module sale
```

**Common filters**:
- **Fields**: `field_type`, `required`, `readonly`, `compute`, `store`
- **Models**: `model_type` (model/transient/abstract), `inherit`
- **Views**: `view_type` (form/list/search/kanban/calendar/pivot/graph)

---

### 7. Search XML IDs

```bash
# Search XML IDs with wildcards
uv run scripts/search_xml_id.py "action_view_%"

# Exact XML ID in module
uv run scripts/search_xml_id.py "sale_order_form_view" --module sale
```

**Returns**:
- Full XML ID (with module prefix)
- Element type (action/view/menu/etc)
- Target model (if applicable)
- File location

**Important**: Always use the full XML ID returned (with module prefix) in `ref()` calls.

---

### 8. Update Index

Keep the index up-to-date with code changes:

```bash
# Incremental update (fast - only changed files)
uv run scripts/update_index.py

# Full rebuild (slow - all files)
uv run scripts/update_index.py --full

# Index specific modules
uv run scripts/update_index.py --modules "sale,account,stock"

# Clear and rebuild
uv run scripts/update_index.py --clear --full
```

**When to update**:
- After installing new modules
- After major code changes
- After git pull with many changes
- Weekly (for active development)

**Performance**:
- Incremental: <30 seconds
- Full rebuild: 2-10 minutes (depending on size)

---

### 9. Index Status

Check index health and statistics:

```bash
uv run scripts/index_status.py
```

**Returns**:
- Database size
- Total elements indexed
- Last update timestamp
- Index health metrics
- Stale files (if any)

---

## Performance Metrics

| Operation | Time | vs File Reading |
|-----------|------|-----------------|
| Exact model search | <20ms | **50x faster** |
| Field lookup | <30ms | **30x faster** |
| Wildcard search | <100ms | **20x faster** |
| Module stats | <50ms | **40x faster** |
| Reference search | <150ms | **15x faster** |

**Token efficiency**: 95% fewer tokens than reading files

---

## Usage Tips

### 1. Use Wildcards for Broad Searches

```bash
# Good - specific
uv run scripts/search.py "sale.order" --type model

# Also good - controlled wildcard
uv run scripts/search.py "sale.%" --type model --limit 10

# Avoid - too broad (slow)
uv run scripts/search.py "%" --type model  # Returns thousands of results
```

### 2. Limit Results for Performance

Always use `--limit` for wildcard searches:
```bash
uv run scripts/search.py "%partner%" --type field --limit 20
```

### 3. Combine Filters

Use specific filters to narrow results:
```bash
uv run scripts/search.py "partner_id" --type field --parent "sale.order" --limit 1
```

### 4. Cache Common Queries

For frequently accessed info, mention you're using cached data:
```
I've already looked up sale.order (from indexer cache).
```

### 5. Prefer Exact Searches

Exact searches are much faster:
```bash
# Fast
uv run scripts/get_details.py model "sale.order"

# Slower
uv run scripts/search.py "%sale.order%" --type model
```

---

## Examples

### Example 1: Model Overview

**Query**: "What is sale.order?"

**Command**:
```bash
uv run scripts/get_details.py model "sale.order"
```

**Response format**:
- Model name and description
- Module location
- Inheritance chain
- Key fields (10-15 most important)
- View count
- Action references
- File location

---

### Example 2: Field Search

**Query**: "What fields does res.partner have?"

**Command**:
```bash
uv run scripts/get_details.py model "res.partner"
```

**Response format**:
- Field count
- Categorized fields (contact info, address, relationships)
- Field types and attributes
- Mention of full list availability

---

### Example 3: Advanced Search

**Query**: "Find all Many2one fields pointing to res.partner"

**Command**:
```bash
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one", "comodel_name": "res.partner"}' --limit 50
```

**Response format**:
- Grouped by module/model
- Field names with context
- Total count
- Query time

---

## Troubleshooting

### Index Not Found

**Error**: `Database file not found`

**Solution**:
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py --full
```

Or run `/odoo-setup` to rebuild everything.

---

### Wrong Odoo Path

**Error**: `Odoo directory not found`

**Solution**:
```bash
# Set correct path
export ODOO_PATH="/path/to/your/odoo/custom/src"

# Verify
ls $ODOO_PATH/odoo  # Should show Odoo core files

# Rebuild index
uv run scripts/update_index.py --full
```

---

### Stale Results

**Issue**: Search returns outdated information

**Solution**:
```bash
# Quick update (incremental)
uv run scripts/update_index.py

# Full rebuild if issues persist
uv run scripts/update_index.py --full
```

---

### Slow Queries

**Issue**: Searches taking >1 second

**Causes**:
1. Too broad search pattern (use `--limit`)
2. Database corruption (rebuild with `--full`)
3. Large database (optimize queries)

**Solution**:
```bash
# Add limit
uv run scripts/search.py "%" --type model --limit 10

# Or rebuild index
uv run scripts/update_index.py --clear --full
```

---

### Missing Dependencies

**Error**: `ModuleNotFoundError: lxml`

**Solution**:
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv sync  # Auto-installs from pyproject.toml
```

---

## Integration with Commands

### Used by `/odoo-search`

The `/odoo-search` command is a user-friendly wrapper around this skill:
- Interprets natural language queries
- Translates to appropriate indexer commands
- Formats results for readability

### Used by Agents

**odoo-developer agent**:
- Validates all model/field references
- Researches codebase before implementation
- Checks XML IDs before use

**odoo-verifier agent**:
- Validates module structure
- Checks security groups
- Verifies view references

---

## Best Practices

### 1. Always Validate References

Before using any model/field/XML ID in code:
```bash
# Verify model exists
uv run scripts/search.py "custom.model" --type model

# Verify field exists
uv run scripts/search.py "custom_field" --type field --parent "custom.model"

# Verify XML ID exists
uv run scripts/search_xml_id.py "custom_action" --module custom
```

### 2. Use Exact Names

Always use exact names from indexer (don't guess):
```bash
# Get exact field name
uv run scripts/get_details.py field "partner" --parent "sale.order"
# Returns: partner_id (not "partner")
```

### 3. Check Module Prefix

Always use module prefix from indexer for XML IDs:
```bash
uv run scripts/search_xml_id.py "action_view_task"
# Returns: project.action_view_task
# Use: ref('project.action_view_task')  # Correct
# NOT: ref('action_view_task')  # Wrong
```

### 4. Batch Validations

For multiple elements, batch searches:
```bash
# Instead of multiple calls, use one search
uv run scripts/search.py "partner_id|user_id|team_id" --type field --parent "sale.order"
```

### 5. Keep Index Fresh

Update index regularly:
```bash
# Daily incremental update
uv run scripts/update_index.py

# Weekly full update
uv run scripts/update_index.py --full
```

---

## Critical Rules for Agents

When agents use this skill:

1. **ALWAYS** validate references before code generation
2. **NEVER** assume field names - get exact names from indexer
3. **NEVER** guess XML ID module prefixes - use indexer results
4. Use `get_details.py` for comprehensive info
5. Use `search.py` for finding elements
6. Use `search_by_attr.py` for filtered searches
7. Report query time in responses
8. Indexer is 95% more efficient than reading files

---

## Database Details

**Location**: `~/.odoo-indexer/odoo_indexer.sqlite3` (default)

**Size**: 10-50 MB (varies with codebase size)

**Schema**:
- `modules` - Module metadata
- `models` - Model definitions
- `fields` - Field definitions
- `views` - View definitions
- `actions` - Action definitions
- `menus` - Menu structure
- `xml_ids` - XML ID mappings
- `references` - Cross-references

**Indexed data**:
- Python files (AST parsing)
- XML files (lxml parsing)
- CSV files (security rules)

---

**Remember**: This skill should be your FIRST choice for any Odoo code exploration. It's 95% faster and more accurate than reading files!
