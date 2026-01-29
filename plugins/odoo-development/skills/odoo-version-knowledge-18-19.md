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
| SQL | `SQL()` builder **REQUIRED** | **CRITICAL** - All raw SQL |
| Type Hints | **REQUIRED** for methods | High - Update all methods |
| SQL Constraints | `models.Constraint()` class **REQUIRED** | High - All SQL constraints |
| res.users | `groups_id` cannot be set in create() | High - User creation code |
| OWL | OWL 3.x replaces 2.x | High - Component rewrite |
| Multi-Company | `_check_company_auto` required | High - All multi-company models |
| Python | Python 3.12+ required | Medium - Check compatibility |

## CRITICAL: SQL() Builder Required

### Before (v18) - Worked but discouraged
```python
# String SQL - NO LONGER WORKS in v19
self.env.cr.execute("""
    SELECT id FROM my_model WHERE state = %s
""", ('draft',))
```

### After (v19) - Required
```python
from odoo.tools import SQL

# MUST use SQL() builder
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

In Odoo 19, SQL constraints must use the `models.Constraint()` class instead of the `_sql_constraints` list.

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

## res.users: groups_id Cannot Be Set in create()

In Odoo 19, `groups_id` is ignored during `res.users.create()` due to security hardening.

### Before (v18) - Worked
```python
user = self.env['res.users'].create({
    'name': 'Portal User',
    'login': 'portal@example.com',
    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
})
```

### After (v19) - Must Add Group Separately
```python
# Create user first
user = self.env['res.users'].create({
    'name': 'Portal User',
    'login': 'portal@example.com',
})

# Then add to group via group's users field
portal_group = self.env.ref('base.group_portal')
portal_group.write({'users': [(4, user.id)]})
```

### Migration Pattern
```python
def migrate(cr, version):
    """Update user creation code for v19 compatibility."""
    # Find all user creation patterns and update them
    # groups_id must be set after create() via group.write()
```

## Type Hints Required

### v19 Required Style
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

## OWL 3.x Migration

### OWL 2.x (v18)
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

### OWL 3.x (v19)
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

### OWL 3.x Key Changes

| OWL 2.x | OWL 3.x |
|---------|---------|
| `static props = { field: Type }` | `static props = { field: { type: Type, required: bool } }` |
| Props validation basic | Enhanced props validation with defaults |
| `onWillStart(async () => {})` | `onWillStart(() => promise)` |
| Basic error boundaries | Enhanced error handling |

## Multi-Company Enforcement

### v19 Required Pattern
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True  # REQUIRED for multi-company

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,  # REQUIRED
        readonly=True,
        default=lambda self: self.env.company,
        index=True,
    )

    # ALL relational fields must have check_company
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # REQUIRED
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        check_company=True,  # REQUIRED
    )
```

## Python 3.12+ Features

### Usable in v19
```python
# Type parameter syntax (PEP 695)
type RecordList = list['MyModel']

# Self type
from typing import Self

class MyModel(models.Model):
    def copy(self) -> Self:
        return super().copy()

# Match statement (structural pattern matching)
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
# SQL builder (required)
https://raw.githubusercontent.com/odoo/odoo/master/odoo/tools/sql.py

# OWL 3.x
https://raw.githubusercontent.com/odoo/odoo/master/addons/web/static/src/core/

# Type hints in core
https://raw.githubusercontent.com/odoo/odoo/master/odoo/models.py

# Note: v19 uses 'master' branch until release
```

## Migration Checklist

- [ ] **CRITICAL**: Migrate ALL raw SQL to `SQL()` builder
- [ ] Add type hints to ALL public methods
- [ ] Update OWL 2.x components to OWL 3.x
- [ ] Ensure `_check_company_auto = True` on all models
- [ ] Add `check_company=True` to all relational fields
- [ ] Verify Python 3.12+ compatibility
- [ ] Update prop definitions in OWL components
- [ ] Test all SQL queries work with SQL builder
- [ ] Review and update all tests

## Common Migration Errors

### Error: `SQL string queries not supported`
**Fix**: Wrap ALL raw SQL with `SQL()`:
```python
from odoo.tools import SQL
self.env.cr.execute(SQL("SELECT ...", param1, param2))
```

### Error: `Type hints required for public method`
**Fix**: Add return type and parameter types:
```python
def my_method(self, param: str) -> bool:
```

### Error: `Props validation failed`
**Fix**: Update OWL props to new format:
```javascript
static props = {
    value: { type: Number, required: true },
    label: { type: String, optional: true },
};
```

## SQL Migration Tool

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

## Comparison: v18 vs v19

```python
# v18 Style (works but not recommended)
class MyModelV18(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    def get_totals(self):
        self.env.cr.execute("""
            SELECT SUM(amount) FROM my_model WHERE state = %s
        """, ('done',))
        return self.env.cr.fetchone()[0]


# v19 Style (required)
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
