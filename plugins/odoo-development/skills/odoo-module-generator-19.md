# Odoo Module Generator - Version 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 19.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 19.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  Released (final) - verified against the 19.0 source.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 19.0 Requirements

- **Python**: 3.10 - 3.14 (`odoo/release.py`)
- **Type Hints**: optional (not enforced by the framework)
- **SQL Builder**: `SQL()` recommended for raw SQL (string + params still accepted)
- **Owl**: 2.8.x (19.0 does not ship Owl 3)
- **View syntax**: Direct `invisible`/`readonly` with Python expressions; `<list>` (no `<tree>`); `<chatter/>`

## Mandatory Changes in v19

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  v19 MANDATORY:                                                              ║
║  • models.Constraint / models.Index instead of _sql_constraints (ignored)    ║
║  • group_ids (not groups_id) on res.users / ir.ui.view / act_window          ║
║  • view type 'list' and view_mode 'list,form' (no 'tree')                    ║
║  • ir.rule domains use company_ids (allowed_company_ids is NOT defined)      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## __manifest__.py Template (v19)

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '19.0.1.0.0',
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

Manifest facts (19.0, `odoo/modules/module.py`):
- `depends`: list direct dependencies only. An empty `depends` gets `['base']` injected; listing
  `base` next to other modules is redundant.
- `license`: missing -> defaults to `LGPL-3` with a warning (missing `author` also warns). Set it.
- `auto_install`: `True` (all depends) or a list that must be a subset of `depends`.
- `assets`: the manifest key for static bundles (`web.assets_backend`, `web.assets_frontend`, ...).
- `data` loads in order (security groups, then ACL csv, then views/menus); `demo` only with demo data.
- `application: True` only for full apps; `external_dependencies` for python/bin requirements.

## Model Template (v19 - Full Type Hints)

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Optional
from collections.abc import Sequence

from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL


class {ModelName}(models.Model):
    _name = '{module_name}.{model_name}'
    _description = '{Model Description}'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True

    # === BASIC FIELDS === #
    name: str = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    active: bool = fields.Boolean(default=True)
    sequence: int = fields.Integer(default=10)
    description: str = fields.Text(string='Description')

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
        tracking=True,
        check_company=True,
    )
    user_id: int = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True,
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

    # === MONETARY FIELDS === #
    currency_id: int = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    amount: float = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
    )

    # === COMPUTED FIELDS === #
    total_amount: float = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
    )

    # === SQL CONSTRAINTS / INDEXES (after the fields) === #
    # v19: `_sql_constraints` is ignored (warning only) -> models.Constraint
    _name_uniq = models.Constraint(
        'UNIQUE(company_id, name)',
        'Name must be unique per company!',
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self) -> None:
        """Compute total from lines."""
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    # === CONSTRAINTS === #
    @api.constrains('amount')
    def _check_amount(self) -> None:
        """Validate amount is positive."""
        for record in self:
            if record.amount < 0:
                raise ValidationError(_("Amount must be positive."))

    # === CRUD METHODS (type hints optional) === #
    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> '{ModelName}':
        """Create records with sequence generation."""
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    '{module_name}.{model_name}'
                ) or _('New')
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        """Write with validation."""
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if not record.line_ids:
                    raise UserError(_("Cannot complete without lines."))
        return super().write(vals)

    def unlink(self) -> bool:
        """Prevent deletion of non-draft records."""
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_("Cannot delete non-draft records."))
        return super().unlink()

    def copy(self, default: Optional[dict[str, Any]] = None) -> '{ModelName}':
        """Custom copy with name suffix."""
        default = dict(default or {})
        default.setdefault('name', _("%s (Copy)", self.name))
        return super().copy(default)

    # === x2many OPERATIONS === #
    def action_add_line(self) -> None:
        """Add a new line using Command."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New Line', 'amount': 0}),
            ]
        })

    # === ACTION METHODS === #
    def action_confirm(self) -> None:
        """Confirm records."""
        self.write({'state': 'confirmed'})

    def action_done(self) -> None:
        """Mark as done."""
        self.write({'state': 'done'})

    def action_cancel(self) -> None:
        """Cancel records."""
        self.write({'state': 'cancelled'})

    def action_draft(self) -> None:
        """Reset to draft."""
        self.write({'state': 'draft'})

    # === SQL OPERATIONS (v19 - SQL() recommended) === #
    def _get_report_data(self) -> list[dict[str, Any]]:
        """Use SQL builder for all raw SQL queries."""
        query = SQL(
            """
            SELECT
                m.id,
                m.name,
                m.state,
                COALESCE(SUM(l.amount), 0) as total
            FROM %s m
            LEFT JOIN %s l ON l.parent_id = m.id
            WHERE m.company_id IN %s
            GROUP BY m.id, m.name, m.state
            ORDER BY m.create_date DESC
            """,
            SQL.identifier(self._table),
            SQL.identifier('{module_name}_{model_name}_line'),
            tuple(self.env.companies.ids),
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    # === SEARCH === #
    # v19: name_search() searches on display_name; there is no _name_search hook
    # in BaseModel anymore. Declare the searched fields (class attribute, placed
    # with the other private attributes at the top of the class):
    #     _rec_names_search = ['name', 'description']
    # or override _search_display_name(self, operator, value) -> Domain.

    # === RETURN ACTION METHODS === #
    def action_view_records(self) -> dict[str, Any]:
        """Return action to view records."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': '{module_name}.{model_name}',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {'default_partner_id': self.partner_id.id},
        }
```

## View Templates (v19)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <!-- v19: Direct Python expressions -->
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
                <chatter/>
            </form>
        </field>
    </record>
</odoo>
```

## Owl Component (v19, Owl 2.8.x)

```javascript
/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";  // v19: user is an object, not a service

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";
    static props = {
        recordId: { type: Number, optional: true },
        mode: { type: String, optional: true },
        onSelect: { type: Function, optional: true },
    };

    setup() {
        // Services
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.user = user;

        // State
        this.state = useState({
            data: [],
            loading: true,
            error: null,
            selectedId: null,
        });

        // Refs
        this.containerRef = useRef("container");

        // Lifecycle
        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            console.log("Component mounted");
        });
    }

    async loadData() {
        try {
            const data = await this.orm.searchRead(
                "{module_name}.{model_name}",
                [],
                ["name", "state", "amount"],
                { limit: 100, order: "create_date DESC" }
            );
            this.state.data = data;
        } catch (error) {
            this.state.error = error.message;
            this.notification.add("Failed to load data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onItemClick(item) {
        this.state.selectedId = item.id;
        if (this.props.onSelect) {
            this.props.onSelect(item.id);
        }
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "{module_name}.{model_name}",
            res_id: item.id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    onRefresh() {
        this.state.loading = true;
        this.loadData();
    }
}

registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

## Owl Template (v19)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="{module_name}.{ComponentName}">
        <div t-ref="container" class="o_{component_name} p-3">
            <!-- Loading state -->
            <t t-if="state.loading">
                <div class="o_loading d-flex justify-content-center align-items-center p-5">
                    <i class="fa fa-spinner fa-spin fa-2x me-2"/>
                    <span>Loading...</span>
                </div>
            </t>

            <!-- Error state -->
            <t t-elif="state.error">
                <div class="alert alert-danger">
                    <i class="fa fa-exclamation-triangle me-2"/>
                    <t t-esc="state.error"/>
                    <button class="btn btn-link" t-on-click="onRefresh">Retry</button>
                </div>
            </t>

            <!-- Content -->
            <t t-else="">
                <div class="o_header d-flex justify-content-between align-items-center mb-3">
                    <h2>Records</h2>
                    <button class="btn btn-primary" t-on-click="onRefresh">
                        <i class="fa fa-refresh me-1"/>
                        Refresh
                    </button>
                </div>

                <t t-if="state.data.length">
                    <div class="o_list">
                        <t t-foreach="state.data" t-as="item" t-key="item.id">
                            <div t-att-class="{'o_item p-3 mb-2 border rounded': true, 'bg-primary-subtle': item.id === state.selectedId}"
                                 t-on-click="() => this.onItemClick(item)"
                                 style="cursor: pointer;">
                                <div class="d-flex justify-content-between">
                                    <strong t-esc="item.name"/>
                                    <span t-attf-class="badge bg-{{ item.state === 'done' ? 'success' : item.state === 'cancelled' ? 'danger' : 'secondary' }}">
                                        <t t-esc="item.state"/>
                                    </span>
                                </div>
                                <div class="text-muted">
                                    Amount: <t t-esc="item.amount"/>
                                </div>
                            </div>
                        </t>
                    </div>
                </t>

                <t t-else="">
                    <div class="o_nocontent_help text-center p-5">
                        <p class="o_view_nocontent_smiling_face">No records found</p>
                        <p>Create your first record to get started.</p>
                    </div>
                </t>
            </t>
        </div>
    </t>
</templates>
```

## Security (v19)

Files: `security/ir.model.access.csv` + `security/<module>_security.xml` (groups, rules).
There is NO `ir.access` / `ir.access.csv` in 19.0.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- v19: ir.rule eval context provides user, company_ids, company_id
         (allowed_company_ids is NOT defined there) -->
    <record id="{model_name}_rule_company" model="ir.rule">
        <field name="name">{Model Name}: Multi-Company</field>
        <field name="model_id" ref="model_{module_name}_{model_name}"/>
        <field name="domain_force">[('company_id', 'in', company_ids + [False])]</field>
    </record>
</odoo>
```

## Additional Rules from Odoo's Official Guidelines (verified for 19.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were
checked against the 19.0 source; master-only APIs are translated to the 19.0 equivalent or marked
as not available.

### Structure and naming
- One model per file named after the model (`models/sale_order.py`); views
  `views/<model>_views.xml`, templates `*_templates.xml`, menus `*_menus.xml`, data
  `data/*_data.xml`, demo `demo/*_demo.xml`.
- Controllers: feature-named files (or `<inherited_module>.py`); `main.py` is legacy.
- Reports: SQL-view model in `<model>_report.py`; printable report split into
  `<model>_reports.xml` (action) and `<model>_templates.xml` (QWeb).
- XML ids: `<model>_view_<type>`, `<model>_action`, `<model>_menu`, `<module>_group_<name>`,
  `<model>_rule_<group>`; inheriting view: same id prefix + `.inherit.<details>` in `name`.
- No `populate/` factory directory: 19.0 `odoo-bin populate` duplicates existing records.

### Model naming and body order
- `_name` dotted, module-prefixed, singular (`my_module.order`); wizards `<base_model>.<action>`;
  SQL reports `<base_model>.report.<action>`. Relational fields end in `_id` / `_ids`.
- Method prefixes: `_compute_`, `_inverse_`, `_search_`, `_default_`, `_selection_`, `_onchange_`,
  `_check_`, `action_*` (starts with `self.ensure_one()` when it acts on one record).
- Methods are private (`_`) by default; a public method is RPC-callable with attacker-chosen
  arguments. Use `@api.private` for public names that must not be exposed.
- Body order: private attributes (`_name`, `_inherit`, `_order`, `_rec_names_search`, ...) ->
  default methods -> fields -> `models.Constraint` / `models.Index` attributes ->
  compute/inverse/search -> selection -> `@api.constrains` / `@api.onchange` -> CRUD overrides ->
  actions -> business methods.
- Imports: stdlib, third-party, `odoo`, `odoo.addons`; e.g. `from odoo import Command, api, fields, models`.

### Generated tests
- Base classes: `TransactionCase`, `HttpCase`; for business tests prefer
  `odoo.addons.base.tests.common.BaseCommon` (mail side effects disabled, `cls.company`,
  `cls.currency`, `cls.partner`, group refs) or `TransactionCaseWithUserDemo`. `SavepointCase`
  does not exist.
- Default tags are `standard` + `at_install`. For post-install tests use
  `@tagged('post_install', '-at_install')` - exactly one of the two must remain, otherwise the
  test runs twice (both) or never (neither).
- Test files must be named `test_*.py` and imported in `tests/__init__.py`; classes imported
  from another file are skipped; inherited `test_*` methods need `allow_inherited_tests_method = True`.

```python
from odoo.addons.base.tests.common import BaseCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestMyModel(BaseCommon):

    def test_confirm(self):
        record = self.env['{module_name}.{model_name}'].create({'name': 'Test'})
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
```

## v19 Checklist

When generating a v19 module:

- [ ] `models.Constraint` / `models.Index` instead of `_sql_constraints`
- [ ] `<list>` views and `view_mode` `'list,form'`; `<chatter/>` in forms
- [ ] `group_ids` (not `groups_id`) wherever groups are set
- [ ] Record rules use `company_ids` / `company_id` / `user`
- [ ] `SQL()` builder for raw SQL (recommended)
- [ ] `_check_company_auto = True` + `check_company=True` on multi-company models
- [ ] `@api.model_create_multi` for create
- [ ] `Command` class for x2many
- [ ] Direct `invisible`/`readonly` in views
- [ ] Owl 2 patterns (`@odoo/owl` as shipped in 19.0)
- [ ] Tests tagged deliberately (`at_install` default, or `post_install` + `-at_install`)

## AI Agent Instructions (v19)

When generating an Odoo 19.0 module:

1. **USE** `models.Constraint` / `models.Index` / `models.UniqueIndex` - `_sql_constraints` is ignored
2. **USE** `list` views / `'list,form'` and `<chatter/>`
3. **USE** `group_ids` for groups on users, views and actions
4. **USE** `company_ids` in record rules (not `allowed_company_ids`)
5. **USE** `@api.model_create_multi` for create
6. **PREFER** `SQL()` for raw SQL; never interpolate values into SQL strings
7. **USE** Owl 2 patterns (19.0 ships Owl 2.8.x); there is no Owl 3 / `computed`
8. Type hints are optional - add them where they help readability
9. **DO NOT** use master-only APIs (`ir.access`, `bearer_scope`, Owl `computed`)
