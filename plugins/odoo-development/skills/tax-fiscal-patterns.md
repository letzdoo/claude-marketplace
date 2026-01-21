# Tax and Fiscal Position Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  TAX & FISCAL POSITION PATTERNS                                              ║
║  Tax configuration, fiscal positions, and tax calculations                   ║
║  Use for multi-tax scenarios, international sales, and tax compliance        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Tax Types Overview

| Type | Description | Use Case |
|------|-------------|----------|
| Sale | Applied on sales | Customer invoices |
| Purchase | Applied on purchases | Vendor bills |
| None | No tax impact | Internal transfers |

---

## Creating Taxes

### Basic Tax Configuration
```python
# Create a sales tax
sales_tax = self.env['account.tax'].create({
    'name': 'Sales Tax 10%',
    'type_tax_use': 'sale',
    'amount_type': 'percent',
    'amount': 10.0,
    'company_id': self.env.company.id,
    'price_include': False,  # Tax excluded from price
})

# Create a purchase tax
purchase_tax = self.env['account.tax'].create({
    'name': 'Purchase Tax 10%',
    'type_tax_use': 'purchase',
    'amount_type': 'percent',
    'amount': 10.0,
    'company_id': self.env.company.id,
})
```

### Tax Amount Types
```python
# Percentage tax
percent_tax = self.env['account.tax'].create({
    'name': 'VAT 21%',
    'amount_type': 'percent',
    'amount': 21.0,
    'type_tax_use': 'sale',
})

# Fixed amount tax
fixed_tax = self.env['account.tax'].create({
    'name': 'Eco Tax',
    'amount_type': 'fixed',
    'amount': 5.0,  # $5 per unit
    'type_tax_use': 'sale',
})

# Division tax (price includes tax)
division_tax = self.env['account.tax'].create({
    'name': 'VAT Included 21%',
    'amount_type': 'division',
    'amount': 21.0,
    'type_tax_use': 'sale',
    'price_include': True,
})

# Group of taxes
group_tax = self.env['account.tax'].create({
    'name': 'Combined Tax',
    'amount_type': 'group',
    'type_tax_use': 'sale',
    'children_tax_ids': [(6, 0, [tax1.id, tax2.id])],
})
```

---

## Tax on Products

### Set Default Taxes
```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Customer taxes (for sales)
    taxes_id = fields.Many2many(
        'account.tax',
        'product_taxes_rel',
        'prod_id', 'tax_id',
        string='Customer Taxes',
        domain=[('type_tax_use', '=', 'sale')],
    )

    # Supplier taxes (for purchases)
    supplier_taxes_id = fields.Many2many(
        'account.tax',
        'product_supplier_taxes_rel',
        'prod_id', 'tax_id',
        string='Vendor Taxes',
        domain=[('type_tax_use', '=', 'purchase')],
    )

# Create product with taxes
product = self.env['product.template'].create({
    'name': 'Taxable Product',
    'list_price': 100.00,
    'taxes_id': [(6, 0, [sales_tax.id])],
    'supplier_taxes_id': [(6, 0, [purchase_tax.id])],
})
```

---

## Tax Calculations

### Compute Tax Amounts
```python
def compute_taxes(self, price_unit, quantity, taxes, currency=None, partner=None):
    """Compute tax amounts for a line."""
    if currency is None:
        currency = self.env.company.currency_id

    result = taxes.compute_all(
        price_unit,
        currency=currency,
        quantity=quantity,
        product=None,
        partner=partner,
    )

    return {
        'total_excluded': result['total_excluded'],
        'total_included': result['total_included'],
        'taxes': result['taxes'],
        'base': result['base'],
    }

# Example
result = compute_taxes(100.0, 2, sales_tax)
# result['total_excluded'] = 200.0
# result['total_included'] = 220.0
# result['taxes'] = [{'amount': 20.0, 'name': 'Sales Tax 10%', ...}]
```

### Tax Computation Details
```python
def get_tax_breakdown(self, order):
    """Get tax breakdown for an order."""
    tax_totals = {}

    for line in order.order_line:
        taxes = line.tax_id.compute_all(
            line.price_unit,
            order.currency_id,
            line.product_uom_qty,
            line.product_id,
            order.partner_id,
        )

        for tax_data in taxes['taxes']:
            tax_id = tax_data['id']
            if tax_id not in tax_totals:
                tax_totals[tax_id] = {
                    'name': tax_data['name'],
                    'base': 0,
                    'amount': 0,
                }
            tax_totals[tax_id]['base'] += tax_data['base']
            tax_totals[tax_id]['amount'] += tax_data['amount']

    return list(tax_totals.values())
```

---

## Fiscal Positions

### What is a Fiscal Position?
```
Fiscal Position = Tax Mapping Rules
- Maps taxes to different taxes (or no tax)
- Maps accounts to different accounts
- Based on customer location, type, or other criteria
```

### Create Fiscal Position
```python
# Create fiscal position for EU customers
eu_fiscal = self.env['account.fiscal.position'].create({
    'name': 'EU Customers',
    'auto_apply': True,
    'country_group_id': self.env.ref('base.europe').id,
    'tax_ids': [
        # Map domestic VAT to EU VAT
        (0, 0, {
            'tax_src_id': domestic_vat.id,
            'tax_dest_id': eu_vat.id,
        }),
    ],
    'account_ids': [
        # Map domestic account to EU account
        (0, 0, {
            'account_src_id': domestic_revenue.id,
            'account_dest_id': eu_revenue.id,
        }),
    ],
})

# Create fiscal position for exports (no tax)
export_fiscal = self.env['account.fiscal.position'].create({
    'name': 'Export - No Tax',
    'auto_apply': True,
    'tax_ids': [
        # Map VAT to no tax
        (0, 0, {
            'tax_src_id': domestic_vat.id,
            'tax_dest_id': False,  # No tax
        }),
    ],
})
```

### Map Taxes with Fiscal Position
```python
def get_taxes_for_partner(self, product, partner):
    """Get applicable taxes for a partner."""
    # Get product's default taxes
    taxes = product.taxes_id

    # Get partner's fiscal position
    fiscal_position = partner.property_account_position_id

    if fiscal_position:
        # Map taxes through fiscal position
        taxes = fiscal_position.map_tax(taxes)

    return taxes

# Usage
taxes = get_taxes_for_partner(product, customer)
```

---

## Auto-Apply Fiscal Positions

### Configuration for Auto-Apply
```python
fiscal_position = self.env['account.fiscal.position'].create({
    'name': 'B2B Foreign',
    'auto_apply': True,

    # Match by country
    'country_id': self.env.ref('base.de').id,  # Germany

    # Or by country group
    'country_group_id': eu_group.id,

    # Or by VAT requirement
    'vat_required': True,  # Partner must have VAT number

    # Sequence for priority
    'sequence': 10,
})
```

### Get Fiscal Position for Partner
```python
def get_fiscal_position(self, partner, delivery_partner=None):
    """Determine fiscal position for a partner."""
    # Use delivery address if provided
    partner_to_check = delivery_partner or partner

    # Find applicable fiscal position
    fiscal_position = self.env['account.fiscal.position']._get_fiscal_position(
        partner_to_check,
        delivery=delivery_partner,
    )

    return fiscal_position

# Or use partner's default
fiscal_position = partner.property_account_position_id
```

---

## Tax Included in Price

### Price Include Configuration
```python
# Tax where price includes tax
vat_included = self.env['account.tax'].create({
    'name': 'VAT 20% (Included)',
    'amount': 20.0,
    'amount_type': 'percent',
    'type_tax_use': 'sale',
    'price_include': True,
    'include_base_amount': False,
})

# Calculate base from tax-included price
def get_base_from_included(self, price_total, tax):
    """Extract base amount from price including tax."""
    result = tax.compute_all(
        price_total,
        quantity=1,
    )
    return result['total_excluded']

# If product price is $120 including 20% VAT
base = get_base_from_included(120, vat_included)  # = $100
```

---

## Tax Repartition

### Define Tax Accounts
```python
# Tax with repartition lines (where tax goes)
tax = self.env['account.tax'].create({
    'name': 'VAT 21%',
    'amount': 21.0,
    'type_tax_use': 'sale',
    'invoice_repartition_line_ids': [
        # Base line
        (0, 0, {
            'repartition_type': 'base',
        }),
        # Tax line
        (0, 0, {
            'repartition_type': 'tax',
            'account_id': vat_payable_account.id,
            'tag_ids': [(6, 0, [vat_tag.id])],
        }),
    ],
    'refund_repartition_line_ids': [
        # Base line for refunds
        (0, 0, {
            'repartition_type': 'base',
        }),
        # Tax line for refunds
        (0, 0, {
            'repartition_type': 'tax',
            'account_id': vat_payable_account.id,
            'tag_ids': [(6, 0, [vat_tag.id])],
        }),
    ],
})
```

---

## Tax Groups

### Configure Tax Groups
```python
# Tax group for display
tax_group = self.env['account.tax.group'].create({
    'name': 'VAT',
    'sequence': 10,
})

tax = self.env['account.tax'].create({
    'name': 'VAT 21%',
    'amount': 21.0,
    'tax_group_id': tax_group.id,
    # ...
})
```

---

## Sales Order with Taxes

### Tax Handling in Sale Order
```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.tax_id.compute_all(
                line.price_unit,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange('product_id')
    def _onchange_product_id_taxes(self):
        """Apply taxes with fiscal position mapping."""
        if self.product_id:
            taxes = self.product_id.taxes_id
            fiscal = self.order_id.fiscal_position_id
            if fiscal:
                taxes = fiscal.map_tax(taxes)
            self.tax_id = taxes
```

---

## Tax Reporting

### Get Tax Report Data
```python
def get_tax_report(self, date_from, date_to, company=None):
    """Generate tax report data."""
    company = company or self.env.company

    # Find all posted invoices in period
    invoices = self.env['account.move'].search([
        ('company_id', '=', company.id),
        ('state', '=', 'posted'),
        ('date', '>=', date_from),
        ('date', '<=', date_to),
        ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']),
    ])

    # Aggregate by tax
    tax_data = {}
    for invoice in invoices:
        for line in invoice.line_ids.filtered(lambda l: l.tax_line_id):
            tax = line.tax_line_id
            if tax.id not in tax_data:
                tax_data[tax.id] = {
                    'tax': tax,
                    'base_amount': 0,
                    'tax_amount': 0,
                }
            # Get base and tax amounts
            tax_data[tax.id]['tax_amount'] += line.balance

    return list(tax_data.values())
```

---

## XML Data for Taxes

### Define Tax in Data
```xml
<record id="tax_sale_21" model="account.tax">
    <field name="name">VAT 21%</field>
    <field name="type_tax_use">sale</field>
    <field name="amount_type">percent</field>
    <field name="amount">21</field>
    <field name="tax_group_id" ref="account.tax_group_taxes"/>
    <field name="company_id" ref="base.main_company"/>
</record>

<record id="fiscal_position_export" model="account.fiscal.position">
    <field name="name">Export</field>
    <field name="auto_apply" eval="True"/>
    <field name="company_id" ref="base.main_company"/>
</record>

<record id="fiscal_position_tax_map_1" model="account.fiscal.position.tax">
    <field name="position_id" ref="fiscal_position_export"/>
    <field name="tax_src_id" ref="tax_sale_21"/>
    <!-- tax_dest_id empty = no tax -->
</record>
```

---

## Best Practices

1. **Separate by type** - Sale vs Purchase taxes
2. **Use fiscal positions** - For tax mapping, not manual overrides
3. **Auto-apply rules** - Set up automatic fiscal position assignment
4. **Test calculations** - Verify tax computations thoroughly
5. **Handle refunds** - Configure refund repartition lines
6. **Group taxes** - Use tax groups for reporting
7. **Price include** - Be consistent within product category
8. **Document rules** - Explain fiscal position logic
9. **Multi-company** - Taxes are company-specific
10. **Compliance** - Follow local tax regulations
