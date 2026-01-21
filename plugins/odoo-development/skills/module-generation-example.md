# Complete Module Generation Example

This document shows the complete output format for module generation, demonstrating how an AI agent should produce production-ready Odoo modules.

## Example Request

```json
{
  "module_name": "equipment_tracking",
  "module_description": "Track company equipment assets with maintenance scheduling",
  "odoo_version": "18.0",
  "target_apps": ["hr", "maintenance"],
  "ui_stack": "owl",
  "multi_company": true,
  "multi_currency": false,
  "security_level": "advanced",
  "performance_critical": false,
  "custom_models": [
    {
      "name": "equipment.asset",
      "description": "Equipment Asset",
      "inherit_mail": true,
      "fields": [
        {"name": "name", "type": "Char", "required": true, "tracking": true},
        {"name": "serial_number", "type": "Char", "index": true},
        {"name": "purchase_date", "type": "Date"},
        {"name": "status", "type": "Selection", "selection": [["active", "Active"], ["maintenance", "In Maintenance"], ["retired", "Retired"]], "default": "active"},
        {"name": "value", "type": "Monetary"},
        {"name": "assigned_employee_id", "type": "Many2one", "comodel": "hr.employee"}
      ]
    }
  ],
  "include_tests": true,
  "include_demo": true,
  "author": "My Company",
  "website": "https://mycompany.com",
  "license": "LGPL-3"
}
```

## Generated Output

### File Structure

```
equipment_tracking/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── equipment_asset.py
├── views/
│   ├── equipment_asset_views.xml
│   └── menuitems.xml
├── security/
│   ├── equipment_tracking_security.xml
│   └── ir.model.access.csv
├── data/
│   └── equipment_tracking_data.xml
├── demo/
│   └── equipment_tracking_demo.xml
├── static/
│   └── src/
│       ├── components/
│       │   └── equipment_dashboard/
│       │       ├── equipment_dashboard.js
│       │       └── equipment_dashboard.xml
│       └── scss/
│           └── equipment_tracking.scss
├── tests/
│   ├── __init__.py
│   └── test_equipment_asset.py
└── i18n/
    └── equipment_tracking.pot
```

### __manifest__.py

```python
# -*- coding: utf-8 -*-
{
    'name': 'Equipment Tracking',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Equipment',
    'summary': 'Track company equipment assets with maintenance scheduling',
    'description': """
Equipment Tracking Module
=========================

This module provides comprehensive equipment asset tracking with:
* Asset management and lifecycle tracking
* Employee assignment
* Maintenance scheduling integration
* Multi-company support

**Version Notes:**
- Odoo 18.0 compatible
- Uses _check_company_auto for multi-company validation
- Type hints on methods (v18 recommended pattern)

**Upgrade Notes:**
- From v17: No breaking changes
- To v19: Add mandatory type hints
    """,
    'author': 'My Company',
    'website': 'https://mycompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'hr', 'maintenance'],
    'data': [
        # Security first (groups defined before referenced)
        'security/equipment_tracking_security.xml',
        'security/ir.model.access.csv',
        # Data files
        'data/equipment_tracking_data.xml',
        # Views (may reference groups)
        'views/equipment_asset_views.xml',
        # Menus last (reference actions from views)
        'views/menuitems.xml',
    ],
    'demo': [
        'demo/equipment_tracking_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'equipment_tracking/static/src/**/*.js',
            'equipment_tracking/static/src/**/*.xml',
            'equipment_tracking/static/src/**/*.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

### models/__init__.py

```python
# -*- coding: utf-8 -*-
from . import equipment_asset
```

### models/equipment_asset.py

```python
# -*- coding: utf-8 -*-
from typing import Optional, Any

from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL


class EquipmentAsset(models.Model):
    _name = 'equipment.asset'
    _description = 'Equipment Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # v18: Enable automatic company validation
    _check_company_auto = True

    # === BASIC FIELDS === #
    name = fields.Char(
        string='Asset Name',
        required=True,
        tracking=True,
    )
    serial_number = fields.Char(
        string='Serial Number',
        index=True,
        tracking=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    description = fields.Text(
        string='Description',
    )

    # === DATE FIELDS === #
    purchase_date = fields.Date(
        string='Purchase Date',
        tracking=True,
    )
    warranty_expiry = fields.Date(
        string='Warranty Expiry',
    )

    # === STATUS === #
    status = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('maintenance', 'In Maintenance'),
            ('retired', 'Retired'),
        ],
        string='Status',
        default='active',
        required=True,
        tracking=True,
    )

    # === MONETARY FIELDS === #
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    value = fields.Monetary(
        string='Asset Value',
        currency_field='currency_id',
        tracking=True,
    )

    # === RELATIONAL FIELDS === #
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    assigned_employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Assigned Employee',
        tracking=True,
        check_company=True,  # v18: Automatic company validation
    )
    maintenance_request_ids = fields.One2many(
        comodel_name='maintenance.request',
        inverse_name='equipment_id',
        string='Maintenance Requests',
    )

    # === COMPUTED FIELDS === #
    maintenance_count = fields.Integer(
        string='Maintenance Count',
        compute='_compute_maintenance_count',
    )
    is_under_warranty = fields.Boolean(
        string='Under Warranty',
        compute='_compute_is_under_warranty',
    )

    @api.depends('maintenance_request_ids')
    def _compute_maintenance_count(self) -> None:
        """Compute number of maintenance requests."""
        for record in self:
            record.maintenance_count = len(record.maintenance_request_ids)

    @api.depends('warranty_expiry')
    def _compute_is_under_warranty(self) -> None:
        """Check if asset is under warranty."""
        today = fields.Date.context_today(self)
        for record in self:
            record.is_under_warranty = (
                record.warranty_expiry and record.warranty_expiry >= today
            )

    # === CONSTRAINTS === #
    @api.constrains('value')
    def _check_value(self) -> None:
        """Validate asset value is non-negative."""
        for record in self:
            if record.value < 0:
                raise ValidationError(_("Asset value cannot be negative."))

    _sql_constraints = [
        ('serial_uniq', 'unique(company_id, serial_number)',
         'Serial number must be unique per company!'),
    ]

    # === CRUD METHODS === #
    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> 'EquipmentAsset':
        """Create assets with sequence generation."""
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'equipment.asset'
                ) or _('New Asset')
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        """Write with status change notification."""
        if 'status' in vals:
            for record in self:
                record.message_post(
                    body=_("Status changed to: %s", vals['status']),
                    message_type='notification',
                )
        return super().write(vals)

    def unlink(self) -> bool:
        """Prevent deletion of assets with active maintenance."""
        for record in self:
            active_maintenance = record.maintenance_request_ids.filtered(
                lambda r: r.stage_id.done is False
            )
            if active_maintenance:
                raise UserError(
                    _("Cannot delete asset with active maintenance requests.")
                )
        return super().unlink()

    # === ACTION METHODS === #
    def action_set_active(self) -> None:
        """Set asset status to active."""
        self.write({'status': 'active'})

    def action_set_maintenance(self) -> None:
        """Set asset to maintenance status."""
        self.write({'status': 'maintenance'})

    def action_retire(self) -> None:
        """Retire the asset."""
        self.write({'status': 'retired', 'active': False})

    def action_view_maintenance(self) -> dict[str, Any]:
        """View maintenance requests for this asset."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Maintenance Requests'),
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }

    # === SQL OPERATIONS (v18 pattern) === #
    def _get_asset_statistics(self) -> list[dict[str, Any]]:
        """Get asset statistics using SQL builder."""
        query = SQL(
            """
            SELECT
                status,
                COUNT(*) as count,
                COALESCE(SUM(value), 0) as total_value
            FROM %s
            WHERE company_id IN %s
              AND active = %s
            GROUP BY status
            ORDER BY count DESC
            """,
            SQL.identifier(self._table),
            tuple(self.env.companies.ids),
            True,
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
```

### views/equipment_asset_views.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View -->
    <record id="equipment_asset_view_form" model="ir.ui.view">
        <field name="name">equipment.asset.form</field>
        <field name="model">equipment.asset</field>
        <field name="arch" type="xml">
            <form string="Equipment Asset">
                <header>
                    <button name="action_set_active"
                            string="Set Active"
                            type="object"
                            class="btn-primary"
                            invisible="status == 'active'"/>
                    <button name="action_set_maintenance"
                            string="Send to Maintenance"
                            type="object"
                            invisible="status == 'maintenance'"/>
                    <button name="action_retire"
                            string="Retire"
                            type="object"
                            invisible="status == 'retired'"
                            confirm="Are you sure you want to retire this asset?"/>
                    <field name="status" widget="statusbar"
                           statusbar_visible="active,maintenance,retired"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_maintenance"
                                type="object"
                                class="oe_stat_button"
                                icon="fa-wrench">
                            <field name="maintenance_count" widget="statinfo"
                                   string="Maintenance"/>
                        </button>
                    </div>
                    <widget name="web_ribbon" title="Retired" bg_color="bg-danger"
                            invisible="status != 'retired'"/>
                    <widget name="web_ribbon" title="Under Warranty" bg_color="bg-success"
                            invisible="not is_under_warranty"/>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Asset Name..."/>
                        </h1>
                    </div>
                    <group>
                        <group string="Asset Information">
                            <field name="serial_number"/>
                            <field name="assigned_employee_id"/>
                            <field name="purchase_date"/>
                            <field name="warranty_expiry"/>
                        </group>
                        <group string="Value &amp; Company">
                            <field name="value"/>
                            <field name="currency_id" invisible="1"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Description" name="description">
                            <field name="description"
                                   placeholder="Add description..."/>
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

    <!-- Tree View -->
    <record id="equipment_asset_view_tree" model="ir.ui.view">
        <field name="name">equipment.asset.tree</field>
        <field name="model">equipment.asset</field>
        <field name="arch" type="xml">
            <tree string="Equipment Assets"
                  decoration-muted="status == 'retired'"
                  decoration-warning="status == 'maintenance'">
                <field name="name"/>
                <field name="serial_number"/>
                <field name="assigned_employee_id"/>
                <field name="status" widget="badge"
                       decoration-success="status == 'active'"
                       decoration-warning="status == 'maintenance'"
                       decoration-danger="status == 'retired'"/>
                <field name="value" sum="Total Value"/>
                <field name="company_id" groups="base.group_multi_company"/>
            </tree>
        </field>
    </record>

    <!-- Search View -->
    <record id="equipment_asset_view_search" model="ir.ui.view">
        <field name="name">equipment.asset.search</field>
        <field name="model">equipment.asset</field>
        <field name="arch" type="xml">
            <search string="Search Assets">
                <field name="name"/>
                <field name="serial_number"/>
                <field name="assigned_employee_id"/>
                <separator/>
                <filter name="filter_active" string="Active"
                        domain="[('status', '=', 'active')]"/>
                <filter name="filter_maintenance" string="In Maintenance"
                        domain="[('status', '=', 'maintenance')]"/>
                <filter name="filter_retired" string="Retired"
                        domain="[('status', '=', 'retired')]"/>
                <separator/>
                <filter name="filter_under_warranty" string="Under Warranty"
                        domain="[('warranty_expiry', '>=', context_today().strftime('%Y-%m-%d'))]"/>
                <separator/>
                <group expand="0" string="Group By">
                    <filter name="groupby_status" string="Status"
                            context="{'group_by': 'status'}"/>
                    <filter name="groupby_employee" string="Employee"
                            context="{'group_by': 'assigned_employee_id'}"/>
                    <filter name="groupby_company" string="Company"
                            context="{'group_by': 'company_id'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Kanban View -->
    <record id="equipment_asset_view_kanban" model="ir.ui.view">
        <field name="name">equipment.asset.kanban</field>
        <field name="model">equipment.asset</field>
        <field name="arch" type="xml">
            <kanban class="o_kanban_mobile">
                <field name="name"/>
                <field name="serial_number"/>
                <field name="status"/>
                <field name="value"/>
                <field name="assigned_employee_id"/>
                <templates>
                    <t t-name="kanban-box">
                        <div class="oe_kanban_card oe_kanban_global_click">
                            <div class="oe_kanban_content">
                                <div class="o_kanban_record_top">
                                    <strong class="o_kanban_record_title">
                                        <field name="name"/>
                                    </strong>
                                    <field name="status" widget="badge"/>
                                </div>
                                <div class="o_kanban_record_bottom">
                                    <div class="oe_kanban_bottom_left">
                                        <field name="serial_number"/>
                                    </div>
                                    <div class="oe_kanban_bottom_right">
                                        <field name="value" widget="monetary"/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>

    <!-- Action -->
    <record id="equipment_asset_action" model="ir.actions.act_window">
        <field name="name">Equipment Assets</field>
        <field name="res_model">equipment.asset</field>
        <field name="view_mode">tree,kanban,form</field>
        <field name="search_view_id" ref="equipment_asset_view_search"/>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first equipment asset
            </p>
            <p>
                Track and manage company equipment with maintenance scheduling.
            </p>
        </field>
    </record>
</odoo>
```

### security/equipment_tracking_security.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Module Category -->
    <record id="module_category_equipment_tracking" model="ir.module.category">
        <field name="name">Equipment Tracking</field>
        <field name="sequence">50</field>
    </record>

    <!-- User Group -->
    <record id="group_equipment_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_equipment_tracking"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>

    <!-- Manager Group -->
    <record id="group_equipment_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_equipment_tracking"/>
        <field name="implied_ids" eval="[(4, ref('group_equipment_user'))]"/>
        <field name="users" eval="[(4, ref('base.user_root')), (4, ref('base.user_admin'))]"/>
    </record>

    <!-- Multi-Company Rule (v18: uses allowed_company_ids) -->
    <record id="rule_equipment_asset_company" model="ir.rule">
        <field name="name">Equipment Asset: Multi-Company</field>
        <field name="model_id" ref="model_equipment_asset"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', allowed_company_ids)
        ]</field>
    </record>
</odoo>
```

### security/ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_equipment_asset_user,equipment.asset.user,model_equipment_asset,group_equipment_user,1,1,1,0
access_equipment_asset_manager,equipment.asset.manager,model_equipment_asset,group_equipment_manager,1,1,1,1
```

### static/src/components/equipment_dashboard/equipment_dashboard.js

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class EquipmentDashboard extends Component {
    static template = "equipment_tracking.EquipmentDashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            stats: null,
            loading: true,
        });

        onWillStart(async () => {
            await this.loadStats();
        });
    }

    async loadStats() {
        try {
            const stats = await this.orm.call(
                "equipment.asset",
                "_get_asset_statistics",
                []
            );
            this.state.stats = stats;
        } finally {
            this.state.loading = false;
        }
    }

    async onViewAssets(status) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Equipment Assets",
            res_model: "equipment.asset",
            view_mode: "tree,form",
            domain: status ? [["status", "=", status]] : [],
        });
    }
}

registry.category("actions").add("equipment_tracking.dashboard", EquipmentDashboard);
```

### tests/test_equipment_asset.py

```python
# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestEquipmentAsset(TransactionCase):
    """Test cases for Equipment Asset model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Asset = cls.env['equipment.asset']
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
        })

    def test_create_asset(self):
        """Test basic asset creation."""
        asset = self.Asset.create({
            'name': 'Test Laptop',
            'serial_number': 'SN001',
        })
        self.assertEqual(asset.status, 'active')
        self.assertTrue(asset.active)

    def test_asset_value_constraint(self):
        """Test that negative values are rejected."""
        with self.assertRaises(ValidationError):
            self.Asset.create({
                'name': 'Test Asset',
                'value': -100,
            })

    def test_retire_asset(self):
        """Test asset retirement."""
        asset = self.Asset.create({
            'name': 'Test Asset',
        })
        asset.action_retire()
        self.assertEqual(asset.status, 'retired')
        self.assertFalse(asset.active)

    def test_unique_serial_number(self):
        """Test serial number uniqueness per company."""
        self.Asset.create({
            'name': 'Asset 1',
            'serial_number': 'SN001',
        })
        with self.assertRaises(Exception):
            self.Asset.create({
                'name': 'Asset 2',
                'serial_number': 'SN001',
            })
```

## Structured JSON Output

```json
{
  "module_skeleton": {
    "name": "equipment_tracking",
    "version": "18.0.1.0.0",
    "odoo_version": "18.0",
    "file_count": 15,
    "files": [
      "__init__.py",
      "__manifest__.py",
      "models/__init__.py",
      "models/equipment_asset.py",
      "views/equipment_asset_views.xml",
      "views/menuitems.xml",
      "security/equipment_tracking_security.xml",
      "security/ir.model.access.csv",
      "data/equipment_tracking_data.xml",
      "demo/equipment_tracking_demo.xml",
      "static/src/components/equipment_dashboard/equipment_dashboard.js",
      "static/src/components/equipment_dashboard/equipment_dashboard.xml",
      "static/src/scss/equipment_tracking.scss",
      "tests/__init__.py",
      "tests/test_equipment_asset.py"
    ]
  },
  "version_compliance": {
    "version": "18.0",
    "patterns_used": [
      "_check_company_auto = True",
      "@api.model_create_multi",
      "check_company=True on fields",
      "SQL() builder for raw SQL",
      "Type hints on methods",
      "Direct invisible/readonly in views",
      "allowed_company_ids in record rules",
      "OWL 2.x components"
    ]
  },
  "dependencies": ["base", "mail", "hr", "maintenance"],
  "security_groups": [
    "group_equipment_user",
    "group_equipment_manager"
  ],
  "github_verified": true,
  "generation_date": "2026-01-16"
}
```
