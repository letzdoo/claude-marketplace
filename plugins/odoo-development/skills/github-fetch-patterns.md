# GitHub Fetch Patterns for Agents

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  GITHUB FETCH PATTERNS                                                       ║
║  Concrete patterns for fetching and verifying Odoo code from GitHub          ║
║  Use WebFetch tool with these URLs and prompts                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Raw URL Format

```
https://raw.githubusercontent.com/odoo/odoo/{branch}/{path}
```

### Version Branch Mapping
| Version | Branch | Raw Base URL |
|---------|--------|--------------|
| 14.0 | `14.0` | `https://raw.githubusercontent.com/odoo/odoo/14.0/` |
| 15.0 | `15.0` | `https://raw.githubusercontent.com/odoo/odoo/15.0/` |
| 16.0 | `16.0` | `https://raw.githubusercontent.com/odoo/odoo/16.0/` |
| 17.0 | `17.0` | `https://raw.githubusercontent.com/odoo/odoo/17.0/` |
| 18.0 | `18.0` | `https://raw.githubusercontent.com/odoo/odoo/18.0/` |
| 19.0 | `master` | `https://raw.githubusercontent.com/odoo/odoo/master/` |

---

## Core Framework Files

### ORM and Models

| File | Path | Verification Use |
|------|------|------------------|
| models.py | `odoo/models.py` | Model class structure, _check_company_auto |
| fields.py | `odoo/fields.py` | Field types, Command class |
| api.py | `odoo/api.py` | Decorators (@api.model, @api.depends) |
| sql.py | `odoo/tools/sql.py` | SQL() builder (v18+) |

### WebFetch Commands

```
# Verify model structure
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/odoo/models.py
Prompt: "Show the Model class definition and _check_company_auto attribute handling"

# Verify Command class
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/odoo/fields.py
Prompt: "Show the Command class definition and all its methods (create, update, delete, link, etc.)"

# Verify API decorators
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/odoo/api.py
Prompt: "Show all available decorators and their signatures (@api.model, @api.model_create_multi, @api.depends, @api.constrains, @api.onchange)"

# Verify SQL builder (v18+)
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/odoo/tools/sql.py
Prompt: "Show the SQL class and how to use it for safe query execution"
```

---

## Reference Module Patterns

### Sale Module (Complex Workflow)

```
# Model with workflow
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order.py
Prompt: "Show the SaleOrder model definition including: 1) class attributes, 2) state field, 3) create method, 4) action_confirm method"

# Line model
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order_line.py
Prompt: "Show how sale.order.line is defined with computed fields and constraints"

# Views
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/views/sale_order_views.xml
Prompt: "Show the form view with visibility expressions and button definitions"

# Security
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/security/sale_security.xml
Prompt: "Show the security group definitions and their hierarchy"

URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/security/ir.model.access.csv
Prompt: "Show the access rights format for sale models"
```

### Mail Thread (Chatter Integration)

```
# Mail thread mixin
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/mail/models/mail_thread.py
Prompt: "Show how to inherit mail.thread and implement tracking"

# Activity mixin
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/mail/models/mail_activity_mixin.py
Prompt: "Show how to inherit mail.activity.mixin for activity support"
```

### Multi-Company (v18+ Pattern)

```
# Company mixin
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/base/models/res_company.py
Prompt: "Show how company_id field is defined in base models"

# Multi-company record rule
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/security/sale_security.xml
Prompt: "Show the multi-company record rule using allowed_company_ids"
```

---

## Version-Specific Verification Patterns

### v14 Patterns

```
# @api.multi usage (deprecated but present)
URL: https://raw.githubusercontent.com/odoo/odoo/14.0/addons/sale/models/sale_order.py
Prompt: "Check if @api.multi decorator is used and how"

# track_visibility
URL: https://raw.githubusercontent.com/odoo/odoo/14.0/addons/sale/models/sale_order.py
Prompt: "Show fields using track_visibility attribute"

# attrs in views
URL: https://raw.githubusercontent.com/odoo/odoo/14.0/addons/sale/views/sale_order_views.xml
Prompt: "Show how attrs attribute is used for visibility"
```

### v15 Patterns

```
# Verify @api.multi removed
URL: https://raw.githubusercontent.com/odoo/odoo/15.0/odoo/api.py
Prompt: "Confirm @api.multi is not present"

# tracking attribute
URL: https://raw.githubusercontent.com/odoo/odoo/15.0/addons/sale/models/sale_order.py
Prompt: "Show fields using tracking=True attribute"

# OWL 1.x
URL: https://raw.githubusercontent.com/odoo/odoo/15.0/addons/web/static/src/core/
Prompt: "Show OWL component structure and owl.tags usage"
```

### v16 Patterns

```
# Command class introduced
URL: https://raw.githubusercontent.com/odoo/odoo/16.0/odoo/fields.py
Prompt: "Show the Command class and its methods"

# attrs deprecation warning
URL: https://raw.githubusercontent.com/odoo/odoo/16.0/odoo/tools/view_validation.py
Prompt: "Show attrs deprecation handling"

# OWL 2.x imports
URL: https://raw.githubusercontent.com/odoo/odoo/16.0/addons/web/static/src/core/utils/hooks.js
Prompt: "Show useState and useService hooks"
```

### v17 Patterns

```
# attrs REMOVED - verify error
URL: https://raw.githubusercontent.com/odoo/odoo/17.0/odoo/tools/view_validation.py
Prompt: "Show that attrs attribute raises error"

# @api.model_create_multi required
URL: https://raw.githubusercontent.com/odoo/odoo/17.0/addons/sale/models/sale_order.py
Prompt: "Show create method uses @api.model_create_multi"

# inline visibility
URL: https://raw.githubusercontent.com/odoo/odoo/17.0/addons/sale/views/sale_order_views.xml
Prompt: "Show invisible attribute with expression syntax"
```

### v18 Patterns

```
# _check_company_auto
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order.py
Prompt: "Show _check_company_auto = True and check_company field attributes"

# SQL() builder
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/odoo/tools/sql.py
Prompt: "Show SQL class for query building"

# Type hints (recommended)
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order.py
Prompt: "Show methods with type hints"
```

### v19 Patterns

```
# SQL() required
URL: https://raw.githubusercontent.com/odoo/odoo/master/odoo/sql_db.py
Prompt: "Show that string SQL is deprecated/removed"

# Type hints required
URL: https://raw.githubusercontent.com/odoo/odoo/master/addons/sale/models/sale_order.py
Prompt: "Show mandatory type hints on methods"

# OWL 3.x
URL: https://raw.githubusercontent.com/odoo/odoo/master/addons/web/static/src/core/utils/hooks.js
Prompt: "Show OWL 3.x hook patterns"
```

---

## Pattern Verification Workflow

### Step 1: Determine What to Verify

```python
VERIFICATION_MATRIX = {
    "model_create": {
        "14": ("addons/sale/models/sale_order.py", "Show create method with @api.model"),
        "15": ("addons/sale/models/sale_order.py", "Show create method"),
        "16": ("addons/sale/models/sale_order.py", "Show create method with @api.model_create_multi optional"),
        "17": ("addons/sale/models/sale_order.py", "Show create method with @api.model_create_multi required"),
        "18": ("addons/sale/models/sale_order.py", "Show create method with @api.model_create_multi and type hints"),
        "19": ("addons/sale/models/sale_order.py", "Show create method with @api.model_create_multi, type hints required"),
    },
    "view_visibility": {
        "14": ("addons/sale/views/sale_order_views.xml", "Show attrs usage for visibility"),
        "15": ("addons/sale/views/sale_order_views.xml", "Show attrs usage for visibility"),
        "16": ("addons/sale/views/sale_order_views.xml", "Show attrs (deprecated) or invisible expression"),
        "17": ("addons/sale/views/sale_order_views.xml", "Show invisible expression syntax only"),
        "18": ("addons/sale/views/sale_order_views.xml", "Show invisible expression syntax"),
        "19": ("addons/sale/views/sale_order_views.xml", "Show invisible expression syntax"),
    },
    "multi_company": {
        "14": ("addons/sale/models/sale_order.py", "Show company_id field definition"),
        "15": ("addons/sale/models/sale_order.py", "Show company_id field definition"),
        "16": ("addons/sale/models/sale_order.py", "Show company_id field definition"),
        "17": ("addons/sale/models/sale_order.py", "Show company_id field definition"),
        "18": ("addons/sale/models/sale_order.py", "Show _check_company_auto and check_company attributes"),
        "19": ("addons/sale/models/sale_order.py", "Show _check_company_auto and check_company required"),
    },
    "sql_queries": {
        "14": ("odoo/sql_db.py", "Show cr.execute with string SQL"),
        "15": ("odoo/sql_db.py", "Show cr.execute with string SQL"),
        "16": ("odoo/sql_db.py", "Show cr.execute with string SQL"),
        "17": ("odoo/sql_db.py", "Show cr.execute with string SQL"),
        "18": ("odoo/tools/sql.py", "Show SQL() builder recommended"),
        "19": ("odoo/tools/sql.py", "Show SQL() builder required"),
    },
}
```

### Step 2: Build Fetch URL

```python
def get_verification_url(version: str, path: str) -> str:
    branch = "master" if version == "19" else f"{version}.0"
    return f"https://raw.githubusercontent.com/odoo/odoo/{branch}/{path}"
```

### Step 3: Execute Verification

```python
def verify_pattern(version: str, pattern_type: str):
    """
    Agent workflow for pattern verification.

    1. Look up pattern in VERIFICATION_MATRIX
    2. Build GitHub raw URL
    3. Use WebFetch with specific prompt
    4. Compare with generated code
    """
    if pattern_type in VERIFICATION_MATRIX:
        path, prompt = VERIFICATION_MATRIX[pattern_type][version]
        url = get_verification_url(version, path)
        # Use WebFetch tool
        # URL: {url}
        # Prompt: {prompt}
```

---

## Quick Reference: Most Used Fetch Commands

### For Any Version - Core Patterns

```
# Model definition
URL: https://raw.githubusercontent.com/odoo/odoo/{version}/addons/sale/models/sale_order.py
Prompt: "Extract the model class definition, _name, _inherit, _description, and key field definitions"

# View structure
URL: https://raw.githubusercontent.com/odoo/odoo/{version}/addons/sale/views/sale_order_views.xml
Prompt: "Extract the form view structure showing header, sheet, and field layouts"

# Security groups
URL: https://raw.githubusercontent.com/odoo/odoo/{version}/addons/sale/security/sale_security.xml
Prompt: "Extract group definitions and implied_ids hierarchy"

# Access rights
URL: https://raw.githubusercontent.com/odoo/odoo/{version}/addons/sale/security/ir.model.access.csv
Prompt: "Extract the CSV format and permission patterns"

# Manifest
URL: https://raw.githubusercontent.com/odoo/odoo/{version}/addons/sale/__manifest__.py
Prompt: "Extract the manifest structure including depends, data, assets"
```

---

## Verification Checklist

Before generating code, verify these patterns:

| Pattern | What to Check | File |
|---------|---------------|------|
| Create method | Decorator type | sale_order.py |
| Field tracking | tracking vs track_visibility | sale_order.py |
| View visibility | attrs vs invisible expression | sale_order_views.xml |
| Company handling | _check_company_auto, check_company | sale_order.py |
| SQL queries | String vs SQL() builder | sale_order.py |
| OWL imports | owl.tags vs @odoo/owl | hooks.js |
| Record rules | domain syntax, allowed_company_ids | sale_security.xml |

---

## Agent Instructions

```
VERIFICATION PROTOCOL FOR AGENTS:

1. IDENTIFY version from user input
2. SELECT appropriate branch (14.0, 15.0, 16.0, 17.0, 18.0, or master for 19)
3. FETCH reference file using WebFetch:
   - URL: https://raw.githubusercontent.com/odoo/odoo/{branch}/{path}
   - Prompt: Specific extraction request
4. COMPARE your generated code with official pattern
5. ADJUST if patterns differ
6. DOCUMENT any version-specific notes

ALWAYS verify when generating:
- Model create methods (decorator changes between versions)
- View visibility expressions (attrs removal in v17)
- Multi-company patterns (v18+ requirements)
- SQL queries (v19 SQL() requirement)
- OWL components (major changes each version)
```
