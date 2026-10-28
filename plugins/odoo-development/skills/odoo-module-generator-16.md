# Odoo Module Generator - Version 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 16.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 16.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 16.0 Requirements

- **Python**: 3.7 - 3.12
- **Key Features**: `Command` class (since 15.0), `attrs`/`states` view modifiers, OWL 2.x
- **View syntax**: `attrs="{'invisible': [...]}"` / `states="..."` for record-dependent modifiers

## IMPORTANT: View modifiers in 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  v16 view modifiers:                                                         ║
║  - record-dependent invisible/readonly/required: attrs (domains) or states   ║
║  - invisible="state == 'draft'" does NOT work in 16.0 (evaluated with only   ║
║    `context`); Python expressions are 17.0+                                  ║
║  - @api.model_create_multi: always (single-dict create logs a WARNING)       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## IMPORTANT: Data File Ordering

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  The ORDER of files in the 'data' list is CRITICAL.                          ║
║  A resource can ONLY be referenced AFTER it has been defined.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

`data` loads in list order (groups before ACL CSV before views before menus); `demo` is loaded as noupdate.

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

Manifest facts (16.0, `odoo/modules/module.py`):
- `depends`: list direct dependencies only. 16.0 does NOT inject `base` for an empty list - write `'depends': ['base']` when there is no other dependency.
- `license`: if missing, defaults to `LGPL-3` with a WARNING - always set it.
- `auto_install`: `True` (all `depends`) or a list that must be a subset of `depends` (asserted).
- `assets`: the manifest key exists (`'web.assets_backend'`, `'web.assets_frontend'`, ...); there is no `<asset>` XML tag in 16.0.
- `external_dependencies`: `{'python': [...], 'bin': [...]}`; `application: True` only for full apps.

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

## View Templates (v16 - attrs / states)

### Recommended Pattern

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <!-- v16: states= shorthand or attrs with a domain -->
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary" states="draft"/>
                    <button name="action_done" string="Done" type="object"
                            states="confirmed"/>
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

### 16.0 vs 17.0 (one view file cannot serve both)

```xml
<!-- 16.0 (correct here; converted to expressions when migrating to 17.0) -->
<button name="action_confirm" string="Confirm"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>

<!-- 17.0+ only - in 16.0 this is evaluated with just `context` and fails -->
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

Files: `security/ir.model.access.csv` (the CSV file name selects the model; there is no `ir.access.csv` in 16.0) and `security/<module>_security.xml` (groups, rules).

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

    <!-- Multi-Company Rule (global = no groups; `global` is computed, never set it) -->
    <record id="rule_{model_name}_company" model="ir.rule">
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

## Additional Rules from Odoo's Official Guidelines (verified for 16.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 16.0 source; master-only APIs are translated to the 16.0 equivalent or marked as not available.

### Structure and naming
- One model per file named after the model (`models/sale_order.py`); views `views/<model>_views.xml`, `views/<module>_menus.xml`, QWeb `views/<model>_templates.xml`, data `data/<module>_data.xml`, demo `demo/<module>_demo.xml`. Security files: see Security Templates.
- Controllers: `controllers/<feature>.py` or `controllers/<inherited_module>.py` (`main.py` is legacy). Reports: SQL-view model `report/<model>_report.py`; printable reports `report/<model>_reports.xml` + `report/<model>_templates.xml`.
- Optional `populate/` directory for the 16.0 populate framework.
- XML ids: `<model>_view_form|tree|search`, `<model>_action`, `<model>_menu`, `<module>_group_<name>`, `<model>_rule_<group>`; in `<record>` put `id` before `model`; `name` first among the fields. `<data noupdate="1">` or `<odoo noupdate="1">` for data the user may edit. `active="False"` on `<template>` is applied on install only.
- CSS classes prefixed `o_<module>_...`; no styling by id.

### Python conventions
- `_name` dotted, module-prefixed, singular (`my_module.order`); wizards `<base_model>.<action>`; SQL reports `<base_model>.report.<action>`.
- Imports: stdlib / third-party / `odoo` / `odoo.addons`; `from odoo import Command, api, fields, models, _`.
- Method prefixes: `_compute_`, `_search_`, `_default_`, `_selection_`, `_onchange_`, `_check_`, `action_*` (starting with `self.ensure_one()` if it handles one record); everything not meant for RPC starts with `_` (or `@api.private`).
- Class body order: private attributes (`_name`, `_description`, `_inherit`, `_order`, `_sql_constraints`) -> default methods -> fields -> compute/inverse/search -> selection -> constrains/onchange -> CRUD overrides -> actions -> business methods.
- Variables: model classes PascalCase (`Partner = self.env['res.partner']`); `*_id`/`*_ids` variables hold ids, not records.

### Tests for generated modules
```python
# tests/__init__.py  -> from . import test_my_model   (files MUST be named test_*.py AND imported)
from odoo import Command
from odoo.tests import tagged
from odoo.addons.base.tests.common import BaseCommon   # 16.0: USD, mail-disabled ctx, cls.partner, still superuser


@tagged('post_install', '-at_install')
class TestMyModel(BaseCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'Test User', 'login': 'test_user_my_model',
            'groups_id': [Command.set([cls.env.ref('base.group_user').id])],
        })

    def test_create(self):
        record = self.env['my_module.my_model'].with_user(self.user).create({'name': 'X'})
        self.assertEqual(record.state, 'draft')
```
- Default tags in 16.0 are `standard` + `at_install`. `@tagged('post_install')` alone keeps `at_install` too (warning, test runs twice); always write `@tagged('post_install', '-at_install')`. Tours/`HttpCase` must be post-install.
- `BaseUsersCommon` (adds `user_internal`, `user_portal`), `TransactionCaseWithUserDemo`, `HttpCaseWithUserDemo` and `new_test_user(env, login=..., groups=...)` are available.
- Do not import test classes into other test files (they are collected again) and keep shared helpers in non-`test_` mixins: inherited `test_*` methods are collected in 16.0.
- Wrap expected error logs in `with mute_logger('odoo.sql_db'):` (`from odoo.tools import mute_logger`). `assertQueryCount` only in dedicated performance tests with `@warmup`/`@users`.
- Run a single class: `--test-tags /my_module:TestMyModel`.

## v16 Checklist

When generating a v16 module:

- [ ] Use `Command` class for x2many operations
- [ ] Record-dependent view modifiers via `attrs` / `states` (never `invisible="expr"`)
- [ ] Use `@api.model_create_multi` for create methods
- [ ] Use `tracking=True` for tracked fields
- [ ] Use OWL 2.x syntax for frontend components
- [ ] Include assets in manifest; `depends` contains `base` if nothing else
- [ ] Data files in correct order
- [ ] Tests tagged `post_install, -at_install` where needed

## AI Agent Instructions (v16)

When generating an Odoo 16.0 module:

1. **USE** `Command` class for x2many operations
2. **USE** `attrs="{'invisible': [...]}"` / `states="..."` for record-dependent modifiers
3. **USE** `@api.model_create_multi` for create
4. **USE** `tracking=True` for field tracking
5. **NEVER** emit `invisible="state == '...'"` (17.0+ syntax) in 16.0 views
6. **USE** OWL 2.x with `/** @odoo-module **/`
7. **INCLUDE** assets in manifest
