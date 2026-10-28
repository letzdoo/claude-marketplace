# Odoo 14.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 14.0 KNOWLEDGE BASE                                                    ║
║  @api.multi already removed; tracking=True; Owl 1.4.11 bundled              ║
║  Released: October 2020                                                      ║
║  VERIFY: https://github.com/odoo/odoo/tree/14.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Release Date | October 2020 |
| Python | 3.6, 3.7, 3.8 |
| PostgreSQL | 10, 11, 12 |
| Frontend | Legacy JS + QWeb |
| OWL | Owl 1.4.11 bundled (`web/static/lib/owl`; no `markup`, `htmlEscape`, `computed`), used by a few core components; custom UI is mostly legacy widgets with `t-esc` in JS QWeb |
| Support | Community: Ongoing, Enterprise: Extended |

## Key Features

### New in Odoo 14
- Improved performance
- Enhanced reporting
- Better mobile experience
- Website improvements
- Accounting enhancements
- Manufacturing improvements

### Technical Stack
- Python 3.6+ (3.8 recommended)
- PostgreSQL 10+
- Werkzeug 0.16
- Jinja2 2.10
- lxml 4.2

## Removed / Deprecated Features

### @api.multi Decorator (REMOVED - already absent in 14.0)
```python
# FAILS in v14: odoo.api has no attribute 'multi' (removed in 13.0)
# @api.multi
# def action_confirm(self): ...

# CORRECT (methods are multi-record by default)
def action_confirm(self):
    for record in self:
        pass
```

### track_visibility (legacy, still honoured with a warning)
```python
# LEGACY: mail.thread still tracks it, but the field setup logs
# "unknown parameter 'track_visibility'" (only 'tracking' is a valid parameter)
state = fields.Selection(..., track_visibility='onchange')

# CORRECT in v14
state = fields.Selection(..., tracking=True)
```

## Version-Specific Patterns

### Field Definitions
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], tracking=True)  # track_visibility='onchange' still tracks but logs a warning

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
```

### X2many Commands (Tuple Syntax)
```python
# Standard v14 tuple syntax (the `Command` class does not exist in 14.0)
def create_with_lines(self):
    self.env['my.model'].create({
        'name': 'Test',
        'line_ids': [
            (0, 0, {'name': 'Line 1'}),  # Create
            (1, id, {'name': 'Updated'}), # Update
            (2, id, 0),                   # Delete (short form: (2, id))
            (3, id, 0),                   # Unlink (short form: (3, id))
            (4, id, 0),                   # Link (short form: (4, id))
            (5, 0, 0),                    # Clear (short form: (5,))
            (6, 0, [id1, id2]),           # Replace
        ],
    })
```

### attrs in Views
```xml
<!-- v14: Full attrs support -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'required': [('state', '=', 'confirmed')],
               'readonly': [('state', '=', 'done')]}"/>

<button name="action_confirm"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

### Create Method
```python
# v14: BaseModel.create is already @api.model_create_multi
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)

# A legacy `@api.model def create(self, vals)` override still works in 14.0
# (silently wrapped, no warning) but creates records one by one.
```

## Frontend Development

### Legacy JavaScript
```javascript
odoo.define('my_module.MyWidget', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');

    var MyWidget = Widget.extend({
        template: 'my_module.MyWidget',
        events: {
            'click .btn-confirm': '_onClickConfirm',
        },

        init: function (parent, options) {
            this._super(parent);
            this.options = options || {};
        },

        start: function () {
            return this._super.apply(this, arguments);
        },

        _onClickConfirm: function (ev) {
            ev.preventDefault();
            // Handle click
        },
    });

    core.action_registry.add('my_module.my_action', MyWidget);

    return MyWidget;
});
```

### QWeb Templates
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyWidget">
        <div class="my-widget">
            <button class="btn btn-primary btn-confirm">
                Confirm
            </button>
        </div>
    </t>
</templates>
```

## Security Configuration

### Access Rights (CSV)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_manager,1,1,1,1
```

14.0 has no `ir.access` / `security/ir.access.csv`: use `ir.model.access` + `ir.rule`. `base.group_everyone` does not exist: an ACL row with empty `group_id` applies to everyone.

### Record Rules
The `domain_force` eval context holds `user`, `time`, `company_ids`, `company_id` (not `allowed_company_ids`).
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

## Manifest Structure

```python
{
    'name': 'My Module',
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'summary': 'Module summary',
    'description': """
Module Description
==================
Long description here.
    """,
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        # Order matters!
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/my_model_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

- `base` is not injected automatically: list real dependencies (`base` if nothing else).
- No `assets` manifest key and no `<asset>` XML tag: inherit `web.assets_backend`/`web.assets_frontend` with `<template inherit_id="web.assets_backend">` in XML; JS QWeb goes in the `'qweb'` key.

## Migration from v13

### Key Changes from v13 to v14
1. Python 3.6+ required (no more Python 2)
2. Performance improvements
3. Improved mail templates
4. Better search panels

### Removed / legacy in v14
- `@api.multi` / `@api.one`: already removed (since 13.0) - fails with AttributeError
- `track_visibility`: legacy; still tracked by `mail.thread` but logs "unknown parameter" - use `tracking=True`
- `oldname` parameter (use direct migration)

## Preparing for v15 Upgrade

### Code Changes Needed
```python
# 1. Manifest: move JS/SCSS from XML asset templates and the 'qweb' key
#    to the 15.0 'assets' manifest key
# 2. x2many commands may use `Command` (15.0+); tuples keep working
# 3. Server QWeb: prefer t-out (15.0+) over t-esc; t-raw is deprecated in 15.0
# 4. Clean-up that is already valid in 14 (do it before migrating):
state = fields.Selection(..., tracking=True)   # not track_visibility
```

### View Changes Needed
- No immediate view changes required for v15
- Consider using `tracking=True` in fields

## Additional Rules from Odoo's Official Guidelines (verified for 14.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 14.0 source; master-only APIs are translated to the 14.0 equivalent or marked as not available.

### API availability in 14.0 vs master

| Topic | 14.0 | Use in 14.0 |
|-------|------|-------------|
| `_allow_sudo_commands` | exists | set `False` on security-sensitive comodels |
| `sudo(user)` | deprecated (warns) | `with_user(user)`; `sudo()` / `sudo(False)` only toggle superuser |
| `odoo.tools.SQL`, `SQL.identifier` | absent | parameters in `cr.execute(q, params)`; identifiers via `psycopg2.sql.Identifier` |
| `_search()` | returns `Query` (or `[]`/int) | `query.select('"table"."col"')` -> `(sql, params)` |
| `fields.Domain` | absent | `odoo.osv.expression.AND/OR/normalize_domain` |
| `@api.private` | absent | prefix the method with `_` (RPC guard `check_method_name` blocks `_*` names and `init`) |
| route `auth` | `user`, `public`, `none` | no `bearer` |
| route `type` | `http`, `json` | no `jsonrpc`/`json2` |
| route override without `@http.route` | URL silently dropped | always re-decorate (`@http.route()` keeps the parent args) |
| server QWeb `t-out` | absent (unknown directive error) | `t-esc` escapes; `t-raw` outputs raw HTML |
| `_()` escapes Markup args | no | escape user input yourself (`odoo.tools.html_escape`) |
| `fields.NO_ACCESS` (`'.'`) | exists | `groups=fields.NO_ACCESS` or `groups='base.group_system'` |
| restricted `odoo.tools.misc.pickle` | exists | prefer JSON anyway |
| `odoo.tools.consteq` | exists | constant-time secret comparison |
| `recordset.grouped()` | absent | `odoo.tools.groupby()` or a dict of recordsets |
| `models.Constraint/Index/UniqueIndex` | absent | `_sql_constraints`; extra indexes in `init()` |
| `read_group` / `_read_group` | `read_group(domain, fields, groupby, lazy=True)` -> list of dicts | no `_read_group(domain, groupby, aggregates)` |
| `self.env._`, `LazyTranslate` | absent | `from odoo import _, _lt` |
| `t-lang` without `t-call` | silently ignored | only use `t-lang` on a `t-call` node |
| default test tags | `standard`, `at_install` | post-install: `@tagged('post_install', '-at_install')` |
| `SavepointCase` | exists (class-level fixtures) | `TransactionCase` has no `cls.env` in 14.0 |
| `BaseCommon`, `BaseUsersCommon` | absent | `TransactionCaseWithUserDemo`, `SavepointCaseWithUserDemo`, `new_test_user` |
| imported TestCase class / inherited `test_*` methods | both collected again | do not import concrete test classes into test files |

### Master/20.0-only things an agent must NOT use in 14.0

`Command`, `odoo.tools.SQL`, `fields.Domain`, `@api.private`, `auth='bearer'`/`bearer_scope`, route types `jsonrpc`/`json2`, `t-out`, Owl `markup`/`htmlEscape`/`computed`, `@web/core/utils/html`, `ir.access` / `security/ir.access.csv`, `base.group_everyone`, `grouped()`, `models.Constraint`/`Index`/`UniqueIndex`, string `index=` values, `_read_group(domain, groupby, aggregates)`, `self.env._`, `LazyTranslate`, manifest `assets` key, `<asset>` tag, `BaseCommon`, `allow_inherited_tests_method`, `populate.blueprint`, `--unsafe-policy`.

## Best Practices for v14

1. **Use tracking=True** instead of track_visibility
2. **Don't use @api.multi** (it does not exist in 14.0)
3. **Use self.env.company** instead of self.env.user.company_id
4. **Test with Python 3.8** for forward compatibility
5. **Document deprecated patterns** in your code

## Common Issues

### Performance
- Use `search_read()` instead of `search()` + `read()`
- Use stored computed fields when possible
- Index frequently searched fields (`index=True`; in 14.0 `index=` is boolean only, no `'btree_not_null'`/`'trigram'`)

### Multi-company
```python
company_id = fields.Many2one(
    'res.company',
    default=lambda self: self.env.company,
)

# Domain for related records
partner_id = fields.Many2one(
    'res.partner',
    domain="[('company_id', 'in', [company_id, False])]",
)
```
