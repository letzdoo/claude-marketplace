---
description: Scaffold a new Odoo module with proper structure
---

# Odoo Scaffold Command

Create a new Odoo module using Doodba's invoke scaffold task.

## What to do:
1. Ask the user for:
   - Module technical name (snake_case, e.g., `custom_sales_report`)
   - Optional: Target path (default: `odoo/custom/src/private/`)

2. Execute the invoke scaffold task:
   ```bash
   # Scaffold in default location (odoo/custom/src/private/)
   invoke scaffold --module-name=module_name

   # Scaffold in specific location
   invoke scaffold --module-name=module_name --path=odoo/custom/src/private/
   ```

3. The task will create the basic Odoo module structure:
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

4. After scaffolding, customize the module:
   - Update `__manifest__.py` with proper metadata
   - Add security rules in `security/ir.model.access.csv`
   - Create models in `models/`
   - Add views in `views/`
   - Add tests in `tests/`

5. Add the module to `odoo/custom/src/addons.yaml` under the `private` section
6. Install the module: `invoke install --modules=module_name`
7. Explain next steps to the user

## Best Practices:
- Use proper Odoo naming conventions (snake_case for technical, proper capitalization for display)
- Include comprehensive docstrings
- Set up basic security (at minimum, read access for base.group_user)
- Create a proper __manifest__.py with all required fields
- Write tests from the start (TDD)

## Invoke Task Options:
- `--module-name`: Name of the module to scaffold (required)
- `--path`: Path where to create the module (optional, defaults to current directory)
