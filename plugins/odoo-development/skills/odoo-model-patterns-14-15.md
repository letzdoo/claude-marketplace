# Odoo Model Patterns Migration: 14.0 → 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODEL PATTERNS MIGRATION: 14.0 → 15.0                                       ║
║  @api.multi REMOVED, tracking=True standardized                              ║
║  VERIFY: https://github.com/odoo/odoo/tree/15.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes

### 1. @api.multi REMOVED

This is the **most critical** breaking change. All methods using `@api.multi` will fail in v15.

```python
# v14 (BREAKS IN v15):
from odoo import models, api

class MyModel(models.Model):
    _name = 'my.model'

    @api.multi
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancelled'})

# v15 (REQUIRED - remove @api.multi):
from odoo import models

class MyModel(models.Model):
    _name = 'my.model'

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
```

### 2. track_visibility → tracking

```python
# v14 (deprecated, still works):
name = fields.Char(track_visibility='always')
state = fields.Selection([...], track_visibility='onchange')

# v15 (RECOMMENDED):
name = fields.Char(tracking=True)
state = fields.Selection([...], tracking=True)
```

### 3. super() Syntax (Best Practice)

```python
# v14 (Python 2 style - works but outdated):
return super(MyModel, self).create(vals)

# v15 (Python 3 style - RECOMMENDED):
return super().create(vals)
```

## Field Changes

### Tracking Fields

| v14 Syntax | v15 Syntax |
|------------|------------|
| `track_visibility='always'` | `tracking=True` |
| `track_visibility='onchange'` | `tracking=True` |
| `track_visibility=True` | `tracking=True` |

```python
# v14:
class MyModel(models.Model):
    _inherit = 'mail.thread'

    name = fields.Char(track_visibility='always')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', track_visibility='onchange')
    amount = fields.Float(track_visibility='always')

# v15:
class MyModel(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
    amount = fields.Float(tracking=True)
```

## CRUD Methods Migration

### Create Method

```python
# v14:
@api.model
def create(self, vals):
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super(MyModel, self).create(vals)

# v15 (single record - still valid):
@api.model
def create(self, vals):
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals)

# v15 (batch - RECOMMENDED for performance):
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)
```

### Write Method

```python
# v14:
@api.multi
def write(self, vals):
    if 'state' in vals and vals['state'] == 'done':
        for record in self:
            if not record.line_ids:
                raise UserError(_("Add at least one line."))
    return super(MyModel, self).write(vals)

# v15:
def write(self, vals):
    if 'state' in vals and vals['state'] == 'done':
        for record in self:
            if not record.line_ids:
                raise UserError(_("Add at least one line."))
    return super().write(vals)
```

### Unlink Method

```python
# v14:
@api.multi
def unlink(self):
    for record in self:
        if record.state == 'done':
            raise UserError(_("Cannot delete done records."))
    return super(MyModel, self).unlink()

# v15:
def unlink(self):
    for record in self:
        if record.state == 'done':
            raise UserError(_("Cannot delete done records."))
    return super().unlink()
```

### Copy Method

```python
# v14:
@api.multi
def copy(self, default=None):
    self.ensure_one()
    default = dict(default or {})
    default['name'] = _("%s (copy)") % self.name
    return super(MyModel, self).copy(default)

# v15:
def copy(self, default=None):
    self.ensure_one()
    default = dict(default or {})
    default['name'] = _("%s (copy)") % self.name
    return super().copy(default)
```

## Action Methods Migration

```python
# v14:
@api.multi
def action_confirm(self):
    for record in self:
        if record.state != 'draft':
            raise UserError(_("Only draft records can be confirmed."))
        record.state = 'confirmed'
    return True

@api.multi
def action_view_partner(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': _('Partner'),
        'res_model': 'res.partner',
        'res_id': self.partner_id.id,
        'view_mode': 'form',
    }

# v15:
def action_confirm(self):
    for record in self:
        if record.state != 'draft':
            raise UserError(_("Only draft records can be confirmed."))
        record.state = 'confirmed'
    return True

def action_view_partner(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': _('Partner'),
        'res_model': 'res.partner',
        'res_id': self.partner_id.id,
        'view_mode': 'form',
    }
```

## Computed Fields (No Change)

Computed fields work the same way in both versions:

```python
# v14 and v15 (same):
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

## Constraints (No Change)

```python
# v14 and v15 (same):
@api.constrains('date_start', 'date_end')
def _check_dates(self):
    for record in self:
        if record.date_start and record.date_end:
            if record.date_start > record.date_end:
                raise ValidationError(_("End date must be after start date."))
```

## Migration Script

Use this script to find and fix v14 patterns:

```bash
#!/bin/bash
# find_v14_patterns.sh

echo "=== Finding @api.multi decorators ==="
grep -rn "@api.multi" --include="*.py"

echo ""
echo "=== Finding track_visibility ==="
grep -rn "track_visibility" --include="*.py"

echo ""
echo "=== Finding old super() patterns ==="
grep -rn "super(.*self)" --include="*.py"
```

## Search and Replace Patterns

| Find | Replace With |
|------|--------------|
| `@api.multi\n    def` | `def` |
| `track_visibility='always'` | `tracking=True` |
| `track_visibility='onchange'` | `tracking=True` |
| `track_visibility=True` | `tracking=True` |
| `super(ClassName, self)` | `super()` |

## Migration Checklist

- [ ] Remove ALL `@api.multi` decorators
- [ ] Replace ALL `track_visibility` with `tracking=True`
- [ ] Update `super()` calls to Python 3 style
- [ ] Add `mail.activity.mixin` where appropriate
- [ ] Consider `@api.model_create_multi` for batch creates
- [ ] Test all action methods
- [ ] Test all CRUD operations
- [ ] Verify mail tracking works

## Common Errors After Migration

### AttributeError: 'api' object has no attribute 'multi'
**Cause**: @api.multi still in code
**Solution**: Remove the decorator, keep the method

### DeprecationWarning: track_visibility is deprecated
**Cause**: track_visibility used
**Solution**: Replace with tracking=True

### TypeError: create() got multiple values for argument 'vals'
**Cause**: Mixing @api.model and @api.model_create_multi
**Solution**: Choose one pattern consistently
