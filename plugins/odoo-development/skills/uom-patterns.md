# Unit of Measure Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  UNIT OF MEASURE (UoM) PATTERNS                                              ║
║  Product quantities, conversions, and multi-UoM handling                     ║
║  Use for inventory, sales, and purchasing with different units               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## UoM Basics

### UoM Category and Units
```
UoM Category: Weight
├── kg (reference unit, factor = 1.0)
├── g (factor = 0.001)
├── lb (factor = 0.453592)
└── oz (factor = 0.0283495)

UoM Category: Unit
├── Unit(s) (reference unit)
├── Dozen (factor = 12)
└── Hundred (factor = 100)
```

---

## Creating UoM Categories and Units

### Create UoM Category
```python
# Create a custom UoM category
category = self.env['uom.category'].create({
    'name': 'Volume',
})
```

### Create Units of Measure
```python
# Reference unit (factor = 1)
liter = self.env['uom.uom'].create({
    'name': 'Liter',
    'category_id': category.id,
    'uom_type': 'reference',  # This is the base unit
    'rounding': 0.001,
})

# Smaller unit
milliliter = self.env['uom.uom'].create({
    'name': 'Milliliter',
    'category_id': category.id,
    'uom_type': 'smaller',
    'factor_inv': 1000,  # 1000 ml = 1 L
    'rounding': 1,
})

# Bigger unit
gallon = self.env['uom.uom'].create({
    'name': 'Gallon',
    'category_id': category.id,
    'uom_type': 'bigger',
    'factor': 3.78541,  # 1 gallon = 3.78541 L
    'rounding': 0.01,
})
```

---

## UoM on Products

### Product UoM Fields
```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Default unit of measure (sales/inventory)
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )

    # Purchase unit of measure
    uom_po_id = fields.Many2one(
        'uom.uom',
        string='Purchase UoM',
        required=True,
    )

    # These must be in the same category for conversion
```

### Set Product UoM
```python
product = self.env['product.template'].create({
    'name': 'Cooking Oil',
    'type': 'product',
    'uom_id': liter.id,  # Sell in liters
    'uom_po_id': gallon.id,  # Buy in gallons
})
```

---

## UoM Conversion

### Convert Quantities
```python
def convert_uom(self, qty, from_uom, to_uom):
    """Convert quantity between units."""
    if from_uom.category_id != to_uom.category_id:
        raise UserError("Cannot convert between different UoM categories.")

    return from_uom._compute_quantity(qty, to_uom)

# Example: Convert 5 gallons to liters
liters = convert_uom(5, gallon, liter)  # = 18.927
```

### Compute Quantity Method
```python
# Built-in conversion
from_uom = self.env.ref('uom.product_uom_dozen')
to_uom = self.env.ref('uom.product_uom_unit')

# Convert 2 dozen to units
units = from_uom._compute_quantity(2, to_uom)  # = 24

# With rounding
units_rounded = from_uom._compute_quantity(
    2.5,
    to_uom,
    round=True,
    rounding_method='UP',
)
```

### Price Conversion
```python
def convert_price(self, price, from_uom, to_uom):
    """Convert unit price between UoMs."""
    return from_uom._compute_price(price, to_uom)

# If product costs $10 per gallon, what's the price per liter?
price_per_liter = convert_price(10, gallon, liter)  # ≈ $2.64
```

---

## UoM in Sales and Purchases

### Sale Order Line with UoM
```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        domain="[('category_id', '=', product_uom_category_id)]",
    )

    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Set default UoM from product."""
        if self.product_id:
            self.product_uom = self.product_id.uom_id

    @api.onchange('product_uom')
    def _onchange_product_uom(self):
        """Recalculate price when UoM changes."""
        if self.product_id and self.product_uom:
            # Get price in product's UoM
            base_price = self.product_id.lst_price
            # Convert to selected UoM
            self.price_unit = self.product_id.uom_id._compute_price(
                base_price, self.product_uom
            )
```

### Purchase Order Line
```python
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        """Default to purchase UoM."""
        result = super().onchange_product_id()
        if self.product_id:
            self.product_uom = self.product_id.uom_po_id
        return result
```

---

## Stock Moves with UoM

### Create Stock Move
```python
def create_stock_move(self, product, qty, uom, location_src, location_dest):
    """Create stock move with UoM conversion."""
    # Quantity in product's UoM for stock
    product_qty = uom._compute_quantity(qty, product.uom_id)

    move = self.env['stock.move'].create({
        'name': product.name,
        'product_id': product.id,
        'product_uom_qty': qty,  # In move's UoM
        'product_uom': uom.id,
        'location_id': location_src.id,
        'location_dest_id': location_dest.id,
    })

    return move
```

### Check Stock in Different UoM
```python
def get_stock_in_uom(self, product, uom, location=None):
    """Get available stock converted to specific UoM."""
    if location:
        qty = product.with_context(location=location.id).qty_available
    else:
        qty = product.qty_available

    # Convert from product UoM to requested UoM
    return product.uom_id._compute_quantity(qty, uom)

# Get stock in dozens
stock_dozens = get_stock_in_uom(product, dozen_uom)
```

---

## UoM Rounding

### Rounding Options
```python
# Rounding precision on UoM
uom = self.env['uom.uom'].create({
    'name': 'Piece',
    'category_id': category.id,
    'uom_type': 'reference',
    'rounding': 1.0,  # Round to whole numbers
})

# Rounding methods
qty = from_uom._compute_quantity(
    10.3,
    to_uom,
    round=True,
    rounding_method='HALF-UP',  # Default, standard rounding
)

qty = from_uom._compute_quantity(
    10.3,
    to_uom,
    round=True,
    rounding_method='UP',  # Always round up
)
```

### Float Comparison
```python
from odoo.tools import float_compare, float_round

# Compare quantities with UoM precision
result = float_compare(
    qty1,
    qty2,
    precision_rounding=uom.rounding,
)
# Returns: -1 (less), 0 (equal), 1 (greater)

# Round to UoM precision
rounded_qty = float_round(qty, precision_rounding=uom.rounding)
```

---

## Custom Model with UoM

### Model with Quantity Field
```python
class InventoryAdjustment(models.Model):
    _name = 'inventory.adjustment'

    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure')
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id',
        string='UoM Category',
    )

    # Quantity in product's base UoM
    product_qty = fields.Float(
        string='Quantity (Base UoM)',
        compute='_compute_product_qty',
        store=True,
    )

    @api.depends('quantity', 'product_uom_id', 'product_id')
    def _compute_product_qty(self):
        for record in self:
            if record.product_uom_id and record.product_id:
                record.product_qty = record.product_uom_id._compute_quantity(
                    record.quantity,
                    record.product_id.uom_id,
                )
            else:
                record.product_qty = record.quantity

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
```

---

## UoM View Patterns

### Form View with UoM
```xml
<form>
    <group>
        <field name="product_id"/>
        <label for="quantity"/>
        <div class="o_row">
            <field name="quantity" class="oe_inline"/>
            <field name="product_uom_id" class="oe_inline"
                   options="{'no_create': True}"
                   groups="uom.group_uom"/>
        </div>
        <field name="product_uom_category_id" invisible="1"/>
    </group>
</form>
```

### List View
```xml
<tree>
    <field name="product_id"/>
    <field name="quantity"/>
    <field name="product_uom_id" groups="uom.group_uom"/>
    <field name="product_qty" string="Qty (Base)"/>
</tree>
```

---

## XML Data for UoM

### Define UoM in Data
```xml
<!-- UoM Category -->
<record id="uom_categ_length" model="uom.category">
    <field name="name">Length</field>
</record>

<!-- Reference unit -->
<record id="uom_meter" model="uom.uom">
    <field name="name">Meter</field>
    <field name="category_id" ref="uom_categ_length"/>
    <field name="uom_type">reference</field>
    <field name="rounding">0.01</field>
</record>

<!-- Smaller unit -->
<record id="uom_centimeter" model="uom.uom">
    <field name="name">Centimeter</field>
    <field name="category_id" ref="uom_categ_length"/>
    <field name="uom_type">smaller</field>
    <field name="factor_inv">100</field>
    <field name="rounding">1</field>
</record>

<!-- Bigger unit -->
<record id="uom_kilometer" model="uom.uom">
    <field name="name">Kilometer</field>
    <field name="category_id" ref="uom_categ_length"/>
    <field name="uom_type">bigger</field>
    <field name="factor">1000</field>
    <field name="rounding">0.001</field>
</record>
```

---

## Common UoM References

### Standard Odoo UoMs
```python
# Unit category
unit = self.env.ref('uom.product_uom_unit')
dozen = self.env.ref('uom.product_uom_dozen')

# Weight category
kg = self.env.ref('uom.product_uom_kgm')
gram = self.env.ref('uom.product_uom_gram')
lb = self.env.ref('uom.product_uom_lb')
oz = self.env.ref('uom.product_uom_oz')

# Time category
hour = self.env.ref('uom.product_uom_hour')
day = self.env.ref('uom.product_uom_day')

# Volume category (if installed)
litre = self.env.ref('uom.product_uom_litre')
```

---

## UoM Feature Group

### Enable Multi-UoM
```python
# Users need this group to see UoM fields
# Settings > Users > Technical Settings > Multiple Units of Measure

# In view, use groups attribute
# groups="uom.group_uom"
```

---

## Best Practices

1. **Same category** - Only convert within same UoM category
2. **Set rounding** - Appropriate precision for each unit
3. **Use product UoM** - For stock quantities, always convert to product's UoM
4. **Separate sale/purchase** - Different UoMs for buying vs selling
5. **Handle precision** - Use float_compare for equality checks
6. **Group visibility** - Hide UoM fields unless group_uom enabled
7. **Default UoM** - Always set sensible default
8. **Test conversions** - Verify conversion factors are correct
9. **Document units** - Clear names and descriptions
10. **Avoid mixing** - Don't mix UoMs from different categories
