# Odoo Module Generator - Version 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 16.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 16.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 16.0 Requirements

- **Python**: 3.8+ required
- **Key Features**: `Command` class introduced, `attrs` deprecated, OWL 2.x
- **View syntax**: `attrs` still works but deprecated, prefer direct attributes

## IMPORTANT: Transition Version

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  v16 is a TRANSITION version:                                                ║
║  - `attrs` works but is DEPRECATED                                           ║
║  - `@api.model_create_multi` recommended but not mandatory                   ║
║  - Start using direct invisible/readonly for v17 compatibility               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## IMPORTANT: Data File Ordering

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  The ORDER of files in the 'data' list is CRITICAL.                          ║
║  A resource can ONLY be referenced AFTER it has been defined.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## __manifest__.py Template (v16)

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '16.0.1.0.0',
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

## Model Template (v16)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command, _
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
        tracking=True,
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

    # === CRUD METHODS === #
    # v16: @api.model_create_multi recommended
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    '{module_name}.{model_name}'
                ) or _('New')
        return super().create(vals_list)

    # === x2many OPERATIONS - v16: Use Command class === #
    def action_add_line(self):
        """Use Command class for x2many operations."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New Line', 'amount': 0}),
            ]
        })

    def action_update_lines(self):
        """Command class examples."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New'}),        # Create new record
                Command.update(1, {'name': 'Updated'}), # Update existing
                Command.delete(2),                      # Delete from DB
                Command.unlink(3),                      # Remove from relation
                Command.link(4),                        # Link existing
                Command.clear(),                        # Clear all
                Command.set([5, 6, 7]),                 # Replace with these
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

## View Templates (v16 - attrs deprecated, prefer direct)

### Recommended Pattern (v17-ready)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <!-- v16: PREFER direct invisible (v17-ready) -->
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" type="object"
                            invisible="state in ('done', 'cancelled')"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
                    <widget name="web_ribbon" title="Archived" bg_color="bg-danger"
                            invisible="active"/>
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

### Legacy Pattern (still works in v16, will break in v17)

```xml
<!-- DEPRECATED: Will break in v17 -->
<button name="action_confirm" string="Confirm"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>

<!-- PREFER THIS INSTEAD (works in v16 AND v17) -->
<button name="action_confirm" string="Confirm"
        invisible="state != 'draft'"/>
```

## OWL Component Template (v16 - OWL 2.x)

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            data: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "{module_name}.{model_name}",
                [],
                ["name", "state"]
            );
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

## Security Templates (v16)

### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_name}_user,{model_name}.user,model_{module_name}_{model_name},{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_manager,{model_name}.manager,model_{module_name}_{model_name},{module_name}.group_{module_name}_manager,1,1,1,1
```

### Security Groups XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_{module_name}" model="ir.module.category">
        <field name="name">{Module Title}</field>
    </record>

    <record id="group_{module_name}_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_{module_name}"/>
    </record>

    <record id="group_{module_name}_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_{module_name}"/>
        <field name="implied_ids" eval="[(4, ref('group_{module_name}_user'))]"/>
    </record>

    <!-- Multi-Company Rule -->
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

## v16 Checklist

When generating a v16 module:

- [ ] Use `Command` class for x2many operations
- [ ] Prefer direct `invisible`/`readonly` over `attrs` (v17 preparation)
- [ ] Use `@api.model_create_multi` for create methods (recommended)
- [ ] Use `tracking=True` for tracked fields
- [ ] Use OWL 2.x syntax for frontend components
- [ ] Include assets in manifest
- [ ] Data files in correct order

## AI Agent Instructions (v16)

When generating an Odoo 16.0 module:

1. **USE** `Command` class for x2many operations (mandatory)
2. **PREFER** direct `invisible`/`readonly` attributes (v17 preparation)
3. **USE** `@api.model_create_multi` for create (recommended)
4. **USE** `tracking=True` for field tracking
5. **NOTE**: `attrs` still works but is deprecated
6. **USE** OWL 2.x with `/** @odoo-module **/`
7. **INCLUDE** assets in manifest
