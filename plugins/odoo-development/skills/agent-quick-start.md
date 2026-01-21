# Agent Quick Start Guide

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  AGENT QUICK START                                                           ║
║  30-second guide to using this plugin for autonomous Odoo development        ║
║  Read this FIRST before any operation                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## The ONE Rule

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   🚨 IDENTIFY ODOO VERSION FIRST - ALWAYS 🚨                                │
│                                                                             │
│   Before generating ANY code, you MUST know the target Odoo version.        │
│   If user doesn't specify → ASK: "What Odoo version? (14-19)"               │
│   Then load version-specific skill files.                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3-Step Quick Process

### Step 1: Get Version
```
User says: "Create a module for..."
You respond: "What Odoo version are you targeting?"
         OR: Look for version in existing code/manifest
```

### Step 2: Load Skills
```python
version = "18"  # Example

# Always load:
skills = [
    f"odoo-module-generator-{version}.md",
    f"odoo-model-patterns-{version}.md",
    f"odoo-security-guide-{version}.md",
]

# If OWL/frontend:
skills.append(f"odoo-owl-components-{version}.md")

# If upgrading from X to Y:
skills.append(f"odoo-version-knowledge-{X}-{Y}.md")
```

### Step 3: Generate Code
```
Use ONLY patterns from loaded version-specific files.
NEVER mix patterns from different versions.
```

---

## Version Quick Matrix

| If Version | Use These Patterns |
|------------|-------------------|
| **14** | `@api.multi`, `track_visibility`, `attrs`, tuples for x2many |
| **15** | NO `@api.multi`, `tracking=True`, `attrs`, OWL 1.x |
| **16** | `Command` class, `attrs` (deprecated), OWL 2.x |
| **17** | NO `attrs`, `@api.model_create_multi`, inline expressions |
| **18** | `_check_company_auto`, `check_company=True`, SQL() builder |
| **19** | Type hints required, SQL() required, OWL 3.x |

---

## File Loading Cheat Sheet

### Generate New Module
```
READ: odoo-module-generator-{version}.md
READ: odoo-model-patterns-{version}.md
READ: odoo-security-guide-{version}.md
IF OWL: READ odoo-owl-components-{version}.md
```

### Review Existing Module
```
READ: odoo-model-patterns-{version}.md
READ: odoo-security-guide-{version}.md
READ: odoo-performance-guide.md
READ: odoo-troubleshooting-guide.md
```

### Upgrade Module (X → Y)
```
FOR each version hop:
  READ: odoo-version-knowledge-{X}-{Y}.md
  READ: odoo-module-generator-{X}-{Y}.md
  READ: odoo-model-patterns-{X}-{Y}.md
```

---

## Manifest Data Order (CRITICAL)

```python
# Security MUST come before views - ALWAYS
'data': [
    # 1. Security groups (defines groups)
    'security/module_security.xml',
    # 2. Access rights (uses groups)
    'security/ir.model.access.csv',
    # 3. Data files
    'data/data.xml',
    # 4. Views (uses groups for visibility)
    'views/model_views.xml',
    # 5. Menus (uses views/actions)
    'views/menuitems.xml',
]
```

---

## Code Templates by Version

### v17+ Model
```python
from odoo import api, fields, models

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft')

    @api.model_create_multi  # REQUIRED v17+
    def create(self, vals_list):
        return super().create(vals_list)
```

### v18+ Model
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True  # ADD for v18+

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)  # ADD for v18+

    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> 'MyModel':  # ADD type hints
        return super().create(vals_list)
```

### v17+ View
```xml
<!-- NO attrs - use inline expressions -->
<field name="partner_id" invisible="state == 'draft'"/>
<button name="action" invisible="state != 'draft'"/>
```

---

## GitHub Verification URLs

```
https://raw.githubusercontent.com/odoo/odoo/{version}/addons/sale/models/sale_order.py
https://raw.githubusercontent.com/odoo/odoo/{version}/addons/sale/views/sale_order_views.xml

Version branches: 14.0, 15.0, 16.0, 17.0, 18.0, master (for 19)
```

---

## Error Quick Fixes

| Error | Fix |
|-------|-----|
| `'api' has no attribute 'multi'` | Remove @api.multi (v15+) |
| `attrs not supported` | Use `invisible="expr"` (v17+) |
| `create() takes 2 args` | Use @api.model_create_multi (v17+) |
| `check_company failed` | Add check_company=True (v18+) |
| `External ID not found` | Check manifest data order |

---

## Minimum Viable Input

```json
{
  "module_name": "my_module",
  "module_description": "My module description",
  "odoo_version": "18.0"
}
```

## Full Input Example

```json
{
  "module_name": "sale_approval",
  "module_description": "Sales approval workflow",
  "odoo_version": "18.0",
  "target_apps": ["sale", "mail"],
  "multi_company": true,
  "security_level": "advanced",
  "include_tests": true,
  "models": [
    {
      "name": "sale.approval.rule",
      "description": "Approval Rule",
      "fields": [
        {"name": "name", "type": "Char", "required": true},
        {"name": "amount", "type": "Monetary"}
      ]
    }
  ]
}
```

---

## Reference Skills

| Need | Load |
|------|------|
| Generate module | `odoo-module-generator-{v}.md` |
| Model patterns | `odoo-model-patterns-{v}.md` |
| Security config | `odoo-security-guide-{v}.md` |
| OWL components | `odoo-owl-components-{v}.md` |
| Upgrade path | `odoo-version-knowledge-{X}-{Y}.md` |
| Performance | `odoo-performance-guide.md` |
| Testing | `odoo-test-patterns.md` |
| Troubleshooting | `odoo-troubleshooting-guide.md` |
| Full examples | `end-to-end-examples.md` |
| API reference | `agent-api-reference.md` |

---

## Output Format

```json
{
  "status": "success",
  "module_name": "my_module",
  "odoo_version": "18.0",
  "files": {
    "__manifest__.py": "...",
    "models/my_model.py": "...",
    "views/my_model_views.xml": "...",
    "security/ir.model.access.csv": "..."
  },
  "version_notes": ["Note 1", "Note 2"],
  "warnings": []
}
```

---

**START HERE**: Identify version → Load skills → Generate code → Verify → Output
