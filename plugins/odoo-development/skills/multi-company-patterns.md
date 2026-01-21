# Multi-Company and Multi-Currency Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MULTI-COMPANY & MULTI-CURRENCY PATTERNS                                     ║
║  Company-aware models, cross-company rules, and currency handling            ║
║  Use for enterprise deployments with multiple business units                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Multi-Company Model Setup

### Basic Company-Aware Model (v18+)
```python
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True  # v18+ automatic company checking

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    # Related records with company check
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        check_company=True,  # Enforces same company
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        check_company=True,
    )
```

### v17 and Earlier Pattern
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        domain="[('company_id', 'in', [company_id, False])]",
    )

    @api.constrains('partner_id', 'company_id')
    def _check_company(self):
        for record in self:
            if record.partner_id.company_id and \
               record.partner_id.company_id != record.company_id:
                raise ValidationError(
                    "Partner company must match record company."
                )
```

---

## Company-Dependent Fields

### Company-Specific Values
```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Different value per company
    x_internal_code = fields.Char(
        string='Internal Code',
        company_dependent=True,
    )
    x_local_price = fields.Float(
        string='Local Price',
        company_dependent=True,
        digits='Product Price',
    )
    x_local_supplier_id = fields.Many2one(
        comodel_name='res.partner',
        string='Local Supplier',
        company_dependent=True,
    )
```

### Accessing Company-Dependent Values
```python
def get_local_data(self):
    """Get company-specific values."""
    # Automatically returns value for current company
    code = self.x_internal_code

    # Get for specific company
    other_company = self.env['res.company'].browse(2)
    code_other = self.with_company(other_company).x_internal_code
```

---

## Record Rules for Multi-Company

### Basic Company Rule
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Users see only their company's records -->
    <record id="my_model_company_rule" model="ir.rule">
        <field name="name">My Model: Company Rule</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
        ]</field>
        <field name="global" eval="True"/>
    </record>
</odoo>
```

### Multi-Company Access Patterns
```xml
<!-- Strict: Only own company -->
<field name="domain_force">[('company_id', '=', company_id)]</field>

<!-- Flexible: Own companies or no company -->
<field name="domain_force">[
    '|',
    ('company_id', '=', False),
    ('company_id', 'in', company_ids)
]</field>

<!-- Child companies included -->
<field name="domain_force">[
    ('company_id', 'child_of', company_id)
]</field>
```

---

## Cross-Company Operations

### Switch Company Context
```python
def action_process_all_companies(self):
    """Process records across all user's companies."""
    for company in self.env.user.company_ids:
        records = self.with_company(company).search([
            ('state', '=', 'pending'),
            ('company_id', '=', company.id),
        ])
        for record in records:
            record._process()
```

### Create in Specific Company
```python
def action_create_in_company(self, company_id: int) -> 'my.model':
    """Create record in specific company."""
    company = self.env['res.company'].browse(company_id)

    return self.with_company(company).create({
        'name': 'New Record',
        'company_id': company.id,
    })
```

### Inter-Company Transactions
```python
class InterCompanyTransfer(models.Model):
    _name = 'inter.company.transfer'
    _description = 'Inter-Company Transfer'

    source_company_id = fields.Many2one(
        comodel_name='res.company',
        string='Source Company',
        required=True,
    )
    dest_company_id = fields.Many2one(
        comodel_name='res.company',
        string='Destination Company',
        required=True,
    )

    def action_transfer(self):
        """Execute inter-company transfer."""
        self.ensure_one()

        # Create in source company
        source_record = self.with_company(self.source_company_id).sudo().create({
            'name': f'Transfer to {self.dest_company_id.name}',
            'type': 'outgoing',
            'company_id': self.source_company_id.id,
        })

        # Create in destination company
        dest_record = self.with_company(self.dest_company_id).sudo().create({
            'name': f'Transfer from {self.source_company_id.name}',
            'type': 'incoming',
            'company_id': self.dest_company_id.id,
            'source_ref': source_record.id,
        })

        return source_record, dest_record
```

---

## Multi-Currency Support

### Currency Fields
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # Monetary fields
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
    )
    amount_tax = fields.Monetary(
        string='Tax Amount',
        currency_field='currency_id',
    )
    amount_total = fields.Monetary(
        string='Total',
        currency_field='currency_id',
        compute='_compute_amount_total',
        store=True,
    )

    # Company currency equivalent
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Company Currency',
    )
    amount_company_currency = fields.Monetary(
        string='Amount (Company Currency)',
        currency_field='company_currency_id',
        compute='_compute_amount_company_currency',
        store=True,
    )

    @api.depends('amount', 'amount_tax')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.amount + record.amount_tax

    @api.depends('amount_total', 'currency_id', 'company_id', 'date')
    def _compute_amount_company_currency(self):
        for record in self:
            if record.currency_id != record.company_currency_id:
                record.amount_company_currency = record.currency_id._convert(
                    record.amount_total,
                    record.company_currency_id,
                    record.company_id,
                    record.date or fields.Date.today(),
                )
            else:
                record.amount_company_currency = record.amount_total
```

### Currency Conversion
```python
def convert_to_currency(self, amount: float, target_currency) -> float:
    """Convert amount to target currency."""
    if self.currency_id == target_currency:
        return amount

    return self.currency_id._convert(
        amount,
        target_currency,
        self.company_id,
        self.date or fields.Date.today(),
    )

def get_rate(self) -> float:
    """Get exchange rate to company currency."""
    return self.currency_id._get_conversion_rate(
        self.currency_id,
        self.company_currency_id,
        self.company_id,
        self.date or fields.Date.today(),
    )
```

### Multi-Currency Reporting
```python
def _get_amounts_by_currency(self) -> dict:
    """Group amounts by currency for reporting."""
    result = {}
    for record in self:
        currency = record.currency_id
        if currency not in result:
            result[currency] = {
                'amount': 0.0,
                'amount_company': 0.0,
            }
        result[currency]['amount'] += record.amount_total
        result[currency]['amount_company'] += record.amount_company_currency
    return result
```

---

## Views for Multi-Company

### Form View with Company
```xml
<form string="My Model">
    <sheet>
        <group>
            <group>
                <field name="name"/>
                <field name="partner_id"
                       context="{'default_company_id': company_id}"
                       domain="[('company_id', 'in', [company_id, False])]"/>
            </group>
            <group>
                <field name="company_id"
                       groups="base.group_multi_company"
                       options="{'no_create': True}"/>
                <field name="currency_id"
                       groups="base.group_multi_currency"/>
            </group>
        </group>
        <group string="Amounts">
            <field name="amount"/>
            <field name="amount_total"/>
            <field name="amount_company_currency"
                   groups="base.group_multi_currency"
                   invisible="currency_id == company_currency_id"/>
        </group>
    </sheet>
</form>
```

### Search View with Company Filter
```xml
<search string="My Model">
    <field name="name"/>
    <field name="partner_id"/>
    <filter string="My Company" name="my_company"
            domain="[('company_id', '=', company_id)]"/>
    <group expand="0" string="Group By">
        <filter string="Company" name="group_company"
                context="{'group_by': 'company_id'}"
                groups="base.group_multi_company"/>
        <filter string="Currency" name="group_currency"
                context="{'group_by': 'currency_id'}"
                groups="base.group_multi_currency"/>
    </group>
</search>
```

---

## Scheduled Actions (Multi-Company)

### Process Each Company
```python
@api.model
def _cron_process_all_companies(self) -> None:
    """Cron that processes each company separately."""
    companies = self.env['res.company'].search([])

    for company in companies:
        self.with_company(company)._process_company_records()

def _process_company_records(self) -> None:
    """Process records for current company context."""
    records = self.search([
        ('company_id', '=', self.env.company.id),
        ('state', '=', 'pending'),
    ])

    for record in records:
        try:
            record._do_process()
        except Exception as e:
            _logger.error(f"Error processing {record.id}: {e}")
```

---

## Best Practices

### 1. Always Include company_id
```python
# Good - explicit company
company_id = fields.Many2one(
    'res.company',
    required=True,
    default=lambda self: self.env.company,
)

# Bad - no company field on business model
```

### 2. Use check_company (v18+)
```python
# Good - automatic validation
partner_id = fields.Many2one('res.partner', check_company=True)

# Manual (older versions)
@api.constrains('partner_id', 'company_id')
def _check_company(self):
    ...
```

### 3. Use with_company() for Context
```python
# Good - explicit company context
record.with_company(company)._process()

# Avoid - changing env.company directly
```

### 4. Handle Shared Records
```python
# Allow records without company (shared)
domain = [
    '|',
    ('company_id', '=', False),
    ('company_id', '=', self.env.company.id),
]
```

### 5. Currency Conversions
```python
# Always specify date for conversions
converted = currency._convert(
    amount,
    target_currency,
    company,
    date,  # Required for correct rate
)
```

---

## Version Differences

| Feature | v14-16 | v17 | v18+ |
|---------|--------|-----|------|
| Company check | Manual `@api.constrains` | Manual | `_check_company_auto = True` |
| Field validation | `domain=` | `domain=` | `check_company=True` |
| Company switch | `with_context(force_company=)` | `with_company()` | `with_company()` |
| Multi-company views | `groups="base.group_multi_company"` | Same | Same |
