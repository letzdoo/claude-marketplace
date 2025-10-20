---
description: Validate Odoo module before installation using indexer
---

# Odoo Validate Command

Pre-installation validation using the Odoo indexer to catch errors early and prevent the issues documented in ERRORS.md.

## Purpose

This command validates all references in a module (models, fields, XML IDs, view inheritance) BEFORE attempting installation, saving time and preventing deployment failures.

## What to do:

1. Ask for the module name or path to validate

2. **Step 1: Locate Module Files**
   ```bash
   # Find module directory
   find odoo/custom/src -type d -name "module_name" | head -1
   ```

3. **Step 2: Parse and Validate __manifest__.py**
   ```python
   # Read manifest to get dependencies
   # Check all dependency modules exist using indexer
   mcp__plugin_odoo-doodba-dev_odoo-indexer__list_modules()

   # For each dependency, verify it exists in the list
   # Warn if dependency not found
   ```

4. **Step 3: Validate Python Model Files**

   For each `.py` file in `models/`:

   **Check Model Inheritance:**
   ```python
   # Find lines with _inherit = 'model.name'
   # For each inherited model, validate it exists
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query="model.name",
       item_type="model",
       limit=1
   )
   # If not found: ERROR - Model doesn't exist
   ```

   **Check Field Definitions:**
   - Parse field definitions (Many2one, Many2many, One2many)
   - Validate comodel_name exists for relational fields
   - Check field naming conventions (Many2one ends with _id)

5. **Step 4: Validate XML View Files** ⚠️ CRITICAL

   For each `.xml` file in `views/` and `data/`:

   **A. Validate Field References in Views:**
   ```python
   # For EVERY <field name="X"/> found in views
   # Extract model name from view's model attribute or inherit_id
   # Then validate:
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query="field_name",
       item_type="field",
       parent_name="model.name",
       limit=1
   )

   # If no results:
   # ERROR: Field 'field_name' not found in model 'model.name'
   # Location: views/some_view.xml:line_number
   # This prevents ERROR #1, #3 from ERRORS.md
   ```

   **B. Validate XML ID References:**
   ```python
   # For EVERY ref="module.xml_id" or inherit_id="module.xml_id"
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_xml_id(
       query="xml_id",
       limit=5
   )

   # If no results:
   # ERROR: XML ID 'module.xml_id' not found
   # Suggestion: Search without module prefix to find correct one
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_xml_id(
       query="xml_id"  # without module prefix
   )
   # If found with different prefix:
   # SUGGESTION: Use 'correct_module.xml_id' instead
   # This prevents ERROR #5, #7 from ERRORS.md
   ```

   **C. Validate View Inheritance:**
   ```python
   # For EVERY <record inherit_id="parent_view">
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_item_details(
       item_type="view",
       name="parent_view_xml_id"
   )

   # If not found:
   # ERROR: Parent view 'parent_view_xml_id' not found
   # Cannot inherit from non-existent view
   ```

   **D. Check XPath Elements for Version Compatibility:**
   ```bash
   # Detect Odoo version
   cat odoo/custom/src/odoo/odoo/release.py | grep "version_info"

   # If Odoo 18+:
   # - Check for XPath with //tree → WARN: Should use //list in Odoo 18
   # - Check for <tree> in view definitions → WARN: Should use <list> in Odoo 18
   # This prevents ERROR #4 from ERRORS.md
   ```

   **E. Validate Widget Usage:**
   ```xml
   # Check for problematic patterns:
   # - many2many_tags widget with inline <tree> or <list>
   #   ERROR: many2many_tags doesn't support inline views
   #   This prevents ERROR #2 from ERRORS.md
   ```

6. **Step 5: Validate Data Files**

   For each `.xml` file in `data/`:

   ```python
   # For EVERY <field ref="module.xml_id"/>
   # Validate the XML ID exists (same as Step 4.B)

   # For EVERY <field name="model_id" ref="ir.model_model_name"/>
   # Validate the model exists
   ```

7. **Step 6: Check Security Files**

   ```bash
   # Parse security/ir.model.access.csv
   # For each model_id column, validate model exists
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query="model.name",
       item_type="model"
   )
   ```

8. **Generate Validation Report:**

   ```
   ═══════════════════════════════════════════════════════
   ODOO MODULE VALIDATION REPORT
   Module: quality_project_task
   ═══════════════════════════════════════════════════════

   ✅ MANIFEST
      Dependencies: 3 modules validated
      - project ✓
      - quality_control ✓
      - hr_timesheet ✓

   ✅ MODELS
      Files checked: 2
      Inheritance: 3 models validated
      - project.task ✓
      - project.task.type ✓
      - account.analytic.line ✓

   ❌ VIEWS (2 ERRORS FOUND)
      Files checked: 2
      Fields validated: 45/47

      ERROR #1: Field not found
      ├─ Field: 'title'
      ├─ Model: 'quality.point'
      ├─ Location: views/project_task_type_views.xml:15
      └─ Fix: Remove field or use 'name' instead

      ERROR #2: Field not found
      ├─ Field: 'test_type'
      ├─ Model: 'quality.point'
      ├─ Location: views/project_task_type_views.xml:16
      └─ Fix: Use 'test_type_id' instead (Many2one fields end with _id)

   ⚠️  XML IDS (1 WARNING)
      References checked: 8/9

      WARNING: XML ID module prefix mismatch
      ├─ Used: 'quality.test_type_passfail'
      ├─ Location: data/quality_point_data.xml:10
      └─ Suggestion: Use 'quality_control.test_type_passfail' instead

   ⚠️  VERSION COMPATIBILITY (1 WARNING)
      Odoo Version: 18.0

      WARNING: Using deprecated element
      ├─ Found: XPath expr="//tree"
      ├─ Location: views/project_task_views.xml:61
      └─ Fix: Use "//list" for Odoo 18+

   ✅ SECURITY
      Access rules: 3 models validated

   ═══════════════════════════════════════════════════════
   SUMMARY
   ═══════════════════════════════════════════════════════
   Total Errors: 2 (MUST FIX before installation)
   Total Warnings: 2 (Recommended to fix)

   ❌ MODULE NOT READY FOR INSTALLATION

   Fix the 2 errors above, then run validation again.
   ═══════════════════════════════════════════════════════
   ```

9. **Offer Auto-Fix (Optional)**

   For simple errors, offer to fix automatically:
   - Wrong field names (if indexer suggests correct one)
   - XML ID module prefix (if indexer found correct one)
   - Version compatibility (//tree → //list)

10. **Next Steps**
    - If validation passes: Suggest running `invoke install --modules=module_name`
    - If errors found: Provide specific fixes for each error
    - Suggest re-running validation after fixes

## Error Prevention Mapping

This command prevents ALL errors from ERRORS.md:

- **ERROR #1**: Non-existent field 'title' → Step 4.A catches this
- **ERROR #2**: many2many_tags with inline tree → Step 4.E catches this
- **ERROR #3**: Wrong field name (test_type vs test_type_id) → Step 4.A catches this
- **ERROR #4**: Odoo 18 XPath compatibility → Step 4.D catches this
- **ERROR #5**: Wrong XML ID module prefix → Step 4.B catches this
- **ERROR #7**: Test file XML ID errors → Step 5 catches this

## Performance

- Uses indexer exclusively (no file reading for validation)
- Validation time: 5-10 seconds for typical module
- Token usage: ~500-1000 tokens (vs 5000-10000 reading files)

## Best Practices

- Run validation BEFORE every installation attempt
- Fix all errors before proceeding
- Pay attention to warnings (they often indicate future problems)
- Use auto-fix for simple issues, manual fix for complex ones

## Usage Examples

```bash
# Validate a module in private/
/odoo-doodba-dev:odoo-validate quality_project_task

# Validate a module in a specific repo
/odoo-doodba-dev:odoo-validate custom_sales_report

# Auto-fix simple errors
/odoo-doodba-dev:odoo-validate quality_project_task --auto-fix
```
