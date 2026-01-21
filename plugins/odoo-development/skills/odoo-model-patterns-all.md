# Odoo Model Patterns - Core Concepts (All Versions)

This document covers ORM model concepts that are consistent across all Odoo versions. For version-specific implementation details, see the version-specific files.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  CRITICAL: Always use version-specific patterns!                             ║
║                                                                              ║
║  Version-specific files: odoo-model-patterns-{14|15|16|17|18|19}.md          ║
║  Migration guides: odoo-model-patterns-{from}-{to}.md                        ║
║                                                                              ║
║  Key differences between versions:                                           ║
║  • v14: @api.multi still used (deprecated)                                   ║
║  • v15: @api.multi removed, use multi-record methods                         ║
║  • v16: Command class introduced, attrs deprecated                           ║
║  • v17: @api.model_create_multi mandatory, attrs removed                     ║
║  • v18: _check_company_auto, SQL() builder, type hints recommended          ║
║  • v19: Type hints mandatory, SQL() mandatory                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Model Types

### models.Model
Persistent business data with database table.

```python
class MyModel(models.Model):
    _name = 'my_module.my_model'
    _description = 'My Model'
```

Use for:
- Business entities (partners, products, orders)
- Configuration records
- Master data

### models.TransientModel
Temporary data that is automatically cleaned up.

```python
class MyWizard(models.TransientModel):
    _name = 'my_module.wizard'
    _description = 'My Wizard'
```

Use for:
- Wizards and dialogs
- Batch operations
- Temporary input forms

### models.AbstractModel
No database table, provides shared functionality.

```python
class MyMixin(models.AbstractModel):
    _name = 'my_module.mixin'
    _description = 'My Mixin'
```

Use for:
- Mixins (mail.thread, portal.mixin)
- Shared field/method definitions
- Reusable behaviors

## Model Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `_name` | Technical name | `'my_module.model'` |
| `_description` | Human name | `'My Model'` |
| `_inherit` | Extend models | `['mail.thread']` |
| `_inherits` | Delegation | `{'res.partner': 'partner_id'}` |
| `_table` | Custom table name | `'my_custom_table'` |
| `_order` | Default sort | `'sequence, name'` |
| `_rec_name` | Display field | `'name'` |
| `_parent_name` | Parent field | `'parent_id'` |
| `_parent_store` | Hierarchical | `True` |
| `_log_access` | Track access | `True` (default) |
| `_auto` | Auto create table | `True` (default) |

## Field Types

### Basic Fields

| Type | Description | Common Attributes |
|------|-------------|-------------------|
| `Char` | Short text | `size`, `trim` |
| `Text` | Long text | - |
| `Html` | Rich HTML | `sanitize` |
| `Boolean` | True/False | - |
| `Integer` | Whole number | - |
| `Float` | Decimal | `digits` |
| `Monetary` | Currency | `currency_field` |
| `Date` | Date only | - |
| `Datetime` | Date + time | - |
| `Binary` | File data | `attachment` |
| `Image` | Image binary | `max_width`, `max_height` |
| `Selection` | Dropdown | `selection` |

### Relational Fields

| Type | Description | Key Attributes |
|------|-------------|----------------|
| `Many2one` | FK reference | `comodel_name`, `ondelete` |
| `One2many` | Reverse FK | `comodel_name`, `inverse_name` |
| `Many2many` | Junction table | `comodel_name`, `relation` |

### Special Fields

| Type | Description |
|------|-------------|
| `Reference` | Dynamic model reference |
| `Monetary` | Currency-aware amount |
| `Properties` | Dynamic key-value |
| `PropertiesDefinition` | Define properties schema |

## Common Field Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `string` | str | User-facing label |
| `required` | bool | Must have value |
| `readonly` | bool | Cannot edit |
| `default` | value/callable | Default value |
| `index` | bool | Database index |
| `copy` | bool | Copy on duplicate |
| `groups` | str | Access groups |
| `tracking` | bool | Track changes |
| `compute` | str | Compute method |
| `inverse` | str | Inverse method |
| `store` | bool | Store computed |
| `help` | str | Tooltip text |
| `translate` | bool | Translatable |

## Compute Patterns

### Basic Compute

```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

### Inverse Method

```python
full_name = fields.Char(compute='_compute_full', inverse='_inverse_full')

@api.depends('first_name', 'last_name')
def _compute_full(self):
    for rec in self:
        rec.full_name = f"{rec.first_name} {rec.last_name}"

def _inverse_full(self):
    for rec in self:
        parts = (rec.full_name or '').split(' ', 1)
        rec.first_name = parts[0]
        rec.last_name = parts[1] if len(parts) > 1 else ''
```

### Context-Dependent

```python
is_manager = fields.Boolean(compute='_compute_is_manager')

@api.depends_context('uid')
def _compute_is_manager(self):
    manager_group = self.env.ref('module.group_manager')
    is_mgr = manager_group in self.env.user.groups_id
    for rec in self:
        rec.is_manager = is_mgr
```

## Constraint Patterns

### Python Constraints

```python
@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for record in self:
        if record.start_date > record.end_date:
            raise ValidationError(_("End date must be after start date."))
```

### SQL Constraints

```python
_sql_constraints = [
    ('name_uniq', 'unique(company_id, name)', 'Name must be unique!'),
    ('positive_amount', 'CHECK(amount >= 0)', 'Amount must be positive!'),
]
```

## Inheritance Types

### Extension (Classical)
Extends existing model with new fields/methods.

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_field = fields.Char()
```

### Prototype (New Model)
Creates new model based on existing one.

```python
class MyPartner(models.Model):
    _name = 'my.partner'
    _inherit = 'res.partner'
```

### Delegation
One model contains another.

```python
class ExtendedProduct(models.Model):
    _name = 'extended.product'
    _inherits = {'product.product': 'product_id'}

    product_id = fields.Many2one('product.product', required=True)
    extra_field = fields.Char()
```

## CRUD Method Patterns

### Create

```python
@api.model_create_multi  # Required in v17+
def create(self, vals_list):
    for vals in vals_list:
        # Pre-processing
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('my.model')
    records = super().create(vals_list)
    # Post-processing
    for record in records:
        record._after_create()
    return records
```

### Write

```python
def write(self, vals):
    # Pre-validation
    if 'state' in vals:
        self._check_state_transition(vals['state'])
    result = super().write(vals)
    # Post-processing
    if 'important_field' in vals:
        self._notify_change()
    return result
```

### Unlink

```python
def unlink(self):
    # Validation
    if any(rec.state != 'draft' for rec in self):
        raise UserError(_("Cannot delete non-draft records."))
    return super().unlink()
```

### Copy

```python
def copy(self, default=None):
    default = dict(default or {})
    default.setdefault('name', _("%s (Copy)", self.name))
    default.setdefault('state', 'draft')
    return super().copy(default)
```

## Search Patterns

### Domain Operators

| Operator | Description |
|----------|-------------|
| `=`, `!=` | Equals, not equals |
| `<`, `>`, `<=`, `>=` | Comparisons |
| `like`, `ilike` | Pattern match |
| `=like`, `=ilike` | SQL pattern |
| `in`, `not in` | List membership |
| `child_of`, `parent_of` | Hierarchy |
| `=?` | Unset or equals |

### Domain Combinations

```python
# AND (implicit)
domain = [('state', '=', 'confirmed'), ('amount', '>', 0)]

# OR
domain = ['|', ('state', '=', 'draft'), ('state', '=', 'confirmed')]

# NOT
domain = ['!', ('active', '=', False)]

# Complex
domain = [
    '|',
    '&', ('state', '=', 'draft'), ('user_id', '=', False),
    '&', ('state', '=', 'confirmed'), ('user_id', '!=', False),
]
```

### Name Search

```python
@api.model
def _name_search(self, name='', domain=None, operator='ilike', limit=100, order=None):
    domain = domain or []
    if name:
        domain = ['|', '|',
            ('name', operator, name),
            ('code', operator, name),
            ('reference', operator, name),
        ] + domain
    return self._search(domain, limit=limit, order=order)
```

## Action Return Patterns

### Open Form View

```python
def action_view_form(self):
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'my.model',
        'res_id': self.id,
        'view_mode': 'form',
        'target': 'current',
    }
```

### Open List View

```python
def action_view_list(self):
    return {
        'type': 'ir.actions.act_window',
        'name': _('Records'),
        'res_model': 'my.model',
        'view_mode': 'tree,form',
        'domain': [('partner_id', '=', self.partner_id.id)],
        'context': {'default_partner_id': self.partner_id.id},
    }
```

### Open Wizard

```python
def action_open_wizard(self):
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'my.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {'active_ids': self.ids},
    }
```

### URL Action

```python
def action_open_url(self):
    return {
        'type': 'ir.actions.act_url',
        'url': f'/my/portal/{self.id}',
        'target': 'self',
    }
```

## Environment Patterns

### User and Company

```python
current_user = self.env.user
current_company = self.env.company
all_companies = self.env.companies

# Sudo for elevated access
admin_user = self.env.ref('base.user_admin').sudo()
```

### Context Manipulation

```python
# Add to context
records = self.with_context(skip_validation=True)

# Replace context
records = self.with_context({'lang': 'fr_FR'})

# Read context
lang = self.env.context.get('lang', 'en_US')
```

### Company Switch

```python
# Work in different company
other_company = self.env['res.company'].browse(2)
records = self.with_company(other_company)
```

## Performance Best Practices

1. **Batch Operations**: Process records in batches
2. **Prefetch**: Use `prefetch_fields` for related data
3. **Store Computed**: Store frequently accessed computes
4. **Indexes**: Add indexes to searched fields
5. **Avoid N+1**: Use `mapped()` instead of loops
6. **Limit Reads**: Only read needed fields

```python
# Good: Batch read
partners = self.env['res.partner'].search([])
names = partners.mapped('name')  # Single query

# Bad: N+1 queries
for partner in partners:
    print(partner.name)  # Query per record
```

## Error Handling

```python
from odoo.exceptions import (
    UserError,       # User-facing error
    ValidationError, # Constraint violation
    AccessError,     # Permission denied
    MissingError,    # Record not found
    RedirectWarning, # Error with action button
)

# User error
if not self.partner_id:
    raise UserError(_("Partner is required."))

# Validation error (in @api.constrains)
if self.amount < 0:
    raise ValidationError(_("Amount must be positive."))

# Redirect warning
action = self.env.ref('module.action_id')
raise RedirectWarning(
    _("Configuration required."),
    action.id,
    _("Go to Settings"),
)
```

---

**Note**: This document covers concepts that apply to all versions. For version-specific syntax and patterns, refer to the appropriate version-specific file.
