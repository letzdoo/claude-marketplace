---
name: Odoo Indexer
description: Index and search Odoo codebase elements (models, fields, functions, views, actions, menus). Use when exploring Odoo code structure, searching for models/fields/views, finding references, or analyzing module dependencies.
allowed-tools: Read, Bash, Grep, Glob
---

# Odoo Indexer

Fast indexing and search for Odoo codebase elements including models, fields, functions, views, actions, and more.

## Prerequisites

This skill requires `uv` (Python package manager). Install it if not already available:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew (macOS)
brew install uv
```

## Configuration

Set environment variables before using:

```bash
export ODOO_PATH="/path/to/odoo/custom/src"
export SQLITE_DB_PATH="$HOME/.odoo-indexer/odoo_indexer.sqlite3"  # Optional
```

Or let the skill auto-detect common Odoo locations.

## Initial Setup

Build the index before first use:

```bash
cd /home/coder/marketplace/odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py --full
```

This will:
1. Auto-install dependencies (lxml, aiosqlite, uvloop)
2. Scan the Odoo codebase
3. Create the searchable index

Indexing large codebases may take a few minutes. Subsequent updates are faster with incremental indexing.

## Usage

All commands use `uv run` to execute scripts directly:

### 1. Search for Elements

```bash
# Search models
uv run scripts/search.py "sale.order" --type model

# Search fields in a module
uv run scripts/search.py "partner_id" --type field --module sale

# Search actions (supports SQL LIKE patterns with %)
uv run scripts/search.py "action_view_%" --type action

# Limit results and use pagination
uv run scripts/search.py "sale%" --type model --limit 5 --offset 10
```

**Parameters:**
- `query`: Search term (supports SQL LIKE patterns with `%`)
- `--type`: Filter by type (model/field/function/view/action/menu/etc)
- `--module`: Filter by module name
- `--parent`: Filter by parent name (e.g., model name for fields)
- `--limit`: Maximum results (default: 20)
- `--offset`: Pagination offset (default: 0)
- `--json`: Output as JSON

### 2. Get Item Details

Get complete details for a specific element including all references:

```bash
# Get model details
uv run scripts/get_details.py model "sale.order"

# Get field details (requires parent)
uv run scripts/get_details.py field "partner_id" --parent "sale.order"

# Get view details
uv run scripts/get_details.py view "sale_order_form_view" --module sale
```

### 3. List Modules

```bash
# List all indexed modules
uv run scripts/list_modules.py

# Filter by pattern
uv run scripts/list_modules.py --pattern "sale*"
```

### 4. Get Module Statistics

```bash
uv run scripts/module_stats.py sale
```

### 5. Find References

Find all file locations where an element is referenced:

```bash
# Find all references to a model
uv run scripts/find_refs.py model "sale.order"

# Filter by reference type
uv run scripts/find_refs.py field "partner_id" --ref-type definition
```

**Reference types:** `definition`, `inheritance`, `override`, `reference`

### 6. Search by Attribute

Advanced search by element attributes:

```bash
# Find all Many2one fields
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one"}'

# Find transient models in a module
uv run scripts/search_by_attr.py model --filters '{"model_type": "transient"}' --module sale

# Find all form views
uv run scripts/search_by_attr.py view --filters '{"view_type": "form"}'
```

### 7. Search XML IDs

```bash
# Search for XML IDs
uv run scripts/search_xml_id.py "action_view_%"

# In specific module
uv run scripts/search_xml_id.py "sale_order_form_view" --module sale
```

### 8. Update Index

Re-index the codebase:

```bash
# Incremental update (skip unchanged files)
uv run scripts/update_index.py

# Full re-index
uv run scripts/update_index.py --full

# Index specific modules
uv run scripts/update_index.py --modules "sale,account,stock"

# Clear and re-index
uv run scripts/update_index.py --clear --full
```

### 9. Index Status

Check indexing status and database statistics:

```bash
uv run scripts/index_status.py
```

## Tips

1. **Pattern matching**: Use `%` as wildcard
   - `"sale.%"` - All models starting with "sale."
   - `"%_id"` - All fields ending with "_id"

2. **Incremental updates**: Run `update_index.py` periodically to keep the index fresh

3. **Performance**: Search is very fast (< 100ms) once indexed

4. **Pagination**: Use `--offset` and `--limit` for large result sets

5. **JSON output**: Add `--json` flag for machine-readable output

## Examples

### Find all Many2one fields in sale module
```bash
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one"}' --module sale
```

### Find where sale.order is defined
```bash
uv run scripts/search.py "sale.order" --type model --limit 1
```

### Get complete details for sale.order model
```bash
uv run scripts/get_details.py model "sale.order"
```

Returns all fields, methods, views, actions, and rules related to sale.order.

## Troubleshooting

### uv not found
Install uv as shown in Prerequisites section.

### No index found
Run initial indexing:
```bash
uv run scripts/update_index.py --full
```

### Wrong Odoo path
Set the correct path:
```bash
export ODOO_PATH="/path/to/your/odoo/custom/src"
uv run scripts/update_index.py --full
```

### Dependencies missing
`uv` automatically installs dependencies from `pyproject.toml`. If issues persist:
```bash
uv sync
```
