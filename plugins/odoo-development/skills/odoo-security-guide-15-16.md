# Odoo Security Guide - Migration 15.0 → 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: ODOO 15.0 → 16.0 SECURITY                                  ║
║  Use this guide when upgrading security code from v15 to v16.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview of Security Changes

| Component | v15 | v16 | Migration Required |
|-----------|-----|-----|-------------------|
| x2many operations | `Command` class or tuples | `Command` class or tuples | No (Command exists since 15.0) |
| View visibility | `attrs` | `attrs` (still the correct syntax; direct `invisible="expr"` is 17.0+) | No |
| OWL | 1.x | 2.x | For OWL components |
| `create` override | `@api.model_create_multi` (single-dict `@api.model` silently wrapped) | `@api.model_create_multi` (`@api.model` logs a warning) | Recommended |

## Key Changes

### 1. Command Class for x2many Operations

The `Command` class provides a cleaner API for x2many field operations. It already exists in 15.0
(`from odoo import Command`); both forms below work in 15.0 and 16.0.

**Tuple syntax (15.0 and 16.0):**
```python
def action_update_lines(self):
    self.write({
        'line_ids': [
            (0, 0, {'name': 'New Line'}),        # Create
            (1, line_id, {'name': 'Updated'}),   # Update
            (2, line_id, 0),                     # Delete
            (3, line_id, 0),                     # Unlink
            (4, line_id, 0),                     # Link
            (5, 0, 0),                           # Clear
            (6, 0, [id1, id2]),                  # Set
        ]
    })
```

**Command class (15.0 and 16.0, preferred):**
```python
from odoo import Command

def action_update_lines(self):
    self.write({
        'line_ids': [
            Command.create({'name': 'New Line'}),
            Command.update(line_id, {'name': 'Updated'}),
            Command.delete(line_id),
            Command.unlink(line_id),
            Command.link(line_id),
            Command.clear(),
            Command.set([id1, id2]),
        ]
    })
```

### 2. View visibility: keep `attrs` in 16.0

`attrs` remains the correct syntax in 15.0 and 16.0. A direct `invisible="state == 'draft'"` is NOT evaluated
as a record condition in 16.0; direct expressions only work from 17.0.

**v15/v16:**
```xml
<field name="notes" attrs="{'invisible': [('state', '=', 'draft')]}"/>
```

### 3. create() override

In 15.0 the base `create` is already `@api.model_create_multi`; a single-dict `@api.model` override is silently
wrapped in 15.0 and logs a warning in 16.0.

**v15 and v16:**
```python
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

## Command Class Reference

```python
from odoo import Command

# Create a new related record
Command.create(values)  # (0, 0, values)

# Update an existing related record
Command.update(id, values)  # (1, id, values)

# Delete a related record (removes from DB)
Command.delete(id)  # (2, id, 0)

# Unlink a related record (removes relation only)
Command.unlink(id)  # (3, id, 0)

# Link an existing record
Command.link(id)  # (4, id, 0)

# Clear all related records (unlink all)
Command.clear()  # (5, 0, 0)

# Replace all with specific records
Command.set(ids)  # (6, 0, ids)
```

## Security Implications of Command Class

The `Command` class improves security by:
1. Making operations more explicit and readable
2. Reducing errors from wrong tuple indices
3. Better type checking

**Example: Secure Line Creation**
```python
def action_create_secure_lines(self):
    """Create lines with proper security context."""
    self.ensure_one()

    # Check permission first
    if not self.env.user.has_group('my_module.group_manager'):
        raise AccessError(_("Only managers can create lines."))

    # Use Command for clear, secure operations
    new_lines = [
        Command.create({
            'name': 'Line 1',
            'amount': 100.0,
            'user_id': self.env.user.id,  # Track who created
        }),
        Command.create({
            'name': 'Line 2',
            'amount': 200.0,
            'user_id': self.env.user.id,
        }),
    ]
    self.write({'line_ids': new_lines})
```

## OWL 2.x Security Changes

### Component Registration

**v15 (OWL 1.x):**
```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";

const { Component } = owl;

export class MyComponent extends Component {
    // ...
}

registry.category('actions').add('my_action', MyComponent);
```

**v16 (OWL 2.x):**
```javascript
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    // ...
}

registry.category('actions').add('my_action', MyComponent);
```

## No Change Required

### Security Groups
```xml
<!-- Same in v15 and v16 -->
<record id="group_user" model="res.groups">
    <field name="name">User</field>
</record>
```

### Access Rights
```csv
# Same format
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

### Record Rules
```xml
<!-- Same syntax -->
<record id="rule_company" model="ir.rule">
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

### Field Groups
```python
# Same
notes = fields.Text(groups='my_module.group_manager')
```

## Migration Checklist

- [ ] Import `Command` from `odoo` and use for x2many operations (already possible in 15.0)
- [ ] Keep `attrs` in 16.0 views (direct attributes only from 17.0)
- [ ] Update to `@api.model_create_multi` for create methods
- [ ] Replace `sudo(user)` by `with_user(user)` (16.0 accepts only a bool)
- [ ] Move `t-lang` onto `t-call` nodes (16.0 raises at template compile)
- [ ] Review the "Official guideline deltas" table below
- [ ] Migrate OWL 1.x components to OWL 2.x
- [ ] Test x2many operations with new Command syntax
- [ ] Update JavaScript module syntax

## Dual Compatibility (v15/v16)

`from odoo import Command` works in both 15.0 and 16.0; no fallback is needed (a fallback is only
required for 14.0, which has no `Command` class).

## Official guideline deltas 15.0 -> 16.0

| Topic | 15.0 | 16.0 |
|---|---|---|
| `sudo(user)` | deprecated, warns, delegates to `with_user` | removed: `sudo()` accepts only a bool |
| RPC guard | `check_method_name`: blocks `_*` and `init` | `get_public_method`: also blocks `@api.private` methods and unsafe attributes |
| `@api.private` | absent | available |
| `odoo.tools.SQL` | absent | `tools.SQL` is psycopg2's `sql.SQL` (NOT the 17.0+ builder API); keep psycopg2 params / `sql.Identifier` |
| route override without `@http.route` | URL silently dropped | auto-decorated, warning logged |
| JS escaping | Owl 1.4: no `markup()`, no `escape` helper (use `t-esc`, `_.escape`) | Owl 2: `markup()`, `escape` in `@web/core/utils/strings` |
| `t-lang` without `t-call` | silently ignored | SyntaxError at compile |
| test fixtures | no `BaseCommon` / `BaseUsersCommon` | `BaseCommon`, `BaseUsersCommon` (`user_internal`, `user_portal`) available |

Unchanged in both: `_allow_sudo_commands`, `related_sudo`, `Command`, `fields.NO_ACCESS`, `file_open`, restricted
`odoo.tools.misc.pickle`, `consteq`, `ir.model.access` + `ir.rule` semantics and rule eval context, route
`auth` (`user`/`public`/`none`) and `type` (`http`/`json`), CSRF behaviour, server QWeb `t-out`/`t-raw`, `_()` not
escaping Markup arguments, `osv.expression` for domains.

## GitHub Reference

- `odoo/__init__.py` - `Command` class export
- `odoo/fields.py` - x2many field handling
- `addons/web/static/src/` - OWL 2.x components
