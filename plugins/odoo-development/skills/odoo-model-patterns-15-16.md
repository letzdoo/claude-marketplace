# Odoo Model Patterns Migration: 15.0 → 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODEL PATTERNS MIGRATION: 15.0 → 16.0                                       ║
║  Command class introduced, attrs deprecated (still works)                    ║
║  VERIFY: https://github.com/odoo/odoo/tree/16.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview

Migration from v15 to v16 is **non-breaking** for model code. The main changes are:
- `Command` class for x2many operations (recommended)
- `attrs` deprecation in views (start migrating)
- `@api.model_create_multi` recommended

## New: Command Class

The `Command` class provides a cleaner API for x2many field operations.

### Import

```python
from odoo.fields import Command
```

### Command Methods

| Command | Tuple Equivalent | Description |
|---------|------------------|-------------|
| `Command.create(vals)` | `(0, 0, vals)` | Create new record |
| `Command.update(id, vals)` | `(1, id, vals)` | Update existing |
| `Command.delete(id)` | `(2, id, 0)` | Delete record |
| `Command.unlink(id)` | `(3, id, 0)` | Unlink (M2M only) |
| `Command.link(id)` | `(4, id, 0)` | Link existing |
| `Command.clear()` | `(5, 0, 0)` | Clear all |
| `Command.set(ids)` | `(6, 0, ids)` | Replace all |

### Migration Examples

```python
# v15 Tuple syntax (still works in v16):
def create_with_lines(self):
    return self.env['sale.order'].create({
        'partner_id': partner.id,
        'order_line': [
            (0, 0, {'product_id': product1.id, 'product_uom_qty': 1}),
            (0, 0, {'product_id': product2.id, 'product_uom_qty': 2}),
        ],
    })

def update_lines(self):
    self.write({
        'order_line': [
            (1, line_id, {'product_uom_qty': 5}),  # Update
            (0, 0, {'product_id': product.id}),    # Create
            (2, old_line_id, 0),                   # Delete
        ],
    })

# v16 Command class (RECOMMENDED):
from odoo.fields import Command

def create_with_lines(self):
    return self.env['sale.order'].create({
        'partner_id': partner.id,
        'order_line': [
            Command.create({'product_id': product1.id, 'product_uom_qty': 1}),
            Command.create({'product_id': product2.id, 'product_uom_qty': 2}),
        ],
    })

def update_lines(self):
    self.write({
        'order_line': [
            Command.update(line_id, {'product_uom_qty': 5}),
            Command.create({'product_id': product.id}),
            Command.delete(old_line_id),
        ],
    })
```

### Many2many Operations

```python
# v15:
def manage_tags_v15(self):
    # Link
    self.write({'tag_ids': [(4, tag.id, 0)]})
    # Unlink
    self.write({'tag_ids': [(3, tag.id, 0)]})
    # Replace
    self.write({'tag_ids': [(6, 0, [tag1.id, tag2.id])]})
    # Clear
    self.write({'tag_ids': [(5, 0, 0)]})

# v16:
from odoo.fields import Command

def manage_tags_v16(self):
    # Link
    self.write({'tag_ids': [Command.link(tag.id)]})
    # Unlink
    self.write({'tag_ids': [Command.unlink(tag.id)]})
    # Replace
    self.write({'tag_ids': [Command.set([tag1.id, tag2.id])]})
    # Clear
    self.write({'tag_ids': [Command.clear()]})
```

## Create Method: model_create_multi

While `@api.model` still works, `@api.model_create_multi` is now **strongly recommended**.

```python
# v15 (still works in v16):
@api.model
def create(self, vals):
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals)

# v16 (RECOMMENDED - prepare for v17 where it's mandatory):
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)
```

### Benefits of model_create_multi

1. **Better Performance**: Batch operations are more efficient
2. **Future Compatibility**: Mandatory in v17
3. **Cleaner API**: Consistent handling of single/batch creates

## Field Indexing (Best Practice)

v16 encourages more explicit indexing for better performance:

```python
# v15:
name = fields.Char(required=True, index=True)

# v16 (enhanced indexing options):
name = fields.Char(required=True, index='trigram')  # For LIKE searches
code = fields.Char(index=True)                       # Standard B-tree
state = fields.Selection([...], index=True)          # For filtering
```

### Index Types

| Type | Use Case |
|------|----------|
| `index=True` | Standard B-tree index |
| `index='trigram'` | For ILIKE/pattern searches |
| `index='btree_not_null'` | B-tree excluding NULL |

## Complete Model Migration Example

```python
# v15 Model:
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    order_id = fields.Many2one('sale.order', required=True)
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(default=1.0)
    price_unit = fields.Float()
    subtotal = fields.Float(compute='_compute_subtotal', store=True)

    @api.model
    def create(self, vals):
        if not vals.get('price_unit') and vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['price_unit'] = product.list_price
        return super().create(vals)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit


class SaleOrder(models.Model):
    _name = 'sale.order'

    name = fields.Char(required=True, index=True)
    partner_id = fields.Many2one('res.partner', required=True)
    line_ids = fields.One2many('sale.order.line', 'order_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft')

    def create_sample_lines(self, products):
        self.write({
            'line_ids': [
                (0, 0, {'product_id': p.id, 'quantity': 1})
                for p in products
            ],
        })


# v16 Model (RECOMMENDED):
from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    order_id = fields.Many2one('sale.order', required=True, index=True)
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(default=1.0)
    price_unit = fields.Float()
    subtotal = fields.Float(compute='_compute_subtotal', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('price_unit') and vals.get('product_id'):
                product = self.env['product.product'].browse(vals['product_id'])
                vals['price_unit'] = product.list_price
        return super().create(vals_list)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit


class SaleOrder(models.Model):
    _name = 'sale.order'

    name = fields.Char(required=True, index='trigram')  # For search
    partner_id = fields.Many2one('res.partner', required=True, index=True)
    line_ids = fields.One2many('sale.order.line', 'order_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft', index=True)  # For filtering

    def create_sample_lines(self, products):
        self.write({
            'line_ids': [
                Command.create({'product_id': p.id, 'quantity': 1})
                for p in products
            ],
        })
```

## View Changes (Start Migrating)

While `attrs` still works in v16, start migrating to prepare for v17:

```xml
<!-- v15 (works in v16 but deprecated): -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- v16 (RECOMMENDED - required in v17): -->
<field name="partner_id"
       invisible="state == 'draft'"/>
```

## Migration Checklist

### Recommended (Non-Breaking)
- [ ] Add `from odoo.fields import Command` to files using x2many
- [ ] Replace tuple x2many syntax with Command class
- [ ] Update `@api.model` create to `@api.model_create_multi`
- [ ] Add `index=True` to frequently filtered fields
- [ ] Consider `index='trigram'` for searchable text fields

### Views (Start Now for v17)
- [ ] Identify all `attrs=` usage in XML views
- [ ] Start converting to `invisible=`, `readonly=`, `required=`
- [ ] Test conditional visibility with new syntax

## Search and Replace Patterns

| Pattern | Replacement |
|---------|-------------|
| `(0, 0, vals)` | `Command.create(vals)` |
| `(1, id, vals)` | `Command.update(id, vals)` |
| `(2, id, 0)` | `Command.delete(id)` |
| `(3, id, 0)` | `Command.unlink(id)` |
| `(4, id, 0)` | `Command.link(id)` |
| `(5, 0, 0)` | `Command.clear()` |
| `(6, 0, ids)` | `Command.set(ids)` |

## Testing

1. **Test x2many operations** - Verify Command class works correctly
2. **Test batch creates** - Ensure model_create_multi handles single and batch
3. **Test view conditionals** - If migrating attrs, verify visibility logic
4. **Performance testing** - Verify indexing improvements
