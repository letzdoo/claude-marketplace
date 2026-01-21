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
| Views | `attrs=` REMOVED | **CRITICAL** - Must migrate |
| ORM | `@api.model_create_multi` required | High - Update all create() |
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

### Before (v16) - Allowed
```python
@api.model
def create(self, vals):
    if 'name' not in vals:
        vals['name'] = 'Default'
    return super().create(vals)
```

### After (v17) - Required
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

## Migration Checklist

- [ ] **CRITICAL**: Replace ALL `attrs=` with inline expressions
- [ ] Update all `@api.model` create to `@api.model_create_multi`
- [ ] Review record rules for stricter validation
- [ ] Test all view visibility conditions
- [ ] Verify JavaScript modules use ES6 imports
- [ ] Test form/tree/kanban views thoroughly
- [ ] Check parent field access in embedded views

## Common Migration Errors

### Error: `ValueError: attrs attribute is no longer supported`
**Fix**: Replace `attrs="{...}"` with inline `invisible=`, `readonly=`, `required=`

### Error: `TypeError: create() takes 2 positional arguments but 3 were given`
**Fix**: Change `@api.model def create(self, vals)` to `@api.model_create_multi def create(self, vals_list)`

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
