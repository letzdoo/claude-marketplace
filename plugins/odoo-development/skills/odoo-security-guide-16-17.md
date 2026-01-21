# Odoo Security Guide - Migration 16.0 → 17.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: ODOO 16.0 → 17.0 SECURITY                                  ║
║  Use this guide when upgrading security code from v16 to v17.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview of Security Changes

| Component | v16 | v17 | Migration Required |
|-----------|-----|-----|-------------------|
| View visibility | `attrs` (deprecated) | Direct attributes | **REQUIRED** |
| Create method | `@api.model_create_multi` optional | Mandatory | **REQUIRED** |
| Python | 3.8+ | 3.10+ | Check compatibility |
| Record rules | `company_ids` | `company_ids` | No change |

## Breaking Changes

### 1. attrs Attribute REMOVED from Views

This is the most significant breaking change. The `attrs` attribute is completely removed in v17.

**v16 Pattern (will break in v17):**
```xml
<field name="secret_field"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<field name="amount"
       attrs="{'readonly': [('state', '!=', 'draft')], 'required': [('type', '=', 'invoice')]}"/>

<button name="action_approve"
        attrs="{'invisible': [('state', '!=', 'pending')]}"/>
```

**v17 Pattern:**
```xml
<field name="secret_field"
       invisible="state == 'draft'"/>

<field name="amount"
       readonly="state != 'draft'"
       required="type == 'invoice'"/>

<button name="action_approve"
        invisible="state != 'pending'"/>
```

### 2. Domain Syntax in Visibility Changed

**v16 (Odoo domain format):**
```xml
attrs="{'invisible': [('state', '=', 'draft'), ('type', '!=', 'invoice')]}"
<!-- This means: invisible if state == 'draft' AND type != 'invoice' -->

attrs="{'invisible': ['|', ('state', '=', 'draft'), ('type', '=', 'invoice')]}"
<!-- This means: invisible if state == 'draft' OR type == 'invoice' -->
```

**v17 (Python expression format):**
```xml
invisible="state == 'draft' and type != 'invoice'"
<!-- Same logic as v16 AND condition -->

invisible="state == 'draft' or type == 'invoice'"
<!-- Same logic as v16 OR condition -->
```

### 3. Group Checks in Visibility

**v16:**
```xml
<!-- No direct way to check groups in attrs -->
<field name="admin_field" groups="base.group_system"/>
<!-- Or use a computed boolean field -->
```

**v17:**
```xml
<field name="admin_field"
       invisible="not user_has_groups('base.group_system')"/>
```

## Migration Script for attrs

Here's a Python script to help migrate `attrs` to direct attributes:

```python
import re
import ast

def convert_domain_to_expression(domain_str):
    """Convert Odoo domain to Python expression."""
    try:
        domain = ast.literal_eval(domain_str)
    except:
        return domain_str  # Can't parse, return as-is

    def convert_condition(cond):
        if isinstance(cond, str):
            return cond  # '|' or '&'
        field, op, value = cond
        if op == '=':
            return f"{field} == {repr(value)}"
        elif op == '!=':
            return f"{field} != {repr(value)}"
        elif op == 'in':
            return f"{field} in {repr(value)}"
        elif op == 'not in':
            return f"{field} not in {repr(value)}"
        elif op in ('<', '>', '<=', '>='):
            return f"{field} {op} {repr(value)}"
        return f"{field} {op} {repr(value)}"

    # Simple case: single condition or AND conditions
    if not any(c in ('|', '&') for c in domain if isinstance(c, str)):
        conditions = [convert_condition(c) for c in domain]
        return ' and '.join(conditions)

    # Handle OR/AND operators (simplified)
    # For complex domains, manual conversion may be needed
    return str(domain)  # Return original for manual review


def migrate_attrs_in_xml(xml_content):
    """Migrate attrs to direct attributes in XML content."""
    # Pattern to match attrs="{'invisible': [...], ...}"
    attrs_pattern = r'attrs="(\{[^"]+\})"'

    def replace_attrs(match):
        attrs_str = match.group(1)
        try:
            attrs = ast.literal_eval(attrs_str)
            result_parts = []
            for attr, domain in attrs.items():
                expr = convert_domain_to_expression(str(domain))
                result_parts.append(f'{attr}="{expr}"')
            return ' '.join(result_parts)
        except:
            return match.group(0)  # Keep original if can't parse

    return re.sub(attrs_pattern, replace_attrs, xml_content)
```

## Manual Migration Examples

### Simple Visibility

**v16:**
```xml
<field name="notes" attrs="{'invisible': [('state', '=', 'draft')]}"/>
```

**v17:**
```xml
<field name="notes" invisible="state == 'draft'"/>
```

### Multiple Conditions (AND)

**v16:**
```xml
<field name="amount" attrs="{'invisible': [('state', '=', 'draft'), ('type', '=', 'draft')]}"/>
```

**v17:**
```xml
<field name="amount" invisible="state == 'draft' and type == 'draft'"/>
```

### OR Conditions

**v16:**
```xml
<field name="field" attrs="{'invisible': ['|', ('state', '=', 'draft'), ('state', '=', 'cancelled')]}"/>
```

**v17:**
```xml
<field name="field" invisible="state == 'draft' or state == 'cancelled'"/>
<!-- Or more elegantly: -->
<field name="field" invisible="state in ('draft', 'cancelled')"/>
```

### Complex Conditions

**v16:**
```xml
<field name="field" attrs="{'invisible': ['|', '&amp;', ('state', '=', 'draft'), ('type', '=', 'a'), ('active', '=', False)]}"/>
```

**v17:**
```xml
<field name="field" invisible="(state == 'draft' and type == 'a') or not active"/>
```

### Multiple Attributes

**v16:**
```xml
<field name="amount"
       attrs="{'readonly': [('state', '!=', 'draft')], 'required': [('type', '=', 'invoice')], 'invisible': [('show_amount', '=', False)]}"/>
```

**v17:**
```xml
<field name="amount"
       readonly="state != 'draft'"
       required="type == 'invoice'"
       invisible="not show_amount"/>
```

### Button Visibility

**v16:**
```xml
<button name="action_confirm"
        string="Confirm"
        type="object"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

**v17:**
```xml
<button name="action_confirm"
        string="Confirm"
        type="object"
        invisible="state != 'draft'"/>
```

## Create Method Migration

**v16 (optional @api.model_create_multi):**
```python
@api.model
def create(self, vals):
    return super().create(vals)

# Or
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

**v17 (mandatory @api.model_create_multi):**
```python
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

## No Change Required

### Security Groups
```xml
<!-- Same in v16 and v17 -->
<record id="group_user" model="res.groups">
    <field name="name">User</field>
</record>
```

### Access Rights
```csv
# Same format in v16 and v17
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

### Record Rules
```xml
<!-- Same syntax in v16 and v17 -->
<record id="rule_company" model="ir.rule">
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

### Field Groups
```python
# Same in v16 and v17
notes = fields.Text(groups='my_module.group_manager')
```

## Migration Checklist

- [ ] **CRITICAL**: Replace ALL `attrs` with direct attributes in views
- [ ] Convert domain syntax to Python expressions
- [ ] Update create methods to use `@api.model_create_multi`
- [ ] Update Python version to 3.10+
- [ ] Test all view visibility conditions
- [ ] Test button visibility with different states
- [ ] Verify groups-based visibility using `user_has_groups()`

## Common Mistakes to Avoid

### 1. Forgetting to Convert Domain Operators

**Wrong:**
```xml
<!-- Still using domain syntax -->
<field name="f" invisible="('state', '=', 'draft')"/>
```

**Correct:**
```xml
<field name="f" invisible="state == 'draft'"/>
```

### 2. Using Wrong Boolean Syntax

**Wrong:**
```xml
<field name="f" invisible="active = False"/>
```

**Correct:**
```xml
<field name="f" invisible="not active"/>
<!-- or -->
<field name="f" invisible="active == False"/>
```

### 3. Forgetting Quotes Around String Values

**Wrong:**
```xml
<field name="f" invisible="state == draft"/>
```

**Correct:**
```xml
<field name="f" invisible="state == 'draft'"/>
```

## Testing After Migration

```python
def test_view_visibility(self):
    """Test that visibility conditions work correctly after migration."""
    # Create record in draft state
    record = self.env['my.model'].create({'name': 'Test', 'state': 'draft'})

    # Get form view
    view = self.env.ref('my_module.view_form')

    # Verify invisible fields are not shown for draft records
    # (This would need UI testing or view parsing)
```

## Rollback Considerations

You cannot support both v16 and v17 with the same view files. If you need dual support:

1. Create version-specific view files
2. Use conditional loading in `__manifest__.py` (not recommended)
3. Maintain separate branches

## GitHub Reference

Check these for v17 view parsing:
- `odoo/tools/view_validation.py` - View validation rules
- `addons/web/static/src/views/` - View rendering
