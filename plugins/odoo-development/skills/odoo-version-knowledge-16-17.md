# Odoo Version Knowledge: 16 to 17 Migration

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  VERSION MIGRATION: 16.0 → 17.0                                              ║
║  Critical changes, breaking changes, and migration patterns                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Category | Change | Impact |
|----------|--------|--------|
| Views | `attrs=` / `states=` (the 16.0 syntax; `invisible="expr"` on record fields does not work in 16.0) replaced by Python expressions; `attrs`/`states` no longer supported | **CRITICAL** - Must migrate |
| ORM | single-dict `create` still works in 17.0 but logs a WARNING (same as 16.0) | Medium - use `@api.model_create_multi` |
| SQL | `odoo.tools.SQL` builder introduced, `SQL.identifier` (16.0: none, `odoo.tools.SQL` = `psycopg2.sql.SQL`; `psycopg2.sql.Identifier`) | Medium - rewrite string SQL helpers |
| JS | `patch(obj, ext)` + `super` (16.0: `patch(obj, name, ext)` + `this._super`) | High - every patch call changes |
| Domain | New domain expression syntax | Medium - Learn new operators |
| Security | Enhanced record rule validation | Medium - Review rules |
| JS | ES6 modules fully enforced | Medium - Update imports |

## CRITICAL: attrs Attribute Removal

**This is the most significant breaking change in v17**

### Before (v16)
```xml
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'readonly': [('state', '!=', 'draft')],
               'required': [('type', '=', 'customer')]}"/>

<group attrs="{'invisible': [('show_details', '=', False)]}">
    <field name="detail_field"/>
</group>

<button name="action_confirm"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

### After (v17)
```xml
<field name="partner_id"
       invisible="state == 'draft'"
       readonly="state != 'draft'"
       required="type == 'customer'"/>

<group invisible="not show_details">
    <field name="detail_field"/>
</group>

<button name="action_confirm"
        invisible="state != 'draft'"/>
```

### Expression Syntax Reference

| attrs Domain | v17 Expression |
|--------------|----------------|
| `[('field', '=', value)]` | `field == value` |
| `[('field', '!=', value)]` | `field != value` |
| `[('field', '>', value)]` | `field > value` |
| `[('field', 'in', [a,b])]` | `field in [a, b]` |
| `[('field', '=', True)]` | `field` or `field == True` |
| `[('field', '=', False)]` | `not field` or `field == False` |
| `['&', A, B]` | `A and B` |
| `['|', A, B]` | `A or B` |
| `['!', A]` | `not A` |

### Complex Expression Examples

```xml
<!-- Multiple conditions with AND -->
<!-- Old: attrs="{'invisible': [('state', '=', 'draft'), ('type', '=', 'internal')]}" -->
<field name="x" invisible="state == 'draft' and type == 'internal'"/>

<!-- Multiple conditions with OR -->
<!-- Old: attrs="{'invisible': ['|', ('state', '=', 'done'), ('state', '=', 'cancel')]}" -->
<field name="x" invisible="state == 'done' or state == 'cancel'"/>

<!-- Nested conditions -->
<!-- Old: attrs="{'invisible': ['|', ('state', '=', 'draft'), '&', ('type', '=', 'service'), ('qty', '=', 0)]}" -->
<field name="x" invisible="state == 'draft' or (type == 'service' and qty == 0)"/>
```

## Create Method Migration

### Before (v16) - works, but logs "not overriding the create method in batch"
```python
@api.model
def create(self, vals):
    if 'name' not in vals:
        vals['name'] = 'Default'
    return super().create(vals)
```

### After (v17) - recommended (the single-dict form still only warns in 17.0)
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if 'name' not in vals:
            vals['name'] = 'Default'
    return super().create(vals_list)
```

### Migration Script
```python
# Replace single create with multi-create
# Old signature: def create(self, vals):
# New signature: def create(self, vals_list):

import re

def migrate_create_method(content):
    # Find @api.model followed by def create(self, vals):
    pattern = r'@api\.model\n(\s+)def create\(self, vals\):'
    replacement = r'@api.model_create_multi\n\1def create(self, vals_list):'

    content = re.sub(pattern, replacement, content)

    # Note: Manual review needed to convert vals → vals_list usage
    return content
```

## Tree View Column Visibility

### New: column_invisible Attribute
```xml
<tree>
    <field name="name"/>
    <field name="internal_code" column_invisible="True"/>
    <field name="partner_id"/>
    <!-- column_invisible hides from tree but field still accessible -->
</tree>
```

### Dynamic Column Visibility
```xml
<tree>
    <field name="name"/>
    <field name="cost" column_invisible="not context.get('show_cost')"/>
</tree>
```

## Domain Expression Improvements

### Parent Field Access
```xml
<!-- Access parent record in embedded views -->
<field name="quantity" invisible="parent.state == 'done'"/>
```

### Context in Expressions
```xml
<field name="price" invisible="context.get('hide_price')"/>
```

## Enhanced Record Rules

### Stricter Validation
```xml
<!-- v17 validates domain expressions more strictly -->
<record id="rule_my_model" model="ir.rule">
    <field name="name">My Model Access</field>
    <field name="model_id" ref="model_my_model"/>
    <!-- Must use valid field references -->
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

## ORM Improvements

### Better Prefetching
```python
# v17 has improved automatic prefetching
records = self.search([])
# Accessing related fields triggers smarter batch loading
for record in records:
    print(record.partner_id.name)  # Better optimized in v17
```

### Explicit Prefetch Control
```python
# Force prefetch specific fields
records = self.with_prefetch(('partner_id', 'line_ids'))
```

## JavaScript Module Updates

### Strict ES6 Enforcement
```javascript
/** @odoo-module **/

// v17 requires proper ES6 imports
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class MyComponent extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ loading: false });
    }
}
```

## GitHub Verification URLs

```
# View validation (attrs removed)
https://raw.githubusercontent.com/odoo/odoo/17.0/odoo/tools/view_validation.py

# Create method changes
https://raw.githubusercontent.com/odoo/odoo/17.0/addons/sale/models/sale_order.py

# Domain expression parser
https://raw.githubusercontent.com/odoo/odoo/17.0/odoo/osv/expression.py
```

## Official guideline deltas 16.0 -> 17.0

Only rules of the official Odoo guidelines (odoo/odoo `skills/`, verified per version) whose 16.0 and 17.0 forms differ:

| Topic | 16.0 | 17.0 |
|---|---|---|
| `_search()` + custom SQL | `query.select('"t"."c"')` -> `(str, params)` | `query.select(SQL(...))` |
| `_()` and Markup | no escaping of Markup args | escapes args when an argument is Markup; `tools.format_list` available |
| `records.grouped()` | absent (`tools.groupby`) | exists |
| Aggregation | `read_group(domain, fields, groupby, lazy)` / `_read_group` same signature -> dicts | `_read_group(domain, groupby, aggregates)` -> tuples (`read_group` still public) |
| `<asset>` XML tag | absent (manifest `assets` only) | exists |
| Python | 3.7 - 3.12 | 3.10+ |

View modifiers, SQL builder and JS `patch`: see Breaking Changes Summary.

Unchanged (16.0 = 17.0): default test tags `standard`+`at_install`, imported test classes and inherited `test_*` methods are collected, `BaseCommon`/`BaseUsersCommon`, `_sql_constraints`, field `index` values, no `base` injection in manifests, `t-lang` without `t-call` = SyntaxError, `@api.private`, route types http/json, auth user/public/none, restricted `tools.misc.pickle`, Owl 2 without `computed`.

## Migration Checklist

- [ ] **CRITICAL**: Replace ALL `attrs=` with inline expressions
- [ ] Update all `@api.model` create to `@api.model_create_multi` (warning in both versions)
- [ ] Convert JS `patch(obj, "name", {...})` + `this._super` to `patch(obj, {...})` + `super`
- [ ] Optionally move `read_group` aggregation to `_read_group(domain, groupby, aggregates)`
- [ ] Review record rules for stricter validation
- [ ] Test all view visibility conditions
- [ ] Verify JavaScript modules use ES6 imports
- [ ] Test form/tree/kanban views thoroughly
- [ ] Check parent field access in embedded views

## Common Migration Errors

### Error: `ValueError: attrs attribute is no longer supported`
**Fix**: Replace `attrs="{...}"` with inline `invisible=`, `readonly=`, `required=`

### Warning: `The model ... is not overriding the create method in batch`
**Fix**: Change `@api.model def create(self, vals)` to `@api.model_create_multi def create(self, vals_list)` (already logged in 16.0)

### Error: `Invalid domain expression`
**Fix**: Review domain syntax - v17 is stricter about field references

## attrs Migration Tool

```python
#!/usr/bin/env python3
"""
Tool to help migrate attrs to v17 inline expressions
"""
import re
import ast

def convert_domain_to_expr(domain_str):
    """Convert Odoo domain to Python expression"""
    try:
        domain = ast.literal_eval(domain_str)
    except:
        return None

    def convert_leaf(leaf):
        if isinstance(leaf, str):
            return leaf  # Operator
        field, op, value = leaf
        if op == '=':
            if value is True:
                return field
            elif value is False:
                return f"not {field}"
            else:
                return f"{field} == {repr(value)}"
        elif op == '!=':
            return f"{field} != {repr(value)}"
        elif op == 'in':
            return f"{field} in {repr(value)}"
        # Add more operators as needed
        return f"{field} {op} {repr(value)}"

    # Simplified conversion - production code needs full implementation
    parts = [convert_leaf(leaf) for leaf in domain if not isinstance(leaf, str)]
    return ' and '.join(parts)

# Example usage
old = "[('state', '=', 'draft'), ('type', '!=', 'service')]"
new = convert_domain_to_expr(old)
print(f"invisible=\"{new}\"")  # invisible="state == 'draft' and type != 'service'"
```
