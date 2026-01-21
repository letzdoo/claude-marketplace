# Odoo Module Generator - Version 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 18.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 18.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 18.0 Requirements

- **Python**: 3.11+ required
- **Key Features**: `_check_company_auto`, `check_company`, type hints, `SQL()` builder
- **OWL**: 2.x
- **View syntax**: Direct `invisible`/`readonly` attributes

## Input Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `module_name` | string | Technical name (lowercase, underscores) | `custom_inventory` |
| `module_description` | string | Human-readable description | `Custom inventory tracking` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_apps` | list | `[]` | Apps to extend: `crm`, `sale`, `purchase`, `account`, `hr`, `website`, `stock`, `mrp`, `project` |
| `ui_stack` | string | `owl` | UI technology: `classic`, `owl`, `hybrid` |
| `multi_company` | boolean | `false` | Enable multi-company support |
| `multi_currency` | boolean | `false` | Enable multi-currency support |
| `security_level` | string | `basic` | Security level: `basic`, `advanced`, `audit` |
| `performance_critical` | boolean | `false` | Enable performance optimizations |
| `custom_models` | list | `[]` | List of custom models to create |
| `custom_fields` | list | `[]` | Fields to add to existing models |
| `include_tests` | boolean | `true` | Generate test files |
| `author` | string | `""` | Module author name |
| `license` | string | `LGPL-3` | Module license |

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
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       │   └── {component_name}.js
│       ├── xml/
│       │   └── {component_name}.xml
│       └── scss/
│           └── {module_name}.scss
├── data/
│   └── {module_name}_data.xml
├── wizard/
│   ├── __init__.py
│   └── {wizard_name}.py
├── report/
│   ├── __init__.py
│   ├── {report_name}.py
│   └── {report_name}_template.xml
├── tests/
│   ├── __init__.py
│   └── test_{model_name}.py
└── i18n/
    └── {module_name}.pot
```

## __manifest__.py Template (v18)

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '18.0.1.0.0',
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

## Model Template (v18)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL

class {ModelName}(models.Model):
    _name = '{module_name}.{model_name}'
    _description = '{Model Description}'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True  # v18: Automatic company validation

    # === BASIC FIELDS === #
    name: str = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        index='btree',
    )
    active: bool = fields.Boolean(default=True)
    sequence: int = fields.Integer(default=10)

    # === RELATIONAL FIELDS === #
    company_id: int = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id: int = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        check_company=True,  # v18: Company validation
        tracking=True,
    )
    user_id: int = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        check_company=True,
        tracking=True,
    )
    line_ids: list = fields.One2many(
        comodel_name='{module_name}.{model_name}.line',
        inverse_name='parent_id',
        string='Lines',
        copy=True,
    )

    # === SELECTION FIELDS === #
    state: str = fields.Selection(
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
    total_amount: float = fields.Float(
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
                raise UserError(_("Cannot delete record in state '%s'.") % record.state)
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

    # === BUSINESS METHODS === #
    def _get_report_data(self):
        """v18: Use SQL builder for complex queries."""
        query = SQL(
            """
            SELECT id, name, total_amount
            FROM %(table)s
            WHERE company_id = %(company_id)s
              AND state = %(state)s
            ORDER BY total_amount DESC
            """,
            table=SQL.identifier(self._table),
            company_id=self.env.company.id,
            state='done',
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()


class {ModelName}Line(models.Model):
    _name = '{module_name}.{model_name}.line'
    _description = '{Model Name} Line'
    _order = 'sequence, id'

    parent_id: int = fields.Many2one(
        comodel_name='{module_name}.{model_name}',
        string='Parent',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id: int = fields.Many2one(
        related='parent_id.company_id',
        store=True,
    )
    sequence: int = fields.Integer(default=10)
    name: str = fields.Char(string='Description', required=True)
    quantity: float = fields.Float(string='Quantity', default=1.0)
    price_unit: float = fields.Float(string='Unit Price')
    amount: float = fields.Float(
        string='Amount',
        compute='_compute_amount',
        store=True,
    )

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_unit
```

## View Templates (v18)

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
                    <!-- v18: Direct invisible attribute -->
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary" invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" type="object"
                            invisible="state in ('done', 'cancelled')"/>
                    <button name="action_draft" string="Reset to Draft" type="object"
                            invisible="state not in ('cancelled',)"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
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
            <filter string="Confirmed" name="confirmed"
                    domain="[('state', '=', 'confirmed')]"/>
            <filter string="Done" name="done"
                    domain="[('state', '=', 'done')]"/>
            <separator/>
            <filter string="Archived" name="inactive"
                    domain="[('active', '=', False)]"/>
            <group expand="0" string="Group By">
                <filter string="Partner" name="group_partner"
                        context="{'group_by': 'partner_id'}"/>
                <filter string="Status" name="group_state"
                        context="{'group_by': 'state'}"/>
                <filter string="Responsible" name="group_user"
                        context="{'group_by': 'user_id'}"/>
            </group>
        </search>
    </field>
</record>
```

### Action and Menu

```xml
<record id="{model_name}_action" model="ir.actions.act_window">
    <field name="name">{Model Title}</field>
    <field name="res_model">{module_name}.{model_name}</field>
    <field name="view_mode">tree,form</field>
    <field name="context">{'search_default_my_records': 1}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first {Model Title}
        </p>
    </field>
</record>

<menuitem id="menu_{module_name}_root"
          name="{Module Title}"
          sequence="100"/>

<menuitem id="menu_{model_name}"
          name="{Model Title}"
          parent="menu_{module_name}_root"
          action="{model_name}_action"
          sequence="10"/>
```

## Security Templates (v18)

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

    <!-- Multi-Company Record Rule (v18 pattern) -->
    <record id="rule_{model_name}_company" model="ir.rule">
        <field name="name">{Model Name}: Multi-Company</field>
        <field name="model_id" ref="model_{module_name}_{model_name}"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', allowed_company_ids)
        ]</field>
    </record>
</odoo>
```

## OWL Component Template (v18 - OWL 2.x)

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";
    static props = {
        recordId: { type: Number, optional: true },
    };

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
                [["state", "=", "confirmed"]],
                ["name", "total_amount", "partner_id"]
            );
        } catch (error) {
            this.notification.add("Error loading data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onRecordClick(recordId) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "{module_name}.{model_name}",
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

## Test Template (v18)

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

        cls.company = cls.env.company
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'company_id': cls.company.id,
        })
        cls.user = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'company_id': cls.company.id,
            'company_ids': [(6, 0, [cls.company.id])],
        })

    def test_create_record(self):
        """Test basic record creation."""
        record = self.env['{module_name}.{model_name}'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
        })
        self.assertTrue(record.id)
        self.assertEqual(record.state, 'draft')

    def test_confirm_record(self):
        """Test record confirmation workflow."""
        record = self.env['{module_name}.{model_name}'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
        })
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')

    def test_cannot_delete_confirmed(self):
        """Test that confirmed records cannot be deleted."""
        record = self.env['{module_name}.{model_name}'].create({
            'name': 'Test Record',
        })
        record.action_confirm()
        with self.assertRaises(UserError):
            record.unlink()

    def test_multi_company(self):
        """Test multi-company record rules."""
        company_2 = self.env['res.company'].create({'name': 'Company 2'})
        record = self.env['{module_name}.{model_name}'].create({
            'name': 'Test Record',
            'company_id': company_2.id,
        })
        # User should not see record from other company
        records = self.env['{module_name}.{model_name}'].with_user(self.user).search([])
        self.assertNotIn(record.id, records.ids)
```

## v18 Checklist

When generating a v18 module, ensure:

- [ ] `_check_company_auto = True` on multi-company models
- [ ] `check_company=True` on relational fields
- [ ] Type hints on all fields: `name: str = fields.Char(...)`
- [ ] `@api.model_create_multi` for create methods
- [ ] Direct `invisible`/`readonly` in views (no `attrs`)
- [ ] `allowed_company_ids` in record rules
- [ ] `SQL()` builder for raw SQL queries
- [ ] `tracking=True` for tracked fields
- [ ] Proper OWL 2.x component syntax
- [ ] Tests with `@tagged` decorator

## AI Agent Instructions

When generating an Odoo 18.0 module:

1. **Always add** `_check_company_auto = True` to models with `company_id`
2. **Always add** `check_company=True` to relational fields
3. **Always add** type hints to fields
4. **Always use** `@api.model_create_multi` for create
5. **Never use** `attrs` in views
6. **Use** `allowed_company_ids` in multi-company rules
7. **Use** `SQL()` builder for any raw SQL
