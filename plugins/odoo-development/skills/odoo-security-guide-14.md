# Odoo Security Guide - Version 14.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 14.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 14.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  NOTE: Odoo 14.0 is LEGACY - consider upgrading to a supported version.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 14.0 Requirements

- **Python**: 3.6+ required
- **Key Features**: `@api.multi` deprecated, `attrs` in views, legacy widget system

## Security Groups (v14 Syntax)

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

## Access Rights (v14)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

## Record Rules (v14 Syntax)

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

<record id="rule_custom_model_user" model="ir.rule">
    <field name="name">Custom Model: User Own Records</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_custom_user'))]"/>
</record>
```

## Model Security (v14 Patterns)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        required=True,
        track_visibility='onchange',  # v14: track_visibility (deprecated in v15+)
    )
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
        track_visibility='onchange',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', track_visibility='onchange')

    # v14: Single record create (vals, not vals_list)
    @api.model
    def create(self, vals):
        return super(SecureModel, self).create(vals)

    def write(self, vals):
        return super(SecureModel, self).write(vals)

    # v14: @api.multi is deprecated but may still appear
    # Do NOT use @api.multi in new v14 code
    def action_sensitive_operation(self):
        """Check permissions before sensitive operations."""
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(_("Only managers can perform this action."))
        for record in self:
            record._do_sensitive_work()
```

## View Security (v14 Syntax - attrs)

### Using attrs for Visibility

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- v14: Use attrs for conditional visibility -->
            <field name="internal_notes"
                   attrs="{'invisible': [('state', '=', 'draft')]}"/>

            <!-- v14: Combine attrs with groups -->
            <field name="secret_field"
                   attrs="{'invisible': [('state', '=', 'draft')]}"
                   groups="custom_module.group_manager"/>

            <!-- v14: Multiple conditions in attrs -->
            <field name="amount"
                   attrs="{'readonly': [('state', '!=', 'draft')], 'required': [('type', '=', 'invoice')]}"/>
        </group>
    </sheet>
</form>
```

### Button Security (v14)

```xml
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_manager"
        attrs="{'invisible': [('state', '!=', 'pending')]}"/>

<button name="action_confirm"
        string="Confirm"
        type="object"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

### Complete Form Example (v14)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="custom_model_view_form" model="ir.ui.view">
        <field name="name">custom.model.form</field>
        <field name="model">custom.model</field>
        <field name="arch" type="xml">
            <form string="Custom Model">
                <header>
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary"
                            attrs="{'invisible': [('state', '!=', 'draft')]}"/>
                    <button name="action_done" string="Done" type="object"
                            attrs="{'invisible': [('state', '!=', 'confirmed')]}"/>
                    <button name="action_approve" string="Approve" type="object"
                            groups="custom_module.group_manager"
                            attrs="{'invisible': [('state', '!=', 'pending')]}"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="partner_id"/>
                        </group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="user_id"/>
                        </group>
                    </group>
                    <group string="Internal" groups="custom_module.group_manager">
                        <field name="internal_notes"/>
                    </group>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids" widget="mail_followers"/>
                    <field name="activity_ids" widget="mail_activity"/>
                    <field name="message_ids" widget="mail_thread"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
```

## Field-Level Security (v14)

```python
class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    name = fields.Char(required=True, track_visibility='onchange')

    internal_notes = fields.Text(
        string='Internal Notes',
        groups='custom_module.group_manager',
    )

    cost_price = fields.Float(
        string='Cost Price',
        groups='account.group_account_user',
    )
```

## v14 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Use `attrs` for view visibility conditions
- [ ] Use `track_visibility` for field tracking
- [ ] Single record create method signature
- [ ] Do NOT use `@api.multi` (deprecated)
- [ ] Use legacy chatter widgets

## Key v14 Patterns

| Feature | v14 Pattern |
|---------|-------------|
| Field tracking | `track_visibility='onchange'` |
| View visibility | `attrs="{'invisible': [...]}"` |
| Create method | `def create(self, vals):` (single dict) |
| Chatter | `widget="mail_followers"`, `widget="mail_thread"` |

## AI Agent Instructions (v14)

When generating Odoo 14.0 security code:

1. **Use** `attrs` for view visibility: `attrs="{'invisible': [...]}"`
2. **Use** `track_visibility='onchange'` for field tracking
3. **Use** single record create: `def create(self, vals):`
4. **Do NOT** use `@api.multi` (deprecated)
5. **Use** legacy chatter widgets: `widget="mail_followers"`
6. **Note**: v14 is legacy - recommend upgrading
