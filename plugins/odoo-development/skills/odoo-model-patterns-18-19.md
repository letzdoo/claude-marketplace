# Odoo Model Patterns Migration Guide: 18.0 → 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODEL MIGRATION GUIDE: Odoo 18.0 → 19.0                                     ║
║  Focus: SQL constraints, domains, aggregation, field renames                 ║
║  Verified against the 18.0 and 19.0 (final) source trees.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Feature | v18 Status | v19 Status | Action |
|---------|------------|------------|--------|
| `_sql_constraints` | Supported: `_sql_constraints = [(name, sql, msg)]` | **Ignored** (warning only) | Convert to `_name_uniq = models.Constraint('UNIQUE(name)', msg)` |
| `odoo.osv.expression` | Standard: `expression.AND([d1, d2])` | Deprecated | Use `odoo.fields.Domain`: `Domain(d1) & Domain(d2)` |
| `read_group()` | Public API (dicts); `_read_group(domain, groupby, aggregates)` -> tuples | Deprecated; `_read_group` unchanged | `_read_group()` / `formatted_read_group()` |
| `groups_id` (res.users) | Field name | Renamed `group_ids` | Rename |
| Type hints | Optional | Optional | Nothing to do |
| `SQL()` builder | Recommended | Recommended (plain `cr.execute(str, params)` still works) | Nothing mandatory |

## Type Hints (optional in both versions)

### Without hints (valid in v18 and v19)
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

### With hints (optional style)
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

## SQL Builder (recommended in both versions)

### Unsafe in any version (identifier formatted into the string)
```python
def _get_report_data(self):
    # Do not build SQL with % / f-strings, even for table names
    query = """
        SELECT id, name, amount
        FROM %s
        WHERE company_id = %%s
        ORDER BY create_date DESC
    """ % self._table
    self.env.cr.execute(query, (self.env.company.id,))
    return self.env.cr.dictfetchall()
```

### Preferred (v18 and v19)
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
            'view_mode': 'list,form',  # 'tree' is not a view type in 18/19
        }

    # Search: name_search() searches display_name in 18 and 19; customize via
    # _rec_names_search or _search_display_name(operator, value)
    _rec_names_search = ['name', 'code']

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

## Additional deltas from Odoo's official guidelines (18.0 -> 19.0)

ORM items of the verified official-guideline matrix that change between 18.0 and 19.0 and are not in the Breaking Changes Summary:

| Topic | 18.0 | 19.0 |
|-------|------|------|
| Multi-column index | `init()` + `odoo.tools.sql.create_index(cr, name, table, [cols])` | `_my_idx = models.Index('(col_a, col_b)')` / `models.UniqueIndex(...)` |
| `create` override with `@api.model` | DeprecationWarning | converted silently (still use `@api.model_create_multi`) |
| Translation | `self.env._("%s", arg)`; list args printed as Python lists | iterable args formatted per language |
| Archiving | `toggle_active()` available | `toggle_active()` deprecated -> `action_archive()` / `action_unarchive()` |
| Public classmethods | RPC-callable unless prefixed `_` | blocked by the RPC guard |

Unchanged: `grouped()`, related-through-x2many truncation (first record only), `with self.env.cr.savepoint():`, `_check_company_auto` opt-in, `t-lang` only with `t-call`, `_get_report_values` must return `doc_ids`/`doc_model`/`docs`.

## Migration Checklist

### For All Models
- [ ] Convert every `_sql_constraints` to `models.Constraint()` / `models.UniqueIndex()`
- [ ] Move `init()`-created multi-column indexes to `models.Index()` (optional)
- [ ] Replace `expression.AND/OR` with `Domain` (optional, deprecated only)
- [ ] Replace `read_group()` calls
- [ ] Rename `groups_id` -> `group_ids`

### For SQL Queries
- [ ] Prefer `SQL()` builder; never format values or identifiers into strings
- [ ] Test with various input parameters

### Python Version
- [ ] Python 3.10+ (both versions)

### Testing
- [ ] Verify constraints are still enforced after migration (write a test that violates them)
- [ ] Verify all methods work correctly

## Type Checker Script (optional)

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

### Warning: `_sql_constraints` no longer supported
```
WARNING ... Model attribute '_sql_constraints' is no longer supported, please define models.Constraint on the model.
```
**Fix**: Convert each tuple to a `models.Constraint` class attribute (name starting with `_`); until then the constraint is NOT applied.

### Error: Invalid field 'groups_id' on model 'res.users'
**Fix**: Use `group_ids`.

### Error: Circular import with type hints
```
ImportError: cannot import name 'MyModel' from partially initialized module
```
**Fix**: Use `from __future__ import annotations` for forward references.
