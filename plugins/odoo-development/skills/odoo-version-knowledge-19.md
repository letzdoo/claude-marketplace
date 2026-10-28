# Odoo 19.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 19.0 KNOWLEDGE BASE                                                    ║
║  models.Constraint (no _sql_constraints), group_ids, Owl 2.8.x               ║
║  Released (final) - verified against the 19.0 source                         ║
║  VERIFY: https://github.com/odoo/odoo/tree/19.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Status | Released (`odoo/release.py`: `version_info = (19, 0, 0, FINAL, 0, '')`) |
| Python | 3.10 - 3.14 (`MIN_PY_VERSION = (3, 10)`, `MAX_PY_VERSION = (3, 14)`) |
| PostgreSQL | 13+ (`MIN_PG_VERSION = 13`) |
| Frontend | Owl 2.8.x (`addons/web/static/lib/owl/owl.js`: `version = "2.8.4"`) - there is NO Owl 3 in 19.0 |

## BREAKING Changes from v18

### SQL Constraints: `_sql_constraints` is IGNORED, use `models.Constraint()`
In 19.0 the registry only logs a warning ("Model attribute '_sql_constraints' is no longer
supported, please define models.Constraint on the model.") and **does not create the constraint**
(`odoo/orm/model_classes.py`). Same for `_constraints`.
```python
# v18 form - SILENTLY IGNORED in v19 (constraint is never created)
class MyModel(models.Model):
    _name = 'my.model'

    _sql_constraints = [
        ('check_percentage', 'CHECK(percentage >= 0 AND percentage <= 100)',
         'The percentage must be between 0 and 100.'),
    ]

# v19 form - class attribute, name must start with '_'
class MyModel(models.Model):
    _name = 'my.model'

    _check_percentage = models.Constraint(
        'CHECK(percentage >= 0 AND percentage <= 100)',
        'The percentage must be between 0 and 100.',
    )
    _code_company_uniq = models.UniqueIndex('(code, company_id)', 'Code must be unique per company.')
    _state_date_idx = models.Index('(state, date)')
```

### res.users: `groups_id` renamed to `group_ids`
The Many2many on `res.users` is `group_ids` (plus computed `all_group_ids`); the inverse on
`res.groups` is `user_ids` (plus `all_user_ids`). `ir.ui.view` and `ir.actions.act_window` also
use `group_ids`. Setting groups in `create()` works; Odoo's own test helpers do it
(`odoo/addons/base/tests/common.py`).
```python
from odoo import Command

# v19
user = self.env['res.users'].create({
    'name': 'Portal User',
    'login': 'portal@example.com',
    'group_ids': [Command.set([self.env.ref('base.group_portal').id])],
})

# or add a user to a group afterwards
self.env.ref('my_module.group_manager').write({'user_ids': [Command.link(user.id)]})
```

### Type Hints: optional
Type hints are NOT enforced in 19.0. Many core public methods have none (e.g. `read_group`).
They are welcome for readability; their absence never raises an error.

### Raw SQL: `SQL()` recommended, string queries still work
`cr.execute()` accepts either a string with a params tuple/list/dict or an `SQL` object
(`odoo/sql_db.py`); there is no deprecation of string queries. Prefer `SQL` because it composes
safely (`SQL.identifier()`, nested `SQL`, `Query.select()`; `_search()` returns a `Query`). Never
format values into the string.
```python
from odoo.tools import SQL

# Works in v19 (parameters passed separately)
self.env.cr.execute("SELECT id FROM my_model WHERE state = %s", ['draft'])

# Preferred in v19
self.env.cr.execute(SQL("SELECT id FROM my_model WHERE state = %s", 'draft'))
```

### Other 19.0 deprecations (still work, emit warnings)
- `odoo.osv.expression.AND/OR/normalize_domain` -> `odoo.fields.Domain`
- `read_group()` -> `_read_group(domain, groupby, aggregates)` (backend, returns a list of tuples) /
  `formatted_read_group()` (UI-style dicts)
- `@route(type='json')` -> `type='jsonrpc'`
- `odoo.models.check_method_name` -> `odoo.service.model.get_public_method` / `@api.private`
- `check_access_rights()` / `check_access_rule()` (since 18.0) -> `check_access()` / `has_access()`
- `toggle_active()` -> `action_archive()` / `action_unarchive()`
- `with_context(force_company=...)` -> `with_company(...)`
- QWeb `t-esc` (still renders escaped, dev-mode warning) and `t-raw` (still renders raw, always
  warns) -> `t-out`

### Owl 2 component (19.0 ships Owl 2.8.x)
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * @typedef {Object} MyComponentProps
 * @property {number} [recordId]
 * @property {(id: number) => void} [onSelect]
 */

/**
 * @typedef {Object} MyComponentState
 * @property {Array<Object>} data
 * @property {boolean} loading
 * @property {string|null} error
 */

export class MyComponent extends Component {
    /** @type {string} */
    static template = "my_module.MyComponent";

    /** @type {MyComponentProps} */
    static props = {
        recordId: { type: Number, optional: true },
        onSelect: { type: Function, optional: true },
    };

    static defaultProps = {
        recordId: null,
    };

    setup() {
        /** @type {import("@web/core/orm_service").ORM} */
        this.orm = useService("orm");
        this.notification = useService("notification");

        /** @type {MyComponentState} */
        this.state = useState({
            data: [],
            loading: true,
            error: null,
        });

        this._abortController = null;

        onWillStart(async () => {
            await this.loadData();
        });

        onWillUnmount(() => {
            this._abortController?.abort();
        });
    }

    /**
     * Load data from server
     * @returns {Promise<void>}
     */
    async loadData() {
        this._abortController = new AbortController();

        try {
            const data = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state"],
                { order: "create_date DESC" }
            );
            this.state.data = data;
            this.state.error = null;
        } catch (error) {
            if (error.name !== 'AbortError') {
                this.state.error = error.message;
                this.notification.add("Failed to load data", { type: "danger" });
            }
        } finally {
            this.state.loading = false;
        }
    }
}
```

## Key Features

### New in Odoo 19 (framework, verified)
- `odoo.fields.Domain` object for domains (`&`, `|`, `~`, `Domain.AND/OR`)
- `models.Constraint` / `models.Index` / `models.UniqueIndex` replace `_sql_constraints`
- `@api.private` to hide public methods from RPC
- `self.env._()` translation helper; `_()` takes interpolation args; `_lt` / `LazyTranslate` exist
- Route type `jsonrpc` (and `json2`); `json` is a deprecated alias
- `formatted_read_group()` (web) replaces `read_group()` for UI-style results

### Technical Stack
- Python 3.10 - 3.14
- PostgreSQL 13+
- Owl 2.8.x

## Version-Specific Patterns

### Model Definition with Type Hints
```python
from __future__ import annotations
from typing import TYPE_CHECKING

from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL
import logging

if TYPE_CHECKING:
    from odoo.addons.base.models.res_partner import Partner
    from odoo.addons.base.models.res_company import Company

_logger = logging.getLogger(__name__)


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'
    _check_company_auto = True

    # Fields with type annotations
    name: str = fields.Char(
        required=True,
        index='trigram',
        tracking=True,
    )

    code: str = fields.Char(index=True, copy=False)

    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True, index=True)

    sequence: int = fields.Integer(default=10)
    active: bool = fields.Boolean(default=True)

    date: fields.Date = fields.Date(default=fields.Date.context_today)

    company_id: Company = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )

    partner_id: Partner = fields.Many2one(
        'res.partner',
        check_company=True,
        tracking=True,
    )

    line_ids: models.Model = fields.One2many(
        'my.model.line',
        'model_id',
        copy=True,
    )

    total_amount: float = fields.Monetary(
        compute='_compute_total',
        store=True,
        currency_field='currency_id',
    )

    currency_id: models.Model = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )
```

### CRUD Methods with Type Hints
`create` with a single dict (no decorator) is still accepted silently in 19.0, but always write
`@api.model_create_multi`.
```python
@api.model_create_multi
def create(self, vals_list: list[dict]) -> 'MyModel':
    """Create records with validation.

    Args:
        vals_list: List of value dictionaries

    Returns:
        Created records
    """
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')

    records = super().create(vals_list)

    for record in records:
        record.message_post(body=_("Record created."))

    return records

def write(self, vals: dict) -> bool:
    """Update records with state validation.

    Args:
        vals: Values to update

    Returns:
        True on success
    """
    if 'state' in vals and vals['state'] == 'confirmed':
        for record in self:
            if not record.line_ids:
                raise UserError(_("Add at least one line."))
    return super().write(vals)

def unlink(self) -> bool:
    """Delete with state check.

    Returns:
        True on success

    Raises:
        UserError: If record cannot be deleted
    """
    for record in self:
        if record.state not in ('draft', 'cancelled'):
            raise UserError(_("Only draft records can be deleted."))
    return super().unlink()

def copy(self, default: dict | None = None) -> 'MyModel':
    """Copy record.

    Args:
        default: Override values

    Returns:
        New record
    """
    self.ensure_one()
    default = dict(default or {})
    default['name'] = _("%s (copy)", self.name)
    return super().copy(default)
```

### SQL Queries with SQL() Builder
```python
from odoo.tools import SQL

def get_summary_data(self) -> list[dict]:
    """Get summary using SQL() builder.

    Returns:
        List of summary dictionaries
    """
    self.env.cr.execute(SQL(
        """
        SELECT state, COUNT(*) as count, SUM(total_amount) as total
        FROM my_model
        WHERE company_id = %s
        GROUP BY state
        ORDER BY count DESC
        """,
        self.env.company.id
    ))
    return self.env.cr.dictfetchall()

def bulk_update(self, state: str, ids: list[int]) -> int:
    """Bulk update using SQL().

    Args:
        state: New state
        ids: Record IDs

    Returns:
        Number of updated records
    """
    if not ids:
        return 0

    self.env.cr.execute(SQL(
        """
        UPDATE my_model
        SET state = %s, write_date = NOW(), write_uid = %s
        WHERE id = ANY(%s) AND company_id = %s
        """,
        state, self.env.uid, ids, self.env.company.id
    ))

    self.browse(ids).invalidate_recordset()
    return self.env.cr.rowcount
```

### Computed Fields with Types
```python
@api.depends('line_ids.amount')
def _compute_total(self) -> None:
    """Compute total from lines."""
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))

@api.depends('line_ids')
def _compute_line_count(self) -> None:
    """Compute line count."""
    for record in self:
        record.line_count = len(record.line_ids)

is_overdue: bool = fields.Boolean(
    compute='_compute_is_overdue',
    search='_search_is_overdue',
    store=True,
)

@api.depends('date_deadline', 'state')
def _compute_is_overdue(self) -> None:
    """Compute overdue status."""
    today = fields.Date.context_today(self)
    for record in self:
        record.is_overdue = (
            record.date_deadline
            and record.date_deadline < today
            and record.state not in ('done', 'cancelled')
        )

def _search_is_overdue(self, operator: str, value: bool) -> list:
    """Search overdue records.

    Args:
        operator: Search operator
        value: Search value

    Returns:
        Search domain
    """
    today = fields.Date.context_today(self)
    if (operator == '=' and value) or (operator == '!=' and not value):
        return [('date_deadline', '<', today), ('state', 'not in', ('done', 'cancelled'))]
    return ['|', ('date_deadline', '>=', today), ('date_deadline', '=', False)]
```

## Owl 2.8 Notes

### Reactivity of Set/Map
Owl 2 already tracks `Set` and `Map` in `useState` (they are listed as reactive raw types in
`owl.js`); this is not new in 19.0. `markup` from `@odoo/owl` works as a tagged template.
```javascript
setup() {
    this.state = useState({
        items: [],
        selectedIds: new Set(),
    });
}

toggleSelect(id) {
    if (this.state.selectedIds.has(id)) {
        this.state.selectedIds.delete(id);
    } else {
        this.state.selectedIds.add(id);
    }
}
```

### Props Validation
```javascript
static props = {
    recordId: { type: Number, optional: true },
    onConfirm: { type: Function, optional: true },
    mode: {
        type: String,
        optional: true,
        validate: (value) => ['view', 'edit'].includes(value),
    },
};

static defaultProps = {
    mode: 'view',
};
```

## Migration from v18

### Constraint Migration (mandatory)
```python
# v18
_sql_constraints = [('code_uniq', 'unique(code)', 'Code must be unique.')]

# v19 (the list above is ignored with only a warning)
_code_uniq = models.Constraint('UNIQUE(code)', 'Code must be unique.')
```

### Group Field Migration (mandatory)
- `res.users.groups_id` -> `group_ids`; `res.groups.users` -> `user_ids`
- `ir.ui.view.groups_id` / `ir.actions.act_window.groups_id` -> `group_ids`

### Domain Migration (recommended)
```python
# v18
from odoo.osv import expression
domain = expression.AND([domain, [('company_id', 'in', company_ids)]])

# v19 (osv.expression still works but warns)
from odoo.fields import Domain
domain = Domain(domain) & Domain('company_id', 'in', company_ids)
```

## Best Practices for v19

1. **models.Constraint / Index / UniqueIndex** - never `_sql_constraints`
2. **Use SQL() builder** for raw SQL (recommended, not enforced)
3. **_check_company_auto = True** - opt-in flag (default False) for multi-company models
4. **check_company=True** - On relational fields
5. **Domain objects** - `odoo.fields.Domain` instead of `osv.expression`
6. Type hints are optional (not enforced)

## Manifest Structure

```python
{
    'name': 'My Module',
    'version': '19.0.1.0.0',
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

## Common Issues

### SQL Constraint Not Created
```
WARNING ... Model attribute '_sql_constraints' is no longer supported, please define models.Constraint on the model.
```
Solution: Convert each tuple to a `models.Constraint(...)` class attribute (see above).

### Invalid Field `groups_id`
Writing `groups_id` on `res.users` fails because the field is `group_ids` in 19.0.
```python
user = self.env['res.users'].create({
    'name': 'Portal User',
    'login': 'portal@example.com',
    'group_ids': [Command.set([self.env.ref('base.group_portal').id])],
})
```

### View Mode `tree`
The view type is `list` (`ir.ui.view.type` has no `tree`); use `'view_mode': 'list,form'` and
`<list>` arch.

## Additional Rules from Odoo's Official Guidelines (verified for 19.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were
checked against the 19.0 source; master-only APIs are translated to the 19.0 equivalent or marked
as not available.

### API availability in 19.0 vs master

| Topic | 19.0 | Notes |
|-------|------|-------|
| Access model | `ir.model.access` + `ir.rule` | master `ir.access` does NOT exist (see list below) |
| `_allow_sudo_commands` | exists | |
| `fields.NO_ACCESS` | exists (`'.'`) | |
| `related_sudo` | default True | `related_sudo=False` for sensitive chains |
| `grouped()` | exists | |
| Route `auth` | `user`, `bearer`, `public`, `none` | NO `bearer_scope` parameter |
| CSRF | on for `http` (non-GET), none for `jsonrpc` | |
| `t-lang` | only on a node with `t-call` | otherwise `SyntaxError` |
| `odoo.tools.consteq` | exists | |
| Restricted pickle (`odoo.tools.pickle`) | absent | never pickle |
| `base.group_everyone` | absent | |
| Test default tags | `standard`, `at_install` | post-install needs `@tagged('post_install', '-at_install')` |
| `BaseCommon`, `TransactionCaseWithUserDemo` | exist | `SavepointCase` absent |
| `allow_inherited_tests_method` | exists | |
| `patch()` | `patch(obj, extension)` | |
| `populate` | `odoo-bin populate` duplicates records | no factory API |

### Master/20.0-only - do NOT use in 19.0
- `ir.access` model and `security/ir.access.csv`
- `bearer_scope=` on `@http.route`
- Owl `computed` (Owl 3)
- `expectUnloadPage` tour step option (not verified for 19.0)
- `populate.blueprint` / factory-based populate
- `--unsafe-policy` server option
