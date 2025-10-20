---
name: Odoo Indexer
description: Index and search Odoo codebase elements (models, fields, functions, views, actions, menus). Use when exploring Odoo code structure, searching for models/fields/views, finding references, or analyzing module dependencies. Requires Python with sqlite3.
allowed-tools: Read, Bash, Grep, Glob
---

# Odoo Indexer

Fast indexing and search for Odoo codebase elements including models, fields, functions, views, actions, and more.

## When to use this Skill

Use this Skill when you need to:
- Search for Odoo models, fields, or methods
- Find XML views, actions, or menu items by XML ID
- Explore module structure and dependencies
- Find where a model or field is defined or used
- Analyze Odoo codebase organization

## Available Operations

### 1. Search for Elements

Search the indexed codebase for models, fields, functions, views, etc.

```bash
uv run scripts/search.py "sale.order" --type model --limit 5
uv run scripts/search.py "partner_id" --type field --module sale
uv run scripts/search.py "action_view_%" --type action
```

**Parameters:**
- `query`: Search term (supports SQL LIKE patterns with %)
- `--type`: Filter by type (model/field/function/view/action/menu/etc)
- `--module`: Filter by module name
- `--parent`: Filter by parent name (e.g., model name for fields)
- `--limit`: Maximum results (default: 20)
- `--offset`: Pagination offset (default: 0)

### 2. Get Item Details

Get complete details for a specific element including all references.

```bash
uv run scripts/get_details.py model "sale.order"
uv run scripts/get_details.py field "partner_id" --parent "sale.order"
uv run scripts/get_details.py view "sale_order_form_view" --module sale
```

**Parameters:**
- `item_type`: Type of item (model/field/function/view/etc)
- `name`: Item name
- `--parent`: Parent name (required for fields/methods)
- `--module`: Module name (optional, helps disambiguate)

### 3. List Modules

List all indexed modules with statistics.

```bash
uv run scripts/list_modules.py
uv run scripts/list_modules.py --pattern "sale*"
```

### 4. Get Module Statistics

Get detailed statistics for a specific module.

```bash
uv run scripts/module_stats.py sale
```

### 5. Find References

Find all file locations where an element is referenced.

```bash
uv run scripts/find_refs.py model "sale.order"
uv run scripts/find_refs.py field "partner_id" --ref-type definition
```

**Parameters:**
- `item_type`: Type of item
- `name`: Item name
- `--ref-type`: Filter by reference type (definition/inheritance/override/reference)

### 6. Search by Attribute

Advanced search by element attributes.

```bash
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one"}'
uv run scripts/search_by_attr.py model --filters '{"model_type": "transient"}' --module sale
```

### 7. Search XML IDs

Search for XML IDs (views, actions, menus, etc).

```bash
uv run scripts/search_xml_id.py "action_view_%"
uv run scripts/search_xml_id.py "sale_order_form_view" --module sale
```

### 8. Update Index

Re-index the Odoo codebase (run in background for large codebases).

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

Check indexing status and database statistics.

```bash
uv run scripts/index_status.py
```

## Configuration

The scripts use these environment variables (configured automatically based on plugin settings):

- `ODOO_PATH`: Path to Odoo source code (e.g., `/home/coder/project/odoo/custom/src`)
- `SQLITE_DB_PATH`: Path to SQLite database (e.g., `~/.odoo-indexer/odoo_indexer.sqlite3`)

## Initial Setup

Before using this Skill for the first time, index your codebase:

```bash
uv run scripts/update_index.py --full
```

This may take several minutes for large codebases. Subsequent updates will be faster using incremental indexing.

## Tips

1. **Use patterns**: Search supports SQL LIKE patterns with `%` wildcard
   - `"sale.%"` - Find all models starting with "sale."
   - `"%_id"` - Find all fields ending with "_id"

2. **Incremental updates**: Run `update_index.py` periodically to keep the index fresh

3. **Performance**: Search is very fast (< 100ms) once indexed

4. **Pagination**: Use `--offset` and `--limit` for large result sets

## Examples

### Find all Many2one fields in sale module
```bash
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one"}' --module sale
```

### Find where sale.order is defined
```bash
uv run scripts/search.py "sale.order" --type model --limit 1
```

### Find all form views
```bash
uv run scripts/search_by_attr.py view --filters '{"view_type": "form"}'
```

### Get complete details for sale.order model
```bash
uv run scripts/get_details.py model "sale.order"
```

This returns all fields, methods, views, actions, and rules related to sale.order.
