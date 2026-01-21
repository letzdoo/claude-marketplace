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
| x2many operations | Tuple syntax | `Command` class | Recommended |
| View visibility | `attrs` | `attrs` (deprecated) | Prepare for v17 |
| OWL | 1.x | 2.x | For OWL components |
| @api.model_create_multi | Optional | Recommended | Recommended |

## Key Changes

### 1. Command Class for x2many Operations

The `Command` class provides a cleaner API for x2many field operations with security implications.

**v15 (tuple syntax):**
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

**v16 (Command class):**
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

### 2. Prepare for attrs Deprecation

While `attrs` still works in v16, it's deprecated. Start migrating to direct attributes.

**v15/v16 (still works but deprecated):**
```xml
<field name="notes" attrs="{'invisible': [('state', '=', 'draft')]}"/>
```

**v16 (recommended, ready for v17):**
```xml
<field name="notes" invisible="state == 'draft'"/>
```

### 3. @api.model_create_multi Recommendation

**v15:**
```python
@api.model
def create(self, vals):
    return super().create(vals)
```

**v16 (recommended):**
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
odoo.define('my_module.MyComponent', function (require) {
    const { Component } = owl;
    const { registry } = require('@web/core/registry');

    class MyComponent extends Component {
        // ...
    }

    registry.category('actions').add('my_action', MyComponent);
});
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

- [ ] Import `Command` from `odoo` and use for x2many operations
- [ ] Start migrating `attrs` to direct attributes (preparation for v17)
- [ ] Update to `@api.model_create_multi` for create methods
- [ ] Migrate OWL 1.x components to OWL 2.x
- [ ] Test x2many operations with new Command syntax
- [ ] Update JavaScript module syntax

## Dual Compatibility (v15/v16)

If you need to support both versions:

```python
try:
    from odoo import Command
except ImportError:
    # Fallback for v15
    class Command:
        @staticmethod
        def create(values):
            return (0, 0, values)
        @staticmethod
        def update(id, values):
            return (1, id, values)
        @staticmethod
        def delete(id):
            return (2, id, 0)
        @staticmethod
        def unlink(id):
            return (3, id, 0)
        @staticmethod
        def link(id):
            return (4, id, 0)
        @staticmethod
        def clear():
            return (5, 0, 0)
        @staticmethod
        def set(ids):
            return (6, 0, ids)
```

## GitHub Reference

- `odoo/__init__.py` - `Command` class export
- `odoo/fields.py` - x2many field handling
- `addons/web/static/src/` - OWL 2.x components
