# Odoo Module Generator - Version 17.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 17.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 17.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 17.0 Requirements

- **Python**: 3.10+ required
- **Key Changes**: `attrs` REMOVED from views, `@api.model_create_multi` mandatory
- **OWL**: 2.x (enhanced)
- **View syntax**: Direct `invisible`/`readonly`/`required` attributes with Python expressions

## IMPORTANT: Breaking Changes from v16

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  CRITICAL: The `attrs` attribute is COMPLETELY REMOVED in v17.               ║
║  All views using attrs="{'invisible': [...]}" WILL FAIL.                     ║
║  You MUST use direct attributes: invisible="expression"                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## IMPORTANT: Data File Ordering

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  The ORDER of files in the 'data' list is CRITICAL.                          ║
║  A resource can ONLY be referenced AFTER it has been defined.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Input Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `module_name` | string | Technical name (lowercase, underscores) | `custom_inventory` |
| `module_description` | string | Human-readable description | `Custom inventory tracking` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_apps` | list | `[]` | Apps to extend |
| `ui_stack` | string | `owl` | UI technology: `classic`, `owl`, `hybrid` |
| `multi_company` | boolean | `false` | Enable multi-company support |
| `multi_currency` | boolean | `false` | Enable multi-currency support |
| `security_level` | string | `basic` | Security level: `basic`, `advanced`, `audit` |
| `performance_critical` | boolean | `false` | Enable performance optimizations |
| `custom_models` | list | `[]` | List of custom models to create |
| `include_tests` | boolean | `true` | Generate test files |

## Generated Module Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── {model_name}.py
├── views/
│   ├── {model_name}_views.xml
│   └── menuitems.xml
├── security/
│   ├── ir.model.access.csv
│   └── {module_name}_security.xml
├── static/
│   └── src/
│       ├── js/
│       ├── xml/
│       └── scss/
├── tests/
│   ├── __init__.py
│   └── test_{model_name}.py
└── i18n/
```

## __manifest__.py Template (v17)

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '17.0.1.0.0',
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
        # ORDER IS CRITICAL - define before reference
        'security/{module_name}_security.xml',  # Groups first
        'security/ir.model.access.csv',          # Access rights
        'views/{model_name}_views.xml',          # Views
        'views/menuitems.xml',                   # Menus last
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

## Model Template (v17)

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
        index='btree',  # v17: index type specification
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
        domain="[('company_id', 'in', [company_id, False])]",
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
        readonly=True,
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    # === CONSTRAINTS === #
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name and len(record.name) < 3:
                raise ValidationError(_("Name must be at least 3 characters."))

    _sql_constraints = [
        ('name_company_uniq', 'UNIQUE(name, company_id)',
         'Name must be unique per company!'),
    ]

    # === CRUD METHODS === #
    # v17: @api.model_create_multi is MANDATORY
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    '{module_name}.{model_name}'
                ) or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if not record.line_ids:
                    raise UserError(_("Cannot complete without lines."))
        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'cancelled'):
                raise UserError(
                    _("Cannot delete record in state '%s'.") % record.state
                )
        return super().unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': _("%s (Copy)") % self.name,
            'state': 'draft',
        })
        return super().copy(default)

    # === ACTION METHODS === #
    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft records can be confirmed."))
        self.write({'state': 'confirmed'})

    def action_done(self):
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_("Only confirmed records can be marked done."))
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    # === x2many OPERATIONS === #
    def action_add_line(self):
        """v17: Use Command class for x2many operations."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New Line', 'amount': 0}),
            ]
        })


class {ModelName}Line(models.Model):
    _name = '{module_name}.{model_name}.line'
    _description = '{Model Name} Line'
    _order = 'sequence, id'

    parent_id = fields.Many2one(
        comodel_name='{module_name}.{model_name}',
        string='Parent',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        related='parent_id.company_id',
        store=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    amount = fields.Float(
        string='Amount',
        compute='_compute_amount',
        store=True,
    )

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_unit
```

## View Templates (v17 - NO attrs!)

### Form View

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <!-- v17: Direct invisible with Python expression -->
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" type="object"
                            invisible="state in ('done', 'cancelled')"/>
                    <button name="action_draft" string="Reset to Draft" type="object"
                            invisible="state != 'cancelled'"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
                    <!-- v17: invisible takes Python expression -->
                    <widget name="web_ribbon" title="Archived" bg_color="bg-danger"
                            invisible="active"/>
                    <div class="oe_title">
                        <label for="name"/>
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

### v17 Visibility Syntax Examples

```xml
<!-- Simple condition -->
<field name="notes" invisible="state == 'draft'"/>

<!-- Multiple conditions with and -->
<field name="amount" invisible="state == 'draft' and not is_manager"/>

<!-- Multiple conditions with or -->
<field name="secret" invisible="state == 'draft' or state == 'cancelled'"/>

<!-- Using in operator -->
<field name="field" invisible="state in ('draft', 'cancelled')"/>

<!-- Not in -->
<field name="field" invisible="state not in ('confirmed', 'done')"/>

<!-- Group check -->
<field name="admin_field" invisible="not user_has_groups('base.group_system')"/>

<!-- Combined with readonly and required -->
<field name="amount"
       readonly="state != 'draft'"
       required="state == 'confirmed'"
       invisible="state == 'cancelled'"/>
```

### Tree View

```xml
<record id="{model_name}_view_tree" model="ir.ui.view">
    <field name="name">{module_name}.{model_name}.tree</field>
    <field name="model">{module_name}.{model_name}</field>
    <field name="arch" type="xml">
        <tree string="{Model Title}" multi_edit="1">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="user_id" widget="many2one_avatar_user"/>
            <field name="total_amount" sum="Total"/>
            <field name="state" widget="badge"
                   decoration-success="state == 'done'"
                   decoration-info="state == 'confirmed'"
                   decoration-warning="state == 'draft'"/>
            <field name="company_id" groups="base.group_multi_company" optional="hide"/>
        </tree>
    </field>
</record>
```

### Search View

```xml
<record id="{model_name}_view_search" model="ir.ui.view">
    <field name="name">{module_name}.{model_name}.search</field>
    <field name="model">{module_name}.{model_name}</field>
    <field name="arch" type="xml">
        <search string="{Model Title}">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="user_id"/>
            <separator/>
            <filter string="My Records" name="my_records"
                    domain="[('user_id', '=', uid)]"/>
            <filter string="Draft" name="draft"
                    domain="[('state', '=', 'draft')]"/>
            <filter string="Archived" name="inactive"
                    domain="[('active', '=', False)]"/>
            <group expand="0" string="Group By">
                <filter string="Partner" name="group_partner"
                        context="{'group_by': 'partner_id'}"/>
                <filter string="Status" name="group_state"
                        context="{'group_by': 'state'}"/>
            </group>
        </search>
    </field>
</record>
```

## Security Templates (v17)

### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_name}_user,{model_name}.user,model_{module_name}_{model_name},{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_manager,{model_name}.manager,model_{module_name}_{model_name},{module_name}.group_{module_name}_manager,1,1,1,1
access_{model_name}_line_user,{model_name}.line.user,model_{module_name}_{model_name}_line,{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_line_manager,{model_name}.line.manager,model_{module_name}_{model_name}_line,{module_name}.group_{module_name}_manager,1,1,1,1
```

### Security Groups XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_{module_name}" model="ir.module.category">
        <field name="name">{Module Title}</field>
        <field name="sequence">100</field>
    </record>

    <record id="group_{module_name}_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_{module_name}"/>
    </record>

    <record id="group_{module_name}_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_{module_name}"/>
        <field name="implied_ids" eval="[(4, ref('group_{module_name}_user'))]"/>
        <field name="users" eval="[(4, ref('base.user_admin'))]"/>
    </record>

    <!-- Multi-Company Record Rule -->
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

## OWL Component Template (v17 - OWL 2.x)

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");

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
                ["name", "state", "total_amount"]
            );
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

## Test Template (v17)

```python
# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError

@tagged('post_install', '-at_install')
class Test{ModelName}(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Model = cls.env['{module_name}.{model_name}']

    def test_create_record(self):
        """Test basic record creation."""
        record = self.Model.create({'name': 'Test'})
        self.assertTrue(record.id)
        self.assertEqual(record.state, 'draft')

    def test_workflow(self):
        """Test state workflow."""
        record = self.Model.create({'name': 'Test'})
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')

    def test_model_create_multi(self):
        """Test batch creation with @api.model_create_multi."""
        records = self.Model.create([
            {'name': 'Test 1'},
            {'name': 'Test 2'},
        ])
        self.assertEqual(len(records), 2)
```

## v17 Checklist

When generating a v17 module, ensure:

- [ ] **NO `attrs` in any view** - use direct `invisible`/`readonly`/`required`
- [ ] `@api.model_create_multi` for ALL create methods
- [ ] `Command` class for x2many operations
- [ ] `tracking=True` for tracked fields (not `track_visibility`)
- [ ] Data files in correct order in manifest
- [ ] Python 3.10+ compatibility
- [ ] `company_ids` in multi-company record rules

## AI Agent Instructions (v17)

When generating an Odoo 17.0 module:

1. **NEVER use** `attrs` attribute in views (removed in v17)
2. **ALWAYS use** direct `invisible`, `readonly`, `required` with Python expressions
3. **ALWAYS use** `@api.model_create_multi` for create methods
4. **USE** `user_has_groups()` for group checks in visibility
5. **USE** `Command` class for x2many operations
6. **USE** `company_ids` in multi-company record rules
7. **VERIFY** data file order in manifest
