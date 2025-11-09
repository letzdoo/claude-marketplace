---
description: Scaffold a new Odoo module with proper structure. AUTO-USE when user says "create a module", "new addon", "scaffold", "generate module". Creates module using Doodba's invoke scaffold with proper __manifest__.py, models/, views/, security/ structure. Always validates module name availability with indexer first.
---

# Odoo Scaffold Command

Create a new Odoo module using Doodba's invoke scaffold task.

## What to do

1. **Ask for**:
   - Module name (snake_case, e.g., `custom_sales_report`)
   - Models to extend (if any)
   - Target path (default: `odoo/custom/src/odoo-sh/`)

2. **Validate with indexer** (use odoo-indexer skill):
   ```bash
   # Check for naming conflicts
   uv run scripts/search.py "${module_name}.%" --type model --limit 5

   # If extending models, validate they exist
   uv run scripts/get_details.py model "sale.order"
   # Returns fields to use in views, methods, module for dependencies

   # Get Odoo version for correct template
   cat odoo/custom/src/odoo/odoo/release.py | grep version_info
   ```

3. **Execute scaffold** (ALWAYS in odoo-sh directory):
   ```bash
   # ALWAYS create modules in odoo-sh directory
   invoke scaffold --module-name=module_name --path=odoo/custom/src/odoo-sh/
   ```

   **⚠️ CRITICAL: Never create modules in odoo/custom/src/private/ to avoid duplicate module issues!**

4. **Customize module** with indexer-assisted development (use odoo-indexer skill):

   **Show available fields**:
   ```bash
   uv run scripts/search_by_attr.py field \
       --filters '{"parent_name": "sale.order"}' --limit 50
   # Use exact field names in views - prevents errors
   ```

   **Suggest dependencies**:
   ```bash
   # Find which module defines a model
   uv run scripts/search.py "quality.check" --type model
   # Add returned module to __manifest__.py dependencies
   ```

   **Generate version-appropriate XML**:
   - Odoo 18+: Use `<list>` for list views
   - Odoo 17-: Use `<tree>` for list views
   - No inline tree in `many2many_tags` widgets

5. **Complete setup**:
   - Update `__manifest__.py` with validated dependencies
   - Add security rules
   - Create models with validated inheritance
   - Add views with validated fields
   - Add tests

6. **Add to addons.yaml** under `odoo-sh` section (NOT private!)
   ```yaml
   odoo-sh:
     - module_name
   ```

7. **Validation**: Validation and testing are now automatic when using `/odoo-doodba-dev:odoo-dev` for further development

8. **Install**: `invoke install --modules=module_name`

## Best Practices

- Use proper naming (snake_case technical, proper display names)
- Validate ALL field names with indexer before using
- Check field types for correct widgets
- Remember: Many2one ends with `_id`, Many2many/One2many end with `_ids`
- Include tests from the start
- Set up basic security (minimum read for base.group_user)
