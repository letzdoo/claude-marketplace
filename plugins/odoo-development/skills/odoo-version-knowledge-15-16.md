# Odoo Version Knowledge: 15 to 16 Migration

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  VERSION MIGRATION: 15.0 → 16.0                                              ║
║  Critical changes, breaking changes, and migration patterns                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Category | Change | Impact |
|----------|--------|--------|
| ORM | `Command` class introduced | Medium - Recommended for x2many |
| OWL | OWL 2.x replaces 1.x | High - Rewrite components |
| Views | `attrs=` deprecated | Medium - Start migrating |
| Assets | New asset bundling system | Medium - Update manifests |
| Batch | `@api.model_create_multi` preferred | Medium - Update create() |

## ORM Command Class

### Before (v15) - Tuple Syntax
```python
# Create
record.write({'line_ids': [(0, 0, {'name': 'Line 1'})]})

# Update
record.write({'line_ids': [(1, line_id, {'name': 'Updated'})]})

# Delete
record.write({'line_ids': [(2, line_id, 0)]})

# Link
record.write({'tag_ids': [(4, tag_id, 0)]})

# Replace all
record.write({'tag_ids': [(6, 0, [tag1_id, tag2_id])]})
```

### After (v16) - Command Class
```python
from odoo.fields import Command

# Create
record.write({'line_ids': [Command.create({'name': 'Line 1'})]})

# Update
record.write({'line_ids': [Command.update(line_id, {'name': 'Updated'})]})

# Delete
record.write({'line_ids': [Command.delete(line_id)]})

# Link
record.write({'tag_ids': [Command.link(tag_id)]})

# Replace all
record.write({'tag_ids': [Command.set([tag1_id, tag2_id])]})

# Clear all
record.write({'tag_ids': [Command.clear()]})
```

### Command Reference
| Tuple | Command Method | Purpose |
|-------|---------------|---------|
| `(0, 0, vals)` | `Command.create(vals)` | Create new record |
| `(1, id, vals)` | `Command.update(id, vals)` | Update existing |
| `(2, id, 0)` | `Command.delete(id)` | Delete record |
| `(3, id, 0)` | `Command.unlink(id)` | Remove link |
| `(4, id, 0)` | `Command.link(id)` | Add link |
| `(5, 0, 0)` | `Command.clear()` | Remove all |
| `(6, 0, ids)` | `Command.set(ids)` | Replace all |

## OWL 2.x Migration

### OWL 1.x (v15)
```javascript
/** @odoo-module **/

const { Component } = owl;
const { xml } = owl.tags;
const { useState } = owl.hooks;

class MyComponent extends Component {
    static template = xml`
        <div t-on-click="onClick">
            <span t-esc="state.count"/>
        </div>
    `;

    state = useState({ count: 0 });

    onClick() {
        this.state.count++;
    }
}
```

### OWL 2.x (v16)
```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({ count: 0 });
    }

    onClick() {
        this.state.count++;
    }
}
```

### Key OWL Changes
| OWL 1.x | OWL 2.x |
|---------|---------|
| `const { Component } = owl` | `import { Component } from "@odoo/owl"` |
| `owl.tags.xml` | External XML templates |
| Direct property `state = useState()` | `setup() { this.state = useState() }` |
| `t-on-click` | `t-on-click` (same) |
| `owl.hooks.useState` | `import { useState }` |

## View Attrs Deprecation

### Before (v15)
```xml
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'readonly': [('state', '!=', 'draft')],
               'required': [('type', '=', 'customer')]}"/>
```

### After (v16) - Start Migration
```xml
<!-- v16 supports both, but start using new syntax -->
<field name="partner_id"
       invisible="state == 'draft'"
       readonly="state != 'draft'"
       required="type == 'customer'"/>
```

**Note**: `attrs=` still works in v16 but is deprecated. Full removal in v17.

## Batch Create Pattern

### Before (v15)
```python
@api.model
def create(self, vals):
    # Set defaults
    if 'code' not in vals:
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals)
```

### After (v16) - Recommended
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if 'code' not in vals:
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)
```

## Asset System Changes

### v15 Manifest
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/my_component.js',
    ],
},
```

### v16 Manifest - ES6 Modules
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/**/*',  # Glob patterns supported
        'my_module/static/src/xml/**/*',
    ],
},
```

## New Features in v16

### 1. PDF Preview Improvements
```xml
<field name="document" widget="pdf_viewer"/>
```

### 2. Improved Search Views
```xml
<filter name="my_filter"
        string="My Filter"
        domain="[('field', '=', value)]"
        context="{'group_by': 'category_id'}"/>
```

### 3. Form View Actions
```xml
<header>
    <button name="action_confirm" type="object"
            string="Confirm"
            invisible="state != 'draft'"
            class="btn-primary"/>
</header>
```

## GitHub Verification URLs

```
# OWL comparison
https://raw.githubusercontent.com/odoo/odoo/15.0/addons/web/static/src/core/
https://raw.githubusercontent.com/odoo/odoo/16.0/addons/web/static/src/core/

# Command class introduced
https://raw.githubusercontent.com/odoo/odoo/16.0/odoo/fields.py

# View changes
https://raw.githubusercontent.com/odoo/odoo/16.0/odoo/tools/view_validation.py
```

## Migration Checklist

- [ ] Replace tuple x2many operations with Command class
- [ ] Migrate OWL 1.x components to OWL 2.x
- [ ] Start replacing `attrs=` with inline expressions
- [ ] Update `@api.model` create to `@api.model_create_multi`
- [ ] Update asset declarations to use glob patterns
- [ ] Test all OWL components for 2.x compatibility
- [ ] Verify Command operations work correctly

## Common Migration Errors

### Error: `Command is not defined`
**Fix**: Add `from odoo.fields import Command`

### Error: OWL `useState` not found
**Fix**: Update import: `import { useState } from "@odoo/owl"`

### Warning: `attrs attribute is deprecated`
**Fix**: Replace with inline expressions (recommended, required in v17)
