---
description: Validate Odoo module before installation using indexer
---

# Odoo Validate Command

Pre-installation validation using indexer to catch errors early.

## Purpose

Validate all references (models, fields, XML IDs, views) BEFORE installation to prevent deployment failures.

## Process

1. **Ask for module name** or path

2. **Locate module**:
   ```bash
   find odoo/custom/src -type d -name "module_name" | head -1
   ```

3. **Validate manifest** - Check dependencies exist:
   ```python
   mcp__plugin_odoo-doodba-dev_odoo-indexer__list_modules()
   ```

4. **Validate models** - Check inheritance:
   ```python
   # For each _inherit = 'model.name'
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query="model.name",
       item_type="model",
       limit=1
   )
   # Validate comodels for relational fields
   ```

5. **Validate views** (CRITICAL):

   **A. Check fields exist**:
   ```python
   # For EVERY <field name="X"/> in views
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
       query="field_name",
       item_type="field",
       parent_name="model.name",
       limit=1
   )
   ```

   **B. Check XML ID references**:
   ```python
   # For EVERY ref="module.xml_id"
   mcp__plugin_odoo-doodba-dev_odoo-indexer__search_xml_id(
       query="xml_id",
       limit=5
   )
   # If not found, search without module prefix to find correct one
   ```

   **C. Check view inheritance**:
   ```python
   mcp__plugin_odoo-doodba-dev_odoo-indexer__get_item_details(
       item_type="view",
       name="parent_view_xml_id"
   )
   ```

   **D. Check version compatibility**:
   ```bash
   cat odoo/custom/src/odoo/odoo/release.py | grep "version_info"
   # Warn if Odoo 18+ using //tree instead of //list
   ```

   **E. Check widget usage**:
   - Warn if `many2many_tags` has inline `<tree>` or `<list>`

6. **Validate data files** - Same as views, check all XML ID refs

7. **Check security** - Validate models and groups in CSV

8. **Generate report**:
   ```
   ═══════════════════════════════════════════════════
   ODOO MODULE VALIDATION
   Module: {module_name}
   ═══════════════════════════════════════════════════

   ✅ MANIFEST: 3 dependencies validated
   ✅ MODELS: 3 inheritance targets validated
   ❌ VIEWS: 2 errors found

      ERROR #1: Field not found
      ├─ Field: 'title'
      ├─ Model: 'quality.point'
      ├─ Location: views/task_type_views.xml:15
      └─ Fix: Use 'name' instead

      ERROR #2: Wrong field name
      ├─ Field: 'test_type'
      ├─ Model: 'quality.point'
      ├─ Location: views/task_type_views.xml:16
      └─ Fix: Use 'test_type_id' (Many2one ends with _id)

   ⚠️  XML IDS: 1 warning

      WARNING: Wrong module prefix
      ├─ Used: 'quality.test_type_passfail'
      ├─ Location: data/quality_point_data.xml:10
      └─ Fix: Use 'quality_control.test_type_passfail'

   ⚠️  VERSION: 1 warning

      WARNING: Deprecated XPath
      ├─ Found: //tree
      ├─ Location: views/task_views.xml:61
      └─ Fix: Use //list for Odoo 18+

   ═══════════════════════════════════════════════════
   SUMMARY: 2 errors, 2 warnings
   ❌ MODULE NOT READY FOR INSTALLATION
   ═══════════════════════════════════════════════════
   ```

9. **Offer auto-fix** for simple errors (field names, XML IDs, XPath)

10. **Next steps**:
    - If passed: `invoke install --modules=module_name`
    - If failed: Fix errors and re-validate

## Performance

- Uses indexer only (no file reading)
- Validation time: 5-10 seconds
- Token usage: ~500-1000 tokens

## Usage

```bash
/odoo-doodba-dev:odoo-validate module_name
/odoo-doodba-dev:odoo-validate module_name --auto-fix
```
