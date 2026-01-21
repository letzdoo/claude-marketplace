# Sequence and Numbering Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  SEQUENCE & NUMBERING PATTERNS                                               ║
║  Automatic numbering, reference generation, and sequence management          ║
║  Use for document numbers, codes, and unique identifiers                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Basic Sequence Setup

### Define Sequence (XML)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="sequence_my_model" model="ir.sequence">
            <field name="name">My Model Sequence</field>
            <field name="code">my.model</field>
            <field name="prefix">MM/%(year)s/</field>
            <field name="padding">5</field>
            <field name="number_increment">1</field>
            <field name="number_next">1</field>
        </record>
    </data>
</odoo>
```

### Sequence Placeholders
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `%(year)s` | 4-digit year | 2024 |
| `%(y)s` | 2-digit year | 24 |
| `%(month)s` | 2-digit month | 01-12 |
| `%(day)s` | 2-digit day | 01-31 |
| `%(doy)s` | Day of year | 001-366 |
| `%(woy)s` | Week of year | 01-53 |
| `%(weekday)s` | Day of week | 0-6 |
| `%(h24)s` | Hour (24h) | 00-23 |
| `%(h12)s` | Hour (12h) | 01-12 |
| `%(min)s` | Minutes | 00-59 |
| `%(sec)s` | Seconds | 00-59 |

### Sequence with Company
```xml
<record id="sequence_my_model_company" model="ir.sequence">
    <field name="name">My Model Sequence</field>
    <field name="code">my.model</field>
    <field name="prefix">%(company_code)s/%(year)s/</field>
    <field name="padding">4</field>
    <field name="company_id" ref="base.main_company"/>
</record>
```

---

## Using Sequences in Models

### Basic Usage
```python
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'my.model'
                ) or 'New'
        return super().create(vals_list)
```

### With Date Context
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', 'New') == 'New':
            # Use specific date for sequence
            sequence_date = vals.get('date') or fields.Date.today()
            vals['name'] = self.env['ir.sequence'].with_context(
                ir_sequence_date=sequence_date
            ).next_by_code('my.model') or 'New'
    return super().create(vals_list)
```

### Company-Specific Sequence
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', 'New') == 'New':
            company_id = vals.get('company_id') or self.env.company.id
            vals['name'] = self.env['ir.sequence'].with_company(
                company_id
            ).next_by_code('my.model') or 'New'
    return super().create(vals_list)
```

### Conditional Sequence
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', 'New') == 'New':
            record_type = vals.get('type', 'standard')
            if record_type == 'internal':
                code = 'my.model.internal'
            else:
                code = 'my.model'
            vals['name'] = self.env['ir.sequence'].next_by_code(code) or 'New'
    return super().create(vals_list)
```

---

## Advanced Sequence Patterns

### Sequence per Partner
```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Invoice Sequence',
        copy=False,
    )

    def _get_or_create_sequence(self):
        """Get or create partner-specific sequence."""
        self.ensure_one()
        if not self.sequence_id:
            self.sequence_id = self.env['ir.sequence'].create({
                'name': f'Invoice Sequence - {self.name}',
                'code': f'account.move.partner.{self.id}',
                'prefix': f'{self.ref or "CUST"}/%(year)s/',
                'padding': 4,
            })
        return self.sequence_id


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_sequence(self):
        """Get appropriate sequence for invoice."""
        if self.partner_id.sequence_id:
            return self.partner_id.sequence_id
        return super()._get_sequence()
```

### Multi-Level Sequence
```python
class MyModel(models.Model):
    _name = 'my.model'

    name = fields.Char(string='Reference', readonly=True, default='New')
    department_id = fields.Many2one('hr.department')
    year = fields.Char(compute='_compute_year', store=True)

    @api.depends('create_date')
    def _compute_year(self):
        for record in self:
            record.year = str(record.create_date.year) if record.create_date else ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                dept_id = vals.get('department_id')
                dept = self.env['hr.department'].browse(dept_id) if dept_id else None
                dept_code = dept.x_code if dept else 'GEN'

                # Create sequence: DEPT/YEAR/NUMBER
                year = fields.Date.today().year
                prefix = f'{dept_code}/{year}/'

                # Get next number for this prefix
                last_record = self.search([
                    ('name', 'like', f'{prefix}%'),
                ], order='name desc', limit=1)

                if last_record:
                    last_num = int(last_record.name.split('/')[-1])
                    next_num = last_num + 1
                else:
                    next_num = 1

                vals['name'] = f'{prefix}{next_num:05d}'

        return super().create(vals_list)
```

### Sequence with Reset
```xml
<!-- Reset yearly -->
<record id="sequence_yearly_reset" model="ir.sequence">
    <field name="name">Yearly Reset Sequence</field>
    <field name="code">my.model.yearly</field>
    <field name="prefix">INV/%(year)s/</field>
    <field name="padding">5</field>
    <field name="use_date_range">True</field>
</record>
```

```python
# The sequence will auto-create date ranges when use_date_range=True
# Each year gets its own counter starting from 1
```

### Sequence for Sub-Records
```python
class MyModelLine(models.Model):
    _name = 'my.model.line'

    model_id = fields.Many2one('my.model', required=True, ondelete='cascade')
    line_number = fields.Integer(string='Line #', readonly=True)
    name = fields.Char(string='Description')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('line_number'):
                model_id = vals.get('model_id')
                if model_id:
                    last_line = self.search([
                        ('model_id', '=', model_id),
                    ], order='line_number desc', limit=1)
                    vals['line_number'] = (last_line.line_number or 0) + 1
        return super().create(vals_list)
```

---

## Custom Reference Generation

### UUID-Based Reference
```python
import uuid


class MyModel(models.Model):
    _name = 'my.model'

    reference = fields.Char(
        string='Reference',
        default=lambda self: str(uuid.uuid4())[:8].upper(),
        readonly=True,
        copy=False,
    )
```

### Hash-Based Reference
```python
import hashlib


class MyModel(models.Model):
    _name = 'my.model'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if not record.reference:
                # Create hash from record data
                data = f'{record.id}{record.create_date}{record.partner_id.id}'
                hash_val = hashlib.md5(data.encode()).hexdigest()[:8].upper()
                record.reference = f'REF-{hash_val}'
        return records
```

### Checksum Reference
```python
class MyModel(models.Model):
    _name = 'my.model'

    def _generate_reference_with_checksum(self):
        """Generate reference with Luhn checksum."""
        base_number = self.env['ir.sequence'].next_by_code('my.model.base')
        checksum = self._luhn_checksum(base_number)
        return f'{base_number}{checksum}'

    def _luhn_checksum(self, number_str):
        """Calculate Luhn checksum digit."""
        digits = [int(d) for d in str(number_str)]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        total = sum(odd_digits)
        for d in even_digits:
            total += sum(divmod(d * 2, 10))
        return (10 - (total % 10)) % 10
```

---

## Sequence Views

### Sequence Form View
```xml
<record id="view_sequence_form_inherit" model="ir.ui.view">
    <field name="name">ir.sequence.form.inherit</field>
    <field name="model">ir.sequence</field>
    <field name="inherit_id" ref="base.sequence_view"/>
    <field name="arch" type="xml">
        <field name="company_id" position="after">
            <field name="x_department_id"/>
        </field>
    </field>
</record>
```

### Menu for Sequence Management
```xml
<menuitem id="menu_sequence_config"
          name="Sequences"
          parent="base.menu_custom"
          action="base.ir_sequence_form"
          groups="base.group_system"/>
```

---

## Sequence Security

### Per-Company Sequences
```python
def _setup_company_sequences(self, company):
    """Create sequences for new company."""
    sequences = [
        {
            'name': f'My Model - {company.name}',
            'code': 'my.model',
            'prefix': f'{company.x_code}/%(year)s/',
            'padding': 5,
            'company_id': company.id,
        },
    ]

    for seq_vals in sequences:
        existing = self.env['ir.sequence'].search([
            ('code', '=', seq_vals['code']),
            ('company_id', '=', company.id),
        ])
        if not existing:
            self.env['ir.sequence'].create(seq_vals)
```

### Sequence Access Rights
```xml
<!-- Allow users to see sequence in selection -->
<record id="rule_sequence_user" model="ir.rule">
    <field name="name">Sequence: User Access</field>
    <field name="model_id" ref="base.model_ir_sequence"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

---

## Best Practices

### 1. Use noupdate for Sequences
```xml
<data noupdate="1">
    <!-- Sequences should not be updated on module upgrade -->
    <record id="sequence_my_model" model="ir.sequence">
        ...
    </record>
</data>
```

### 2. Handle Concurrent Access
```python
# Sequences are thread-safe by design
# But custom numbering may need locking
def _get_next_number(self):
    self.env.cr.execute("""
        SELECT COALESCE(MAX(sequence_number), 0) + 1
        FROM my_model
        WHERE parent_id = %s
        FOR UPDATE
    """, (self.parent_id.id,))
    return self.env.cr.fetchone()[0]
```

### 3. Never Reuse Numbers
```python
# Bad - gaps are OK, reusing is not
def _fill_gap(self):
    # Never do this!
    pass

# Good - let gaps exist
# Document that gaps are normal and expected
```

### 4. Meaningful Prefixes
```python
# Good - meaningful prefixes
'prefix': 'INV/%(year)s/'  # Invoice
'prefix': 'SO/%(year)s/'   # Sale Order
'prefix': 'PO/%(year)s/'   # Purchase Order

# Bad - cryptic prefixes
'prefix': 'X1/%(year)s/'
```

### 5. Consistent Padding
```python
# Choose padding based on expected volume
# 4 digits = up to 9,999 per period
# 5 digits = up to 99,999 per period
# 6 digits = up to 999,999 per period
```

### 6. Document Sequence Logic
```python
class MyModel(models.Model):
    """
    Reference format: TYPE/YEAR/NUMBER
    - TYPE: 2-letter type code (IN=Internal, EX=External)
    - YEAR: 4-digit year
    - NUMBER: 5-digit sequential number, resets yearly

    Examples: IN/2024/00001, EX/2024/00042
    """
    _name = 'my.model'
```

---

## Troubleshooting

### Reset Sequence
```sql
-- Reset sequence to specific number (use with caution!)
UPDATE ir_sequence
SET number_next = 1
WHERE code = 'my.model';

-- Check current value
SELECT code, number_next, prefix, suffix
FROM ir_sequence
WHERE code = 'my.model';
```

### Fix Gaps
```python
# Gaps are normal - don't fix them
# But if required for reporting:
def _get_missing_numbers(self):
    """Find gaps in sequence (for audit only)."""
    all_nums = self.search([]).mapped(
        lambda r: int(r.name.split('/')[-1])
    )
    full_range = set(range(1, max(all_nums) + 1))
    missing = full_range - set(all_nums)
    return sorted(missing)
```
