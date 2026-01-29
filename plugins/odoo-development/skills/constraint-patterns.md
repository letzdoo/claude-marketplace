# Constraint Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  CONSTRAINT PATTERNS                                                         ║
║  SQL constraints, Python constraints, and data validation                    ║
║  Use for data integrity, validation rules, and business logic enforcement    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Constraint Types

| Type | When Checked | Use Case |
|------|--------------|----------|
| SQL | Database level | Uniqueness, basic checks |
| Python | ORM level | Complex business rules |

---

## SQL Constraints

### Odoo 19: models.Constraint() Class (REQUIRED)
```python
from odoo import models, fields


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(required=True)
    code = fields.Char()
    amount = fields.Float()
    percentage = fields.Float()
    date_start = fields.Date()
    date_end = fields.Date()
    company_id = fields.Many2one('res.company')

    # Unique constraint
    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Code must be unique.',
    )

    # Unique per company
    _code_company_unique = models.Constraint(
        'UNIQUE(code, company_id)',
        'Code must be unique per company.',
    )

    # Check constraint
    _amount_positive = models.Constraint(
        'CHECK(amount >= 0)',
        'Amount must be positive.',
    )

    # Range constraint
    _percentage_range = models.Constraint(
        'CHECK(percentage >= 0 AND percentage <= 100)',
        'Percentage must be between 0 and 100.',
    )

    # Date constraint
    _dates_check = models.Constraint(
        'CHECK(date_end >= date_start)',
        'End date must be after start date.',
    )

    # Not null with condition
    _code_required_if_active = models.Constraint(
        'CHECK(active = false OR code IS NOT NULL)',
        'Code is required for active records.',
    )
```

### Odoo 18 and Earlier: _sql_constraints List (DEPRECATED in v19)
```python
from odoo import models, fields


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(required=True)
    code = fields.Char()
    amount = fields.Float()
    percentage = fields.Float()
    date_start = fields.Date()
    date_end = fields.Date()
    company_id = fields.Many2one('res.company')

    _sql_constraints = [
        # Unique constraint
        ('code_unique', 'UNIQUE(code)',
         'Code must be unique.'),

        # Unique per company
        ('code_company_unique', 'UNIQUE(code, company_id)',
         'Code must be unique per company.'),

        # Check constraint
        ('amount_positive', 'CHECK(amount >= 0)',
         'Amount must be positive.'),

        # Range constraint
        ('percentage_range', 'CHECK(percentage >= 0 AND percentage <= 100)',
         'Percentage must be between 0 and 100.'),

        # Date constraint
        ('dates_check', 'CHECK(date_end >= date_start)',
         'End date must be after start date.'),

        # Not null with condition
        ('code_required_if_active',
         'CHECK(active = false OR code IS NOT NULL)',
         'Code is required for active records.'),
    ]
```

### Common SQL Constraint Patterns (Odoo 19 Syntax)

#### Uniqueness
```python
# Simple unique
_name_unique = models.Constraint(
    'UNIQUE(name)',
    'Name must be unique.',
)

# Unique combination
_name_date_unique = models.Constraint(
    'UNIQUE(name, date)',
    'Name must be unique per date.',
)

# Unique per parent
_name_parent_unique = models.Constraint(
    'UNIQUE(name, parent_id)',
    'Name must be unique within parent.',
)

# Unique per company (common pattern)
_reference_company_unique = models.Constraint(
    'UNIQUE(reference, company_id)',
    'Reference must be unique per company.',
)
```

#### Value Checks
```python
# Positive value
_quantity_positive = models.Constraint(
    'CHECK(quantity > 0)',
    'Quantity must be greater than zero.',
)

# Non-negative
_balance_non_negative = models.Constraint(
    'CHECK(balance >= 0)',
    'Balance cannot be negative.',
)

# Range
_discount_range = models.Constraint(
    'CHECK(discount >= 0 AND discount <= 100)',
    'Discount must be between 0% and 100%.',
)

# Not equal
_not_self_parent = models.Constraint(
    'CHECK(id != parent_id)',
    'Record cannot be its own parent.',
)
```

#### Conditional Checks
```python
# Required if condition
_email_required_for_customers = models.Constraint(
    'CHECK(is_customer = false OR email IS NOT NULL)',
    'Email is required for customers.',
)

# Either/or
_product_or_description = models.Constraint(
    'CHECK(product_id IS NOT NULL OR description IS NOT NULL)',
    'Either product or description is required.',
)

# Mutually exclusive
_exclusive_type = models.Constraint(
    'CHECK((type_a = true AND type_b = false) OR (type_a = false AND type_b = true) OR (type_a = false AND type_b = false))',
    'Cannot be both type A and type B.',
)
```

---

## Python Constraints

### Basic Python Constraint
```python
from odoo import api, models, fields
from odoo.exceptions import ValidationError


class MyModel(models.Model):
    _name = 'my.model'

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError("Amount cannot be negative.")
```

### Multiple Fields
```python
@api.constrains('date_start', 'date_end')
def _check_dates(self):
    for record in self:
        if record.date_start and record.date_end:
            if record.date_start > record.date_end:
                raise ValidationError(
                    "End date must be after start date."
                )
```

### Complex Validation
```python
@api.constrains('line_ids')
def _check_lines(self):
    for record in self:
        if not record.line_ids:
            raise ValidationError("At least one line is required.")

        total = sum(record.line_ids.mapped('amount'))
        if total != record.amount_total:
            raise ValidationError(
                f"Line amounts ({total}) must equal total ({record.amount_total})."
            )
```

### Cross-Record Validation
```python
@api.constrains('code', 'company_id')
def _check_code_unique(self):
    """Check uniqueness with more control than SQL constraint."""
    for record in self:
        if not record.code:
            continue

        duplicate = self.search([
            ('id', '!=', record.id),
            ('code', '=ilike', record.code),  # Case-insensitive
            ('company_id', '=', record.company_id.id),
        ], limit=1)

        if duplicate:
            raise ValidationError(
                f"Code '{record.code}' already exists in this company."
            )
```

### Validation with External Data
```python
@api.constrains('email')
def _check_email_format(self):
    import re
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    for record in self:
        if record.email and not re.match(email_pattern, record.email):
            raise ValidationError(
                f"Invalid email format: {record.email}"
            )

@api.constrains('phone')
def _check_phone_format(self):
    import re
    phone_pattern = r'^\+?[\d\s-]{8,}$'

    for record in self:
        if record.phone and not re.match(phone_pattern, record.phone):
            raise ValidationError(
                f"Invalid phone format: {record.phone}"
            )
```

### Validation with Context
```python
@api.constrains('quantity')
def _check_quantity_available(self):
    """Skip validation during import."""
    if self.env.context.get('import_mode'):
        return

    for record in self:
        available = record.product_id.qty_available
        if record.quantity > available:
            raise ValidationError(
                f"Requested quantity ({record.quantity}) exceeds "
                f"available stock ({available})."
            )
```

---

## Advanced Patterns

### Hierarchical Validation
```python
@api.constrains('parent_id')
def _check_hierarchy(self):
    """Prevent circular references."""
    if not self._check_recursion():
        raise ValidationError(
            "Error! You cannot create recursive categories."
        )
```

### State-Dependent Validation
```python
@api.constrains('state', 'partner_id', 'line_ids')
def _check_state_requirements(self):
    for record in self:
        if record.state == 'confirmed':
            if not record.partner_id:
                raise ValidationError(
                    "Partner is required for confirmed records."
                )
            if not record.line_ids:
                raise ValidationError(
                    "Lines are required for confirmed records."
                )
```

### Aggregate Validation
```python
@api.constrains('percentage')
def _check_total_percentage(self):
    """Ensure percentages sum to 100%."""
    for record in self:
        siblings = self.search([
            ('parent_id', '=', record.parent_id.id),
        ])
        total = sum(siblings.mapped('percentage'))

        if abs(total - 100) > 0.01:  # Allow small rounding errors
            raise ValidationError(
                f"Percentages must sum to 100%. Current total: {total}%"
            )
```

### Business Period Validation
```python
@api.constrains('date', 'company_id')
def _check_fiscal_period(self):
    """Ensure date is in open fiscal period."""
    for record in self:
        period = self.env['account.fiscal.year'].search([
            ('company_id', '=', record.company_id.id),
            ('date_from', '<=', record.date),
            ('date_to', '>=', record.date),
        ], limit=1)

        if not period:
            raise ValidationError(
                f"No fiscal year defined for date {record.date}."
            )

        if period.state == 'closed':
            raise ValidationError(
                f"Cannot post to closed fiscal period: {period.name}"
            )
```

---

## Constraint with Detailed Messages

### Multiple Error Collection
```python
@api.constrains('name', 'code', 'amount', 'date_start', 'date_end')
def _check_all_fields(self):
    """Validate all fields and collect errors."""
    for record in self:
        errors = []

        if not record.name or len(record.name) < 3:
            errors.append("Name must be at least 3 characters.")

        if record.code and not record.code.isalnum():
            errors.append("Code must be alphanumeric only.")

        if record.amount <= 0:
            errors.append("Amount must be greater than zero.")

        if record.date_start and record.date_end:
            if record.date_start > record.date_end:
                errors.append("Start date must be before end date.")

        if errors:
            raise ValidationError("\n".join(errors))
```

### Field-Specific Error Messages
```python
@api.constrains('quantity', 'product_id')
def _check_quantity(self):
    for record in self:
        if record.quantity <= 0:
            raise ValidationError(
                f"Invalid quantity for product '{record.product_id.name}': "
                f"must be greater than zero."
            )

        min_qty = record.product_id.x_min_order_qty
        if min_qty and record.quantity < min_qty:
            raise ValidationError(
                f"Minimum order quantity for '{record.product_id.name}' "
                f"is {min_qty}. Requested: {record.quantity}"
            )
```

---

## When to Use Which

### Use SQL Constraints For:
- Simple uniqueness checks
- Basic numeric checks (positive, range)
- Database-level integrity
- Performance-critical validations

### Use Python Constraints For:
- Complex business logic
- Cross-record validation
- External data validation
- Conditional validation
- Custom error messages
- Validation that needs ORM features

---

## Best Practices

1. **Prefer SQL for simple checks** - More efficient, database-level
2. **Use Python for complex logic** - More flexibility
3. **Clear error messages** - Tell user what's wrong and how to fix
4. **Validate early** - Catch errors before processing
5. **Consider context** - Skip validation during imports if appropriate
6. **Test constraints** - Write tests for validation logic
7. **Don't over-constrain** - Balance integrity vs usability
8. **Document constraints** - Explain business rules
9. **Handle upgrades** - New constraints may fail on existing data
10. **Performance** - Avoid heavy queries in constraints

---

## Handling Existing Data

### Adding Constraints to Existing Tables
```python
# In migration script
def migrate(cr, version):
    """Fix data before adding constraint."""
    # Fix invalid data first
    cr.execute("""
        UPDATE my_model
        SET amount = 0
        WHERE amount < 0
    """)

    # Remove duplicates
    cr.execute("""
        DELETE FROM my_model a
        USING my_model b
        WHERE a.id > b.id
        AND a.code = b.code
        AND a.company_id = b.company_id
    """)
```
