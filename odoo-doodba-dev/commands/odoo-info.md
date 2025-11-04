---
name: odoo-info
description: Get information about Odoo modules, models, and structure
---

# Odoo Info Command

Get detailed information about Odoo installation, modules, and structure using the indexer.

**IMPORTANT: Always use indexer FIRST - it's 90% faster and uses 95% fewer tokens!**

## What to do

1. Ask what information is needed

2. **For modules** - Use odoo-indexer skill (no file reading):
   ```bash
   # List all modules
   uv run scripts/list_modules.py

   # Get module statistics
   uv run scripts/module_stats.py sale
   # Returns: models, fields, views, actions, menus counts
   ```

3. **For models** - Use odoo-indexer skill (90% of cases):
   ```bash
   # Get complete model details (all fields, methods, views)
   uv run scripts/get_details.py model "sale.order"
   # Returns: All fields with types, methods, views, inheritance

   # List all models in module
   uv run scripts/search.py "%" --type model --module sale --limit 50

   # Find Many2one fields
   uv run scripts/search_by_attr.py field \
       --filters '{"parent_name": "sale.order", "field_type": "Many2one"}'
   ```

4. **For views/actions/menus** - Use odoo-indexer skill:
   ```bash
   # Find view
   uv run scripts/search_xml_id.py "sale_order_form" --module sale

   # Get view details
   uv run scripts/get_details.py view "sale.sale_order_form"

   # Find all form views for model
   uv run scripts/search_by_attr.py view \
       --filters '{"model": "sale.order", "view_type": "form"}'
   ```

5. **For system info** (use relative paths):
   - Odoo version: `odoo/custom/src/odoo/odoo/release.py`
   - Active addons: `odoo/custom/src/addons.yaml`
   - Repositories: `odoo/custom/src/repos.yaml`

6. **Only read Python files when user needs**:
   - Actual implementation code
   - Business logic details
   - Docstrings and comments

## Performance

- Indexer: <1s, ~50-100 tokens
- File reading: 10-30s, ~500-2000 tokens
- **Result: 90-95% faster, 90-95% fewer tokens**

## Useful Locations

- Core Odoo: `odoo/custom/src/odoo/`
- Custom modules: `odoo/custom/src/private/`
- Enterprise: `odoo/custom/src/enterprise/`
- OCA modules: `odoo/custom/src/[repo-name]/`
