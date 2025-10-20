---
description: Scaffold a new Odoo module with proper structure
---

# Odoo Scaffold Command

Create a new Odoo module using Doodba's invoke scaffold task.

## What to do:
1. Ask the user for:
   - Module technical name (snake_case, e.g., `custom_sales_report`)
   - Models to extend or reference (if any)
   - Optional: Target path (default: `odoo/custom/src/private/`)

2. **VALIDATE with indexer** (before scaffolding):

   **Check if module name conflicts exist:**
   ```python
   # Search for any models with similar module prefix
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query=f"{module_name}.%",
       item_type="model",
       limit=5
   )
   # If results found, warn user about potential naming conflicts
   ```

   **If user mentions extending models, validate they exist:**
   ```python
   # Example: User wants to extend sale.order
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_item_details(
       item_type="model",
       name="sale.order"
   )
   # Returns: All fields (for suggesting which to use in views)
   #          All methods (for understanding model behavior)
   #          Module location (for adding to dependencies)
   ```

   **Get Odoo version for correct template generation:**
   ```bash
   cat odoo/custom/src/odoo/odoo/release.py | grep -A 3 "version_info"
   ```

3. Execute the invoke scaffold task:
   ```bash
   # Scaffold in default location (odoo/custom/src/private/)
   invoke scaffold --module-name=module_name

   # Scaffold in specific location
   invoke scaffold --module-name=module_name --path=odoo/custom/src/private/
   ```

4. The task will create the basic Odoo module structure:
   ```
   module_name/
   ├── __init__.py
   ├── __manifest__.py
   ├── models/
   │   └── __init__.py
   ├── views/
   ├── security/
   │   └── ir.model.access.csv
   ├── data/
   └── demo/
   ```

5. **Post-scaffold indexer-assisted customization:**

   **If extending a model, show available fields from indexer:**
   ```python
   # Get all fields for the model being extended
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_by_attribute(
       item_type="field",
       attribute_filters={"parent_name": "sale.order"},
       limit=50
   )
   # Present user with available fields to choose from for views
   # This prevents ERROR #1, #3 from ERRORS.md (non-existent fields)
   ```

   **Suggest proper dependencies based on indexer:**
   ```python
   # If user wants to use quality.check
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query="quality.check",
       item_type="model",
       limit=1
   )
   # Returns the module where it's defined → add to __manifest__.py dependencies
   ```

   **When creating views, validate field names:**
   - For EVERY field added to a view, query indexer first
   - Use exact field names from indexer (not assumptions)
   - Check field types to assign correct widgets
   - Remember: Many2one ends with `_id`, Many2many/One2many end with `_ids`

   **Generate version-appropriate XML:**
   - Odoo 18+: Use `<list>` for list views
   - Odoo 17-: Use `<tree>` for list views
   - No inline `<tree>` in `many2many_tags` widgets (ERROR #2 prevention)

6. After scaffolding, customize the module:
   - Update `__manifest__.py` with proper metadata and validated dependencies
   - Add security rules in `security/ir.model.access.csv`
   - Create models in `models/` (with indexer-validated inheritance)
   - Add views in `views/` (with indexer-validated fields)
   - Add tests in `tests/`

7. Add the module to `odoo/custom/src/addons.yaml` under the `private` section
8. **OPTIONAL: Run validation before install:**
   ```bash
   # Use /odoo-doodba-dev:odoo-validate command to catch errors early
   ```
9. Install the module: `invoke install --modules=module_name`
10. Explain next steps to the user

## Best Practices:
- Use proper Odoo naming conventions (snake_case for technical, proper capitalization for display)
- Include comprehensive docstrings
- Set up basic security (at minimum, read access for base.group_user)
- Create a proper __manifest__.py with all required fields
- Write tests from the start (TDD)

## Invoke Task Options:
- `--module-name`: Name of the module to scaffold (required)
- `--path`: Path where to create the module (optional, defaults to current directory)
