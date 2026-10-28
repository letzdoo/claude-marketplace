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
| ORM | `Command` class (already in 15.0) | None - use it in both versions |
| OWL | OWL 2.x replaces 1.x | High - Rewrite components |
| Views | `attrs=` still the correct syntax (direct `invisible="expr"` only from 17.0) | None |
| Assets | `assets` manifest key unchanged (already in 15.0); `web.assets_qweb` XML moves into `web.assets_backend` | Low - move XML entries |
| Batch | `@api.model` single-dict `create`: silently wrapped in 15.0, works but logs a warning in 16.0 | Medium - Update create() |

## ORM Command Class

`Command` exists in 15.0 already (`from odoo import Command`); both styles work in 15.0 and 16.0.

### Tuple Syntax (15.0 and 16.0)
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

### Command Class (15.0 and 16.0, preferred)
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
| JS escaping: no `markup()`, no `escape` util (use `t-esc`, `_.escape`) | `markup()`, `escape` in `@web/core/utils/strings` |

## View Modifiers: keep `attrs` in 16.0

```xml
<!-- 15.0 and 16.0: attrs is the correct syntax -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'readonly': [('state', '!=', 'draft')],
               'required': [('type', '=', 'customer')]}"/>
```

**Note**: In 16.0 a direct `invisible="state == 'draft'"` is NOT evaluated as a record condition. Direct
Python-expression modifiers replace `attrs` only in 17.0.

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

### v15 Manifest (globs already supported; XML templates in web.assets_qweb)
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/**/*',
    ],
    'web.assets_qweb': [
        'my_module/static/src/xml/**/*',
    ],
},
```

### v16 Manifest (XML templates move into the JS bundle)
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
            attrs="{'invisible': [('state', '!=', 'draft')]}"
            class="btn-primary"/>
</header>
```

## GitHub Verification URLs

```
# OWL comparison
https://raw.githubusercontent.com/odoo/odoo/15.0/addons/web/static/src/core/
https://raw.githubusercontent.com/odoo/odoo/16.0/addons/web/static/src/core/

# Command class (present in both)
https://raw.githubusercontent.com/odoo/odoo/15.0/odoo/fields.py

# View changes
https://raw.githubusercontent.com/odoo/odoo/16.0/odoo/tools/view_validation.py
```

## Migration Checklist

- [ ] (Optional) Replace tuple x2many operations with Command class (works in 15.0 too)
- [ ] Migrate OWL 1.x components to OWL 2.x
- [ ] Keep `attrs=` in 16.0 views (inline expressions are 17.0+)
- [ ] Update `@api.model` create to `@api.model_create_multi`
- [ ] Move XML template entries from `web.assets_qweb` into the JS bundle
- [ ] Test all OWL components for 2.x compatibility
- [ ] Replace `sudo(user)` by `with_user(user)`; move `t-lang` onto `t-call`

## Common Migration Errors

### Error: `Command is not defined`
**Fix**: Add `from odoo import Command` (available since 15.0)

### Error: OWL `useState` not found
**Fix**: Update import: `import { useState } from "@odoo/owl"`

## Official guideline deltas 15.0 -> 16.0

Only rows of the verified 14-19 matrix that change between 15.0 and 16.0 and are not covered above (`create` warning, assets XML and JS escaping are in the tables above):

| Topic | 15.0 | 16.0 |
|---|---|---|
| `sudo(user)` | deprecated, warns, delegates to `with_user` | removed (`sudo()` asserts a bool) |
| RPC guard | `check_method_name` (`_*`, `init`) | `get_public_method` (`_*`, `@api.private`, unsafe attributes) |
| `@api.private` | absent | available |
| `odoo.tools.SQL` | absent | name exists but is psycopg2 `sql.SQL` (not the 17.0+ builder) |
| route override without `@http.route` | URL silently dropped | auto-decorated + warning |
| `index=` values | bool only | `True`/`'btree'`/`'btree_not_null'`/`'trigram'` |
| `t-lang` without `t-call` | silently ignored | SyntaxError |
| `BaseCommon` / `BaseUsersCommon` test fixtures | absent | available (still SUPERUSER env) |
| `patch` | `patch(obj, name, ext)` + `this._super` | same signature |

Unchanged in 15.0 and 16.0: `Command`, `_allow_sudo_commands`, `related_sudo`, `osv.expression` domains,
`read_group` (dict API), `_sql_constraints`, no `grouped()`, `_()`/`_lt` (no `env._`), no `base` injection in
`depends`, `assets` key, no `<asset>` tag, `attrs` view modifiers, default test tags `standard` + `at_install`,
test loader re-collecting imported classes and inherited `test_*` methods, min Python 3.7.
