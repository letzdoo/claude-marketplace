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
| `@api.multi` | ❌ REM | ❌ | ❌ | ❌ | ❌ | ❌ |
| `@api.one` | ❌ REM | ❌ | ❌ | ❌ | ❌ | ❌ |
| `@api.returns` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.model` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.model_create_multi` | ✅ | ✅ | ✅ REC | ✅ REC | ✅ REC | ✅ |
| `@api.model` on a single-dict `create` override | wrapped silently | wrapped silently | ⚠️ logs WARNING | ⚠️ WARNING | ⚠️ DEP (DeprecationWarning) | converted silently |
| `@api.private` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| `@api.depends` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.constrains` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.onchange` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `@api.depends_context` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Legend: ✅ = Supported, ⚠️ DEP = Deprecated, ✅ REC = Recommended (the alternative warns), ❌ REM = Removed, ➖ = Not available

`@api.multi` and `@api.one` were already removed before 14.0 (Odoo 13). Always write `create` overrides as `@api.model_create_multi def create(self, vals_list)` - it works in every version 14-19.

### Field Attributes

| Attribute | v14 | v15 | v16 | v17 | v18 | v19 |
|-----------|-----|-----|-----|-----|-----|-----|
| `track_visibility` | ⚠️ unknown-parameter warning (mail still reads it as fallback) | ⚠️ same | ⚠️ same | ➖ | ➖ | ➖ |
| `tracking` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `oldname` | ❌ REM | ❌ | ❌ | ❌ | ❌ | ❌ |
| `check_company` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `index=True` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `index='btree_not_null'` / `'trigram'` | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| `related_sudo` (default True) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `groups=fields.NO_ACCESS` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Type hints on fields/methods are optional in every version 14-19 (core code has many unannotated methods); they are never required.

### View Attributes

| Attribute | v14 | v15 | v16 | v17 | v18 | v19 |
|-----------|-----|-----|-----|-----|-----|-----|
| `attrs` | ✅ | ✅ | ✅ | ❌ REM (ValidationError) | ❌ | ❌ |
| `states` | ✅ | ✅ | ✅ | ❌ REM (ValidationError) | ❌ | ❌ |
| Static `invisible="1"` / `readonly="1"` / `required="1"` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Python expressions (`invisible="state == 'draft'"`) | ➖ | ➖ | ➖ (not a record condition in 16!) | ✅ | ✅ | ✅ |
| `column_invisible` | ➖ | ➖ | ➖ | ✅ | ✅ | ✅ |
| List view type `tree` (`<tree>`, `view_mode='tree,form'`) | ✅ | ✅ | ✅ | ✅ | ❌ (use `list`) | ❌ |
| List view type `list` (`<list>`, `view_mode='list,form'`) | ➖ | ➖ | ➖ | ➖ | ✅ | ✅ |
| `<asset>` XML tag | ➖ | ➖ | ➖ | ✅ | ✅ | ✅ |
| `t-out` (server QWeb) | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `t-esc` (server QWeb) | ✅ escapes | ⚠️ alias of `t-out` | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| `t-raw` (server QWeb) | ✅ raw | ⚠️ DEP, still raw | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

### x2many Operations

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| Tuple commands `(0, 0, {...})` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Command.create({...})` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Command.update(id, {...})` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Command.delete(id)` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Command.unlink(id)` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Command.link(id)` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Command.clear()` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Command.set([ids])` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |

`Command` is an `IntEnum`, so plain tuples keep working in 15-19 without any warning; prefer `Command` in new code from 15.0 (`from odoo import Command` or `from odoo.fields import Command`).

### Model Attributes

| Attribute | v14 | v15 | v16 | v17 | v18 | v19 |
|-----------|-----|-----|-----|-----|-----|-----|
| `_check_company_auto` (opt-in, default False) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `_parent_store` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `_order` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `_rec_name` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `_allow_sudo_commands` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `_sql_constraints` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ IGNORED (warning only) |
| `models.Constraint` / `Index` / `UniqueIndex` | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ |

Before 19.0, constraints and custom indexes are declared with `_sql_constraints` and `init()` + `tools.create_index`.

### SQL Operations

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| `cr.execute(query, params)` with string SQL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `odoo.tools.SQL("... %s", value)` builder | ➖ | ➖ | ➖ (`odoo.tools.SQL` is psycopg2's `sql.SQL`!) | ✅ | ✅ | ✅ |
| `SQL.identifier()` | ➖ (`psycopg2.sql.Identifier`) | ➖ | ➖ | ✅ | ✅ | ✅ |

String SQL with parameters is not deprecated in any version; it must never be built with `%`, `.format`, f-strings or `+`.

### JavaScript/OWL

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| `odoo.define(name, function (require) {...})` legacy modules | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| ES modules / `@odoo-module` | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manifest `assets` key | ➖ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Owl 1.x (1.4.11) | ✅ | ✅ | ➖ | ➖ | ➖ | ➖ |
| Owl 2.x | ➖ | ➖ | ✅ | ✅ | ✅ | ✅ |
| Owl 3.x | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ |
| `patch(obj, name, ext)` + `this._super` | ➖ (`.include()`) | ✅ | ✅ | ➖ | ➖ | ➖ |
| `patch(obj, ext)` + `super` | ➖ | ➖ | ➖ | ✅ | ✅ | ✅ |

### Security/Rules

| Pattern | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| `company_ids` in rules | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `allowed_company_ids` in rules | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `user.company_id` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `user.company_ids` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `time` in rule eval context | ✅ | ✅ | ✅ | ✅ | ✅ | ➖ |
| `check_access_rights` / `check_access_rule` | ✅ | ✅ | ✅ | ✅ | ⚠️ DEP | ⚠️ DEP |
| `check_access()` / `has_access()` | ➖ | ➖ | ➖ | ➖ | ✅ | ✅ |
| `res.users` groups field | `groups_id` | `groups_id` | `groups_id` | `groups_id` | `groups_id` | `group_ids` |

`allowed_company_ids` is a **context** key, not a record-rule variable: a rule domain using it fails validation. Use `[('company_id', 'in', company_ids)]` (or `company_ids + [False]`) in every version.

## Additional Rules from Odoo's Official Guidelines (verified for 14.0-19.0)

Condensed from a version-by-version check of Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) against the 14.0-19.0 sources. yes = exists/works as master; - = absent. Items already covered by the tables above and the migration path summary below are not repeated here.

| Topic | 14 | 15 | 16 | 17 | 18 | 19 |
|---|---|---|---|---|---|---|
| `sudo(user)` | deprecated -> `with_user` | same | - (bool only) | - | - | - |
| ORM-filtered custom SQL | `query.select('"t"."c"')` -> (sql, params) | same | same | `query.select(SQL(...))` | same | same |
| route override without `@route` | URL dropped silently | same | auto-decorated + warning | same | same | same |
| translation | `_()` (`%` args), `_lt` | same | same | + `_()` escapes Markup args, `tools.format_list` | `self.env._`, `LazyTranslate`, `_lt` | + list args formatted per language |
| JS escaping | Owl 1, none | Owl 1, none | Owl 2 `markup`/`htmlEscape` | same | + `@web/core/utils/html` | + `htmlJoin`, `htmlSprintf`, ... |
| class-level test fixtures | `SavepointCase` | `TransactionCase` (`SavepointCase` deprecated alias) | same | same (no `SavepointCase`) | same | same |
| `BaseCommon` / `BaseUsersCommon` | - | - | yes / yes | yes / yes | yes / yes | yes (+ optional user/company hooks) / - |

### Master/20.0-only - never use in 14.0-19.0

Odoo's official skills are written for master (20.0). These items do **not** exist in any of 14.0-19.0; translate them as shown:

| Master/20.0 item | Use instead in 14.0-19.0 |
|---|---|
| `ir.access` model / `ir.access.csv`, `base.group_everyone` | `ir.model.access` (`security/ir.model.access.csv`) + `ir.rule`; an empty `group_id` = every user |
| `bearer_scope` route parameter | none; 18.0-19.0 have `auth='bearer'` without scopes |
| Owl `computed` | plain getters |
| `populate.blueprint` | the populate framework of the version (or none) |
| `--unsafe-policy` server option | none; never `eval`, restrict `safe_eval` to trusted users |
| tests defaulting to `post_install` | default tags are `standard`, `at_install`; write `@tagged('post_install', '-at_install')` |
| `t-esc` "renders nothing" | in 14.0-19.0 `t-esc` still renders, escaped |
| tour step `expectUnloadPage` | not verified for 14.0-19.0 - do not emit |

## Python Version Requirements

| Odoo Version | Python Min (enforced by `odoo/__init__.py` / `release.py`) |
|--------------|------------|
| 14.0 | 3.6 |
| 15.0 | 3.7 |
| 16.0 | 3.7 |
| 17.0 | 3.10 |
| 18.0 | 3.10 |
| 19.0 | 3.10 |

## Manifest Changes Across Versions

### v14 Manifest (no `assets` key)
```python
{
    'name': 'Module',
    'version': '14.0.1.0.0',
    'depends': ['base'],
    'data': [
        'views/assets.xml',  # inherits web.assets_backend to add JS/SCSS
        'views/views.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],  # client-side QWeb templates
}
```

### v15+ Manifest (Assets)
```python
{
    'name': 'Module',
    'version': '18.0.1.0.0',
    'depends': ['base'],
    'data': ['views/views.xml'],
    'assets': {
        'web.assets_backend': [
            'module/static/src/**/*.js',
            'module/static/src/**/*.scss',
            'module/static/src/**/*.xml',  # 15.0: XML templates go to 'web.assets_qweb' instead
        ],
    },
}
```

Always declare `'depends': ['base']` when there is no other dependency (only 19.0 injects `base` automatically).

## Migration Path Summary

### v14 → v15
1. Move assets from XML inheritance (`web.assets_backend` templates) and the `qweb` key to the manifest `assets` key (XML templates into `web.assets_qweb`)
2. `Command` becomes available for x2many values (tuples keep working)
3. Server QWeb: `t-out` replaces `t-esc`/`t-raw` (both still render)
4. Python 3.7+

### v15 → v16
1. Owl 1 → Owl 2 (`patch(obj, name, ext)` keeps `this._super`)
2. `@api.private` available; RPC guard is `get_public_method` (14.0-15.0: `check_method_name`)
3. Field `index` accepts `'btree_not_null'` / `'trigram'`
4. Single-dict `@api.model` create overrides now log a warning: use `@api.model_create_multi`
5. `t-lang` without `t-call` now raises SyntaxError (silently ignored in 14.0-15.0)
6. Keep `attrs`/`states` - they are still the correct syntax in 16.0

### v16 → v17
1. **MUST** replace all `attrs` and `states` with direct expressions (`invisible="..."`, `readonly="..."`, `required="..."`, `column_invisible`) - views using them fail validation
2. `_read_group(domain, groupby, aggregates)` returns tuples (14.0-16.0: `read_group(dom, fields, groupby, lazy)` -> dicts; 16.0 `_read_group` has that same old signature); `grouped()` available (14.0-16.0: `tools.groupby`)
3. `odoo.tools.SQL` builder available (`SQL.identifier`)
4. `patch(obj, ext)` with `super` (no patch name)
5. Legacy `odoo.define(name, function (require) {...})` modules are no longer supported
6. Python 3.10+
7. `SavepointCase` removed (deprecated alias in 15.0-16.0)

### v17 → v18
1. View type `tree` → `list` (`<list>`, `view_mode='list,form'`)
2. `check_access_rights`/`check_access_rule` → `check_access()`/`has_access()`
3. `self.env._()` and `LazyTranslate` for translations
4. Imported test classes and inherited `test_*` methods are no longer collected (`allow_inherited_tests_method = True`)
5. Restricted `pickle` wrapper removed
6. Route `auth='bearer'` available (14.0-17.0: `user`/`public`/`none` only)

### v18 → v19
1. **MUST** replace `_sql_constraints` with `models.Constraint` / `models.Index` / `models.UniqueIndex` (`_sql_constraints` is silently ignored)
2. `odoo.fields.Domain` replaces `osv.expression.AND/OR` (`expression.*` deprecated)
3. `read_group` deprecated → `_read_group` / `formatted_read_group`
4. `res.users.groups_id` → `group_ids`
5. Route type `json` → `jsonrpc` (alias kept); new type `json2`
6. `time` no longer in record-rule eval context
7. RPC guard also blocks classmethods/staticmethods

## Quick Reference Cards

### v18 Model Template
```python
from odoo import api, fields, models, Command, _
from odoo.tools import SQL

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', check_company=True)

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
```

### v18 View Template
```xml
<button name="action" invisible="state != 'draft'"/>
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
| `module 'odoo.api' has no attribute 'multi'` | v14+ | `@api.multi` still used | Remove decorator |
| `Since 17.0, the "attrs" and "states" attributes are no longer used.` | v17+ | `attrs`/`states` in a view | Use direct `invisible`/`readonly`/`required` expressions |
| `Field ...: unknown parameter 'track_visibility'` (warning) | v14+ | Old tracking parameter | Use `tracking=True` |
| Warning on `@api.model` create | v16+ | Single-dict `create` override | Use `@api.model_create_multi` |
| `_sql_constraints` warning, constraint missing | v19 | Old constraint declaration | Use `models.Constraint` |
| Invalid domain on `ir.rule` mentioning `allowed_company_ids` | v14+ | Context key used in a rule domain | Use `company_ids` |

---

**IMPORTANT**: This reference is for comparison purposes. Always use version-specific files for actual implementation patterns.
