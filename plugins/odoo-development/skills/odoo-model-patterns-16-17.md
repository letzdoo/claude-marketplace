# Odoo Model Patterns Migration Guide: 16.0 → 17.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODEL MIGRATION GUIDE: Odoo 16.0 → 17.0                                     ║
║  Focus: Python models, decorators, CRUD methods                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Pattern | v16 | v17 | Action |
|---------|-----|-----|--------|
| `@api.model_create_multi` | single-dict create logs a WARNING | same WARNING (not an error) | Should add |
| `attrs` in views | The 16.0 syntax (domains) | Replaced by Python expressions | Must migrate |
| `states` in views | The 16.0 shorthand | Replaced by `invisible="state not in (...)"` | Must migrate |

## Recommended: @api.model_create_multi

### Before (v16, logs "not overriding the create method in batch")
```python
@api.model
def create(self, vals):
    if not vals.get('name'):
        vals['name'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals)
```

### After (v17)
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)
```

## View Visibility Changes (Affects Model Logic)

Models that reference view visibility in their logic need updates:

### Before (v16)
```python
def get_view_attrs(self):
    return {
        'invisible': [('state', '!=', 'draft')],
        'readonly': [('locked', '=', True)],
    }
```

### After (v17)
```python
def get_view_visibility(self):
    # Return Python expressions instead of domains
    return {
        'invisible': "state != 'draft'",
        'readonly': "locked",
    }
```

## Command Class (available since 15.0, unchanged in 17.0)

Prefer the Command class for x2many operations (tuples still work in both versions):

```python
from odoo import Command

# Correct for both v16 and v17
self.write({
    'line_ids': [
        Command.create({'name': 'New'}),
        Command.update(1, {'name': 'Updated'}),
        Command.delete(2),
        Command.link(3),
        Command.unlink(4),
        Command.clear(),
        Command.set([5, 6, 7]),
    ]
})
```

## Python Version Updates

- v16: Python 3.7+ (up to 3.12)
- v17: Python 3.10+

### New Python Features Available

```python
# Match statement (Python 3.10+)
match self.state:
    case 'draft':
        self.action_confirm()
    case 'confirmed':
        self.action_done()
    case _:
        pass

# Improved type hints
def process(self, data: list[dict]) -> bool:
    return True
```

## Migration Checklist

### For Each Model
- [ ] Update `create()` to use `@api.model_create_multi`
- [ ] Change signature from `create(vals)` to `create(vals_list)`
- [ ] Iterate over `vals_list` in create logic
- [ ] Verify all x2many use `Command` class
- [ ] Update any view visibility logic for Python expressions

### Testing
- [ ] Test bulk create operations
- [ ] Verify single record creation still works
- [ ] Test all form views for visibility
- [ ] Test all buttons for state visibility

## Official guideline deltas 16.0 -> 17.0

Only ORM rules of the official Odoo guidelines (odoo/odoo `skills/`, verified per version) whose 16.0 and 17.0 forms differ:

| Topic | 16.0 | 17.0 |
|---|---|---|
| Aggregate per group | `read_group(domain, ['amount:sum'], ['partner_id'], lazy=False)` -> list of dicts (`_read_group` has the same signature) | `_read_group(domain, ['partner_id'], ['amount:sum'])` -> list of tuples |
| `records.grouped(key)` | absent: `tools.groupby(records, key)` | exists |
| Custom SQL over ORM rows | `query = M._search(dom)`; `sql, params = query.select('"t"."id"')` | `M._search(dom).select(SQL(...))` with `odoo.tools.SQL` |
| Dynamic SQL identifiers | `psycopg2.sql.Identifier` | `SQL.identifier(name)` |
| Translations | `_()` with `%` args, no Markup escaping | `_()` escapes args when one is Markup; `tools.format_list` |
| `<asset>` XML records | absent | exists |

View modifiers and the single-dict create WARNING: see Breaking Changes Summary.

Unchanged (16.0 = 17.0): `_sql_constraints` (no `models.Constraint`), `index` values `btree`/`btree_not_null`/`trigram`, `osv.expression.AND/OR`, related through x2many truncates to the first record, `default_<field>` context leak, `t-lang` only with `t-call`, custom `_get_report_values` must return `docs`/`doc_ids`/`doc_model`, `cr.savepoint()`.

## Common Errors and Fixes

### Warning: create() not batched
```
The model ... is not overriding the create method in batch
```
**Fix**: Use `@api.model_create_multi` and accept `vals_list` (logged in 16.0 and 17.0).

### Error: Missing return in create
```
TypeError: create() should return recordset
```
**Fix**: Ensure super().create() is called with `vals_list`.

## Automated Migration Pattern

```python
# Find and replace pattern
# Before:
@api.model
def create(self, vals):
    # ... logic with vals ...
    return super().create(vals)

# After:
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        # ... logic with vals ...
    return super().create(vals_list)
```
