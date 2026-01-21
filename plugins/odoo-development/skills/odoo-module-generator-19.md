# Odoo Module Generator - Version 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 19.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 19.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  Note: v19 is in DEVELOPMENT - patterns may change before release.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 19.0 Requirements

- **Python**: 3.12+ required
- **Type Hints**: MANDATORY on all methods
- **SQL Builder**: MANDATORY for all raw SQL
- **OWL**: 3.x (new patterns)
- **View syntax**: Direct `invisible`/`readonly` with Python expressions

## MANDATORY Features in v19

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  v19 MANDATORY REQUIREMENTS:                                                 ║
║  • Type hints on ALL method parameters and return types                      ║
║  • SQL() builder for ALL raw SQL queries                                     ║
║  • OWL 3.x patterns (OWL 2.x will not work)                                  ║
║  • Python 3.12+ syntax                                                       ║
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

    _sql_constraints = [
        ('name_uniq', 'unique(company_id, name)', 'Name must be unique per company!'),
    ]

    # === CRUD METHODS (v19 - Type hints mandatory) === #
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

    # === SQL OPERATIONS (v19 - SQL() MANDATORY) === #
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

    # === SEARCH METHODS === #
    @api.model
    def _name_search(
        self,
        name: str = '',
        domain: Optional[list[tuple[str, str, Any]]] = None,
        operator: str = 'ilike',
        limit: int = 100,
        order: Optional[str] = None,
    ) -> Sequence[int]:
        """Extended name search with type hints."""
        domain = domain or []
        if name:
            domain = [
                '|',
                ('name', operator, name),
                ('sequence', operator, name),
            ] + domain
        return self._search(domain, limit=limit, order=order)

    # === RETURN ACTION METHODS === #
    def action_view_records(self) -> dict[str, Any]:
        """Return action to view records."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': '{module_name}.{model_name}',
            'view_mode': 'tree,form',
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

## OWL 3.x Component (v19)

```javascript
/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

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
        this.user = useService("user");

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

## OWL 3.x Template (v19)

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

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- v19: Uses allowed_company_ids -->
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

## v19 Checklist

When generating a v19 module:

- [ ] Add `from __future__ import annotations`
- [ ] Type hints on ALL method parameters
- [ ] Type hints on ALL return types
- [ ] Use `SQL()` builder for ALL raw SQL
- [ ] Use `_check_company_auto = True`
- [ ] Use `check_company=True` on relational fields
- [ ] Use `@api.model_create_multi` for create
- [ ] Use `Command` class for x2many
- [ ] Use direct `invisible`/`readonly` in views
- [ ] Use `allowed_company_ids` in record rules
- [ ] Use OWL 3.x patterns
- [ ] Python 3.12+ compatible code

## AI Agent Instructions (v19)

When generating an Odoo 19.0 module:

1. **MANDATORY**: Add type hints to ALL methods
2. **MANDATORY**: Use `SQL()` for ALL raw SQL queries
3. **USE** `from __future__ import annotations`
4. **USE** `_check_company_auto = True`
5. **USE** `@api.model_create_multi` for create
6. **USE** OWL 3.x patterns
7. **USE** Python 3.12+ syntax (match statements, etc.)
8. **DO NOT** use raw SQL strings
9. **DO NOT** use OWL 2.x patterns
10. **DO NOT** use methods without type hints
