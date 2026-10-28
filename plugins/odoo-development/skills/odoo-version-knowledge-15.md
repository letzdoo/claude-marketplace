# Odoo 15.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 KNOWLEDGE BASE                                                    ║
║  Owl 1.4 + new @web/core client, Command class, assets manifest key          ║
║  Released: October 2021                                                      ║
║  VERIFY: https://github.com/odoo/odoo/tree/15.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Release Date | October 2021 |
| Python | 3.7+ (MIN_PY_VERSION 3.7; the maintained 15.0 branch declares support up to 3.12) |
| PostgreSQL | 10, 11, 12, 13 |
| Frontend | Owl 1.4 (already shipped in 14.0) + new `@web/core` web client with `@odoo-module` ES modules; legacy widgets still present |
| Support | Community: Ongoing, Enterprise: Active |

## Breaking Changes from v14

### @api.multi does not exist (absent since before 14.0)
```python
# BREAKS (AttributeError)
@api.multi
def action_confirm(self):
    pass

# v15 REQUIRED
def action_confirm(self):
    for record in self:
        pass
```

### track_visibility Deprecated
```python
# DEPRECATED (still works but warns)
state = fields.Selection(..., track_visibility='onchange')

# v15 CORRECT
state = fields.Selection(..., tracking=True)
```

## Key Features

### New in Odoo 15
- OWL Framework 1.x for frontend
- Enhanced Spreadsheet (Enterprise)
- Knowledge app (Enterprise)
- Improved website builder
- Better appointment scheduling
- Enhanced manufacturing

### Technical Stack
- Python 3.7+ (3.9 recommended)
- PostgreSQL 10+
- OWL 1.x framework
- ES6+ JavaScript

## OWL 1.x Components

### Component Structure
```javascript
/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";

const { Component, useState } = owl;
const { onMounted } = owl.hooks;  // Owl 1: lifecycle hooks live in owl.hooks

class MyComponent extends Component {
    setup() {
        this.state = useState({
            data: [],
            loading: true,
        });
        this.orm = useService('orm');

        onMounted(() => {
            this.loadData();
        });
    }

    async loadData() {
        this.state.data = await this.orm.searchRead(
            'my.model',
            [],
            ['name', 'state']
        );
        this.state.loading = false;
    }
}

MyComponent.template = 'my_module.MyComponent';
```

### OWL Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent" owl="1">
        <div class="my-component">
            <t t-if="state.loading">
                <div class="loading">Loading...</div>
            </t>
            <t t-else="">
                <t t-foreach="state.data" t-as="item" t-key="item.id">
                    <div class="item" t-esc="item.name"/>
                </t>
            </t>
        </div>
    </t>
</templates>
```

## Version-Specific Patterns

### Model Definition
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)  # Use tracking, not track_visibility

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    line_ids = fields.One2many(
        'my.model.line',
        'model_id',
    )
```

### CRUD Methods
```python
# Base create() is @api.model_create_multi in 15.0: override it the same way.
# (@api.model on a single-dict create() is silently wrapped - no warning - and then
#  creates record by record.)
@api.model_create_multi
def create(self, vals_list):
    """Batch create - the standard override form"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)

def write(self, vals):
    """Write - no decorator needed"""
    return super().write(vals)

def unlink(self):
    """Delete - no decorator needed"""
    return super().unlink()
```

### Views with attrs
```xml
<!-- v15: attrs fully supported -->
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                attrs="{'invisible': [('state', '!=', 'draft')]}"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <field name="name"/>
            <field name="partner_id"
                   attrs="{'required': [('state', '=', 'confirmed')]}"/>
        </group>
    </sheet>
</form>
```

## Manifest Structure

```python
{
    'name': 'My Module',
    'version': '15.0.1.0.0',
    'category': 'Tools',
    'summary': 'Module summary',
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    # 15.0 does not auto-add 'base' to an empty depends: declare it explicitly
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/**/*',
            'my_module/static/src/scss/**/*',
        ],
        # 15.0: QWeb/Owl XML templates go to web.assets_qweb
        'web.assets_qweb': [
            'my_module/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'application': False,
}
```

## Asset Management

### New Asset Bundle System
Assets are declared with the manifest `assets` key (or `ir.asset` records); there is no `<asset>` XML data tag in 15.0.
```python
'assets': {
    'web.assets_backend': [
        # JavaScript
        'my_module/static/src/js/my_component.js',

        # SCSS
        'my_module/static/src/scss/my_component.scss',
    ],
    # OWL / QWeb templates (15.0: separate bundle; XML in assets_backend is not loaded)
    'web.assets_qweb': [
        'my_module/static/src/xml/my_component.xml',
    ],
    'web.assets_frontend': [
        'my_module/static/src/js/frontend.js',
    ],
}
```

## Migration from v14

### Mandatory Changes
1. Remove all `@api.multi` decorators
2. Replace `track_visibility` with `tracking=True`
3. Update Python version if needed (3.7+)

### Code Migration
```python
# v14 → v15 changes

# 1. Remove @api.multi
# Before
@api.multi
def action_test(self):
    pass

# After
def action_test(self):
    pass

# 2. Change track_visibility
# Before
state = fields.Selection(..., track_visibility='onchange')

# After
state = fields.Selection(..., tracking=True)

# 3. Use super() without arguments
# Before (Python 2 style, works but outdated)
return super(MyModel, self).create(vals)

# After (Python 3 style)
return super().create(vals)
```

## Preparing for v16 Upgrade

### Upcoming Changes
- OWL 2.x (`import ... from "@odoo/owl"`, `markup()`)
- `index=` gains `'trigram'` / `'btree_not_null'`
- `@api.private` and a stricter RPC guard
- (`Command` already exists in 15.0; `attrs` stays valid in 16.0)

### Recommended Actions
1. Start using `@api.model_create_multi`
2. Document attrs usage for future migration
3. Plan OWL component upgrades

```python
# Prepare for v16: Use create_multi
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

## Additional Rules from Odoo's Official Guidelines (verified for 15.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 15.0 source; master-only APIs are translated to the 15.0 equivalent or marked as not available.

### API availability in 15.0 vs master

| Topic | 15.0 | Use in 15.0 |
|---|---|---|
| `Command` / `from odoo import Command` | exists | `Command.create(vals)`, `Command.set(ids)`; tuples still valid |
| `_allow_sudo_commands` | exists | `False` on security-sensitive comodels |
| `sudo(user)` | different | deprecated (warning) -> `with_user(user)`; `sudo()` takes a bool |
| `related_sudo` (default True) | exists | `related_sudo=False` on sensitive chains |
| `odoo.tools.SQL`, `SQL.identifier` | absent | psycopg2 parameters, `psycopg2.sql.Identifier`; `query = self._search(domain)` (a `Query`, or `[]` for a trivially false domain), then `query.select('"t"."col"')` -> `(query_str, params)` |
| `odoo.fields.Domain` | absent | `odoo.osv.expression.AND/OR/normalize_domain` |
| `@api.private` | absent | `_` prefix (guard `check_method_name`: `^(_.*\|init)$`) |
| route `auth` | different | `user` (default), `public`, `none`; no `bearer` |
| route `type` | different | `http`, `json` only (no `jsonrpc`/`json2`) |
| route override without `@http.route` | different | URL silently dropped: always re-decorate (`@http.route()` keeps parent args) |
| server QWeb `t-out` | exists | `t-out`; `t-esc` = escaping alias; `t-raw` deprecated, renders unescaped |
| `_()` escapes Markup args | absent | escape yourself; `_("text %s", value)` / `_("%(x)s", x=...)` |
| `self.env._`, `LazyTranslate` | absent | `from odoo import _, _lt` |
| `fields.NO_ACCESS` | exists | `groups=fields.NO_ACCESS` |
| `odoo.tools.file_open` confinement | exists | instead of `open()` |
| restricted `odoo.tools.misc.pickle` | exists | still prefer JSON |
| `odoo.tools.consteq` | exists | secret comparison |
| `ir.access` / `security/ir.access.csv` | absent | `ir.model.access` CSV + `ir.rule` XML |
| `base.group_everyone` | absent | empty `group_id` ACL row = everyone |
| `recordset.grouped()` | absent | `odoo.tools.groupby(records, key)` (lists) |
| `_read_group(domain, groupby, aggregates)` tuples | absent | `read_group(domain, ['amount:sum'], ['partner_id'], lazy=False)` -> dicts |
| `models.Constraint` / `models.Index` / `UniqueIndex` | absent | `_sql_constraints`; multi-column indexes in `init()` with `odoo.tools.create_index` |
| `index='trigram'` / `'btree_not_null'` | absent | `index=True` only |
| `t-lang` without `t-call` | different | silently ignored (no error); use it on `t-call` |
| `BaseCommon` / `BaseUsersCommon` | absent | `TransactionCase`, `TransactionCaseWithUserDemo`, `HttpCaseWithUserDemo`, `new_test_user` |
| `SavepointCase` | different | deprecated alias of `TransactionCase` (which is savepoint-based) |
| default test tags | `standard`, `at_install` | post-install: `@tagged('post_install', '-at_install')` (needed for HttpCase/tours) |
| imported TestCase classes / inherited `test_*` | different | collected and run again; `allow_inherited_tests_method` does not exist |
| Owl `markup()`, Owl `computed`, `@web/core/utils/html` | absent | Owl 1.4: `t-esc` / underscore `_.escape` |
| `patch` | different | `patch(obj, "patch_name", { ... })` with `this._super(...)` |

### Master/20.0-only - do NOT use in 15.0

Everything marked "absent" above, the `<asset>` XML tag, plus: `auth='bearer'` / `bearer_scope`, tour `expectUnloadPage`, `populate.blueprint`, `--unsafe-policy`, `import ... from "@odoo/owl"`, direct `invisible="expr"` view modifiers (use `attrs`).

## Best Practices for v15

1. **Use tracking=True** - Not track_visibility
2. **No @api.multi** - Methods iterate by default
3. **Use @api.model_create_multi** - For every create override (see CRUD Methods)
4. **Use OWL for new components** - Legacy JS for maintenance
5. **Use asset bundles** - New asset management system
6. **Python 3 super()** - No need for class/self arguments

## Common Patterns

### Computed Fields
```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

### Onchange
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.contact_id = self.partner_id.child_ids[:1]
```

### Action Return
```python
def action_view_lines(self):
    return {
        'type': 'ir.actions.act_window',
        'name': _('Lines'),
        'res_model': 'my.model.line',
        'view_mode': 'tree,form',
        'domain': [('model_id', '=', self.id)],
    }
```

## Common Issues

### @api.multi Errors
```
AttributeError: 'api' object has no attribute 'multi'
```
Solution: Remove all @api.multi decorators

### track_visibility Warnings
```
DeprecationWarning: track_visibility is deprecated
```
Solution: Replace with `tracking=True`
