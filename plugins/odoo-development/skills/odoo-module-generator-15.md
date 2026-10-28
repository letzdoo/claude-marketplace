# Odoo Module Generator - Version 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 15.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 15.0 Requirements

- **Python**: 3.7+
- **Key facts**: no `@api.multi`, `tracking=True` for field tracking, `Command` class available
- **View syntax**: `attrs` for visibility (standard)
- **OWL**: Owl 1.4 with `/** @odoo-module **/` ES modules for new components

## Breaking Changes from v14

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  NOT AVAILABLE in v15:                                                       ║
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
            '{module_name}/static/src/**/*.scss',
        ],
        # 15.0: QWeb/Owl XML templates go to web.assets_qweb (not assets_backend)
        'web.assets_qweb': [
            '{module_name}/static/src/**/*.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

- `depends`: list direct dependencies only. 15.0 does NOT add `base` automatically to an empty `depends`: if the module needs nothing else, write `'depends': ['base']`.
- `license`: missing key defaults to `LGPL-3` (with a warning) - always set it explicitly.
- `auto_install`: `True` (all of `depends`) or a list that must be a subset of `depends`.
- `assets`: globs and `('include', ...)`, `('remove', ...)`, `('prepend', ...)` directives are supported. JS/SCSS in `web.assets_backend` / `web.assets_frontend`, QWeb/Owl XML in `web.assets_qweb`. There is no `<asset>` XML tag in 15.0.
- `application: True` only for full apps; `data` loads in list order (security groups before ACL CSV before views/menus); `demo` only demo data.

## Model Template (v15)

```python
# -*- coding: utf-8 -*-
from odoo import Command, api, fields, models, _
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

    # === CRUD METHODS (v15: base create() is model_create_multi) === #
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    '{module_name}.{model_name}'
                ) or _('New')
        return super().create(vals_list)

    # === x2many OPERATIONS - v15: Command class available === #
    def action_add_line(self):
        """Command.create(...) == (0, 0, {...}); both work in 15.0."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New Line', 'amount': 0}),
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
/** @odoo-module **/
// 15.0 new web client: ES module + Owl 1.4 globals (owl / owl.hooks)
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component } = owl;
const { useState, onWillStart } = owl.hooks;

export class {ComponentName} extends Component {
    setup() {
        this.orm = useService("orm");
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
                "{module_name}.{model_name}", [], ["name", "state"]
            );
        } finally {
            this.state.loading = false;
        }
    }
}

{ComponentName}.template = "{module_name}.{ComponentName}";

registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
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

### x2many Commands (v15 - Command class available)
```python
from odoo import Command

Command.create(values)   # == (0, 0, values)
Command.update(id, values)  # == (1, id, values)
Command.delete(id)       # == (2, id, 0)
Command.unlink(id)       # == (3, id, 0)
Command.link(id)         # == (4, id, 0)
Command.clear()          # == (5, 0, 0)
Command.set(ids)         # == (6, 0, ids)
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

## Additional Rules from Odoo's Official Guidelines (verified for 15.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 15.0 source; master-only APIs are translated to the 15.0 equivalent or marked as not available.

### Structure and naming

- One model class per file, named after the model (`models/sale_order.py`); views `<model>_views.xml`, templates `<model>_templates.xml`, menus `<module>_menus.xml`, data `<module>_data.xml`, demo `<module>_demo.xml`.
- Security: `security/ir.model.access.csv` + `security/<module>_security.xml` (groups, `ir.rule`). No `ir.access.csv` in 15.0.
- Controllers: feature-named files (or `<inherited_module>.py`), `main.py` is legacy. Overriding a route: re-decorate with `@http.route()` - in 15.0 an override without the decorator silently drops the URL.
- Reports: SQL-view model `<model>_report.py`; printable reports split into `<model>_reports.xml` (action) and `<model>_templates.xml` (QWeb).
- XML ids: `<model>_view_form` / `_view_tree`, `<model>_action`, `<model>_menu`, `<module>_group_<name>`, `<model>_rule_<group>`. `id` before `model` on `<record>`; inherited views keep the parent name + `.inherit.<details>`.
- Model `_name`: dotted, module-prefixed, singular (`my_module.order`); wizards `<base_model>.<action>`; SQL reports `<base_model>.report.<action>`.
- Methods: `_compute_*`, `_search_*`, `_default_*`, `_selection_*`, `_onchange_*`, `_check_*` (constraints), `action_*` (start with `self.ensure_one()` when single-record). Non-`_` methods are RPC-callable: keep helpers private.
- Class body order: private attributes (`_name`, `_description`, `_inherit`, `_order`, `_sql_constraints`) -> default methods -> fields -> compute/inverse/search -> selection methods -> constrains/onchange -> CRUD overrides -> actions -> business methods.
- Imports: stdlib, third-party, `from odoo import Command, api, fields, models, _`, then `odoo.addons...`.

### Tests for generated modules (15.0)

```python
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, HttpCase, tagged, new_test_user
from odoo.tools import mute_logger


class TestMyModel(TransactionCase):          # default tags: standard, at_install

    @classmethod
    def setUpClass(cls):
        super().setUpClass()                  # TransactionCase is savepoint-based in 15.0
        cls.user = new_test_user(cls.env, login='my_module_user', groups='base.group_user')

    def test_constraint(self):
        with self.assertRaises(ValidationError):
            self.env['my.model'].with_user(self.user).create({...})

    @mute_logger('odoo.sql_db')
    def test_unique(self):
        ...


@tagged('post_install', '-at_install')       # HttpCase / tours must run post-install
class TestMyModelUi(HttpCase):
    def test_tour(self):
        self.start_tour('/web', 'my_module_tour', login='admin')
```

- 15.0 default tags are `standard` + `at_install`. Set exactly one of `at_install` / `post_install`: both -> the test runs twice, neither -> it never runs (`tagged()` logs a warning).
- No `BaseCommon` / `BaseUsersCommon` in 15.0; reusable fixtures: `odoo.addons.base.tests.common.TransactionCaseWithUserDemo`, `HttpCaseWithUserDemo`, `HttpCaseWithUserPortal`. `SavepointCase` is a deprecated alias.
- Test files must be named `test_*.py` AND imported in `tests/__init__.py`. TestCase classes imported into a test file are collected again (run twice) and inherited `test_*` methods are collected: keep shared base classes without `test_*` methods.
- `assertQueryCount` only in dedicated performance tests with `@warmup` (and `@users`); exceeding fails, a lower count only logs.
- Run one class: `--test-tags /my_module:TestMyModel`.

## v15 Checklist

When generating a v15 module:

- [ ] Use `tracking=True` for field tracking (NOT `track_visibility`)
- [ ] Remove any `@api.multi` decorators
- [ ] Remove any `@api.one` decorators
- [ ] Use `Command` (or tuples) for x2many operations
- [ ] Override `create` with `@api.model_create_multi`
- [ ] Use `attrs` for view visibility
- [ ] Use OWL 1.x if adding new components
- [ ] Include `assets` in manifest for JS/CSS (XML templates in `web.assets_qweb`)
- [ ] Tag HttpCase/tour tests `@tagged('post_install', '-at_install')`
- [ ] Data files in correct order in manifest

## AI Agent Instructions (v15)

When generating an Odoo 15.0 module:

1. **USE** `tracking=True` for tracked fields
2. **REMOVE** any `@api.multi` or `@api.one` decorators
3. **USE** `Command` (`from odoo import Command`) or tuples for x2many
4. **USE** `attrs` in views for visibility/readonly
5. **USE** OWL 1.x patterns (`/** @odoo-module **/`, `owl` / `owl.hooks` globals, `registry.category("actions")`)
6. **INCLUDE** `assets` key in manifest (XML templates in `web.assets_qweb`)
7. **USE** `@api.model_create_multi` for `create` overrides
8. **DO NOT** use direct `invisible`/`readonly` (v17+)
9. **FOLLOW** "Additional Rules from Odoo's Official Guidelines (verified for 15.0)" above
