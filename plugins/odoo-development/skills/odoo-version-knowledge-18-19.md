# Odoo Version Knowledge: 18 to 19 Migration

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  VERSION MIGRATION: 18.0 → 19.0                                              ║
║  Critical changes, breaking changes, and migration patterns                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Category | Change | Impact |
|----------|--------|--------|
| SQL Constraints | `_sql_constraints` is **ignored** in 19 (only a warning is logged); use `models.Constraint()` / `models.Index()` / `models.UniqueIndex()` | **CRITICAL** - constraints silently disappear |
| Domains | `odoo.fields.Domain` (`&`, `|`, `~`, `Domain.AND/OR`) replaces `odoo.osv.expression.AND/OR` helpers (still available, deprecated) | Medium |
| res.users / views / actions | `groups_id` renamed to `group_ids` | High - user creation, data files |
| Routes | `type='json'` becomes a deprecated alias of `type='jsonrpc'`; new `type='json2'` | Low |
| `read_group()` | `read_group()` (dicts) deprecated -> `formatted_read_group()` (`_read_group()`, returning tuples, unchanged) | Medium |
| ir.rule eval context | `time` removed (`user`, `company_ids`, `company_id` remain) | Low |
| Manifest | empty `depends` -> `['base']` injected (18: stays empty, declare `base`) | Low |
| SQL | `SQL()` builder recommended in both versions; plain `cr.execute(str, params)` still works in 19 | None |
| Type Hints | optional in both versions | None |
| OWL | Owl 2.x in both (19.0 ships Owl 2.8.4, not Owl 3) | None |
| Multi-Company | `_check_company_auto` stays opt-in (default False) | None |
| Python | 3.10+ in both (19.0 `release.py`: `MIN_PY_VERSION = (3, 10)`) | None |

## SQL() Builder (recommended in both versions)

### v18 and v19 - plain parameterized SQL still works
```python
# Still valid in v19 (core itself uses it); never format values into the string
self.env.cr.execute("""
    SELECT id FROM my_model WHERE state = %s
""", ('draft',))
```

### Preferred in v18 and v19
```python
from odoo.tools import SQL

self.env.cr.execute(SQL(
    "SELECT id FROM my_model WHERE state = %s",
    'draft'
))
```

### SQL Builder Patterns

```python
from odoo.tools import SQL

class MyModel(models.Model):
    _name = 'my.model'

    def _get_statistics(self) -> dict:
        """Get aggregated statistics using SQL builder"""
        self.env.cr.execute(SQL(
            """
            SELECT
                state,
                COUNT(*) as count,
                SUM(amount) as total
            FROM my_model
            WHERE company_id = %s
              AND create_date >= %s
            GROUP BY state
            """,
            self.env.company.id,
            fields.Date.today() - timedelta(days=30)
        ))
        return {row['state']: row for row in self.env.cr.dictfetchall()}

    def _bulk_update(self, ids: list[int], new_state: str) -> int:
        """Bulk update using SQL builder"""
        if not ids:
            return 0

        self.env.cr.execute(SQL(
            """
            UPDATE my_model
            SET state = %s, write_date = %s, write_uid = %s
            WHERE id IN %s
            RETURNING id
            """,
            new_state,
            fields.Datetime.now(),
            self.env.uid,
            tuple(ids)
        ))
        updated_ids = [row[0] for row in self.env.cr.fetchall()]

        # Invalidate ORM cache
        self.browse(updated_ids).invalidate_recordset()
        return len(updated_ids)
```

## SQL Constraints: models.Constraint() Class Required

In Odoo 19, SQL constraints must use the `models.Constraint()` class instead of the `_sql_constraints` list. A remaining `_sql_constraints` attribute is not applied at all: 19 only logs "Model attribute '_sql_constraints' is no longer supported" (`odoo/orm/model_classes.py`).

### Before (v18) - Worked
```python
class MyModel(models.Model):
    _name = 'my.model'

    percentage = fields.Float()

    _sql_constraints = [
        ('check_percentage',
         'CHECK(percentage >= 0 AND percentage <= 100)',
         'The percentage must be between 0 and 100.'),
    ]
```

### After (v19) - Required
```python
class MyModel(models.Model):
    _name = 'my.model'

    percentage = fields.Float()

    _check_percentage = models.Constraint(
        'CHECK(percentage >= 0 AND percentage <= 100)',
        'The percentage of an analytic distribution should be between 0 and 100.',
    )
```

### Migration Pattern
```python
# Convert each constraint from _sql_constraints list to class attribute
# Old format: (name, sql, message)
# New format: attribute_name = models.Constraint(sql, message)

# Before (v18)
_sql_constraints = [
    ('code_unique', 'UNIQUE(code)', 'Code must be unique.'),
    ('amount_positive', 'CHECK(amount >= 0)', 'Amount must be positive.'),
]

# After (v19)
_code_unique = models.Constraint(
    'UNIQUE(code)',
    'Code must be unique.',
)
_amount_positive = models.Constraint(
    'CHECK(amount >= 0)',
    'Amount must be positive.',
)
```

## res.users: groups_id Renamed to group_ids

In Odoo 19 the user's groups field is `group_ids` (`odoo/addons/base/models/res_users.py`);
`ir.ui.view` and `ir.actions.act_window` use `group_ids` as well.

### Before (v18)
```python
user = self.env['res.users'].create({
    'name': 'Portal User',
    'login': 'portal@example.com',
    'groups_id': [Command.set([self.env.ref('base.group_portal').id])],
})
```

### After (v19)
```python
user = self.env['res.users'].create({
    'name': 'Portal User',
    'login': 'portal@example.com',
    'group_ids': [Command.set([self.env.ref('base.group_portal').id])],
})
```

## Type Hints (optional in v18 and v19)

Odoo 19 core still has public methods without annotations; nothing enforces them.

### Example Style
```python
from typing import Optional, Any
from collections.abc import Iterable
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True

    name: str = fields.Char(required=True, index=True)
    active: bool = fields.Boolean(default=True)
    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)
    amount: float = fields.Monetary(currency_field='currency_id')
    company_id = fields.Many2one('res.company', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )

    def action_confirm(self) -> bool:
        """Confirm records and return success status."""
        for record in self:
            if record.state != 'draft':
                continue
            record.state = 'confirmed'
        return True

    def action_done(self) -> bool:
        """Mark records as done."""
        self.filtered(lambda r: r.state == 'confirmed').write({
            'state': 'done'
        })
        return True

    def get_partner_name(self) -> Optional[str]:
        """Get partner name or None."""
        self.ensure_one()
        return self.partner_id.name if self.partner_id else None

    @api.model
    def search_by_state(self, state: str, limit: int = 100) -> 'MyModel':
        """Search records by state."""
        return self.search([('state', '=', state)], limit=limit)

    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> 'MyModel':
        """Create records with sequence generation."""
        for vals in vals_list:
            if 'code' not in vals:
                vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        """Update records with audit logging."""
        if 'state' in vals:
            self._log_state_change(vals['state'])
        return super().write(vals)

    def _log_state_change(self, new_state: str) -> None:
        """Log state change for audit."""
        for record in self:
            record.message_post(
                body=f"State changed to {new_state}",
                message_type='notification',
            )
```

### Type Hint Reference

| Return Type | Usage |
|-------------|-------|
| `bool` | Action methods returning success |
| `'ModelName'` | Methods returning recordset |
| `Optional[T]` | May return None |
| `list[dict]` | List of dictionaries |
| `dict[str, Any]` | Flexible dictionary |
| `None` | Void methods (use `-> None`) |
| `int` | Count/ID methods |
| `str` | String methods |

## OWL: 2.x in Both Versions

Odoo 19.0 ships Owl 2.8.4 (`addons/web/static/lib/owl/owl.js`), not Owl 3. Existing v18
components keep working; the "v19" variant below is only a style refresh (object prop
specs, try/finally), not a required migration.

### v18
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: Number,
        onSave: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: null, loading: true });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        const data = await this.orm.read("my.model", [this.props.recordId]);
        this.state.data = data[0];
        this.state.loading = false;
    }
}
```

### v19 (same Owl 2 API)
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, required: true },
        onSave: { type: Function, optional: true },
        config: { type: Object, optional: true },
    };
    static defaultProps = {
        config: {},
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            data: null,
            loading: true,
            error: null,
        });

        onWillStart(() => this.loadData());
    }

    async loadData() {
        try {
            const [data] = await this.orm.read(
                "my.model",
                [this.props.recordId],
                ["name", "state", "amount"]
            );
            this.state.data = data;
        } catch (error) {
            this.state.error = error.message;
            this.notification.add("Failed to load data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onConfirm() {
        await this.orm.call("my.model", "action_confirm", [[this.props.recordId]]);
        await this.loadData();
        this.props.onSave?.();
    }
}
```

Both prop forms (`field: Type` and `field: { type: Type, optional: true }`) are valid Owl 2 syntax in v18 and v19.

## Multi-Company (unchanged)

`_check_company_auto` is opt-in in both versions (default `False` in 19.0
`odoo/orm/models.py`). Recommended pattern for multi-company models:
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,
    )
```

## Python Features

Both versions require Python 3.10+ (3.12 recommended). Keep code 3.10-compatible
(no PEP 695 `type` statements) unless the deployment pins a newer Python.

```python
# Match statement (Python 3.10+)
def process_state(self) -> str:
    match self.state:
        case 'draft':
            return 'Processing draft'
        case 'confirmed' | 'validated':
            return 'In progress'
        case 'done':
            return 'Completed'
        case _:
            return 'Unknown state'
```

## GitHub Verification URLs

```
# SQL builder
https://raw.githubusercontent.com/odoo/odoo/19.0/odoo/tools/sql.py

# ORM (19.0 moved the ORM to odoo/orm/)
https://raw.githubusercontent.com/odoo/odoo/19.0/odoo/orm/models.py

# Web client (Owl 2.8.x)
https://raw.githubusercontent.com/odoo/odoo/19.0/addons/web/static/src/core/
```

## Migration Checklist

- [ ] **CRITICAL**: Convert every `_sql_constraints` to `models.Constraint()` / `models.UniqueIndex()` (ignored in 19)
- [ ] Rename `groups_id` to `group_ids` on res.users, views and actions (Python and XML data)
- [ ] Replace `odoo.osv.expression` helpers with `odoo.fields.Domain` (old ones still work, deprecated)
- [ ] Replace `read_group()` calls with `_read_group()` or `formatted_read_group()`
- [ ] Remove `time` from record rule domains (no longer in the eval context)
- [ ] Review routes declared with `type='json'` (deprecated alias of `jsonrpc`)
- [ ] Review and update all tests

## Common Migration Errors

### Unique/check constraint no longer enforced
**Cause**: `_sql_constraints` left in place (19 logs a warning and ignores it).
**Fix**: Declare `_name_uniq = models.Constraint('UNIQUE(name)', 'Name must be unique.')`.

### `Invalid field 'groups_id' on model 'res.users'`
**Fix**: Use `group_ids`.

## SQL Builder Conversion Helper (optional)

```python
#!/usr/bin/env python3
"""
Tool to migrate raw SQL to SQL() builder
"""
import re

def migrate_sql(content: str) -> str:
    """Convert raw SQL execute calls to SQL() builder"""

    # Add import if not present
    if 'from odoo.tools import SQL' not in content:
        content = 'from odoo.tools import SQL\n' + content

    # Pattern for execute with string
    pattern = r'self\.env\.cr\.execute\(\s*(["\'])(.*?)\1\s*,\s*\((.*?)\)\s*\)'

    def replace_sql(match):
        quote = match.group(1)
        sql = match.group(2)
        params = match.group(3)
        # Convert tuple params to positional
        param_list = [p.strip() for p in params.split(',')]
        return f'self.env.cr.execute(SQL({quote}{sql}{quote}, {", ".join(param_list)}))'

    content = re.sub(pattern, replace_sql, content, flags=re.DOTALL)
    return content
```

## Additional deltas from Odoo's official guidelines (18.0 -> 19.0)

Items of the verified 14-19 matrix (official Odoo skill rules, checked against both source trees) that change between 18.0 and 19.0 and are not in the Breaking Changes Summary:

| Topic | 18.0 | 19.0 |
|-------|------|------|
| RPC guard (`get_public_method`) | blocks `_` names, `@api.private`, unsafe attribute names | + blocks classmethods/staticmethods; `check_method_name` deprecated |
| Web HTML helpers | `htmlEscape`, `setElementContent`, `isHtmlEmpty` | + `htmlJoin`, `htmlSprintf`, `htmlReplace`, ... (still no `setInnerHtml`) |
| `@api.model` on `create` | works, DeprecationWarning | converted silently |
| Multi-column index | `init()` + `tools.sql.create_index` | `models.Index` |
| Translation | `env._`, `_()`, `LazyTranslate`; list args not localized | + iterable args formatted per language |
| Archiving | `action_archive`, `toggle_active` | `toggle_active` deprecated |
| `BaseCommon` (tests) | runs as superuser | optional independent user/company |

Unchanged between 18.0 and 19.0: default test tags `standard` + `at_install`; post-install via `@tagged('post_install', '-at_install')`; `check_access()` API; Owl without `computed`; `patch(obj, extension)`; no `ir.access`, no `base.group_everyone`, no `bearer_scope`; `t-raw` still renders unescaped, `t-esc` escapes (both deprecated).

## Comparison: v18 vs v19

```python
# v18 Style (still valid in v19)
class MyModelV18(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    def get_totals(self):
        self.env.cr.execute("""
            SELECT SUM(amount) FROM my_model WHERE state = %s
        """, ('done',))
        return self.env.cr.fetchone()[0]


# Preferred style in v18 and v19 (SQL builder)
class MyModelV19(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    def get_totals(self) -> float:
        self.env.cr.execute(SQL(
            "SELECT SUM(amount) FROM my_model WHERE state = %s",
            'done'
        ))
        result = self.env.cr.fetchone()
        return result[0] if result else 0.0
```
