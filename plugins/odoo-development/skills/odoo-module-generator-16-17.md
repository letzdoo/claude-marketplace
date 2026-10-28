# Odoo Module Migration Guide: 16.0 → 17.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: Odoo 16.0 → 17.0                                           ║
║  This document covers ONLY changes between these specific versions.          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Component | v16 Status | v17 Status | Action Required |
|-----------|------------|------------|-----------------|
| `attrs` attribute | The record-dependent modifier syntax | **REMOVED** | Must migrate |
| `states` attribute | Supported shorthand | **REMOVED** | Must migrate |
| `@api.model_create_multi` | single-dict create logs a WARNING | same WARNING | Should add |
| Direct `invisible`/`readonly` expressions on fields | **Not supported** (only constants / `context.get(...)`) | Required | Use exclusively in 17 |
| OWL | 2.x, `patch(obj, name, ext)` | 2.x, `patch(obj, ext)` | Update patch calls |

## CRITICAL: attrs Removal

### Before (v16 - correct 16.0 syntax)
```xml
<button name="action_confirm"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>

<field name="partner_id"
       attrs="{'readonly': [('state', '!=', 'draft')],
               'required': [('type', '=', 'invoice')]}"/>
```

### After (v17 - Required)
```xml
<button name="action_confirm"
        invisible="state != 'draft'"/>

<field name="partner_id"
       readonly="state != 'draft'"
       required="type == 'invoice'"/>
```

### Migration Pattern

| v16 `attrs` Pattern | v17 Replacement |
|---------------------|-----------------|
| `[('field', '=', value)]` | `field == value` |
| `[('field', '!=', value)]` | `field != value` |
| `[('field', 'in', [a, b])]` | `field in [a, b]` or `field in (a, b)` |
| `[('field', 'not in', [a, b])]` | `field not in [a, b]` |
| `[('field', '=', True)]` | `field` |
| `[('field', '=', False)]` | `not field` |
| Multiple conditions (AND) | `cond1 and cond2` |
| Multiple conditions (OR) | `cond1 or cond2` |

### Complex Example

```xml
<!-- v16 -->
<field name="amount"
       attrs="{'invisible': [('state', '=', 'draft'), ('amount', '=', 0)],
               'readonly': ['|', ('state', '!=', 'draft'), ('locked', '=', True)]}"/>

<!-- v17 -->
<field name="amount"
       invisible="state == 'draft' and amount == 0"
       readonly="state != 'draft' or locked"/>
```

## CRITICAL: states Removal

### Before (v16)
```xml
<field name="partner_id" states="draft,sent"/>
```

### After (v17 - Required)
```xml
<field name="partner_id" invisible="state not in ('draft', 'sent')"/>
```

## Recommended: @api.model_create_multi

### Before (v16 - works, logs "not overriding the create method in batch"; same in 17.0)
```python
@api.model
def create(self, vals):
    if not vals.get('name'):
        vals['name'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals)
```

### After (v16 and v17 - recommended)
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)
```

## Manifest Version Update

```python
# v16
'version': '16.0.1.0.0',

# v17
'version': '17.0.1.0.0',
```

## Python Changes

### Minimum Python Version
- v16: Python 3.7+ (up to 3.12)
- v17: Python 3.10+

### Type Hints (Recommended)
```python
# v17 encourages type hints
def process_data(self, partner_id: int, options: dict = None) -> bool:
    options = options or {}
    return True
```

## OWL 2.x Updates

### patch() signature changes
OWL remains at 2.x, but Odoo's `patch` helper changes: 16.0 `patch(obj, "my_module.Name", { m() { this._super(...arguments); } })` becomes 17.0 `patch(obj, { m() { super.m(...arguments); } })`.

### Component Registration
```javascript
// Unchanged in v17
registry.category("actions").add("my_module.component", MyComponent);
```

## Official guideline deltas 16.0 -> 17.0

Only module-generation rules of the official Odoo guidelines (odoo/odoo `skills/`, verified per version) whose 16.0 and 17.0 forms differ:

| Topic | 16.0 | 17.0 |
|---|---|---|
| `<asset>` XML tag | absent - only the manifest `assets` key | exists (manifest `assets` still the normal way) |
| Generated SQL helpers | params / `psycopg2.sql` | `odoo.tools.SQL` |

View modifiers, JS `patch()` and Python version: see Breaking Changes Summary, OWL 2.x Updates and Python Changes.

Unchanged (16.0 = 17.0): no `base` injection for empty `depends` (declare `['base']`), `license` defaults to `LGPL-3` with a warning, `auto_install` list must be a subset of `depends`, `security/ir.model.access.csv` (no `ir.access`), default test tags `standard`+`at_install` (post-install = `@tagged('post_install', '-at_install')`), `BaseCommon`/`BaseUsersCommon`, imported test classes and inherited `test_*` methods are collected, `--test-tags /module:Class`.

## Migration Checklist

### Views (XML)
- [ ] Replace all `attrs="{'invisible': ...}"` with `invisible="..."`
- [ ] Replace all `attrs="{'readonly': ...}"` with `readonly="..."`
- [ ] Replace all `attrs="{'required': ...}"` with `required="..."`
- [ ] Replace all `states="..."` with `invisible="state not in (...)"`
- [ ] Convert domain syntax to Python expression syntax

### Models (Python)
- [ ] Add `@api.model_create_multi` to all `create()` methods (removes the batch warning)
- [ ] Convert JS `patch()` calls to the 17.0 signature
- [ ] Update `create(vals)` to `create(vals_list)` signature
- [ ] Update Python version compatibility to 3.10+
- [ ] Add type hints where appropriate

### Manifest
- [ ] Update version from `16.0.x.x.x` to `17.0.x.x.x`
- [ ] Verify all dependencies are v17 compatible

### Testing
- [ ] Run all tests with v17
- [ ] Test all form views for visibility rules
- [ ] Test all buttons for state-based visibility
- [ ] Verify computed field readonly behavior

## Common Migration Errors

### Error: attrs not supported
```
Error: attrs="..." is no longer supported in Odoo 17
```
**Solution**: Convert to direct Python expression syntax.

### Warning: create() not batched
```
The model ... is not overriding the create method in batch
```
**Solution**: Use `@api.model_create_multi def create(self, vals_list)` (logged in 16.0 and 17.0).

### Error: Invalid expression syntax
```
Error: Invalid expression: field = value
```
**Solution**: Use `==` for comparison, not `=`.

## Automated Migration Script

```python
#!/usr/bin/env python3
"""
Basic migration helper for attrs to direct expressions.
Run manually and verify results!
"""
import re
import sys

def convert_domain_to_expr(domain_str):
    """Convert domain list to Python expression."""
    # This is a simplified converter - verify results manually
    domain_str = domain_str.strip()
    if domain_str.startswith('[') and domain_str.endswith(']'):
        domain_str = domain_str[1:-1]

    # Handle simple cases
    patterns = [
        (r"\('(\w+)',\s*'=',\s*'([^']+)'\)", r"\1 == '\2'"),
        (r"\('(\w+)',\s*'=',\s*(\d+)\)", r"\1 == \2"),
        (r"\('(\w+)',\s*'=',\s*True\)", r"\1"),
        (r"\('(\w+)',\s*'=',\s*False\)", r"not \1"),
        (r"\('(\w+)',\s*'!=',\s*'([^']+)'\)", r"\1 != '\2'"),
    ]

    for pattern, replacement in patterns:
        domain_str = re.sub(pattern, replacement, domain_str)

    return domain_str

if __name__ == '__main__':
    print("Manual verification required for all conversions!")
```

## GitHub Reference

For official migration notes, consult:
- https://github.com/odoo/odoo/tree/17.0
- Odoo 17.0 release notes
- Community upgrade scripts

---

**IMPORTANT**: Always test thoroughly after migration. The automated patterns cover common cases but complex domains may require manual adjustment.
