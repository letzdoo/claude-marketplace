# Odoo Module Generator - Version 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 18.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 18.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
> Includes rules from Odoo's official skill library (odoo/odoo skills/, branch 20.0), verified against the 18.0 source.

## Version 18.0 Requirements

- **Python**: 3.10+ required
- **Key Features**: `_check_company_auto`, `check_company`, `SQL()` builder, `check_access()`
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
│   └── {module_name}_menus.xml
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
│   ├── {model_name}_report.py
│   ├── {model_name}_reports.xml
│   └── {model_name}_templates.xml
├── tests/
│   ├── __init__.py
│   └── test_{model_name}.py
└── i18n/
    └── {module_name}.pot
```

### File and naming conventions

| Item | Convention |
|------|------------|
| Models | one main model per file, named after the model: `models/sale_order.py` |
| Views / menus / templates / data | `views/<model>_views.xml`, `views/<module>_menus.xml`, `views/<model>_templates.xml`, `data/<module>_data.xml`, `demo/<module>_demo.xml` |
| Security | `security/ir.model.access.csv` + `security/<module>_security.xml` (groups, rules); no `ir.access.csv` in 18 |
| Controllers | feature-named file or `<inherited_module>.py`; `main.py` is legacy |
| Reports | SQL-view model `report/<model>_report.py`; printable report split into `report/<model>_reports.xml` (action) and `report/<model>_templates.xml` (QWeb) |
| Model `_name` | dotted, module-prefixed, singular: `my_module.order`; wizard `<base_model>.<action>`; SQL report `<base_model>.report.<action>` |
| XML ids | `<model>_view_<type>` (`_view_form`, `_view_list`, `_view_search`), `<model>_action`, `<model>_menu`, `<module>_group_<name>`, `<model>_rule_<group>` |
| Python | model vars PascalCase (`Partner = self.env['res.partner']`); `_id`/`_ids` variables hold ids, not records |
| Method prefixes | `_compute_`, `_search_`, `_default_`, `_selection_`, `_onchange_`, `_check_`, `action_` (starts with `self.ensure_one()` when it acts on one record) |
| Class body order | private attributes (`_name`, `_description`, `_inherit`, `_order`, `_sql_constraints`) -> default methods -> fields -> compute/inverse/search methods -> selection methods -> `@api.constrains`/`@api.onchange` -> CRUD overrides -> actions -> business methods |
| Imports | stdlib / third-party / `from odoo import Command, _, api, fields, models` / `from odoo.addons...` |
| CSS | classes prefixed `o_<module>_`, no id selectors |

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
    'depends': ['mail'],  # direct dependencies only (mail already depends on base)
    'data': [
        'security/{module_name}_security.xml',
        'security/ir.model.access.csv',
        'views/{model_name}_views.xml',
        'views/{module_name}_menus.xml',
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

Manifest facts (18.0, `odoo/modules/module.py`):

- `depends`: list direct dependencies only. 18.0 does **not** inject `base` for an empty `depends`; declare `['base']` when the module needs nothing else.
- `license`: missing key defaults to `LGPL-3` with a warning; always set it explicitly.
- `auto_install`: `True` (all `depends` installed) or a list that must be a subset of `depends`.
- `assets`: the manifest key exists (`web.assets_backend`, `web.assets_frontend`, ...); the `<asset>` XML tag also exists.
- `application: True` only for full apps; `external_dependencies: {'python': [...], 'bin': [...]}`.
- `data` loads in list order (security groups before `ir.model.access.csv`, views before menus); `demo` only with demo data.

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
    _sql_constraints = [
        ('name_company_uniq', 'UNIQUE(name, company_id)',
         'Name must be unique per company!'),
    ]

    # === BASIC FIELDS === #
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        index='trigram',  # searched with ilike
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
        check_company=True,  # Company validation
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        check_company=True,
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
                raise UserError(_("Cannot delete record in state '%s'.", record.state))
        return super().unlink()

    def copy_data(self, default=None):
        # v18: copy() handles multi-record sets via copy_data() (one dict per record)
        vals_list = super().copy_data(default=default)
        return [
            dict(vals, name=_("%s (Copy)", record.name), state='draft')
            for record, vals in zip(self, vals_list)
        ]

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
                                <list editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="amount"/>
                                </list>
                            </field>
                        </page>
                    </notebook>
                </sheet>
                <!-- v18: <chatter/> tag (compiled by mail's form compiler) -->
                <chatter/>
            </form>
        </field>
    </record>
</odoo>
```

### List View

```xml
<record id="{model_name}_view_list" model="ir.ui.view">
    <field name="name">{module_name}.{model_name}.list</field>
    <field name="model">{module_name}.{model_name}</field>
    <field name="arch" type="xml">
        <list string="{Model Title}" multi_edit="1">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="user_id" widget="many2one_avatar_user"/>
            <field name="total_amount" sum="Total"/>
            <field name="state" widget="badge"
                   decoration-success="state == 'done'"
                   decoration-info="state == 'confirmed'"
                   decoration-warning="state == 'draft'"/>
            <field name="company_id" groups="base.group_multi_company" optional="hide"/>
        </list>
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
    <field name="view_mode">list,form</field>
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

<menuitem id="{model_name}_menu"
          name="{Model Title}"
          parent="menu_{module_name}_root"
          action="{model_name}_action"
          sequence="10"/>
```

## Security Templates (v18)

### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_name}_user,{model_name}.user,model_{module_name}_{model_name},{module_name}.{module_name}_group_user,1,1,1,0
access_{model_name}_manager,{model_name}.manager,model_{module_name}_{model_name},{module_name}.{module_name}_group_manager,1,1,1,1
access_{model_name}_line_user,{model_name}.line.user,model_{module_name}_{model_name}_line,{module_name}.{module_name}_group_user,1,1,1,0
access_{model_name}_line_manager,{model_name}.line.manager,model_{module_name}_{model_name}_line,{module_name}.{module_name}_group_manager,1,1,1,1
```

### Security Groups XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_{module_name}" model="ir.module.category">
        <field name="name">{Module Title}</field>
        <field name="sequence">100</field>
    </record>

    <record id="{module_name}_group_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_{module_name}"/>
    </record>

    <record id="{module_name}_group_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_{module_name}"/>
        <field name="implied_ids" eval="[(4, ref('{module_name}_group_user'))]"/>
        <field name="users" eval="[(4, ref('base.user_admin'))]"/>
    </record>

    <!-- Multi-Company Record Rule: no groups = global rule.
         Eval context is user, time, company_ids, company_id (no allowed_company_ids). -->
    <record id="{model_name}_rule_company" model="ir.rule">
        <field name="name">{Model Name}: Multi-Company</field>
        <field name="model_id" ref="model_{module_name}_{model_name}"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
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

- Base classes: `odoo.tests.TransactionCase` (each test in a savepoint), `odoo.tests.HttpCase` for HTTP/tours. `odoo.addons.base.tests.common.BaseCommon` disables mail side effects but in 18 still runs as superuser; `BaseUsersCommon` adds `user_internal` / `user_portal`; `new_test_user(env, login, groups=...)` creates users.
- Default tags in 18.0 are `standard` + `at_install`. Post-install tests (required for `HttpCase`): `@tagged('post_install', '-at_install')`. Both tags -> the test runs twice; neither -> it never runs.
- Test files are `tests/test_*.py`, each imported in `tests/__init__.py`; the TestCase class must be defined in that file (imported classes are skipped); inherited `test_*` methods are only collected with `allow_inherited_tests_method = True`.
- Run one class: `--test-tags /my_module:TestMyModel`. Wrap expected error logs in `with mute_logger('odoo.sql_db'):` (`from odoo.tools import mute_logger`). Use `assertQueryCount` only in dedicated performance tests with `@warmup`.

## v18 Checklist

When generating a v18 module, ensure:

- [ ] `_check_company_auto = True` on multi-company models
- [ ] `check_company=True` on relational fields
- [ ] Field type annotations are optional (no `name: str = ...` needed)
- [ ] `@api.model_create_multi` for create methods
- [ ] Direct `invisible`/`readonly` in views (no `attrs`)
- [ ] `company_ids` in record rules (never `allowed_company_ids`)
- [ ] `SQL()` builder for raw SQL queries
- [ ] `tracking=True` for tracked fields
- [ ] Proper OWL 2.x component syntax
- [ ] Tests with `@tagged` decorator

## AI Agent Instructions

When generating an Odoo 18.0 module:

1. **Always add** `_check_company_auto = True` to models with `company_id`
2. **Always add** `check_company=True` to relational fields
3. **Use** `<list>` (not `<tree>`) and `view_mode` `list,form`; `<chatter/>` in forms
4. **Always use** `@api.model_create_multi` for create
5. **Never use** `attrs` in views
6. **Use** `company_ids` in multi-company rules
7. **Use** `SQL()` builder for any raw SQL
