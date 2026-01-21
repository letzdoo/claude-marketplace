# Odoo Version Knowledge - Complete Reference (All Versions)

This document provides a comprehensive reference for Odoo version differences, deprecations, and migration paths across all supported versions.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMPLETE DEPRECATION AND CHANGE REFERENCE                                   ║
║  Versions: 14.0 - 19.0                                                       ║
║  Use version-specific files for detailed implementation patterns.            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Complete Deprecation Timeline

### Decorators

| Decorator | v14 | v15 | v16 | v17 | v18 | v19 |
|-----------|-----|-----|-----|-----|-----|-----|
| `@api.multi` | ⚠️ DEP | ❌ REM | ❌ | ❌ | ❌ | ❌ |
| `@api.one` | ⚠️ DEP | ❌ REM | ❌ | ❌ | ❌ | ❌ |
| `@api.returns` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.model` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.model_create_multi` | ➖ | ⚠️ REC | ⚠️ REC | ✅ REQ | ✅ REQ | ✅ REQ |
| `@api.depends` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.constrains` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.onchange` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.depends_context` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Legend: ✅ = Supported, ⚠️ DEP = Deprecated, ⚠️ REC = Recommended, ✅ REQ = Required, ❌ REM = Removed, ➖ = Not available

### Field Attributes

| Attribute | v14 | v15 | v16 | v17 | v18 | v19 |
|-----------|-----|-----|-----|-----|-----|-----|
| `track_visibility` | ⚠️ DEP | ❌ REM | ❌ | ❌ | ❌ | ❌ |
| `tracking` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `oldname` | ⚠️ DEP | ❌ REM | ❌ | ❌ | ❌ | ❌ |
| `check_company` | ➖ | ➖ | ➖ | ➖ | ✅ | ✅ |
| Type hints on fields | ➖ | ➖ | ➖ | ➖ | ⚠️ REC | ✅ REQ |

### View Attributes

| Attribute | v14 | v15 | v16 | v17 | v18 | v19 |
|-----------|-----|-----|-----|-----|-----|-----|
| `attrs` | ✅ | ✅ | ⚠️ DEP | ❌ REM | ❌ | ❌ |
| `states` | ✅ | ✅ | ⚠️ DEP | ❌ REM | ❌ | ❌ |
| Direct `invisible` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| Direct `readonly` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| Direct `required` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| Python expressions | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |

### x2many Operations

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| Tuple commands `(0, 0, {...})` | ✅ | ✅ | ⚠️ DEP | ⚠️ DEP | ⚠️ DEP | ❌ REM |
| `Command.create({...})` | ➖ | ➖ | ✅ | ✅ REQ | ✅ REQ | ✅ REQ |
| `Command.update(id, {...})` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| `Command.delete(id)` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| `Command.unlink(id)` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| `Command.link(id)` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| `Command.clear()` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| `Command.set([ids])` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |

### Model Attributes

| Attribute | v14 | v15 | v16 | v17 | v18 | v19 |
|-----------|-----|-----|-----|-----|-----|-----|
| `_check_company_auto` | ➖ | ➖ | ➖ | ➖ | ✅ | ✅ |
| `_parent_store` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `_order` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `_rec_name` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### SQL Operations

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| Raw SQL strings | ✅ | ✅ | ✅ | ✅ | ⚠️ DEP | ❌ REM |
| `SQL()` builder | ➖ | ➖ | ➖ | ➖ | ✅ | ✅ REQ |
| `SQL.identifier()` | ➖ | ➖ | ➖ | ➖ | ✅ | ✅ REQ |

### JavaScript/OWL

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| `odoo.define()` | ✅ | ⚠️ DEP | ❌ REM | ❌ | ❌ | ❌ |
| ES modules | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@odoo-module` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OWL 1.x | ➖ | ✅ | ❌ | ❌ | ❌ | ❌ |
| OWL 2.x | ➖ | ➖ | ✅ | ✅ | ✅ | ❌ |
| OWL 3.x | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ |

### Security/Rules

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| `company_ids` in rules | ✅ | ✅ | ✅ | ⚠️ DEP | ❌ REM | ❌ |
| `allowed_company_ids` | ➖ | ➖ | ➖ | ✅ | ✅ | ✅ |
| `user.company_id` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `user.company_ids` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Python Version Requirements

| Odoo Version | Python Min | Python Recommended |
|--------------|------------|-------------------|
| 14.0 | 3.6 | 3.8 |
| 15.0 | 3.8 | 3.10 |
| 16.0 | 3.8 | 3.10 |
| 17.0 | 3.10 | 3.11 |
| 18.0 | 3.11 | 3.12 |
| 19.0 | 3.12 | 3.12 |

## Manifest Changes Across Versions

### v14-v15 Manifest
```python
{
    'name': 'Module',
    'version': '15.0.1.0.0',
    'depends': ['base'],
    'data': ['views/views.xml'],
}
```

### v16+ Manifest (Assets)
```python
{
    'name': 'Module',
    'version': '18.0.1.0.0',
    'depends': ['base'],
    'data': ['views/views.xml'],
    'assets': {
        'web.assets_backend': [
            'module/static/src/**/*.js',
            'module/static/src/**/*.xml',
            'module/static/src/**/*.scss',
        ],
    },
}
```

## Migration Path Summary

### v14 → v15
1. Remove `@api.multi` decorator
2. Replace `track_visibility` with `tracking`
3. Adopt OWL 1.x for new components
4. Update Python to 3.8+

### v15 → v16
1. Adopt `Command` class for x2many
2. Move assets to manifest `assets` key
3. Start using direct `invisible`/`readonly`
4. Migrate to OWL 2.x patterns

### v16 → v17
1. **MUST** remove all `attrs` usage
2. **MUST** remove all `states` usage
3. **MUST** use `@api.model_create_multi`
4. Convert to Python expression syntax
5. Update Python to 3.10+

### v17 → v18
1. Add `_check_company_auto = True`
2. Add `check_company=True` to fields
3. Start using `SQL()` builder
4. Add type hints to methods
5. Use `allowed_company_ids` in rules

### v18 → v19
1. **MUST** add type hints everywhere
2. **MUST** use `SQL()` for all raw SQL
3. Migrate to OWL 3.x
4. Update Python to 3.12+

## Quick Reference Cards

### v18 Model Template
```python
from typing import Optional
from odoo import api, fields, models, Command, _
from odoo.tools import SQL

class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> 'MyModel':
        return super().create(vals_list)
```

### v18 View Template
```xml
<button name="action" invisible="state != 'draft'" readonly="locked"/>
<field name="partner_id" readonly="state != 'draft'" required="type == 'invoice'"/>
```

### v18 OWL Template
```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "module.Component";
    setup() { this.orm = useService("orm"); }
}
registry.category("actions").add("module.action", MyComponent);
```

## Error Messages Reference

| Error | Version | Cause | Fix |
|-------|---------|-------|-----|
| `@api.multi is deprecated` | v14 | Decorator still used | Remove decorator |
| `attrs is not supported` | v17+ | Using `attrs` in view | Use direct attributes |
| `states is not supported` | v17+ | Using `states` in view | Use `invisible` expression |
| `create() expects vals_list` | v17+ | Old create signature | Use `@api.model_create_multi` |
| `Raw SQL not allowed` | v19+ | Using string SQL | Use `SQL()` builder |
| `Missing type annotation` | v19+ | No type hints | Add type hints |

---

**IMPORTANT**: This reference is for comparison purposes. Always use version-specific files for actual implementation patterns.
