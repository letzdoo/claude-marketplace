# Odoo Security Guide - Version 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 15.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  NOTE: Odoo 15.0 is LEGACY - consider upgrading to a supported version.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 15.0 Requirements

- **Python**: 3.8+ required
- **Key Changes**: `@api.multi` removed, `tracking` replaces `track_visibility`, OWL 1.x introduced

## Security Groups (v15 Syntax)

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

## Access Rights (v15)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

## Record Rules (v15 Syntax)

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

## Model Security (v15 Patterns)

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
        tracking=True,  # v15: tracking replaces track_visibility
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
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)

    # v15: @api.model for single record create
    @api.model
    def create(self, vals):
        return super().create(vals)

    # v15: @api.multi is REMOVED - do not use
    def action_sensitive_operation(self):
        """Check permissions before sensitive operations."""
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(_("Only managers can perform this action."))
        for record in self:
            record._do_sensitive_work()
```

## View Security (v15 Syntax - attrs)

### Using attrs for Visibility

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- v15: Use attrs for conditional visibility -->
            <field name="internal_notes"
                   attrs="{'invisible': [('state', '=', 'draft')]}"/>

            <!-- v15: Combine attrs with groups -->
            <field name="secret_field"
                   attrs="{'invisible': [('state', '=', 'draft')]}"
                   groups="custom_module.group_manager"/>
        </group>
    </sheet>
</form>
```

### Button Security (v15)

```xml
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_manager"
        attrs="{'invisible': [('state', '!=', 'pending')]}"/>
```

### Complete Form Example (v15)

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
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
```

## Field-Level Security (v15)

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

## v15 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Use `attrs` for view visibility conditions
- [ ] Use `tracking=True` (NOT `track_visibility`)
- [ ] Do NOT use `@api.multi` (removed)
- [ ] Update chatter widgets (simplified)

## Key Differences from v14

| Feature | v14 | v15 |
|---------|-----|-----|
| Field tracking | `track_visibility='onchange'` | `tracking=True` |
| @api.multi | Deprecated | Removed |
| OWL | Not available | OWL 1.x introduced |
| Chatter widgets | Legacy widgets | Simplified |

## AI Agent Instructions (v15)

When generating Odoo 15.0 security code:

1. **Use** `attrs` for view visibility: `attrs="{'invisible': [...]}"`
2. **Use** `tracking=True` for field tracking (NOT `track_visibility`)
3. **Do NOT** use `@api.multi` (removed in v15)
4. **Use** updated chatter syntax (no widget attribute needed)
5. **Note**: v15 is legacy - recommend upgrading
