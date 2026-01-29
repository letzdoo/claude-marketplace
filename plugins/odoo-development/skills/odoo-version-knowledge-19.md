# Odoo 19.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 19.0 KNOWLEDGE BASE                                                    ║
║  Type hints mandatory, SQL() required, OWL 3.x                               ║
║  WARNING: v19 is in development - patterns may change                        ║
║  VERIFY: https://github.com/odoo/odoo/tree/master                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Release Date | October 2024 (Expected) |
| Python | 3.11, 3.12 |
| PostgreSQL | 14, 15, 16 |
| Frontend | OWL 3.x |
| Status | In Development |

## BREAKING Changes from v18

### SQL Constraints Use models.Constraint() Class
```python
# DEPRECATED in v19 - _sql_constraints list
class MyModel(models.Model):
    _name = 'my.model'

    _sql_constraints = [
        ('check_percentage', 'CHECK(percentage >= 0 AND percentage <= 100)',
         'The percentage must be between 0 and 100.'),
    ]

# v19 REQUIRED - models.Constraint() class
class MyModel(models.Model):
    _name = 'my.model'

    _check_percentage = models.Constraint(
        'CHECK(percentage >= 0 AND percentage <= 100)',
        'The percentage of an analytic distribution should be between 0 and 100.',
    )
```

### res.users.create() Cannot Set groups_id
```python
# BROKEN - groups_id ignored during create
user = self.env['res.users'].create({
    'login': 'user@example.com',
    'groups_id': [(6, 0, [group.id])],  # IGNORED!
})

# CORRECT - Add to group after creation
user = self.env['res.users'].create({'login': 'user@example.com'})
group.write({'users': [(4, user.id)]})
```

### Type Hints MANDATORY
```python
# DEPRECATED in v19
def action_confirm(self):
    pass

# v19 REQUIRED
def action_confirm(self) -> bool:
    return True

def create_record(self, name: str, partner_id: int | None = None) -> 'MyModel':
    return self.create({'name': name, 'partner_id': partner_id})
```

### SQL() Builder REQUIRED
```python
from odoo.tools import SQL

# DEPRECATED in v19
self.env.cr.execute("SELECT id FROM my_model WHERE state = %s", ['draft'])

# v19 REQUIRED
self.env.cr.execute(SQL(
    "SELECT id FROM my_model WHERE state = %s",
    'draft'
))
```

### OWL 3.x
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

### New in Odoo 19 (Expected)
- OWL 3.x framework
- Mandatory type hints
- SQL() builder required
- Enhanced performance
- AI integrations
- Improved mobile experience

### Technical Stack
- Python 3.11+ (3.12 recommended)
- PostgreSQL 14+
- OWL 3.x framework
- Full ES2022+ support

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

## OWL 3.x Features

### Enhanced Reactivity
```javascript
setup() {
    this.state = useState({
        items: [],
        selectedIds: new Set(),  // Sets now fully reactive
    });
}

toggleSelect(id) {
    // Direct mutation works in OWL 3.x
    if (this.state.selectedIds.has(id)) {
        this.state.selectedIds.delete(id);
    } else {
        this.state.selectedIds.add(id);
    }
    // No need to recreate Set
}
```

### Enhanced Props Validation
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

### Type Hints Migration
```python
# v18 (worked without types)
def action_confirm(self):
    for record in self:
        record.state = 'confirmed'
    return True

# v19 (types required)
def action_confirm(self) -> bool:
    for record in self:
        record.state = 'confirmed'
    return True
```

### SQL Migration
```python
# v18 (string queries worked)
self.env.cr.execute("SELECT id FROM my_model WHERE state = %s", ['draft'])

# v19 (SQL() required)
from odoo.tools import SQL
self.env.cr.execute(SQL("SELECT id FROM my_model WHERE state = %s", 'draft'))
```

### OWL Migration (2.x → 3.x)
- Add comprehensive JSDoc annotations
- Use AbortController for cancellation
- Implement proper cleanup in onWillUnmount
- Update Set/Map usage (now reactive)

## Best Practices for v19

1. **Type hints everywhere** - On all public methods
2. **Use SQL() builder** - For all raw SQL
3. **_check_company_auto = True** - On multi-company models
4. **check_company=True** - On relational fields
5. **OWL 3.x patterns** - Comprehensive JSDoc, cleanup
6. **from __future__ import annotations** - For forward refs

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

### Missing Type Hints
```
TypeError: Missing return type annotation
```
Solution: Add return type to all public methods

### SQL String Deprecated
```
DeprecationWarning: String SQL queries are deprecated
```
Solution: Use `SQL()` builder from `odoo.tools`

### OWL Set Reactivity
```javascript
// v18 issue - Set not reactive
this.state.selectedIds = new Set(this.state.selectedIds);

// v19 - Direct mutation works
this.state.selectedIds.add(id);
```

### groups_id Cannot Be Set During res.users.create()

In Odoo 19, `groups_id` cannot be set directly during `res.users.create()`.

```python
# BROKEN in v19
user = self.env['res.users'].create({
    'name': 'Portal User',
    'login': 'portal@example.com',
    'groups_id': [(6, 0, [portal_group.id])],  # This will NOT work
})

# CORRECT in v19 - Create user first, then add to group
user = self.env['res.users'].create({
    'name': 'Portal User',
    'login': 'portal@example.com',
})
portal_group = self.env.ref('base.group_portal')
portal_group.write({'users': [(4, user.id)]})
```

**Why**: Security hardening prevents group assignment during user creation to avoid privilege escalation.
