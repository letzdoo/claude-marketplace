# Odoo Security Guide - Migration 18.0 → 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: ODOO 18.0 → 19.0 SECURITY                                  ║
║  Use this guide when upgrading security code from v18 to v19.                ║
║  Verified against the 18.0 and 19.0 (final) source trees.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview of Security Changes

| Component | v18 | v19 | Migration Required |
|-----------|-----|-----|-------------------|
| Record rule eval context | `user`, `time`, `company_ids`, `company_id` | `user`, `company_ids`, `company_id` | Remove `time` from rule domains |
| User groups field | `groups_id` | `group_ids` | Rename |
| Domain combination (no list concatenation onto security domains) | `odoo.osv.expression`: `expression.AND([...])` | `odoo.fields.Domain`: `Domain(a) & Domain(b)` (expression deprecated) | Recommended |
| RPC guard `get_public_method` | blocks `_` names, `@api.private`, unsafe attribute names; classmethods callable | + blocks classmethods/staticmethods | None |
| Route types | `http`, `json` | `http`, `jsonrpc`, `json2`; `json` = deprecated alias | Optional |
| Type hints | Optional | Optional | None |
| SQL builder | Recommended | Recommended | None |
| Python | 3.10+ | 3.10+ | None |
| OWL | 2.x | 2.x (2.8.4) | None |

## Style Notes (not breaking)

### 1. Type Hints (optional in both versions)

**Without hints:**
```python
class MyModel(models.Model):
    _name = 'my.model'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner')
    line_ids = fields.One2many('my.line', 'parent_id')
```

**With method hints (optional style):**
```python
class MyModel(models.Model):
    _name = 'my.model'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner')

    def _get_partner_name(self) -> str:
        self.ensure_one()
        return self.partner_id.name or ''
```

### 2. SQL Builder (recommended in both versions)

**Parameterized string SQL (still valid in v18 and v19):**
```python
self.env.cr.execute(
    "SELECT id FROM my_table WHERE company_id = %s",
    [self.env.company.id]
)
```

**SQL builder (preferred in v18 and v19):**
```python
from odoo.tools import SQL

query = SQL(
    "SELECT id FROM %(table)s WHERE company_id = %(company_id)s",
    table=SQL.identifier('my_table'),
    company_id=self.env.company.id,
)
self.env.cr.execute(query)
```

## Optional Helper Scripts (style only, nothing here is required by 19.0)

Note: annotations like `partner_id: int = fields.Many2one(...)` are not real types for
Odoo fields; they are cosmetic. Prefer no field annotations.

```python
import re

def add_type_hints(python_content):
    """Add type hints to field definitions."""

    # Pattern for field definitions without type hints
    field_patterns = {
        r"(\w+)\s*=\s*fields\.Char\(": r"\1: str = fields.Char(",
        r"(\w+)\s*=\s*fields\.Text\(": r"\1: str = fields.Text(",
        r"(\w+)\s*=\s*fields\.Boolean\(": r"\1: bool = fields.Boolean(",
        r"(\w+)\s*=\s*fields\.Integer\(": r"\1: int = fields.Integer(",
        r"(\w+)\s*=\s*fields\.Float\(": r"\1: float = fields.Float(",
        r"(\w+)\s*=\s*fields\.Monetary\(": r"\1: float = fields.Monetary(",
        r"(\w+)\s*=\s*fields\.Date\(": r"\1: date = fields.Date(",
        r"(\w+)\s*=\s*fields\.Datetime\(": r"\1: datetime = fields.Datetime(",
        r"(\w+)\s*=\s*fields\.Selection\(": r"\1: str = fields.Selection(",
        r"(\w+)\s*=\s*fields\.Many2one\(": r"\1: int = fields.Many2one(",
        r"(\w+)\s*=\s*fields\.One2many\(": r"\1: list[int] = fields.One2many(",
        r"(\w+)\s*=\s*fields\.Many2many\(": r"\1: list[int] = fields.Many2many(",
    }

    content = python_content
    for pattern, replacement in field_patterns.items():
        content = re.sub(pattern, replacement, content)

    # Add future annotations import if not present
    if "from __future__ import annotations" not in content:
        content = "from __future__ import annotations\n" + content

    return content


def convert_to_sql_builder(python_content):
    """Convert raw SQL to SQL builder pattern."""
    # This is a complex transformation that often requires manual review
    # Basic pattern detection
    if "self.env.cr.execute" in python_content and "SQL(" not in python_content:
        print("NOTE: Found string SQL execution. It still works in 19.0; migration to SQL() is recommended, not required.")
    return python_content
```

## Detailed Type Hint Examples

### Field Type Hints

```python
from __future__ import annotations
from datetime import date, datetime
from typing import Any

from odoo import api, fields, models

class SecureModel(models.Model):
    _name = 'secure.model'
    _description = 'Secure Model'

    # Scalar fields
    name: str = fields.Char(required=True)
    description: str = fields.Text()
    active: bool = fields.Boolean(default=True)
    sequence: int = fields.Integer(default=10)
    amount: float = fields.Float()
    percentage: float = fields.Float(digits=(16, 2))

    # Date fields
    date_start: date = fields.Date()
    datetime_action: datetime = fields.Datetime()

    # Selection
    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft')

    # Relational fields
    company_id: int = fields.Many2one('res.company')
    partner_id: int = fields.Many2one('res.partner')
    user_id: int = fields.Many2one('res.users')
    line_ids: list[int] = fields.One2many('secure.model.line', 'parent_id')
    tag_ids: list[int] = fields.Many2many('secure.model.tag')

    # Related fields
    partner_name: str = fields.Char(related='partner_id.name')
    company_currency_id: int = fields.Many2one(related='company_id.currency_id')
```

### Method Type Hints

```python
from __future__ import annotations
from typing import Any

class SecureModel(models.Model):
    _name = 'secure.model'

    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> SecureModel:
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        return super().write(vals)

    def unlink(self) -> bool:
        return super().unlink()

    def copy(self, default: dict[str, Any] | None = None) -> SecureModel:
        return super().copy(default)

    def action_confirm(self) -> dict[str, Any] | bool:
        """Returns action dict or True."""
        self.write({'state': 'confirmed'})
        return True

    def _compute_total(self) -> None:
        for record in self:
            record.total = sum(record.line_ids.mapped('amount'))
```

## SQL Builder Migration Examples

### Simple Query

**v18:**
```python
def _get_records(self):
    self.env.cr.execute(
        "SELECT id, name FROM my_table WHERE active = %s",
        [True]
    )
    return self.env.cr.fetchall()
```

**v19:**
```python
from odoo.tools import SQL

def _get_records(self) -> list[tuple[int, str]]:
    query = SQL(
        "SELECT id, name FROM %(table)s WHERE active = %(active)s",
        table=SQL.identifier('my_table'),
        active=True,
    )
    self.env.cr.execute(query)
    return self.env.cr.fetchall()
```

### Query with Dynamic Table

**Never (any version):** an f-string or `%` for identifiers, e.g.
`f"SELECT id FROM {self._table} ..."`. `SQL.identifier()` exists in 18 and 19.

**v18 and v19:**
```python
def _get_model_records(self) -> list[tuple[int]]:
    query = SQL(
        "SELECT id FROM %(table)s WHERE company_id = %(company_id)s",
        table=SQL.identifier(self._table),
        company_id=self.env.company.id,
    )
    self.env.cr.execute(query)
    return self.env.cr.fetchall()
```

### Complex Query with Joins

**v19 Pattern:**
```python
def _get_report_data(self) -> list[dict[str, Any]]:
    query = SQL(
        """
        SELECT
            m.id,
            m.name,
            p.name AS partner_name,
            COALESCE(SUM(l.amount), 0) AS total_amount
        FROM %(main_table)s m
        LEFT JOIN %(partner_table)s p ON m.partner_id = p.id
        LEFT JOIN %(line_table)s l ON l.parent_id = m.id
        WHERE m.company_id IN %(company_ids)s
          AND m.state = %(state)s
          AND m.date >= %(date_from)s
        GROUP BY m.id, m.name, p.name
        ORDER BY %(order_field)s %(order_dir)s
        """,
        main_table=SQL.identifier(self._table),
        partner_table=SQL.identifier('res_partner'),
        line_table=SQL.identifier('secure_model_line'),
        company_ids=tuple(self.env.companies.ids) or (0,),
        state='confirmed',
        date_from=fields.Date.today(),
        order_field=SQL.identifier('total_amount'),
        order_dir=SQL('DESC'),
    )
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()
```

## OWL (2.x in both versions)

19.0 ships Owl 2.8.4; components need no framework migration. Declaring `static props`
is good practice in both versions.

### Component Structure

**v18:**
```javascript
import { Component, useState } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({ count: 0 });
    }
}
```

**v19 (same Owl 2 API, props declared):**
```javascript
import { Component, useState } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        // Explicit prop definitions
    };

    setup() {
        this.state = useState({ count: 0 });
    }
}
```

## Additional deltas from Odoo's official guidelines (18.0 -> 19.0)

Verified official-guideline security items that change between 18.0 and 19.0 and are not in the overview above:

| Topic | 18.0 | 19.0 |
|-------|------|------|
| JS escaping helpers (`@web/core/utils/html`) | `htmlEscape`, `setElementContent`, `isHtmlEmpty` | + `htmlJoin`, `htmlSprintf`, `htmlReplace`, ...; still no `setInnerHtml` |
| Field access check helper | `check_field_access_rights()` | deprecated (internal `_check_field_access`) |

## Migration Checklist

- [ ] Remove `time` from record rule domains
- [ ] Rename `groups_id` -> `group_ids` (users, views, actions, data files, tests)
- [ ] Replace `expression.AND/OR` with `Domain` where security domains are combined (recommended)
- [ ] Review public classmethods/staticmethods relied on over RPC (now blocked)
- [ ] Keep raw SQL parameterized; prefer `SQL()` builder
- [ ] Test all SQL queries work correctly

## No Change Required

### Security Groups, Access Rights, Record Rules

These remain unchanged from v18 to v19:
- ir.model.access.csv format; `ir.model.access` + `ir.rule` (no `ir.access`, no `base.group_everyone`)
- Record rule combination semantics: global rules AND-ed, group rules OR-ed (except the removed `time` name)
- `check_access()` / `has_access()` (old `check_access_rights`/`check_access_rule` deprecated since 18)
- Field groups attribute, `fields.NO_ACCESS`
- View visibility syntax
- `sudo(flag)` / `with_user()`; `_allow_sudo_commands`; `related_sudo=True` default
- `odoo.tools.SQL` + `SQL.identifier`
- Routes: `auth` values `user`/`bearer`/`public`/`none` with no `bearer_scope`; CSRF on for http routes, no token check for JSON routes
- Server QWeb: `t-out` (with `t-esc` escaping and `t-raw` unescaped, both deprecated)
- `file_open` confinement; `safe_eval` dunder blocking; no restricted pickle; `odoo.tools.consteq`

## GitHub Reference

Check the `19.0` branch for v19 patterns:
- `odoo/orm/` - ORM (models, fields, domains) moved here in 19.0
- `odoo/tools/sql.py` - SQL builder
- `odoo/addons/base/models/ir_rule.py` - rule eval context
- `addons/web/static/src/core/utils/html.js` - JS escaping helpers
