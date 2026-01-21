# Product Variant Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PRODUCT VARIANT PATTERNS                                                    ║
║  Product templates, variants, attributes, and configurators                  ║
║  Use for managing products with multiple variations (size, color, etc.)      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Product Structure Overview

```
product.template (T-Shirt)
├── product.product (T-Shirt, Red, S)
├── product.product (T-Shirt, Red, M)
├── product.product (T-Shirt, Red, L)
├── product.product (T-Shirt, Blue, S)
├── product.product (T-Shirt, Blue, M)
└── product.product (T-Shirt, Blue, L)
```

---

## Product Template vs Product

### Understanding the Difference
```python
# product.template = The "master" product
# product.product = Specific variant (SKU)

# Template fields (shared across variants)
template = self.env['product.template'].create({
    'name': 'T-Shirt',
    'type': 'product',
    'categ_id': category.id,
    'description': 'Cotton t-shirt',  # Same for all variants
})

# Variant fields (unique per variant)
variant = self.env['product.product'].create({
    'product_tmpl_id': template.id,
    'default_code': 'TSHIRT-RED-M',  # Unique SKU
    'barcode': '1234567890123',       # Unique barcode
})
```

### Accessing Template from Variant
```python
# From variant to template
variant = self.env['product.product'].browse(product_id)
template = variant.product_tmpl_id

# From template to variants
template = self.env['product.template'].browse(template_id)
variants = template.product_variant_ids
first_variant = template.product_variant_id  # Single variant
```

---

## Product Attributes

### Creating Attributes
```python
# Create attribute (e.g., Color, Size)
color_attr = self.env['product.attribute'].create({
    'name': 'Color',
    'display_type': 'color',  # radio, select, color, multi
    'create_variant': 'always',  # always, dynamic, no_variant
})

size_attr = self.env['product.attribute'].create({
    'name': 'Size',
    'display_type': 'radio',
    'create_variant': 'always',
})
```

### Creating Attribute Values
```python
# Create attribute values
colors = self.env['product.attribute.value'].create([
    {'name': 'Red', 'attribute_id': color_attr.id, 'html_color': '#FF0000'},
    {'name': 'Blue', 'attribute_id': color_attr.id, 'html_color': '#0000FF'},
    {'name': 'Green', 'attribute_id': color_attr.id, 'html_color': '#00FF00'},
])

sizes = self.env['product.attribute.value'].create([
    {'name': 'S', 'attribute_id': size_attr.id, 'sequence': 1},
    {'name': 'M', 'attribute_id': size_attr.id, 'sequence': 2},
    {'name': 'L', 'attribute_id': size_attr.id, 'sequence': 3},
    {'name': 'XL', 'attribute_id': size_attr.id, 'sequence': 4},
])
```

---

## Assigning Attributes to Products

### Add Attribute Lines to Template
```python
template = self.env['product.template'].create({
    'name': 'T-Shirt',
    'type': 'product',
    'attribute_line_ids': [
        (0, 0, {
            'attribute_id': color_attr.id,
            'value_ids': [(6, 0, colors.ids)],  # Red, Blue, Green
        }),
        (0, 0, {
            'attribute_id': size_attr.id,
            'value_ids': [(6, 0, sizes.ids)],  # S, M, L, XL
        }),
    ],
})

# This creates 3 colors × 4 sizes = 12 variants automatically
print(f"Created {len(template.product_variant_ids)} variants")
```

### Variant Creation Modes
```python
# 'always' - Variants created immediately for all combinations
# 'dynamic' - Variants created only when selected (sales/purchases)
# 'no_variant' - No variants, attribute stored on order line only
```

---

## Working with Variants

### Finding Specific Variant
```python
def get_variant(self, template, attribute_values):
    """Find variant matching specific attribute values."""
    domain = [('product_tmpl_id', '=', template.id)]

    for attr_value in attribute_values:
        domain.append(('product_template_attribute_value_ids.product_attribute_value_id', '=', attr_value.id))

    return self.env['product.product'].search(domain, limit=1)

# Usage
red = self.env['product.attribute.value'].search([('name', '=', 'Red')])
medium = self.env['product.attribute.value'].search([('name', '=', 'M')])
variant = get_variant(template, red | medium)
```

### Get Variant by Attribute Combination
```python
def _get_variant_for_combination(self, template, combination):
    """Get or create variant for attribute combination."""
    product = template._get_variant_for_combination(combination)
    if not product:
        # Create if dynamic variants enabled
        product = template._create_product_variant(combination)
    return product
```

---

## Variant Pricing

### Price Extra per Attribute Value
```python
# Add price extra to attribute value
template.attribute_line_ids.filtered(
    lambda l: l.attribute_id == size_attr
).product_template_value_ids.filtered(
    lambda v: v.name == 'XL'
).price_extra = 5.00  # +$5 for XL size

# Or via product.template.attribute.value
ptav = self.env['product.template.attribute.value'].search([
    ('product_tmpl_id', '=', template.id),
    ('product_attribute_value_id.name', '=', 'XL'),
])
ptav.price_extra = 5.00
```

### Get Variant Price
```python
def get_variant_price(self, variant, pricelist=None):
    """Get variant price including extras."""
    if pricelist:
        price = pricelist._get_product_price(
            variant,
            quantity=1.0,
            currency=pricelist.currency_id,
        )
    else:
        price = variant.lst_price  # Includes price_extra

    return price
```

---

## Variant-Specific Fields

### Extending Product Variant
```python
class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Variant-specific fields
    variant_sku = fields.Char(string='Variant SKU')
    variant_weight = fields.Float(string='Variant Weight')

    # Override to make template field variant-specific
    weight = fields.Float(
        string='Weight',
        compute='_compute_weight',
        inverse='_set_weight',
        store=True,
    )

    @api.depends('product_tmpl_id.weight', 'variant_weight')
    def _compute_weight(self):
        for product in self:
            product.weight = product.variant_weight or product.product_tmpl_id.weight

    def _set_weight(self):
        for product in self:
            product.variant_weight = product.weight
```

---

## Configurable Products

### Product Configurator in Sales
```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # For no_variant attributes
    product_no_variant_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value',
        string='Extra Values',
    )

    @api.onchange('product_id')
    def _onchange_product_id_variant_selector(self):
        """Open configurator for products with variants."""
        if self.product_id.product_tmpl_id.has_configurable_attributes:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.product.configurator',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_product_template_id': self.product_id.product_tmpl_id.id,
                },
            }
```

### Custom Configurator
```python
class ProductConfigurator(models.TransientModel):
    _name = 'product.configurator'
    _description = 'Product Configurator'

    product_template_id = fields.Many2one('product.template', required=True)
    attribute_line_ids = fields.One2many(
        'product.configurator.line',
        'configurator_id',
        string='Attributes',
    )

    @api.onchange('product_template_id')
    def _onchange_product_template(self):
        """Load attribute lines."""
        self.attribute_line_ids = [(5, 0, 0)]
        lines = []
        for attr_line in self.product_template_id.attribute_line_ids:
            lines.append((0, 0, {
                'attribute_id': attr_line.attribute_id.id,
                'value_ids': [(6, 0, attr_line.value_ids.ids)],
            }))
        self.attribute_line_ids = lines

    def action_configure(self):
        """Get configured variant."""
        combination = self.env['product.template.attribute.value']
        for line in self.attribute_line_ids:
            if line.selected_value_id:
                ptav = self.env['product.template.attribute.value'].search([
                    ('product_tmpl_id', '=', self.product_template_id.id),
                    ('product_attribute_value_id', '=', line.selected_value_id.id),
                ])
                combination |= ptav

        variant = self.product_template_id._get_variant_for_combination(combination)
        return variant


class ProductConfiguratorLine(models.TransientModel):
    _name = 'product.configurator.line'
    _description = 'Product Configurator Line'

    configurator_id = fields.Many2one('product.configurator')
    attribute_id = fields.Many2one('product.attribute')
    value_ids = fields.Many2many('product.attribute.value')
    selected_value_id = fields.Many2one(
        'product.attribute.value',
        domain="[('id', 'in', value_ids)]",
    )
```

---

## Variant Images

### Per-Variant Images
```python
class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Variant has its own image or falls back to template
    image_variant_1920 = fields.Image(max_width=1920, max_height=1920)

    # The standard image field computes from variant or template
    image_1920 = fields.Image(compute='_compute_image_1920', store=True)

    @api.depends('image_variant_1920', 'product_tmpl_id.image_1920')
    def _compute_image_1920(self):
        for record in self:
            record.image_1920 = record.image_variant_1920 or record.product_tmpl_id.image_1920
```

### Image per Attribute Value
```python
# Assign image to attribute value (color swatch)
color_value = self.env['product.attribute.value'].browse(value_id)
color_value.write({
    'image': base64_encoded_image,
})
```

---

## Variant Stock

### Check Stock per Variant
```python
def check_variant_availability(self, variant, warehouse=None):
    """Check stock for specific variant."""
    if warehouse:
        qty = variant.with_context(warehouse=warehouse.id).qty_available
    else:
        qty = variant.qty_available

    return {
        'available': qty,
        'incoming': variant.incoming_qty,
        'outgoing': variant.outgoing_qty,
        'forecasted': variant.virtual_available,
    }
```

### Stock per Location
```python
def get_variant_stock_by_location(self, variant):
    """Get stock breakdown by location."""
    quants = self.env['stock.quant'].search([
        ('product_id', '=', variant.id),
        ('quantity', '>', 0),
    ])

    return [{
        'location': q.location_id.complete_name,
        'quantity': q.quantity,
        'reserved': q.reserved_quantity,
    } for q in quants]
```

---

## XML Data for Attributes

### Attribute Definition
```xml
<record id="product_attribute_color" model="product.attribute">
    <field name="name">Color</field>
    <field name="display_type">color</field>
    <field name="create_variant">always</field>
</record>

<record id="product_attribute_value_red" model="product.attribute.value">
    <field name="name">Red</field>
    <field name="attribute_id" ref="product_attribute_color"/>
    <field name="html_color">#FF0000</field>
    <field name="sequence">1</field>
</record>

<record id="product_attribute_value_blue" model="product.attribute.value">
    <field name="name">Blue</field>
    <field name="attribute_id" ref="product_attribute_color"/>
    <field name="html_color">#0000FF</field>
    <field name="sequence">2</field>
</record>
```

### Product with Attributes
```xml
<record id="product_template_tshirt" model="product.template">
    <field name="name">T-Shirt</field>
    <field name="type">product</field>
    <field name="categ_id" ref="product.product_category_all"/>
    <field name="list_price">29.99</field>
    <field name="attribute_line_ids" eval="[
        (0, 0, {
            'attribute_id': ref('product_attribute_color'),
            'value_ids': [(6, 0, [ref('product_attribute_value_red'), ref('product_attribute_value_blue')])],
        }),
    ]"/>
</record>
```

---

## Variant Search and Filtering

### Search by Attribute
```python
def search_by_attribute(self, attribute_name, value_name):
    """Find variants with specific attribute value."""
    return self.env['product.product'].search([
        ('product_template_attribute_value_ids.product_attribute_value_id.name', '=', value_name),
        ('product_template_attribute_value_ids.attribute_id.name', '=', attribute_name),
    ])

# Find all red products
red_products = search_by_attribute('Color', 'Red')
```

### Filter in View
```xml
<search>
    <field name="name"/>
    <field name="categ_id"/>
    <filter name="filter_red" string="Red Products"
            domain="[('product_template_attribute_value_ids.product_attribute_value_id.name', '=', 'Red')]"/>
    <group expand="0" string="Group By">
        <filter name="group_by_attribute" string="Color"
                context="{'group_by': 'product_template_attribute_value_ids'}"/>
    </group>
</search>
```

---

## Best Practices

1. **Use templates** - Define shared data on template, unique on variant
2. **Choose variant mode** - `always` for few combos, `dynamic` for many
3. **Price extras** - Use for simple attribute-based pricing
4. **Separate SKUs** - Each variant should have unique identifier
5. **Image strategy** - Template image as fallback, variant when different
6. **Stock tracking** - Always at variant level
7. **Limit combinations** - Too many variants = performance issues
8. **Archive unused** - Don't delete, archive discontinued variants
9. **Test configurator** - Ensure all valid combinations work
10. **Document attributes** - Clear naming for attributes and values
