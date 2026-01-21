# Agent Quick Reference Card

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  QUICK REFERENCE CARD FOR AI AGENTS                                          ║
║  Fast lookup for version patterns, file loading, and common operations       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Pattern Matrix

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| `@api.multi` | ⚠️ DEP | ❌ | ❌ | ❌ | ❌ | ❌ |
| `track_visibility` | ⚠️ DEP | ⚠️ DEP | ❌ | ❌ | ❌ | ❌ |
| `tracking=True` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `attrs=` in views | ✅ | ✅ | ⚠️ DEP | ❌ | ❌ | ❌ |
| `invisible=` expr | ❌ | ❌ | ✅ | ✅ REQ | ✅ REQ | ✅ REQ |
| Tuple x2many | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| `Command` class | ❌ | ❌ | ✅ REC | ✅ REC | ✅ REC | ✅ REC |
| `@api.model` create | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ❌ |
| `@api.model_create_multi` | ❌ | ✅ OPT | ✅ REC | ✅ REQ | ✅ REQ | ✅ REQ |
| `_check_company_auto` | ❌ | ❌ | ❌ | ❌ | ✅ REC | ✅ REQ |
| `check_company=True` | ❌ | ❌ | ❌ | ❌ | ✅ REC | ✅ REQ |
| `SQL()` builder | ❌ | ❌ | ❌ | ❌ | ✅ REC | ✅ REQ |
| Type hints | ❌ | ❌ | ❌ | ❌ | ✅ REC | ✅ REQ |
| OWL version | ❌ | 1.x | 2.x | 2.x | 2.x | 3.x |

**Legend**: ✅ = Use, ❌ = Don't use, ⚠️ DEP = Deprecated, REQ = Required, REC = Recommended, OPT = Optional

## File Loading by Task

### Generate New Module
```
READ: odoo-module-generator-{version}.md
READ: odoo-model-patterns-{version}.md
READ: odoo-security-guide-{version}.md
IF OWL: READ odoo-owl-components-{version}.md
```

### Review Module
```
READ: odoo-model-patterns-{version}.md
READ: odoo-security-guide-{version}.md
READ: odoo-performance-guide.md
```

### Upgrade Module
```
FOR EACH hop in migration_path:
  READ: odoo-module-generator-{source}-{target}.md
  READ: odoo-model-patterns-{source}-{target}.md
  READ: odoo-security-guide-{source}-{target}.md
  IF OWL: READ odoo-owl-components-{source}-{target}.md
```

## Manifest Data File Order

```python
'data': [
    # 1. Security (groups MUST come first)
    'security/my_module_security.xml',   # Groups defined here
    'security/ir.model.access.csv',       # References groups

    # 2. Data files
    'data/sequences.xml',
    'data/mail_templates.xml',

    # 3. Views (reference models and may reference groups)
    'views/my_model_views.xml',
    'views/res_partner_views.xml',        # Inherited views

    # 4. Menus (reference views/actions)
    'views/menuitems.xml',

    # 5. Reports
    'report/my_report.xml',
]
```

## Version-Specific Code Templates

### v14-v15 Create Method
```python
@api.model
def create(self, vals):
    return super().create(vals)
```

### v16+ Create Method
```python
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

### v14-v16 View Visibility
```xml
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>
```

### v17+ View Visibility
```xml
<field name="partner_id"
       invisible="state == 'draft'"/>
```

### v18+ Multi-Company Model
```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
```

### v18+ Record Rule
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        ('company_id', 'in', allowed_company_ids)
    ]</field>
</record>
```

### v19+ Method with Type Hints
```python
def action_confirm(self) -> bool:
    for record in self:
        record.state = 'confirmed'
    return True

@api.model_create_multi
def create(self, vals_list: list[dict]) -> 'MyModel':
    return super().create(vals_list)
```

### v19+ SQL Query
```python
from odoo.tools import SQL

self.env.cr.execute(SQL(
    "SELECT id FROM my_model WHERE state = %s",
    'draft'
))
```

## GitHub Verification URLs

| Version | Raw URL Base |
|---------|--------------|
| 14.0 | `https://raw.githubusercontent.com/odoo/odoo/14.0/` |
| 15.0 | `https://raw.githubusercontent.com/odoo/odoo/15.0/` |
| 16.0 | `https://raw.githubusercontent.com/odoo/odoo/16.0/` |
| 17.0 | `https://raw.githubusercontent.com/odoo/odoo/17.0/` |
| 18.0 | `https://raw.githubusercontent.com/odoo/odoo/18.0/` |
| 19.0 | `https://raw.githubusercontent.com/odoo/odoo/master/` |

### Key Reference Files
- ORM: `odoo/models.py`
- Fields: `odoo/fields.py`
- API: `odoo/api.py`
- Sale (example): `addons/sale/models/sale_order.py`
- Views (example): `addons/sale/views/sale_order_views.xml`

## Common Field Types

```python
# String
name = fields.Char(required=True, index=True, tracking=True)
description = fields.Text()
html_content = fields.Html(sanitize=True)

# Numeric
sequence = fields.Integer(default=10)
quantity = fields.Float(digits='Product Unit of Measure')
amount = fields.Monetary(currency_field='currency_id')

# Date/Time
date = fields.Date(default=fields.Date.context_today)
datetime = fields.Datetime(default=fields.Datetime.now)

# Boolean
active = fields.Boolean(default=True)

# Selection
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
], default='draft', tracking=True)

# Relations
company_id = fields.Many2one('res.company', required=True,
    default=lambda self: self.env.company)
partner_id = fields.Many2one('res.partner', tracking=True)
line_ids = fields.One2many('my.model.line', 'model_id', copy=True)
tag_ids = fields.Many2many('my.model.tag')

# Computed
total = fields.Float(compute='_compute_total', store=True)
```

## Security Group XML Template

```xml
<record id="group_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="base.module_category_services"/>
</record>

<record id="group_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="category_id" ref="base.module_category_services"/>
    <field name="implied_ids" eval="[(4, ref('group_user'))]"/>
</record>
```

## Access Rights CSV Template

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,group_manager,1,1,1,1
```

## Error Patterns by Version

| Error | Likely Version Issue |
|-------|---------------------|
| `'api' has no attribute 'multi'` | Using @api.multi in v15+ |
| `attrs attribute is no longer supported` | Using attrs in v17+ |
| `create() takes 2 positional arguments` | Using single create() in v17+ |
| `check_company failed` | Missing check_company in v18+ |
| `SQL string query deprecated` | Using string SQL in v19 |

## Input Parameter Defaults

```json
{
  "module_name": "REQUIRED",
  "module_description": "REQUIRED",
  "odoo_version": "REQUIRED - ask if not provided",
  "target_apps": [],
  "ui_stack": "classic",
  "multi_company": false,
  "multi_currency": false,
  "security_level": "basic",
  "performance_critical": false,
  "include_tests": true,
  "include_demo": false
}
```

## Output Structure

```json
{
  "status": "success",
  "module_name": "my_module",
  "odoo_version": "18.0",
  "files": {
    "__manifest__.py": "...",
    "__init__.py": "...",
    "models/__init__.py": "...",
    "models/my_model.py": "...",
    "views/my_model_views.xml": "...",
    "views/menuitems.xml": "...",
    "security/my_module_security.xml": "...",
    "security/ir.model.access.csv": "..."
  },
  "version_notes": ["..."],
  "warnings": [],
  "github_verified": true
}
```
