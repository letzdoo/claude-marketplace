# Odoo Model Patterns Migration Guide: 18.0 → 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODEL MIGRATION GUIDE: Odoo 18.0 → 19.0                                     ║
║  Focus: Mandatory type hints, mandatory SQL builder                          ║
║  Note: v19 is in development - patterns may change.                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Feature | v18 Status | v19 Status | Action |
|---------|------------|------------|--------|
| Type hints | Recommended | **Mandatory** | Must add |
| `SQL()` builder | Recommended | **Mandatory** | Must use |
| Raw SQL strings | Deprecated | **Removed** | Must migrate |

## MANDATORY: Type Hints

### Before (v18 - Optional)
```python
def calculate_totals(self, options=None):
    options = options or {}
    results = []
    for record in self:
        total = sum(record.line_ids.mapped('amount'))
        if options.get('include_tax'):
            total *= 1.21
        results.append({'id': record.id, 'total': total})
    return results

def get_partner_data(self):
    return {
        'id': self.partner_id.id,
        'name': self.partner_id.name,
        'email': self.partner_id.email,
    }

@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('name'):
            vals['name'] = 'New'
    return super().create(vals_list)
```

### After (v19 - Mandatory)
```python
from __future__ import annotations

from typing import Any, Optional
from collections.abc import Sequence

def calculate_totals(
    self,
    options: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    options = options or {}
    results: list[dict[str, Any]] = []
    for record in self:
        total: float = sum(record.line_ids.mapped('amount'))
        if options.get('include_tax'):
            total *= 1.21
        results.append({'id': record.id, 'total': total})
    return results

def get_partner_data(self) -> dict[str, Any]:
    return {
        'id': self.partner_id.id,
        'name': self.partner_id.name,
        'email': self.partner_id.email,
    }

@api.model_create_multi
def create(self, vals_list: list[dict[str, Any]]) -> 'MyModel':
    for vals in vals_list:
        if not vals.get('name'):
            vals['name'] = 'New'
    return super().create(vals_list)
```

## MANDATORY: SQL Builder

### Before (v18 - Allowed but deprecated)
```python
def _get_report_data(self):
    # This will FAIL in v19
    query = """
        SELECT id, name, amount
        FROM %s
        WHERE company_id = %%s
        ORDER BY create_date DESC
    """ % self._table
    self.env.cr.execute(query, (self.env.company.id,))
    return self.env.cr.dictfetchall()
```

### After (v19 - Required)
```python
from odoo.tools import SQL

def _get_report_data(self) -> list[dict[str, Any]]:
    query = SQL(
        """
        SELECT id, name, amount
        FROM %s
        WHERE company_id = %s
        ORDER BY %s
        """,
        SQL.identifier(self._table),
        self.env.company.id,
        SQL('create_date DESC'),
    )
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()
```

## Type Hint Reference

### Common Patterns

```python
from __future__ import annotations

from typing import Any, Optional, Union, Literal
from collections.abc import Sequence, Mapping, Iterable

# Model class
class MyModel(models.Model):
    _name = 'my.model'

    # CRUD methods
    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> 'MyModel':
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        return super().write(vals)

    def unlink(self) -> bool:
        return super().unlink()

    def copy(self, default: Optional[dict[str, Any]] = None) -> 'MyModel':
        return super().copy(default)

    # Compute methods
    @api.depends('line_ids.amount')
    def _compute_total(self) -> None:
        for record in self:
            record.total = sum(record.line_ids.mapped('amount'))

    # Constraint methods
    @api.constrains('amount')
    def _check_amount(self) -> None:
        for record in self:
            if record.amount < 0:
                raise ValidationError(_("Amount must be positive"))

    # Action methods
    def action_confirm(self) -> None:
        self.write({'state': 'confirmed'})

    def action_view_records(self) -> dict[str, Any]:
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'my.model',
            'view_mode': 'tree,form',
        }

    # Search methods
    @api.model
    def _name_search(
        self,
        name: str = '',
        domain: Optional[list[tuple[str, str, Any]]] = None,
        operator: str = 'ilike',
        limit: int = 100,
        order: Optional[str] = None,
    ) -> Sequence[int]:
        return self._search(domain or [], limit=limit, order=order)

    # Custom methods with various types
    def process_data(
        self,
        partner_ids: list[int],
        options: Optional[dict[str, Any]] = None,
        mode: Literal['create', 'update', 'delete'] = 'create',
    ) -> tuple[int, list[str]]:
        options = options or {}
        count = 0
        errors: list[str] = []
        # ...
        return count, errors
```

## SQL Builder Complete Reference

```python
from odoo.tools import SQL

# Basic query
query = SQL(
    "SELECT * FROM %s WHERE id = %s",
    SQL.identifier('my_table'),
    record_id,
)

# Complex query with joins
query = SQL(
    """
    SELECT
        m.id,
        m.name,
        p.name as partner_name,
        COALESCE(SUM(l.amount), 0) as total
    FROM %s m
    LEFT JOIN %s p ON p.id = m.partner_id
    LEFT JOIN %s l ON l.parent_id = m.id
    WHERE m.company_id IN %s
      AND m.state = %s
      AND m.active = %s
    GROUP BY m.id, m.name, p.name
    HAVING SUM(l.amount) > %s
    ORDER BY %s
    LIMIT %s OFFSET %s
    """,
    SQL.identifier('my_model'),
    SQL.identifier('res_partner'),
    SQL.identifier('my_model_line'),
    tuple(company_ids),
    'confirmed',
    True,
    100.0,
    SQL('total DESC'),
    limit,
    offset,
)

# Dynamic conditions
conditions = [SQL("company_id = %s", company_id)]
if partner_id:
    conditions.append(SQL("partner_id = %s", partner_id))
if state:
    conditions.append(SQL("state = %s", state))

where_clause = SQL(" AND ").join(conditions)
query = SQL(
    "SELECT * FROM %s WHERE %s",
    SQL.identifier(self._table),
    where_clause,
)
```

## Migration Checklist

### For All Models
- [ ] Add `from __future__ import annotations` at file top
- [ ] Add type hints to ALL method parameters
- [ ] Add return type annotations to ALL methods
- [ ] Import types from `typing` and `collections.abc`

### For SQL Queries
- [ ] Replace ALL raw SQL strings with `SQL()` builder
- [ ] Verify all queries work correctly
- [ ] Test with various input parameters

### Python Version
- [ ] Ensure Python 3.12+ is installed
- [ ] Use new Python features where beneficial

### Testing
- [ ] Run type checker (mypy, pyright) on code
- [ ] Test all SQL queries
- [ ] Verify all methods work correctly

## Type Checker Script

```python
#!/usr/bin/env python3
"""Check for missing type hints in Odoo models."""
import ast
import sys
from pathlib import Path

def check_file(filepath: Path) -> list[str]:
    issues = []
    with open(filepath) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('_') and node.name not in ('__init__', '__new__'):
                continue

            # Check return annotation
            if node.returns is None and node.name != '__init__':
                issues.append(f"{filepath}:{node.lineno}: {node.name}() missing return type")

            # Check parameter annotations
            for arg in node.args.args:
                if arg.arg != 'self' and arg.annotation is None:
                    issues.append(f"{filepath}:{node.lineno}: {node.name}({arg.arg}) missing type hint")

    return issues

if __name__ == '__main__':
    for path in Path('models').rglob('*.py'):
        for issue in check_file(path):
            print(issue)
```

## Common Migration Errors

### Error: Missing type hints
```
TypeError: Missing type annotation for parameter 'vals'
```
**Fix**: Add type hints to all method parameters.

### Error: Raw SQL not allowed
```
SecurityError: Raw SQL strings are deprecated. Use SQL() builder.
```
**Fix**: Convert all raw SQL to use `SQL()` builder.

### Error: Invalid type hint syntax
```
SyntaxError: invalid syntax (type hint)
```
**Fix**: Ensure Python 3.12+ is used and correct syntax.

### Error: Circular import with type hints
```
ImportError: cannot import name 'MyModel' from partially initialized module
```
**Fix**: Use `from __future__ import annotations` for forward references.
