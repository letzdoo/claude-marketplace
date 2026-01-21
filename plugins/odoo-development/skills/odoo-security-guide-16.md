# Odoo Security Guide - Version 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 16.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 16.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 16.0 Requirements

- **Python**: 3.8+ required
- **Key Features**: `Command` class, `attrs` still supported (deprecated), OWL 2.x

## Security Groups (v16 Syntax)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_custom" model="ir.module.category">
        <field name="name">Custom Module</field>
        <field name="sequence">100</field>
    </record>

    <record id="group_custom_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_custom"/>
    </record>

    <record id="group_custom_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_custom"/>
        <field name="implied_ids" eval="[(4, ref('group_custom_user'))]"/>
    </record>
</odoo>
```

## Access Rights (v16)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

## Record Rules (v16 Syntax)

### Multi-Company Rule

```xml
<record id="rule_custom_model_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

## Model Security (v16 Patterns)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
    )
    line_ids = fields.One2many('custom.secure.line', 'parent_id')

    # v16: @api.model_create_multi recommended but not mandatory
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def action_update_lines(self):
        """v16: Use Command class for x2many operations."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New Line'}),
                Command.update(1, {'name': 'Updated'}),
                Command.delete(2),
                Command.link(3),
                Command.unlink(4),
                Command.clear(),
                Command.set([5, 6]),
            ]
        })
```

## View Security (v16 Syntax - attrs DEPRECATED)

### Using attrs (Deprecated but supported)

```xml
<!-- v16: attrs still works but is DEPRECATED -->
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- DEPRECATED: Using attrs -->
            <field name="internal_notes"
                   attrs="{'invisible': [('state', '=', 'draft')]}"/>

            <!-- RECOMMENDED: Using direct invisible (v16 supports both) -->
            <field name="secret_field"
                   invisible="state == 'draft'"
                   groups="custom_module.group_manager"/>
        </group>
    </sheet>
</form>
```

### Recommended v16 Pattern (Prepare for v17)

```xml
<!-- v16: Prefer direct attributes for future compatibility -->
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- Direct invisible attribute -->
            <field name="manager_notes"
                   invisible="state == 'draft'"
                   groups="custom_module.group_manager"/>

            <!-- Direct readonly attribute -->
            <field name="amount"
                   readonly="state != 'draft'"/>
        </group>
    </sheet>
</form>
```

### Button Security (v16)

```xml
<!-- v16: attrs still works -->
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_manager"
        attrs="{'invisible': [('state', '!=', 'pending')]}"/>

<!-- v16: Direct invisible also works (preferred) -->
<button name="action_confirm"
        string="Confirm"
        type="object"
        invisible="state != 'draft'"/>
```

## Field-Level Security (v16)

```python
class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    name = fields.Char(required=True, tracking=True)

    internal_notes = fields.Text(
        string='Internal Notes',
        groups='custom_module.group_manager',
    )

    cost_price = fields.Float(
        string='Cost Price',
        groups='account.group_account_user',
    )
```

## Complete Security Template (v16)

### security/custom_module_security.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_custom" model="ir.module.category">
        <field name="name">Custom Module</field>
        <field name="sequence">100</field>
    </record>

    <record id="group_custom_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_custom"/>
    </record>

    <record id="group_custom_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_custom"/>
        <field name="implied_ids" eval="[(4, ref('group_custom_user'))]"/>
        <field name="users" eval="[(4, ref('base.user_admin'))]"/>
    </record>

    <record id="rule_custom_model_company" model="ir.rule">
        <field name="name">Custom Model: Multi-Company</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
        ]</field>
    </record>

    <record id="rule_custom_model_user" model="ir.rule">
        <field name="name">Custom Model: User Own Records</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('group_custom_user'))]"/>
    </record>

    <record id="rule_custom_model_manager" model="ir.rule">
        <field name="name">Custom Model: Manager All Records</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('group_custom_manager'))]"/>
    </record>
</odoo>
```

## v16 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Record rules use `company_ids` for multi-company
- [ ] Prefer direct `invisible` attribute over `attrs`
- [ ] Use `Command` class for x2many security operations
- [ ] Use `tracking=True` instead of `track_visibility`
- [ ] Prepare for `attrs` removal by using direct attributes

## Key Differences

| Feature | v15 | v16 |
|---------|-----|-----|
| x2many commands | Tuple syntax | `Command` class |
| View visibility | `attrs` | `attrs` (deprecated) or direct |
| Tracking | `tracking=True` | `tracking=True` |

## AI Agent Instructions (v16)

When generating Odoo 16.0 security code:

1. **Prefer** direct `invisible`, `readonly`, `required` attributes over `attrs`
2. **Use** `Command` class for x2many operations
3. **Use** `tracking=True` for field tracking
4. **Use** `company_ids` in multi-company record rules
5. **Note**: `attrs` still works but is deprecated - avoid for new code
6. **Use** `@api.model_create_multi` (recommended but not mandatory yet)
