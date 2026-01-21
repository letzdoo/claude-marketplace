# Odoo Security Guide - Migration 18.0 → 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: ODOO 18.0 → 19.0 SECURITY                                  ║
║  Use this guide when upgrading security code from v18 to v19.                ║
║  NOTE: v19 is in development - patterns may change.                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview of Security Changes

| Component | v18 | v19 | Migration Required |
|-----------|-----|-----|-------------------|
| Type hints | Recommended | **Mandatory** | **REQUIRED** |
| SQL builder | Recommended | **Mandatory** | **REQUIRED** |
| Python | 3.11+ | 3.12+ | Check compatibility |
| OWL | 2.x | 3.x | For OWL components |

## Breaking Changes

### 1. Type Hints Now Mandatory

**v18 (recommended):**
```python
class MyModel(models.Model):
    _name = 'my.model'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner')
    line_ids = fields.One2many('my.line', 'parent_id')
```

**v19 (mandatory):**
```python
from __future__ import annotations

class MyModel(models.Model):
    _name = 'my.model'

    name: str = fields.Char(required=True)
    partner_id: int = fields.Many2one('res.partner')
    line_ids: list[int] = fields.One2many('my.line', 'parent_id')
```

### 2. SQL Builder Now Mandatory

**v18 (recommended):**
```python
# Still allowed in v18
self.env.cr.execute(
    "SELECT id FROM my_table WHERE company_id = %s",
    [self.env.company.id]
)
```

**v19 (mandatory):**
```python
from odoo.tools import SQL

query = SQL(
    "SELECT id FROM %(table)s WHERE company_id = %(company_id)s",
    table=SQL.identifier('my_table'),
    company_id=self.env.company.id,
)
self.env.cr.execute(query)
```

## Migration Script

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
        print("WARNING: Found raw SQL execution. Manual migration to SQL() required.")
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

**v18:**
```python
def _get_model_records(self):
    self.env.cr.execute(
        f"SELECT id FROM {self._table} WHERE company_id = %s",
        [self.env.company.id]
    )
```

**v19:**
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

## OWL 3.x Migration

### Component Structure

**v18 (OWL 2.x):**
```javascript
import { Component, useState } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({ count: 0 });
    }
}
```

**v19 (OWL 3.x):**
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

## Migration Checklist

- [ ] **CRITICAL**: Add type hints to ALL field definitions
- [ ] **CRITICAL**: Add type hints to ALL method signatures
- [ ] **CRITICAL**: Convert ALL raw SQL to `SQL()` builder
- [ ] Add `from __future__ import annotations` to all Python files
- [ ] Update Python to 3.12+
- [ ] Migrate OWL 2.x to OWL 3.x components
- [ ] Test all SQL queries work correctly
- [ ] Verify type hints don't cause runtime errors

## No Change Required

### Security Groups, Access Rights, Record Rules

These remain unchanged from v18 to v19:
- Group definitions
- ir.model.access.csv format
- Record rule syntax
- Field groups attribute
- View visibility syntax

## GitHub Reference

Check the `master` branch for v19 patterns:
- `odoo/fields.py` - Type hint support
- `odoo/tools/sql.py` - SQL builder enhancements
- `odoo/models.py` - Model type annotations
- `addons/web/static/src/` - OWL 3.x patterns
