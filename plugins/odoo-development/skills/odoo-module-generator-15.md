# Odoo Module Generator - Version 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 15.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 15.0 Requirements

- **Python**: 3.8+ required
- **Key Changes**: `@api.multi` removed, `tracking` replaces `track_visibility`
- **View syntax**: `attrs` for visibility (standard)
- **OWL**: 1.x introduced for new components

## Breaking Changes from v14

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  REMOVED in v15:                                                             ║
║  • @api.multi decorator - REMOVED (methods work on recordsets by default)    ║
║  • @api.one decorator - REMOVED                                              ║
║  • track_visibility - DEPRECATED (use tracking=True)                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## __manifest__.py Template (v15)

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '15.0.1.0.0',
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
    'assets': {
        'web.assets_backend': [
            '{module_name}/static/src/**/*.js',
            '{module_name}/static/src/**/*.xml',
            '{module_name}/static/src/**/*.scss',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## Model Template (v15)

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
        tracking=True,  # v15: New tracking syntax
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
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
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
        tracking=True,
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

    # === CRUD METHODS (v15 - multi-record aware) === #
    @api.model
    def create(self, vals):
        """Create method - no @api.multi needed."""
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                '{module_name}.{model_name}'
            ) or _('New')
        return super().create(vals)

    # === x2many OPERATIONS - v15: Still tuple syntax === #
    def action_add_line(self):
        """Use tuple syntax for x2many operations."""
        self.write({
            'line_ids': [
                (0, 0, {'name': 'New Line', 'amount': 0}),
            ]
        })

    # === ACTION METHODS === #
    def action_confirm(self):
        # v15: Methods work on recordsets, no @api.multi needed
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
```

## View Templates (v15 - attrs syntax)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <!-- v15: attrs syntax still standard -->
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
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
```

## OWL 1.x Component (v15)

```javascript
odoo.define('{module_name}.{ComponentName}', function (require) {
    "use strict";

    const { Component } = owl;
    const { useState, onWillStart } = owl.hooks;
    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');

    class {ComponentName} extends Component {
        setup() {
            this.state = useState({
                data: [],
                loading: true,
            });

            onWillStart(async () => {
                await this.loadData();
            });
        }

        async loadData() {
            const rpc = this.env.services.rpc;
            try {
                const data = await rpc({
                    model: '{module_name}.{model_name}',
                    method: 'search_read',
                    args: [[], ['name', 'state']],
                });
                this.state.data = data;
            } finally {
                this.state.loading = false;
            }
        }
    }

    {ComponentName}.template = '{module_name}.{ComponentName}';

    core.action_registry.add('{module_name}.{component_name}', {ComponentName});

    return {ComponentName};
});
```

## OWL 1.x Template (v15)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="{module_name}.{ComponentName}" owl="1">
        <div class="o_action o_{component_name}">
            <t t-if="state.loading">
                <div class="o_loading">Loading...</div>
            </t>
            <t t-else="">
                <div class="o_content">
                    <t t-foreach="state.data" t-as="item" t-key="item.id">
                        <div class="o_item">
                            <span t-esc="item.name"/>
                        </div>
                    </t>
                </div>
            </t>
        </div>
    </t>
</templates>
```

## v15 Patterns Reference

### Field Tracking (v15 syntax)
```python
# v15: Use tracking=True (not track_visibility)
name = fields.Char(tracking=True)
state = fields.Selection([...], tracking=True)
```

### x2many Commands (v15 - still tuple syntax)
```python
# v15: Tuple syntax (Command class comes in v16)
(0, 0, values)      # Create
(1, id, values)     # Update
(2, id)             # Delete
(3, id)             # Unlink
(4, id)             # Link
(5, 0, 0)           # Clear
(6, 0, [ids])       # Set
```

### No More @api.multi
```python
# v14 (OLD):
@api.multi
def action_confirm(self):
    ...

# v15 (NEW):
def action_confirm(self):
    # Works on recordset by default
    ...
```

## v15 Checklist

When generating a v15 module:

- [ ] Use `tracking=True` for field tracking (NOT `track_visibility`)
- [ ] Remove any `@api.multi` decorators
- [ ] Remove any `@api.one` decorators
- [ ] Use tuple syntax for x2many operations
- [ ] Use `attrs` for view visibility
- [ ] Use OWL 1.x if adding new components
- [ ] Include `assets` in manifest for JS/CSS
- [ ] Data files in correct order in manifest

## AI Agent Instructions (v15)

When generating an Odoo 15.0 module:

1. **USE** `tracking=True` for tracked fields
2. **REMOVE** any `@api.multi` or `@api.one` decorators
3. **USE** tuple syntax for x2many (Command class is v16+)
4. **USE** `attrs` in views for visibility/readonly
5. **USE** OWL 1.x patterns with `odoo.define()`
6. **INCLUDE** `assets` key in manifest
7. **DO NOT** use `Command` class (v16+)
8. **DO NOT** use direct `invisible`/`readonly` (v17+)
