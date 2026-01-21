# Odoo Module Generator - Version 14.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 14.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 14.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  Note: v14 is LEGACY - consider upgrading to v17+ for new projects.          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 14.0 Requirements

- **Python**: 3.6+ required, 3.8 recommended
- **Key Features**: Last version with `@api.multi`, `track_visibility`
- **View syntax**: `attrs` for visibility/readonly
- **OWL**: Not available (legacy widgets only)

## IMPORTANT: Legacy Version Notes

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  v14 is END OF LIFE (October 2023)                                           ║
║  Only use for maintaining existing modules.                                  ║
║  For new projects, use v17+ with modern patterns.                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## __manifest__.py Template (v14)

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '14.0.1.0.0',
    'category': '{Category}',
    'summary': '{Short description}',
    'description': """
{Detailed description}
    """,
    'author': '{Author}',
    'website': '{Website}',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        # ORDER IS CRITICAL
        'security/{module_name}_security.xml',
        'security/ir.model.access.csv',
        'views/{model_name}_views.xml',
        'views/menuitems.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## Model Template (v14)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class {ModelName}(models.Model):
    _name = '{module_name}.{model_name}'
    _description = '{Model Description}'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # === BASIC FIELDS === #
    name = fields.Char(
        string='Name',
        required=True,
        track_visibility='onchange',  # v14 syntax
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    # === RELATIONAL FIELDS === #
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        track_visibility='onchange',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        track_visibility='onchange',
    )
    line_ids = fields.One2many(
        comodel_name='{module_name}.{model_name}.line',
        inverse_name='parent_id',
        string='Lines',
        copy=True,
    )

    # === SELECTION FIELDS === #
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        track_visibility='onchange',
        copy=False,
    )

    # === COMPUTED FIELDS === #
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    # === CRUD METHODS (v14 style) === #
    @api.model
    def create(self, vals):
        """Single record create - v14 style."""
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                '{module_name}.{model_name}'
            ) or _('New')
        return super().create(vals)

    # === x2many OPERATIONS - v14: Use tuple syntax === #
    def action_add_line(self):
        """Use tuple syntax for x2many operations in v14."""
        self.write({
            'line_ids': [
                (0, 0, {'name': 'New Line', 'amount': 0}),  # Create new
            ]
        })

    def action_update_lines(self):
        """Tuple command reference for v14."""
        self.write({
            'line_ids': [
                (0, 0, {'name': 'New'}),        # Create new record
                (1, line_id, {'name': 'Upd'}),  # Update existing
                (2, line_id),                   # Delete from DB
                (3, line_id),                   # Remove from relation
                (4, line_id),                   # Link existing
                (5, 0, 0),                      # Clear all
                (6, 0, [id1, id2]),             # Replace with these
            ]
        })

    # === ACTION METHODS === #
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
```

## View Templates (v14 - attrs syntax)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <!-- v14: Use attrs for visibility -->
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary"
                            attrs="{'invisible': [('state', '!=', 'draft')]}"/>
                    <button name="action_done" string="Done" type="object"
                            attrs="{'invisible': [('state', '!=', 'confirmed')]}"/>
                    <button name="action_cancel" string="Cancel" type="object"
                            attrs="{'invisible': [('state', 'in', ('done', 'cancelled'))]}"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
                    <widget name="web_ribbon" title="Archived" bg_color="bg-danger"
                            attrs="{'invisible': [('active', '=', True)]}"/>
                    <div class="oe_title">
                        <h1><field name="name" placeholder="Name..."/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="partner_id"/>
                            <field name="user_id"/>
                        </group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="total_amount"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids">
                                <tree editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="amount"/>
                                </tree>
                            </field>
                        </page>
                    </notebook>
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

## Security Templates (v14)

### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_name}_user,{model_name}.user,model_{module_name}_{model_name},{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_manager,{model_name}.manager,model_{module_name}_{model_name},{module_name}.group_{module_name}_manager,1,1,1,1
```

### Record Rules (v14 - uses company_ids)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Multi-Company Rule - v14 syntax -->
    <record id="rule_{model_name}_company" model="ir.rule">
        <field name="name">{Model Name}: Multi-Company</field>
        <field name="model_id" ref="model_{module_name}_{model_name}"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
        ]</field>
    </record>
</odoo>
```

## v14 Patterns Reference

### Field Tracking (v14 syntax)
```python
# v14: Use track_visibility
name = fields.Char(track_visibility='onchange')
state = fields.Selection([...], track_visibility='always')
```

### x2many Commands (v14 tuple syntax)
```python
# v14: Tuple syntax
(0, 0, values)      # Create
(1, id, values)     # Update
(2, id)             # Delete
(3, id)             # Unlink
(4, id)             # Link
(5, 0, 0)           # Clear
(6, 0, [ids])       # Set
```

### View Visibility (v14 attrs)
```xml
<!-- v14: attrs with domain syntax -->
<field name="x" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
<field name="y" attrs="{'readonly': [('state', '!=', 'draft')],
                        'required': [('type', '=', 'invoice')]}"/>
```

## v14 Checklist

When generating a v14 module:

- [ ] Use `track_visibility` for field tracking (NOT `tracking`)
- [ ] Use tuple syntax for x2many operations (NOT `Command`)
- [ ] Use `attrs` for view visibility
- [ ] Use single-record `create(vals)` method
- [ ] Use `company_ids` in record rules (NOT `allowed_company_ids`)
- [ ] No OWL components (legacy widgets only)
- [ ] Data files in correct order in manifest

## Migration Note

To upgrade this module to v15+:
1. Replace `track_visibility` with `tracking`
2. Read `odoo-module-generator-14-15.md` for full migration guide

## AI Agent Instructions (v14)

When generating an Odoo 14.0 module:

1. **USE** `track_visibility='onchange'` for tracked fields
2. **USE** tuple syntax `(0, 0, {...})` for x2many
3. **USE** `attrs` in views for visibility/readonly
4. **USE** `company_ids` in record rules
5. **DO NOT** use `Command` class (v16+)
6. **DO NOT** use `tracking=True` (v15+)
7. **DO NOT** use direct `invisible`/`readonly` (v17+)
8. **DO NOT** create OWL components (use legacy widgets)
