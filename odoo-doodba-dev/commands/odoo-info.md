---
description: Get information about Odoo modules, models, and structure
---

# Odoo Info Command

Get detailed information about Odoo installation, modules, and structure using the indexer.

**IMPORTANT: Always use indexer FIRST - it's 90% faster and uses 95% fewer tokens!**

## What to do

1. Ask what information is needed

2. **For modules** - Use indexer (no file reading):
   ```python
   # List all modules
   mcp__plugin_odoo-doodba-dev_odoo-indexer__list_modules()

   # Get module statistics
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_module_stats(module="sale")
   # Returns: models, fields, views, actions, menus counts
   ```

3. **For models** - Use indexer (90% of cases):
   ```python
   # Get complete model details (all fields, methods, views)
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_item_details(
       item_type="model",
       name="sale.order"
   )
   # Returns: All fields with types, methods, views, inheritance

   # List all models in module
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query="%",
       item_type="model",
       module="sale",
       limit=50
   )

   # Find Many2one fields
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_by_attribute(
       item_type="field",
       attribute_filters={
           "parent_name": "sale.order",
           "field_type": "Many2one"
       }
   )
   ```

4. **For views/actions/menus** - Use indexer:
   ```python
   # Find view
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_xml_id(
       query="sale_order_form",
       module="sale"
   )

   # Get view details
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_item_details(
       item_type="view",
       name="sale.sale_order_form"
   )

   # Find all form views for model
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_by_attribute(
       item_type="view",
       attribute_filters={
           "model": "sale.order",
           "view_type": "form"
       }
   )
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
