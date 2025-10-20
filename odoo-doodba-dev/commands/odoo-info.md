---
description: Get information about Odoo modules, models, and structure
---

# Odoo Info Command

Retrieve detailed information about Odoo installation, modules, and structure in the Doodba environment.

## Path Information:
Use **relative paths** when reading files from the project root: `odoo/...`

## What to do:

**IMPORTANT: Use the indexer FIRST for all queries - it's faster and uses fewer tokens!**

1. Ask what information is needed:
   - Module details (version, dependencies, description)
   - Model fields and methods
   - Installed modules
   - Available modules
   - Database structure
   - Doodba configuration

2. **For module info, use INDEXER FIRST:**

   **Get module statistics (instant, no file reading):**
   ```python
   # List all modules
   mcp__plugin_odoo-doodba-dev_odoo-indexer__list_modules()

   # Get detailed stats for specific module
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_module_stats(
       module="sale"
   )
   # Returns: Total models, fields, views, actions, menus, etc.
   # Shows module structure without reading any files!
   ```

   **Only read manifest if user needs specific metadata:**
   - `odoo/custom/src/private/[module]/__manifest__.py`
   - `odoo/custom/src/[repo]/[module]/__manifest__.py`

3. **For model information, use INDEXER (90% of cases):**

   **Get complete model details (all fields, methods, views):**
   ```python
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_item_details(
       item_type="model",
       name="sale.order"
   )
   # Returns:
   # - All fields with types, attributes (required, readonly, etc.)
   # - All methods with signatures
   # - All views (form, tree, search, etc.)
   # - Module location
   # - Inheritance information
   # NO FILE READING - instant results!
   ```

   **List all models in a module:**
   ```python
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query="%",
       item_type="model",
       module="sale",
       limit=50
   )
   ```

   **Find all Many2one fields in a model:**
   ```python
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_by_attribute(
       item_type="field",
       attribute_filters={
           "parent_name": "sale.order",
           "field_type": "Many2one"
       },
       limit=50
   )
   ```

   **Only read Python files if user needs:**
   - Actual implementation code
   - Complex business logic
   - Docstrings and detailed comments

4. **For view/action/menu information, use INDEXER:**

   **Search for views:**
   ```python
   # Find specific view
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_xml_id(
       query="sale_order_form",
       module="sale"
   )

   # Get view details
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_item_details(
       item_type="view",
       name="sale.sale_order_form"
   )
   # Returns: view_type, model, module, file location
   ```

   **Find all form views for a model:**
   ```python
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_by_attribute(
       item_type="view",
       attribute_filters={
           "model": "sale.order",
           "view_type": "form"
       }
   )
   ```

5. **For system info (use RELATIVE PATHS when needed):**
   - Odoo version: Check `odoo/custom/src/odoo/odoo/release.py`
   - Active addons: Read `odoo/custom/src/addons.yaml`
   - Repository config: Read `odoo/custom/src/repos.yaml`

6. **Performance Benefits:**
   - Indexer query: < 1 second, ~50-100 tokens
   - File reading: 10-30 seconds, ~500-2000 tokens
   - **Result: 90-95% faster, 90-95% fewer tokens**

7. Present information clearly and offer related actions

## Useful Locations (RELATIVE PATHS):
- Core Odoo: `odoo/custom/src/odoo/`
- Custom modules: `odoo/custom/src/private/`
- Enterprise: `odoo/custom/src/enterprise/` (if applicable)
- OCA modules: `odoo/custom/src/[repo-name]/`
- Auto-linked: `odoo/auto/addons/`
