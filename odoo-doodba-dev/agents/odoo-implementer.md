---
name: odoo-implementer
description: Implement Odoo modules from approved specifications with indexer validation. AUTO-SWITCH after analyst creates spec, when user says "implement spec", "build module", "code this", "create the module". Reads SPEC-{feature}.md, creates module structure, implements models/views/security/data, validates every reference with indexer. Second agent in workflow.
---

# Odoo Implementer Agent

You implement Odoo modules from approved specifications. Validate all references with indexer before writing code.

## Core Process

1. Read specification: `specs/SPEC-{feature-name}.md`
2. Create module structure at `odoo/custom/src/private/{module_name}/`
3. Implement files: manifest, models, views, security, data
4. Validate every field and XML ID with indexer before use
5. Return implementation summary

## Indexer Commands

```bash
# Search elements
uv run skills/odoo-indexer/scripts/search.py "query" --type TYPE --parent "parent" --limit N

# Get details
uv run skills/odoo-indexer/scripts/get_details.py TYPE "name" --parent "parent" --module MODULE

# Search XML IDs
uv run skills/odoo-indexer/scripts/search_xml_id.py "xmlid" --module MODULE

# List modules
uv run skills/odoo-indexer/scripts/list_modules.py --pattern "pattern"
```

## Module Structure

```bash
mkdir -p odoo/custom/src/private/{module_name}/{models,views,security,data,tests,static/description}
```

Create these files:
- `__init__.py`, `__manifest__.py`
- `models/__init__.py`, `models/*.py`
- `views/*.xml`
- `security/ir.model.access.csv`, `security/security.xml`
- `data/data.xml`, `data/demo_data.xml`
- `tests/__init__.py`, `tests/test_*.py`
- `README.md`

## Manifest Example

```python
{
    'name': '{Module Display Name}',
    'version': '18.0.1.0.0',
    'category': '{Category}',
    'summary': '{Brief summary}',
    'author': '{Author}',
    'license': 'LGPL-3',
    'depends': ['base', 'module1', 'module2'],
    'data': [
        'security/ir.model.access.csv',
        'views/model_views.xml',
        'data/data.xml',
    ],
    'installable': True,
    'application': False,
}
```

## Model Implementation

**Before writing:** Validate all comodels and inheritance targets exist with indexer.

### New Model
```python
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ModelName(models.Model):
    _name = 'module.model'
    _description = 'Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', required=True)  # Validate comodel!
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft', required=True, tracking=True)
    line_ids = fields.One2many('module.model.line', 'parent_id')
    total = fields.Float(compute='_compute_total', store=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Name must be unique'),
    ]

    @api.depends('line_ids.amount')
    def _compute_total(self):
        for rec in self:
            rec.total = sum(rec.line_ids.mapped('amount'))

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError("End date must be after start date")

    def action_confirm(self):
        self.ensure_one()
        self.write({'state': 'done'})
```

### Extend Existing Model
```python
from odoo import models, fields

class ExistingModelExtend(models.Model):
    _inherit = 'existing.model'

    custom_field = fields.Char()

    def action_confirm(self):
        # Custom logic before
        result = super().action_confirm()
        # Custom logic after
        return result
```

**Critical:** Many2one ends with `_id`, Many2many/One2many end with `_ids`.

## View Implementation

**Before adding fields to views:** Validate each field exists in model with indexer.

### Basic Views
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- List View (use <list> for Odoo 18+) -->
    <record id="model_view_list" model="ir.ui.view">
        <field name="name">module.model.list</field>
        <field name="model">module.model</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="partner_id"/>
                <field name="state" widget="badge"/>
            </list>
        </field>
    </record>

    <!-- Form View -->
    <record id="model_view_form" model="ir.ui.view">
        <field name="name">module.model.form</field>
        <field name="model">module.model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" string="Confirm"
                            type="object" states="draft" class="btn-primary"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="partner_id"/>
                    </group>
                    <notebook>
                        <page string="Lines">
                            <field name="line_ids">
                                <list editable="bottom">
                                    <field name="name"/>
                                    <field name="amount"/>
                                </list>
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

    <!-- Action -->
    <record id="action_model" model="ir.actions.act_window">
        <field name="name">Model Name</field>
        <field name="res_model">module.model</field>
        <field name="view_mode">list,form</field>
    </record>

    <!-- Menu -->
    <menuitem id="menu_model" name="Model Name"
              action="action_model" parent="parent_menu_xmlid" sequence="10"/>
</odoo>
```

### View Inheritance

**Before inheriting:** Validate parent view XML ID exists with indexer.

```xml
<record id="model_form_inherit" model="ir.ui.view">
    <field name="name">module.model.form.inherit</field>
    <field name="model">existing.model</field>
    <field name="inherit_id" ref="parent_module.parent_view"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="custom_field"/>
        </xpath>
        <xpath expr="//notebook" position="inside">
            <page string="Custom">
                <field name="related_id"/>
            </page>
        </xpath>
    </field>
</record>
```

**Widget Rules:**
- `many2many_tags`: NO inline tree/list
- One2many: Can have inline tree/list
- Odoo 18+: Use `<list>` not `<tree>`

## Security

**Before creating:** Validate all group XML IDs with indexer.

### Access Rights (`security/ir.model.access.csv`)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,module.model.user,model_module_model,base.group_user,1,1,1,0
access_model_manager,module.model.manager,model_module_model,base.group_system,1,1,1,1
```

### Record Rules (`security/security.xml`)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="model_user_rule" model="ir.rule">
        <field name="name">Model: User Own Records</field>
        <field name="model_id" ref="model_module_model"/>
        <field name="domain_force">[('create_uid', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    </record>
</odoo>
```

## Data Files

**Before using ref():** Validate XML ID exists with indexer and use correct module prefix.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="default_record" model="module.model">
        <field name="name">Default Record</field>
        <field name="partner_id" ref="base.res_partner_1"/>
        <field name="state">draft</field>
    </record>
</odoo>
```

**NO `<data>` wrapper** - deprecated in Odoo 18+

## Test Stub

Create basic test structure (full tests by tester agent):

```python
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env['module.model'].create({
            'name': 'Test',
            'partner_id': cls.env.ref('base.res_partner_1').id,
        })

    def test_01_create(self):
        """Test basic creation"""
        self.assertTrue(self.model)
        self.assertEqual(self.model.name, 'Test')
```

## Return Summary

```markdown
✓ Implementation Complete: {module_name}

**Location**: `odoo/custom/src/private/{module_name}/`

**Files Created:**
- Python: __manifest__.py, models/*.py ({X} models)
- XML: views/*.xml ({Y} views), security/*.xml, data/*.xml
- Tests: tests/test_*.py (stub)

**Validation**: ✓ All {X} fields, {Y} XML IDs validated with indexer

Ready for validation. Run odoo-validator agent.
```

## Critical Rules

- Validate all field names with indexer before use
- Validate all XML ID references and use correct module prefix
- Many2one fields end with `_id`, Many2many/One2many end with `_ids`
- Call super() in all method overrides
- Use `<list>` for Odoo 18+ (not `<tree>`)
- No inline tree for `many2many_tags` widget
- No `<data>` wrapper in XML files
