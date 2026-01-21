# Pricelist and Pricing Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PRICELIST & PRICING PATTERNS                                                ║
║  Dynamic pricing, discounts, and multi-currency price management             ║
║  Use for sales pricing, promotions, and customer-specific pricing            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Pricelist Structure

### Pricelist Hierarchy
```
product.pricelist (Retail Pricelist)
├── product.pricelist.item (All Products: 10% discount)
├── product.pricelist.item (Category "Electronics": 15% discount)
├── product.pricelist.item (Product "Laptop": Fixed $999)
└── product.pricelist.item (Qty >= 10: 20% discount)
```

---

## Creating Pricelists

### Basic Pricelist
```python
pricelist = self.env['product.pricelist'].create({
    'name': 'Retail Pricelist',
    'currency_id': self.env.ref('base.USD').id,
    'company_id': self.env.company.id,
    'sequence': 10,
})
```

### Pricelist with Rules
```python
pricelist = self.env['product.pricelist'].create({
    'name': 'VIP Customers',
    'currency_id': self.env.ref('base.USD').id,
    'item_ids': [
        # 10% discount on all products
        (0, 0, {
            'applied_on': '3_global',  # All products
            'compute_price': 'percentage',
            'percent_price': 10,
        }),
        # 20% off electronics category
        (0, 0, {
            'applied_on': '2_product_category',
            'categ_id': electronics_categ.id,
            'compute_price': 'percentage',
            'percent_price': 20,
        }),
        # Fixed price for specific product
        (0, 0, {
            'applied_on': '1_product',
            'product_tmpl_id': laptop_template.id,
            'compute_price': 'fixed',
            'fixed_price': 899.00,
        }),
        # Quantity-based discount
        (0, 0, {
            'applied_on': '3_global',
            'min_quantity': 10,
            'compute_price': 'percentage',
            'percent_price': 15,
        }),
    ],
})
```

---

## Pricelist Item Types

### Applied On (Scope)
```python
# Global: All products
item = self.env['product.pricelist.item'].create({
    'pricelist_id': pricelist.id,
    'applied_on': '3_global',
    'compute_price': 'percentage',
    'percent_price': 5,
})

# Product Category
item = self.env['product.pricelist.item'].create({
    'pricelist_id': pricelist.id,
    'applied_on': '2_product_category',
    'categ_id': category.id,
    'compute_price': 'percentage',
    'percent_price': 10,
})

# Product Template (all variants)
item = self.env['product.pricelist.item'].create({
    'pricelist_id': pricelist.id,
    'applied_on': '1_product',
    'product_tmpl_id': template.id,
    'compute_price': 'fixed',
    'fixed_price': 50.00,
})

# Product Variant (specific)
item = self.env['product.pricelist.item'].create({
    'pricelist_id': pricelist.id,
    'applied_on': '0_product_variant',
    'product_id': variant.id,
    'compute_price': 'fixed',
    'fixed_price': 45.00,
})
```

### Compute Price Methods
```python
# Fixed price
item.write({
    'compute_price': 'fixed',
    'fixed_price': 99.99,
})

# Percentage discount
item.write({
    'compute_price': 'percentage',
    'percent_price': 15,  # 15% discount
})

# Formula based
item.write({
    'compute_price': 'formula',
    'base': 'list_price',  # or 'standard_price', 'pricelist'
    'price_discount': 10,  # 10% discount
    'price_surcharge': 5,  # Add $5
    'price_round': 0.99,   # Round to .99
    'price_min_margin': 10,  # Minimum 10% margin
    'price_max_margin': 50,  # Maximum 50% margin
})
```

---

## Getting Prices

### Get Product Price
```python
def get_product_price(self, product, pricelist, quantity=1.0, partner=None, date=None):
    """Get product price from pricelist."""
    if date is None:
        date = fields.Date.today()

    return pricelist._get_product_price(
        product,
        quantity,
        partner=partner,
        date=date,
    )

# Usage
price = get_product_price(product, customer_pricelist, quantity=5)
```

### Get Price Rule
```python
def get_price_with_rule(self, product, pricelist, quantity=1.0):
    """Get price and the rule that was applied."""
    price, rule_id = pricelist._get_product_price_rule(
        product,
        quantity,
    )
    rule = self.env['product.pricelist.item'].browse(rule_id)
    return {
        'price': price,
        'rule': rule,
        'discount_percent': rule.percent_price if rule else 0,
    }
```

### Batch Price Calculation
```python
def get_prices_for_products(self, products, pricelist, quantity=1.0):
    """Get prices for multiple products at once."""
    prices = {}
    for product in products:
        prices[product.id] = pricelist._get_product_price(
            product,
            quantity,
        )
    return prices
```

---

## Date-Based Pricing

### Time-Limited Promotions
```python
# Promotional pricing with date range
promo_item = self.env['product.pricelist.item'].create({
    'pricelist_id': pricelist.id,
    'applied_on': '3_global',
    'compute_price': 'percentage',
    'percent_price': 25,  # 25% off
    'date_start': fields.Date.today(),
    'date_end': fields.Date.today() + timedelta(days=7),  # 1 week promo
    'name': 'Summer Sale',
})
```

### Check Active Promotions
```python
def get_active_promotions(self, pricelist):
    """Get currently active promotional rules."""
    today = fields.Date.today()
    return self.env['product.pricelist.item'].search([
        ('pricelist_id', '=', pricelist.id),
        '|',
        ('date_start', '=', False),
        ('date_start', '<=', today),
        '|',
        ('date_end', '=', False),
        ('date_end', '>=', today),
    ])
```

---

## Multi-Currency Pricing

### Currency Conversion
```python
def convert_price(self, amount, from_currency, to_currency, company=None, date=None):
    """Convert price between currencies."""
    if company is None:
        company = self.env.company
    if date is None:
        date = fields.Date.today()

    return from_currency._convert(
        amount,
        to_currency,
        company,
        date,
    )

# Usage
usd_price = 100.00
eur_price = convert_price(
    usd_price,
    self.env.ref('base.USD'),
    self.env.ref('base.EUR'),
)
```

### Pricelist per Currency
```python
# Create pricelist for each currency
usd_pricelist = self.env['product.pricelist'].create({
    'name': 'USD Pricelist',
    'currency_id': self.env.ref('base.USD').id,
})

eur_pricelist = self.env['product.pricelist'].create({
    'name': 'EUR Pricelist',
    'currency_id': self.env.ref('base.EUR').id,
})
```

---

## Customer-Specific Pricing

### Assign Pricelist to Customer
```python
# Set customer's default pricelist
partner = self.env['res.partner'].browse(partner_id)
partner.write({
    'property_product_pricelist': vip_pricelist.id,
})
```

### Get Customer's Price
```python
def get_customer_price(self, partner, product, quantity=1.0):
    """Get price for specific customer."""
    pricelist = partner.property_product_pricelist
    if not pricelist:
        pricelist = self.env.ref('product.list0')  # Default pricelist

    return pricelist._get_product_price(product, quantity, partner=partner)
```

### Customer Price Tiers
```python
# Create customer-specific pricelist
customer_pricelist = self.env['product.pricelist'].create({
    'name': f'Pricelist for {partner.name}',
    'currency_id': partner.currency_id.id or self.env.company.currency_id.id,
    'item_ids': [
        (0, 0, {
            'applied_on': '3_global',
            'compute_price': 'percentage',
            'percent_price': partner.x_discount_rate or 0,
        }),
    ],
})
partner.property_product_pricelist = customer_pricelist
```

---

## Quantity Breaks

### Volume Discounts
```python
pricelist = self.env['product.pricelist'].create({
    'name': 'Volume Discount Pricelist',
    'item_ids': [
        # Base price (qty 1-9)
        (0, 0, {
            'applied_on': '1_product',
            'product_tmpl_id': product.id,
            'min_quantity': 1,
            'compute_price': 'fixed',
            'fixed_price': 100.00,
        }),
        # 10% off for 10-49
        (0, 0, {
            'applied_on': '1_product',
            'product_tmpl_id': product.id,
            'min_quantity': 10,
            'compute_price': 'fixed',
            'fixed_price': 90.00,
        }),
        # 20% off for 50-99
        (0, 0, {
            'applied_on': '1_product',
            'product_tmpl_id': product.id,
            'min_quantity': 50,
            'compute_price': 'fixed',
            'fixed_price': 80.00,
        }),
        # 30% off for 100+
        (0, 0, {
            'applied_on': '1_product',
            'product_tmpl_id': product.id,
            'min_quantity': 100,
            'compute_price': 'fixed',
            'fixed_price': 70.00,
        }),
    ],
})
```

---

## Sales Order Pricing

### Apply Pricelist in Sale Order
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Set pricelist from partner."""
        super().onchange_partner_id()
        if self.partner_id:
            self.pricelist_id = self.partner_id.property_product_pricelist


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_pricelist(self):
        """Update price from pricelist."""
        if self.product_id and self.order_id.pricelist_id:
            self.price_unit = self.order_id.pricelist_id._get_product_price(
                self.product_id,
                self.product_uom_qty or 1.0,
                partner=self.order_id.partner_id,
            )
```

---

## Custom Pricing Logic

### Override Price Calculation
```python
class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _get_product_price(self, product, quantity, partner=None, date=False, uom_id=False):
        """Override to add custom pricing logic."""
        price = super()._get_product_price(
            product, quantity, partner=partner, date=date, uom_id=uom_id
        )

        # Custom logic: apply partner-specific discount
        if partner and partner.x_special_discount:
            price = price * (1 - partner.x_special_discount / 100)

        return price
```

### Dynamic Pricing
```python
class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_dynamic_price(self):
        """Calculate price based on external factors."""
        base_price = self.list_price

        # Example: adjust based on stock level
        if self.qty_available < 10:
            # Low stock premium
            return base_price * 1.1
        elif self.qty_available > 100:
            # Overstock discount
            return base_price * 0.95

        return base_price
```

---

## XML Data for Pricelists

### Pricelist Definition
```xml
<record id="pricelist_wholesale" model="product.pricelist">
    <field name="name">Wholesale</field>
    <field name="currency_id" ref="base.USD"/>
    <field name="sequence">5</field>
</record>

<record id="pricelist_item_wholesale_global" model="product.pricelist.item">
    <field name="pricelist_id" ref="pricelist_wholesale"/>
    <field name="applied_on">3_global</field>
    <field name="compute_price">percentage</field>
    <field name="percent_price">20</field>
</record>

<record id="pricelist_item_wholesale_electronics" model="product.pricelist.item">
    <field name="pricelist_id" ref="pricelist_wholesale"/>
    <field name="applied_on">2_product_category</field>
    <field name="categ_id" ref="product.product_category_3"/>
    <field name="compute_price">percentage</field>
    <field name="percent_price">25</field>
</record>
```

---

## Price Display

### Show Prices with Taxes
```python
def get_display_price(self, product, pricelist, fiscal_position=None):
    """Get price as displayed to customer (with/without tax)."""
    price = pricelist._get_product_price(product, 1.0)

    if fiscal_position:
        taxes = product.taxes_id.filtered(
            lambda t: t.company_id == self.env.company
        )
        mapped_taxes = fiscal_position.map_tax(taxes)
        price = mapped_taxes.compute_all(
            price,
            currency=pricelist.currency_id,
            quantity=1.0,
            product=product,
        )['total_included']

    return price
```

### Format Price for Display
```python
def format_price(self, amount, currency):
    """Format price for display."""
    from odoo.tools import formatLang
    return formatLang(self.env, amount, currency_obj=currency)
```

---

## Best Practices

1. **Use rule priority** - Specific rules before global (sequence matters)
2. **Date ranges** - Use for promotions, not permanent pricing
3. **Test thoroughly** - Verify all quantity breaks work
4. **Currency consistency** - Match pricelist and partner currency
5. **Audit trail** - Log price changes
6. **Performance** - Cache frequent price lookups
7. **Multi-company** - Separate pricelists per company
8. **Clear naming** - Descriptive pricelist names
9. **Limit complexity** - Too many rules = slow calculation
10. **Document rules** - Explain business logic behind pricing
