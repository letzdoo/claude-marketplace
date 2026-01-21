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
| `@api.model_create_multi` | Recommended | **Mandatory** | Must add |
| `attrs` in views | Deprecated | Removed | Must migrate |
| `states` in views | Deprecated | Removed | Must migrate |

## MANDATORY: @api.model_create_multi

### Before (v16)
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

## Command Class (Already Required in v16)

Ensure all x2many operations use Command class:

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

- v16: Python 3.8+
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

## Common Errors and Fixes

### Error: create() expects vals_list
```
TypeError: create() got an unexpected keyword argument 'vals'
```
**Fix**: Update method signature to accept `vals_list`.

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
