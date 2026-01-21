# End-to-End Generation Examples

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  END-TO-END GENERATION EXAMPLES                                              ║
║  Complete input → output examples for autonomous agent operation             ║
║  Copy these patterns for consistent module generation                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Example 1: Equipment Tracking Module (v18)

### User Request
```
"Create a module to track company equipment assigned to employees.
It should have equipment items with serial numbers, assignment history,
and maintenance schedules. Use Odoo 18 with multi-company support."
```

### Agent Analysis
```json
{
  "identified_requirements": {
    "module_name": "equipment_tracking",
    "odoo_version": "18.0",
    "multi_company": true,
    "target_apps": ["hr", "maintenance"],
    "models_needed": [
      "equipment.item",
      "equipment.assignment",
      "equipment.maintenance"
    ],
    "features": ["workflow", "mail_thread", "tracking"]
  }
}
```

### Input to Workflow
```json
{
  "module_name": "equipment_tracking",
  "module_description": "Track company equipment with employee assignments and maintenance schedules",
  "odoo_version": "18.0",
  "target_apps": ["hr", "maintenance"],
  "ui_stack": "classic",
  "multi_company": true,
  "multi_currency": false,
  "security_level": "advanced",
  "performance_critical": false,
  "include_tests": true,
  "include_demo": true,
  "models": [
    {
      "name": "equipment.item",
      "description": "Equipment Item",
      "inherit_mail": true,
      "has_workflow": true,
      "workflow_states": [
        {"value": "available", "label": "Available"},
        {"value": "assigned", "label": "Assigned"},
        {"value": "maintenance", "label": "In Maintenance"},
        {"value": "retired", "label": "Retired"}
      ],
      "fields": [
        {"name": "name", "type": "Char", "required": true, "tracking": true},
        {"name": "serial_number", "type": "Char", "index": true},
        {"name": "category_id", "type": "Many2one", "comodel_name": "equipment.category"},
        {"name": "employee_id", "type": "Many2one", "comodel_name": "hr.employee", "tracking": true},
        {"name": "purchase_date", "type": "Date"},
        {"name": "purchase_value", "type": "Monetary"},
        {"name": "assignment_ids", "type": "One2many", "comodel_name": "equipment.assignment", "inverse_name": "equipment_id"}
      ]
    },
    {
      "name": "equipment.category",
      "description": "Equipment Category",
      "fields": [
        {"name": "name", "type": "Char", "required": true},
        {"name": "code", "type": "Char"},
        {"name": "parent_id", "type": "Many2one", "comodel_name": "equipment.category"}
      ]
    },
    {
      "name": "equipment.assignment",
      "description": "Equipment Assignment History",
      "fields": [
        {"name": "equipment_id", "type": "Many2one", "comodel_name": "equipment.item", "required": true},
        {"name": "employee_id", "type": "Many2one", "comodel_name": "hr.employee", "required": true},
        {"name": "date_assigned", "type": "Date", "required": true},
        {"name": "date_returned", "type": "Date"},
        {"name": "notes", "type": "Text"}
      ]
    }
  ]
}
```

### Generated Output

#### File Tree
```
equipment_tracking/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── equipment_item.py
│   ├── equipment_category.py
│   └── equipment_assignment.py
├── views/
│   ├── equipment_item_views.xml
│   ├── equipment_category_views.xml
│   ├── equipment_assignment_views.xml
│   └── menuitems.xml
├── security/
│   ├── equipment_tracking_security.xml
│   └── ir.model.access.csv
├── data/
│   └── demo_data.xml
└── tests/
    ├── __init__.py
    ├── common.py
    └── test_equipment_item.py
```

#### __manifest__.py
```python
{
    'name': 'Equipment Tracking',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Track company equipment with employee assignments and maintenance schedules',
    'description': """
Equipment Tracking
==================

This module provides:
* Equipment item management with serial numbers
* Employee assignment tracking with history
* Maintenance scheduling
* Multi-company support

Version Notes (v18):
* Uses _check_company_auto for automatic company validation
* Uses @api.model_create_multi for batch creation
* Uses inline visibility expressions in views
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['hr', 'maintenance', 'mail'],
    'data': [
        # Security (MUST be first)
        'security/equipment_tracking_security.xml',
        'security/ir.model.access.csv',
        # Views
        'views/equipment_item_views.xml',
        'views/equipment_category_views.xml',
        'views/equipment_assignment_views.xml',
        'views/menuitems.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

#### models/equipment_item.py
```python
from odoo import api, fields, models
from odoo.exceptions import UserError


class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _description = 'Equipment Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _order = 'name'

    name = fields.Char(
        string='Equipment Name',
        required=True,
        tracking=True,
        index=True,
    )
    serial_number = fields.Char(
        string='Serial Number',
        index='btree_not_null',
        copy=False,
    )
    state = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('assigned', 'Assigned'),
            ('maintenance', 'In Maintenance'),
            ('retired', 'Retired'),
        ],
        string='Status',
        default='available',
        required=True,
        tracking=True,
    )
    category_id = fields.Many2one(
        comodel_name='equipment.category',
        string='Category',
        check_company=True,
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Assigned To',
        tracking=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='company_id.currency_id',
    )
    purchase_date = fields.Date(string='Purchase Date')
    purchase_value = fields.Monetary(
        string='Purchase Value',
        currency_field='currency_id',
    )
    assignment_ids = fields.One2many(
        comodel_name='equipment.assignment',
        inverse_name='equipment_id',
        string='Assignment History',
    )
    assignment_count = fields.Integer(
        string='Assignments',
        compute='_compute_assignment_count',
    )

    def _compute_assignment_count(self) -> None:
        for record in self:
            record.assignment_count = len(record.assignment_ids)

    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> 'EquipmentItem':
        return super().create(vals_list)

    def action_assign(self) -> bool:
        """Assign equipment to employee."""
        for record in self:
            if record.state != 'available':
                raise UserError(f"Equipment '{record.name}' is not available for assignment.")
            if not record.employee_id:
                raise UserError("Please select an employee before assigning.")
            record.state = 'assigned'
            self.env['equipment.assignment'].create({
                'equipment_id': record.id,
                'employee_id': record.employee_id.id,
                'date_assigned': fields.Date.today(),
            })
        return True

    def action_return(self) -> bool:
        """Return equipment from employee."""
        for record in self:
            if record.state != 'assigned':
                raise UserError(f"Equipment '{record.name}' is not currently assigned.")
            # Close current assignment
            current_assignment = record.assignment_ids.filtered(
                lambda a: not a.date_returned
            )
            current_assignment.write({'date_returned': fields.Date.today()})
            record.write({
                'state': 'available',
                'employee_id': False,
            })
        return True

    def action_retire(self) -> bool:
        """Retire equipment."""
        for record in self:
            if record.state == 'assigned':
                raise UserError(f"Cannot retire assigned equipment '{record.name}'. Return it first.")
            record.state = 'retired'
        return True

    def action_view_assignments(self) -> dict:
        """Open assignment history."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignment History',
            'res_model': 'equipment.assignment',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }
```

#### views/equipment_item_views.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View -->
    <record id="equipment_item_view_form" model="ir.ui.view">
        <field name="name">equipment.item.form</field>
        <field name="model">equipment.item</field>
        <field name="arch" type="xml">
            <form string="Equipment">
                <header>
                    <button name="action_assign"
                            type="object"
                            string="Assign"
                            class="btn-primary"
                            invisible="state != 'available' or not employee_id"/>
                    <button name="action_return"
                            type="object"
                            string="Return"
                            invisible="state != 'assigned'"/>
                    <button name="action_retire"
                            type="object"
                            string="Retire"
                            invisible="state in ('assigned', 'retired')"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="available,assigned,maintenance,retired"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_assignments"
                                type="object"
                                class="oe_stat_button"
                                icon="fa-history">
                            <field name="assignment_count" widget="statinfo"
                                   string="Assignments"/>
                        </button>
                    </div>
                    <widget name="web_ribbon" title="Retired"
                            bg_color="bg-danger"
                            invisible="state != 'retired'"/>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Equipment Name"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="serial_number"/>
                            <field name="category_id"/>
                            <field name="employee_id"/>
                        </group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="purchase_date"/>
                            <field name="purchase_value"/>
                            <field name="currency_id" invisible="1"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Assignment History" name="assignments">
                            <field name="assignment_ids" readonly="1">
                                <tree>
                                    <field name="employee_id"/>
                                    <field name="date_assigned"/>
                                    <field name="date_returned"/>
                                    <field name="notes"/>
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

    <!-- Tree View -->
    <record id="equipment_item_view_tree" model="ir.ui.view">
        <field name="name">equipment.item.tree</field>
        <field name="model">equipment.item</field>
        <field name="arch" type="xml">
            <tree string="Equipment">
                <field name="name"/>
                <field name="serial_number"/>
                <field name="category_id"/>
                <field name="employee_id"/>
                <field name="state" widget="badge"
                       decoration-success="state == 'available'"
                       decoration-info="state == 'assigned'"
                       decoration-warning="state == 'maintenance'"
                       decoration-danger="state == 'retired'"/>
                <field name="company_id" groups="base.group_multi_company"/>
            </tree>
        </field>
    </record>

    <!-- Search View -->
    <record id="equipment_item_view_search" model="ir.ui.view">
        <field name="name">equipment.item.search</field>
        <field name="model">equipment.item</field>
        <field name="arch" type="xml">
            <search string="Search Equipment">
                <field name="name"/>
                <field name="serial_number"/>
                <field name="employee_id"/>
                <separator/>
                <filter name="available" string="Available"
                        domain="[('state', '=', 'available')]"/>
                <filter name="assigned" string="Assigned"
                        domain="[('state', '=', 'assigned')]"/>
                <filter name="maintenance" string="In Maintenance"
                        domain="[('state', '=', 'maintenance')]"/>
                <separator/>
                <group expand="0" string="Group By">
                    <filter name="group_category" string="Category"
                            context="{'group_by': 'category_id'}"/>
                    <filter name="group_state" string="Status"
                            context="{'group_by': 'state'}"/>
                    <filter name="group_employee" string="Employee"
                            context="{'group_by': 'employee_id'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="equipment_item_action" model="ir.actions.act_window">
        <field name="name">Equipment</field>
        <field name="res_model">equipment.item</field>
        <field name="view_mode">tree,form,kanban</field>
        <field name="context">{'search_default_available': 1}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first equipment item
            </p>
        </field>
    </record>
</odoo>
```

#### security/equipment_tracking_security.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Category -->
    <record id="module_category_equipment" model="ir.module.category">
        <field name="name">Equipment</field>
        <field name="sequence">30</field>
    </record>

    <!-- Groups -->
    <record id="group_equipment_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_equipment"/>
    </record>

    <record id="group_equipment_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_equipment"/>
        <field name="implied_ids" eval="[(4, ref('group_equipment_user'))]"/>
    </record>

    <!-- Record Rules -->
    <record id="equipment_item_rule_company" model="ir.rule">
        <field name="name">Equipment Item: Multi-company</field>
        <field name="model_id" ref="model_equipment_item"/>
        <field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>
    </record>
</odoo>
```

#### security/ir.model.access.csv
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_equipment_item_user,equipment.item.user,model_equipment_item,group_equipment_user,1,1,1,0
access_equipment_item_manager,equipment.item.manager,model_equipment_item,group_equipment_manager,1,1,1,1
access_equipment_category_user,equipment.category.user,model_equipment_category,group_equipment_user,1,0,0,0
access_equipment_category_manager,equipment.category.manager,model_equipment_category,group_equipment_manager,1,1,1,1
access_equipment_assignment_user,equipment.assignment.user,model_equipment_assignment,group_equipment_user,1,0,0,0
access_equipment_assignment_manager,equipment.assignment.manager,model_equipment_assignment,group_equipment_manager,1,1,1,1
```

#### tests/test_equipment_item.py
```python
from odoo.tests import tagged
from odoo.exceptions import UserError
from .common import TestEquipmentCommon


@tagged('post_install', '-at_install')
class TestEquipmentItem(TestEquipmentCommon):
    """Unit tests for equipment.item model"""

    def test_create_equipment(self):
        """Test basic equipment creation"""
        equipment = self.env['equipment.item'].create({
            'name': 'Test Laptop',
            'serial_number': 'SN-TEST-001',
        })
        self.assertTrue(equipment.id)
        self.assertEqual(equipment.state, 'available')
        self.assertEqual(equipment.company_id, self.env.company)

    def test_assign_equipment(self):
        """Test equipment assignment workflow"""
        self.equipment.employee_id = self.employee
        self.equipment.action_assign()

        self.assertEqual(self.equipment.state, 'assigned')
        self.assertEqual(len(self.equipment.assignment_ids), 1)
        self.assertEqual(
            self.equipment.assignment_ids[0].employee_id,
            self.employee
        )

    def test_assign_unavailable_fails(self):
        """Test that assigning unavailable equipment fails"""
        self.equipment.state = 'maintenance'
        self.equipment.employee_id = self.employee

        with self.assertRaises(UserError):
            self.equipment.action_assign()

    def test_return_equipment(self):
        """Test equipment return workflow"""
        self.equipment.employee_id = self.employee
        self.equipment.action_assign()
        self.equipment.action_return()

        self.assertEqual(self.equipment.state, 'available')
        self.assertFalse(self.equipment.employee_id)
        self.assertTrue(self.equipment.assignment_ids[0].date_returned)

    def test_retire_equipment(self):
        """Test equipment retirement"""
        self.equipment.action_retire()
        self.assertEqual(self.equipment.state, 'retired')

    def test_retire_assigned_fails(self):
        """Test that retiring assigned equipment fails"""
        self.equipment.employee_id = self.employee
        self.equipment.action_assign()

        with self.assertRaises(UserError):
            self.equipment.action_retire()

    def test_multi_company_isolation(self):
        """Test multi-company record isolation"""
        # Create equipment in main company
        equipment_c1 = self.env['equipment.item'].create({
            'name': 'Company 1 Equipment',
            'company_id': self.env.company.id,
        })

        # User in company 2 should not see it
        visible = self.env['equipment.item'].with_user(
            self.user_company2
        ).search([])
        self.assertNotIn(equipment_c1.id, visible.ids)
```

### Version Notes Generated
```json
{
  "version_notes": [
    "Using _check_company_auto = True for automatic multi-company validation (v18 pattern)",
    "Using @api.model_create_multi for batch record creation (required in v17+)",
    "Using inline visibility expressions in views (attrs removed in v17)",
    "Using check_company=True on relational fields for cross-company validation (v18 pattern)",
    "Using allowed_company_ids in record rules (v18 pattern)",
    "Using btree_not_null index type for serial_number (v16+ optimization)"
  ]
}
```

---

## Example 2: Quick Module for v17 (Minimal)

### User Request
```
"Create a simple task priority module for Odoo 17"
```

### Minimal Input
```json
{
  "module_name": "task_priority",
  "module_description": "Add priority levels to project tasks",
  "odoo_version": "17.0",
  "target_apps": ["project"],
  "inherit_models": [
    {
      "model": "project.task",
      "fields": [
        {
          "name": "x_priority_level",
          "type": "Selection",
          "string": "Priority Level",
          "selection": [
            ["low", "Low"],
            ["medium", "Medium"],
            ["high", "High"],
            ["critical", "Critical"]
          ],
          "tracking": true
        }
      ]
    }
  ]
}
```

### Generated Output (v17 Pattern)

#### models/project_task.py
```python
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_priority_level = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Priority Level',
        tracking=True,
    )
```

#### views/project_task_views.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="project_task_view_form_inherit" model="ir.ui.view">
        <field name="name">project.task.form.inherit.priority</field>
        <field name="model">project.task</field>
        <field name="inherit_id" ref="project.view_task_form2"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='user_ids']" position="after">
                <field name="x_priority_level"/>
            </xpath>
        </field>
    </record>

    <record id="project_task_view_tree_inherit" model="ir.ui.view">
        <field name="name">project.task.tree.inherit.priority</field>
        <field name="model">project.task</field>
        <field name="inherit_id" ref="project.view_task_tree2"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='stage_id']" position="after">
                <field name="x_priority_level" widget="badge"
                       decoration-success="x_priority_level == 'low'"
                       decoration-info="x_priority_level == 'medium'"
                       decoration-warning="x_priority_level == 'high'"
                       decoration-danger="x_priority_level == 'critical'"
                       optional="show"/>
            </xpath>
        </field>
    </record>
</odoo>
```

---

## Example 3: Upgrade Example (v16 → v18)

### Input
```json
{
  "workflow": "upgrade_module",
  "source_version": "16.0",
  "target_version": "18.0",
  "module_path": "/path/to/my_module"
}
```

### Original Code (v16)
```python
# models/my_model.py (v16)
from odoo import api, fields, models

class MyModel(models.Model):
    _name = 'my.model'

    company_id = fields.Many2one('res.company')
    partner_id = fields.Many2one('res.partner')

    @api.model
    def create(self, vals):
        return super().create(vals)
```

```xml
<!-- views/my_views.xml (v16) -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>
```

### Migration Output

#### Updated Code (v18)
```python
# models/my_model.py (v18)
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # ADDED for v18

    company_id = fields.Many2one(
        'res.company',
        required=True,  # ADDED
        default=lambda self: self.env.company,  # ADDED
    )
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # ADDED for v18
    )

    @api.model_create_multi  # CHANGED from @api.model
    def create(self, vals_list: list[dict]) -> 'MyModel':  # CHANGED signature + type hints
        return super().create(vals_list)
```

```xml
<!-- views/my_views.xml (v18) -->
<field name="partner_id"
       invisible="state == 'draft'"/>  <!-- CHANGED from attrs -->
```

#### Migration Script
```python
# migrations/18.0.1.0.0/pre-migration.py
def migrate(cr, version):
    """Pre-migration: Ensure company_id has values"""
    cr.execute("""
        UPDATE my_model
        SET company_id = (SELECT id FROM res_company LIMIT 1)
        WHERE company_id IS NULL
    """)
```

---

## Agent Execution Summary

```
WORKFLOW EXECUTION PATTERN:

1. RECEIVE user request
2. PARSE requirements → structured input
3. VALIDATE input against schema
4. DETERMINE version → load skills
5. VERIFY patterns via GitHub (critical patterns only)
6. GENERATE files in correct order
7. VALIDATE generated code
8. OUTPUT with version notes and file tree

ALWAYS REMEMBER:
- Security files BEFORE views in manifest
- Version-specific patterns are MANDATORY
- Multi-company requires _check_company_auto (v18+)
- Create uses @api.model_create_multi (v17+)
- Views use inline expressions (v17+)
```
