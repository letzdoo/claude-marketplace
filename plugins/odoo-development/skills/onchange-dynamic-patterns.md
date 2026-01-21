# Onchange and Dynamic Form Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ONCHANGE & DYNAMIC FORM PATTERNS                                            ║
║  @api.onchange, dynamic domains, and form field updates                      ║
║  Use for interactive form behavior and field auto-population                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Basic Onchange

### Simple Field Update
```python
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    product_id = fields.Many2one('product.product')
    name = fields.Char(string='Description')
    price_unit = fields.Float()
    quantity = fields.Float(default=1.0)
    discount = fields.Float()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Update fields when product changes."""
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.list_price
        else:
            self.name = ''
            self.price_unit = 0.0
```

### Onchange with Warning
```python
@api.onchange('quantity')
def _onchange_quantity(self):
    """Warn if quantity exceeds stock."""
    if self.product_id and self.quantity:
        available = self.product_id.qty_available
        if self.quantity > available:
            return {
                'warning': {
                    'title': 'Insufficient Stock',
                    'message': (
                        f"Requested quantity ({self.quantity}) exceeds "
                        f"available stock ({available})."
                    ),
                }
            }
```

### Onchange with Domain
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    """Filter products based on partner."""
    if self.partner_id:
        # Clear current selection if doesn't match new domain
        if self.product_id and self.product_id.partner_id != self.partner_id:
            self.product_id = False

        return {
            'domain': {
                'product_id': [('partner_id', '=', self.partner_id.id)],
            }
        }
    return {
        'domain': {
            'product_id': [],
        }
    }
```

---

## Onchange vs Computed

### When to Use Onchange
```python
# Onchange: user can modify the auto-filled value
@api.onchange('partner_id')
def _onchange_partner_id(self):
    """Fill address from partner (user can edit)."""
    if self.partner_id:
        self.street = self.partner_id.street
        self.city = self.partner_id.city
```

### When to Use Computed
```python
# Computed: value always derived from other fields
partner_id = fields.Many2one('res.partner')
partner_name = fields.Char(
    compute='_compute_partner_name',
    store=True,
)

@api.depends('partner_id')
def _compute_partner_name(self):
    for record in self:
        record.partner_name = record.partner_id.name or ''
```

### Combined Pattern
```python
class Order(models.Model):
    _name = 'my.order'

    partner_id = fields.Many2one('res.partner')

    # Computed (always calculated)
    partner_email = fields.Char(
        compute='_compute_partner_email',
        store=True,
    )

    # Editable (filled by onchange, user can modify)
    delivery_address = fields.Text()

    @api.depends('partner_id')
    def _compute_partner_email(self):
        for record in self:
            record.partner_email = record.partner_id.email or ''

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Pre-fill delivery address."""
        if self.partner_id:
            self.delivery_address = self._format_address(self.partner_id)
```

---

## Complex Onchange Patterns

### Cascading Onchange
```python
class Order(models.Model):
    _name = 'my.order'

    country_id = fields.Many2one('res.country')
    state_id = fields.Many2one('res.country.state')
    city_id = fields.Many2one('res.city')

    @api.onchange('country_id')
    def _onchange_country_id(self):
        """Clear state and city when country changes."""
        self.state_id = False
        self.city_id = False
        if self.country_id:
            return {
                'domain': {
                    'state_id': [('country_id', '=', self.country_id.id)],
                }
            }
        return {'domain': {'state_id': []}}

    @api.onchange('state_id')
    def _onchange_state_id(self):
        """Clear city when state changes."""
        self.city_id = False
        if self.state_id:
            return {
                'domain': {
                    'city_id': [('state_id', '=', self.state_id.id)],
                }
            }
        return {'domain': {'city_id': []}}
```

### Onchange on One2many
```python
class Order(models.Model):
    _name = 'my.order'

    line_ids = fields.One2many('my.order.line', 'order_id')
    amount_total = fields.Float(compute='_compute_amount_total')

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        """Recalculate total when lines change."""
        # This triggers when lines are added/removed/modified
        self.amount_total = sum(
            line.quantity * line.price_unit
            for line in self.line_ids
        )
```

### Onchange with External Lookup
```python
@api.onchange('vat')
def _onchange_vat(self):
    """Look up company info from VAT number."""
    if self.vat:
        try:
            # External API call
            info = self._lookup_vat(self.vat)
            if info:
                self.name = info.get('name', '')
                self.street = info.get('address', '')
                return {
                    'warning': {
                        'title': 'Company Found',
                        'message': f"Company info loaded for VAT {self.vat}",
                    }
                }
        except Exception as e:
            return {
                'warning': {
                    'title': 'VAT Lookup Failed',
                    'message': str(e),
                }
            }
```

---

## Dynamic Domains

### Domain in Field Definition
```python
class Task(models.Model):
    _name = 'my.task'

    project_id = fields.Many2one('project.project')

    # Static domain
    user_id = fields.Many2one(
        'res.users',
        domain=[('share', '=', False)],  # Internal users only
    )

    # Dynamic domain (string evaluated at runtime)
    assignee_id = fields.Many2one(
        'res.users',
        domain="[('id', 'in', allowed_user_ids)]",
    )

    allowed_user_ids = fields.Many2many(
        'res.users',
        compute='_compute_allowed_users',
    )

    @api.depends('project_id')
    def _compute_allowed_users(self):
        for record in self:
            if record.project_id:
                record.allowed_user_ids = record.project_id.member_ids
            else:
                record.allowed_user_ids = self.env['res.users'].search([])
```

### Domain in View
```xml
<form>
    <group>
        <field name="project_id"/>
        <!-- Domain evaluated in context -->
        <field name="task_id"
               domain="[('project_id', '=', project_id)]"/>

        <!-- Domain with parent reference -->
        <field name="line_ids">
            <tree editable="bottom">
                <field name="product_id"
                       domain="[('categ_id', '=', parent.category_id)]"/>
            </tree>
        </field>
    </group>
</form>
```

### Context-Based Domain
```python
@api.onchange('type')
def _onchange_type(self):
    """Set domain based on type selection."""
    domains = {
        'product': [('type', '=', 'product')],
        'service': [('type', '=', 'service')],
        'consumable': [('type', '=', 'consu')],
    }
    return {
        'domain': {
            'product_id': domains.get(self.type, []),
        }
    }
```

---

## Form Field Visibility

### Dynamic Visibility with Onchange
```python
class Document(models.Model):
    _name = 'my.document'

    type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ])

    # Fields that appear based on type
    internal_ref = fields.Char()
    external_partner_id = fields.Many2one('res.partner')

    @api.onchange('type')
    def _onchange_type(self):
        """Clear irrelevant fields when type changes."""
        if self.type == 'internal':
            self.external_partner_id = False
        elif self.type == 'external':
            self.internal_ref = False
```

### View with Conditional Visibility
```xml
<form>
    <group>
        <field name="type"/>
        <field name="internal_ref" invisible="type != 'internal'"/>
        <field name="external_partner_id" invisible="type != 'external'"/>
    </group>
</form>
```

---

## Onchange Return Values

### Complete Return Structure
```python
@api.onchange('field_name')
def _onchange_field(self):
    """Full onchange return options."""
    # Set field values directly
    self.other_field = 'value'
    self.computed_value = self.field_name * 2

    return {
        # Filter options for other fields
        'domain': {
            'related_field': [('condition', '=', True)],
        },
        # Show warning to user
        'warning': {
            'title': 'Warning Title',
            'message': 'Warning message to display',
            'type': 'notification',  # or 'dialog'
        },
    }
```

### Warning Types
```python
# Notification (non-blocking)
return {
    'warning': {
        'title': 'Info',
        'message': 'This is informational',
        'type': 'notification',
    }
}

# Dialog (blocking)
return {
    'warning': {
        'title': 'Attention',
        'message': 'Please confirm this action',
        'type': 'dialog',
    }
}
```

---

## Multiple Field Onchange

### Single Decorator, Multiple Fields
```python
@api.onchange('quantity', 'price_unit', 'discount')
def _onchange_amount(self):
    """Recalculate when any pricing field changes."""
    subtotal = self.quantity * self.price_unit
    discount_amount = subtotal * (self.discount / 100)
    self.amount = subtotal - discount_amount
```

### Order of Execution
```python
# Onchanges execute in definition order
@api.onchange('partner_id')
def _onchange_partner_id(self):
    """First: set pricelist from partner."""
    if self.partner_id:
        self.pricelist_id = self.partner_id.property_product_pricelist

@api.onchange('pricelist_id')
def _onchange_pricelist_id(self):
    """Second: update prices based on pricelist."""
    if self.pricelist_id:
        self._update_line_prices()
```

---

## Onchange in Wizards

### Wizard Onchange Pattern
```python
class ConfigWizard(models.TransientModel):
    _name = 'config.wizard'

    template_id = fields.Many2one('config.template')
    name = fields.Char()
    settings = fields.Text()

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Load template settings."""
        if self.template_id:
            self.name = self.template_id.name
            self.settings = self.template_id.default_settings
```

---

## Best Practices

### Do's
```python
# Good: Clear dependent fields
@api.onchange('parent_id')
def _onchange_parent_id(self):
    self.child_id = False  # Clear when parent changes

# Good: Handle empty values
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.phone = self.partner_id.phone
    else:
        self.phone = ''

# Good: Return domains for filtering
@api.onchange('category_id')
def _onchange_category_id(self):
    return {
        'domain': {
            'product_id': [('categ_id', '=', self.category_id.id)]
                          if self.category_id else [],
        }
    }
```

### Don'ts
```python
# Bad: Heavy computation in onchange
@api.onchange('product_id')
def _onchange_product_id(self):
    # Don't do expensive operations
    all_orders = self.env['sale.order'].search([])  # Bad!

# Bad: Database writes in onchange
@api.onchange('quantity')
def _onchange_quantity(self):
    self.env['stock.move'].create({})  # Bad! Record doesn't exist yet

# Bad: Modifying records outside self
@api.onchange('partner_id')
def _onchange_partner_id(self):
    self.partner_id.last_accessed = fields.Date.today()  # Bad!
```

---

## Debugging Onchange

### Logging Onchange Values
```python
import logging
_logger = logging.getLogger(__name__)

@api.onchange('field_name')
def _onchange_field_name(self):
    _logger.info(
        "Onchange triggered: field=%s, value=%s, self.id=%s",
        'field_name', self.field_name, self.id
    )
    # Note: self.id is NewId for unsaved records
```

### Testing Onchange
```python
def test_onchange_product(self):
    """Test product onchange fills name and price."""
    line = self.env['sale.order.line'].new({
        'order_id': self.order.id,
    })

    line.product_id = self.product
    line._onchange_product_id()

    self.assertEqual(line.name, self.product.name)
    self.assertEqual(line.price_unit, self.product.list_price)
```

---

## Summary Table

| Feature | Onchange | Computed |
|---------|----------|----------|
| Trigger | User interaction | Dependency change |
| User editable | Yes | No (unless inverse) |
| Works before save | Yes | Yes |
| Works after save | No | Yes |
| Database query | Avoid | OK with store=True |
| Return domains | Yes | No |
| Return warnings | Yes | No |
| Use case | Auto-fill suggestions | Derived values |
