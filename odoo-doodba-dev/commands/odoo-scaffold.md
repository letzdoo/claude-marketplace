---
description: Scaffold a new Odoo module with proper structure
---

# Odoo Scaffold Command

Create a new Odoo module using Doodba's invoke scaffold task.

## What to do

1. **Ask for**:
   - Module name (snake_case, e.g., `custom_sales_report`)
   - Models to extend (if any)
   - Target path (default: `odoo/custom/src/private/`)

2. **Validate with indexer** (use odoo-indexer skill):
   ```bash
   # Check for naming conflicts
   ./scripts/run.sh scripts/search.py "${module_name}.%" --type model --limit 5

   # If extending models, validate they exist
   ./scripts/run.sh scripts/get_details.py model "sale.order"
   # Returns fields to use in views, methods, module for dependencies

   # Get Odoo version for correct template
   cat odoo/custom/src/odoo/odoo/release.py | grep version_info
   ```

3. **Execute scaffold**:
   ```bash
   invoke scaffold --module-name=module_name
   # Or with custom path
   invoke scaffold --module-name=module_name --path=odoo/custom/src/private/
   ```

4. **Customize module** with indexer-assisted development (use odoo-indexer skill):

   **Show available fields**:
   ```bash
   ./scripts/run.sh scripts/search_by_attr.py field \
       --filters '{"parent_name": "sale.order"}' --limit 50
   # Use exact field names in views - prevents errors
   ```

   **Suggest dependencies**:
   ```bash
   # Find which module defines a model
   ./scripts/run.sh scripts/search.py "quality.check" --type model
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

6. **Add to addons.yaml** under `private` section

7. **Optional**: Run `/odoo-doodba-dev:odoo-validate` to catch errors early

8. **Install**: `invoke install --modules=module_name`

## Best Practices

- Use proper naming (snake_case technical, proper display names)
- Validate ALL field names with indexer before using
- Check field types for correct widgets
- Remember: Many2one ends with `_id`, Many2many/One2many end with `_ids`
- Include tests from the start
- Set up basic security (minimum read for base.group_user)
