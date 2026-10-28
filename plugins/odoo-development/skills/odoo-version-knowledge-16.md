# Odoo 16.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 16.0 KNOWLEDGE BASE                                                    ║
║  attrs/states view modifiers, Command class, OWL 2.x, @api.private           ║
║  Released: October 2022                                                      ║
║  VERIFY: https://github.com/odoo/odoo/tree/16.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Release Date | October 2022 |
| Python | 3.7 - 3.12 (`MIN_PY_VERSION`/`MAX_PY_VERSION` in `odoo/__init__.py`) |
| PostgreSQL | 12, 13, 14 |
| Frontend | OWL 2.x |
| Support | Community: Active, Enterprise: Active |

## Key Changes from v15

### Command Class (available since 15.0)
```python
from odoo import Command   # or: from odoo.fields import Command

line_ids = [
    Command.create({'name': 'Line 1'}),
    Command.update(id, {'name': 'Updated'}),
    Command.delete(id),
    Command.link(id),
    Command.clear(),
    Command.set([id1, id2]),
]

# Old tuple syntax still works
line_ids = [(0, 0, {'name': 'Line 1'})]
```

### View modifiers: `attrs` / `states` (NOT deprecated in 16.0)
```xml
<!-- v16: record-dependent visibility/readonly/required = attrs with domains -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- v16 shorthand: visible only in these states -->
<button name="action_confirm" type="object" string="Confirm" states="draft"/>

<!-- WRONG in v16: a non-boolean invisible/readonly/required value is treated as a
     context-only expression (evaluated with just `context`), so `state` is unknown.
     Python expressions on record fields are a 17.0 feature. -->
<!-- <field name="partner_id" invisible="state == 'draft'"/> -->

<!-- OK in v16: constants and context lookups -->
<field name="partner_id" invisible="context.get('hide_partner', False)"/>
```
Source: `odoo/addons/base/models/ir_ui_view.py` (`transfer_node_to_modifiers`, `_postprocess_context_dependent`).

### OWL 2.x
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: [], loading: true });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.data = await this.orm.searchRead(
            "my.model",
            [],
            ["name", "state"]
        );
        this.state.loading = false;
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

## Key Features

### New in Odoo 16
- OWL 2.x framework
- `@api.private` (for public names that must not be RPC-callable) and the `get_public_method` RPC guard (blocks `_` prefix, `@api.private`, `_UNSAFE_ATTRIBUTES`; classmethods/staticmethods are NOT blocked: prefix them with `_`)
- `index='btree_not_null'` / `index='trigram'` field indexes (besides `True`/`'btree'`)
- Improved Knowledge app
- Enhanced Spreadsheet
- Better project management
- WhatsApp integration (Enterprise)

### Technical Stack
- Python 3.7 - 3.12
- PostgreSQL 12+
- OWL 2.x framework
- ES modules

## Version-Specific Patterns

### Model Definition
```python
from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True, index=True)

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    partner_id = fields.Many2one(
        'res.partner',
        domain="[('company_id', 'in', [company_id, False])]",
    )

    line_ids = fields.One2many(
        'my.model.line',
        'model_id',
        copy=True,
    )
```

### Using Command Class
```python
from odoo.fields import Command

def create_with_lines(self):
    return self.env['my.model'].create({
        'name': 'New Record',
        'line_ids': [
            Command.create({'name': 'Line 1', 'quantity': 1}),
            Command.create({'name': 'Line 2', 'quantity': 2}),
        ],
    })

def update_lines(self):
    self.write({
        'line_ids': [
            Command.update(self.line_ids[0].id, {'quantity': 5}),
            Command.create({'name': 'New Line'}),
            Command.delete(self.line_ids[-1].id),
        ],
    })

def manage_tags(self):
    # Many2many operations
    self.write({
        'tag_ids': [
            Command.link(tag.id),      # Add existing
            Command.unlink(tag.id),    # Remove (M2M only)
            Command.set([id1, id2]),   # Replace all
            Command.clear(),           # Remove all
        ],
    })
```

### CRUD Methods
```python
@api.model_create_multi
def create(self, vals_list):
    """Batch create - recommended in v16"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)
```

### XML Views (16.0 modifier syntax)
```xml
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'readonly': [('state', '=', 'done')],
               'required': [('state', '=', 'confirmed')]}"/>

<!-- Buttons -->
<button name="action_confirm" type="object" string="Confirm"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
<!-- or the shorthand -->
<button name="action_done" type="object" string="Done" states="confirmed"/>
```

## OWL 2.x Patterns

Owl 2 has no `computed`: use getters or compute in `setup()`.

### Component with Services
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");

        this.state = useState({
            data: [],
            loading: true,
            error: null,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state"],
                { limit: 100 }
            );
        } catch (error) {
            this.state.error = error.message;
            this.notification.add("Failed to load data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onItemClick(item) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "my.model",
            res_id: item.id,
            views: [[false, "form"]],
        });
    }
}
```

### OWL Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="my-component">
            <t t-if="state.loading">
                <div class="text-center p-4">
                    <i class="fa fa-spinner fa-spin fa-2x"/>
                </div>
            </t>
            <t t-elif="state.error">
                <div class="alert alert-danger" t-esc="state.error"/>
            </t>
            <t t-else="">
                <div class="list-group">
                    <t t-foreach="state.data" t-as="item" t-key="item.id">
                        <a class="list-group-item list-group-item-action"
                           t-on-click="() => this.onItemClick(item)">
                            <span t-esc="item.name"/>
                            <span class="badge" t-esc="item.state"/>
                        </a>
                    </t>
                </div>
            </t>
        </div>
    </t>
</templates>
```

## Migration from v15

### Mandatory Changes
- None strictly required (v15 code works)

### Recommended Changes
1. Use the Command class (available since 15.0)
2. Keep `attrs`/`states` in views (they remain the 16.0 syntax)
3. Update OWL components to 2.x

### Code Migration
```python
# v15 → v16 changes

# 1. Use Command class (recommended)
# Before
line_ids = [(0, 0, {'name': 'Test'})]

# After
from odoo.fields import Command
line_ids = [Command.create({'name': 'Test'})]

# 2. Use model_create_multi
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

### View Migration
```xml
<!-- v15 → v16: no change, attrs/states stay -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>
```

## Preparing for v17 Upgrade

### attrs/states are replaced by expressions in v17 - convert DURING the 17.0 migration
```xml
<!-- v16 (correct in 16.0, no longer supported in 17.0) -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- v17 form (does NOT work as a record condition in 16.0 - do not use it in 16 code) -->
<field name="partner_id"
       invisible="state == 'draft'"/>
```
A single view file cannot serve both versions; keep `attrs` on the 16.0 branch.

### create(): batch it now
```python
# 16.0 and 17.0: a single-dict @api.model create still works but logs
# "not overriding the create method in batch" (WARNING). Use:
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

## Best Practices for v16

1. **Use Command class** - For x2many operations
2. **Use attrs/states** - The 16.0 view modifier syntax
3. **Use @api.model_create_multi** - Avoids the batch warning
4. **Build with OWL 2.x** - For new frontend components
5. **Index important fields** - `index=True` only on searched, selective fields (`'btree_not_null'`/`'trigram'` available)

## Manifest Structure

```python
{
    'name': 'My Module',
    'version': '16.0.1.0.0',
    'category': 'Tools',
    'summary': 'Module summary',
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/**/*.js',
            'my_module/static/src/**/*.xml',
            'my_module/static/src/**/*.scss',
        ],
    },
    'installable': True,
    'application': False,
}
```

## Additional Rules from Odoo's Official Guidelines (verified for 16.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 16.0 source; master-only APIs are translated to the 16.0 equivalent or marked as not available.

### API availability in 16.0 vs master

| Topic | 16.0 | Use in 16.0 |
|---|---|---|
| `sudo(user)` | absent (bool only) | `with_user(user)` |
| `_allow_sudo_commands` | exists | set `False` on security-sensitive comodels |
| `related_sudo` default `True` | same as master | `related_sudo=False` on sensitive chains |
| `odoo.tools.SQL` builder, `SQL.identifier` | different: `odoo.tools.SQL` is `psycopg2.sql.SQL` | `cr.execute(query, params)`; identifiers via `psycopg2.sql.Identifier` |
| `_search()` + `Query.select(SQL(...))` | different | `query = M._search(dom)` -> `Query` (or `[]`); `sql, params = query.select('"t"."id"')` |
| `odoo.fields.Domain` | absent | `odoo.osv.expression.AND/OR/normalize_domain` |
| route `auth` | `user`, `public`, `none` | no `bearer` |
| route `type` | `http`, `json` | no `jsonrpc` / `json2` |
| QWeb `t-out` / `t-esc` / `t-raw` | `t-out` escapes; `t-esc` = alias; `t-raw` still renders unescaped (deprecated) | use `t-out` |
| `_()` escaping Markup args | absent | `Markup(_("... %s")) % value` |
| `env._`, `LazyTranslate` | absent | `from odoo import _, _lt` |
| `fields.NO_ACCESS` | exists (`'.'`) | `groups=fields.NO_ACCESS` |
| restricted `odoo.tools.misc.pickle` | exists | still prefer `json` |
| `ir.access` (unified ACL) | absent | `ir.model.access.csv` + `ir.rule` |
| `grouped()` | absent | `odoo.tools.groupby(records, key)` |
| `_read_group(domain, groupby, aggregates)` tuples | different | `read_group(domain, fields, groupby, lazy=...)` -> list of dicts |
| `models.Constraint` / `Index` / `UniqueIndex` | absent | `_sql_constraints`; indexes via `index=` or `tools.create_index()` in `init()` |
| manifest `base` injection for empty `depends` | absent | declare `'depends': ['base']` |
| `<asset>` XML tag | absent | manifest `'assets'` key |
| `t-lang` without `t-call` | SyntaxError (same as master) | put `t-lang` on the `t-call` node |
| default test tags | `standard`, `at_install` | post-install: `@tagged('post_install', '-at_install')` |
| `allow_inherited_tests_method` | absent | inherited `test_*` methods ARE collected; keep shared code in non-`test_` mixins |
| `BaseCommon` | exists (USD, mail-disabled context, `cls.partner`, still superuser) | `BaseUsersCommon` for `user_internal`/`user_portal` |
| JS `patch` | `patch(obj, "name", ext)`, `this._super(...)` | not `patch(obj, ext)` / `super` (17.0+) |
| JS escape helpers | `htmlEscape`, `markup` (`@odoo/owl`), `escape` (`@web/core/utils/strings`) | no `@web/core/utils/html` |

### Master/20.0-only - do NOT use in 16.0
Everything marked absent/different above (including `auth='bearer'` / `bearer_scope`, `security/ir.access.csv`, Owl `computed`), and direct `invisible="<python expr>"` (see Common Issues).

## Common Issues

### Record-based `invisible="..."` fails in 16.0
A value like `invisible="state == 'draft'"` is evaluated with only `context` available.
Solution: `attrs="{'invisible': [('state', '=', 'draft')]}"` or `states="..."`.

### Command Import
```
ImportError: cannot import name 'Command' from 'odoo.fields'
```
Solution: `Command` exists in 15.0 and 16.0; on 14.0 use the tuple syntax `(0, 0, vals)`.
