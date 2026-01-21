# Odoo Model Patterns Migration Guide: 17.0 → 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODEL MIGRATION GUIDE: Odoo 17.0 → 18.0                                     ║
║  Focus: Company checks, SQL builder, type hints                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## New Features Summary

| Feature | v17 | v18 | Recommendation |
|---------|-----|-----|----------------|
| `_check_company_auto` | N/A | Available | Add to multi-company models |
| `check_company` on fields | N/A | Available | Add to cross-company fields |
| `SQL()` builder | N/A | Recommended | Use for raw SQL |
| Type hints | Optional | Recommended | Add where possible |

## NEW: Automatic Company Validation

### Before (v17 - Manual)
```python
class MyModel(models.Model):
    _name = 'my.model'

    company_id = fields.Many2one('res.company')
    partner_id = fields.Many2one('res.partner')

    @api.constrains('partner_id', 'company_id')
    def _check_partner_company(self):
        for record in self:
            if record.partner_id.company_id and record.partner_id.company_id != record.company_id:
                raise ValidationError(_("Partner company must match record company."))
```

### After (v18 - Automatic)
```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # Enable automatic checking

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # Framework handles validation
    )
    # No manual constraint needed!
```

## NEW: SQL Builder

### Before (v17 - Raw SQL)
```python
def _get_statistics(self):
    query = """
        SELECT partner_id, SUM(amount) as total
        FROM %s
        WHERE company_id = %%s AND state = %%s
        GROUP BY partner_id
    """ % self._table
    self.env.cr.execute(query, (self.env.company.id, 'confirmed'))
    return self.env.cr.dictfetchall()
```

### After (v18 - SQL Builder)
```python
from odoo.tools import SQL

def _get_statistics(self):
    query = SQL(
        """
        SELECT partner_id, SUM(amount) as total
        FROM %s
        WHERE company_id = %s AND state = %s
        GROUP BY partner_id
        """,
        SQL.identifier(self._table),
        self.env.company.id,
        'confirmed',
    )
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()
```

### SQL Builder Benefits
- Automatic SQL injection prevention
- Type-safe identifiers
- Clear parameter binding
- Better debugging

## RECOMMENDED: Type Hints

### Before (v17)
```python
def calculate_total(self, include_tax=True, discount=None):
    discount = discount or 0
    total = sum(self.mapped('amount'))
    if include_tax:
        total *= 1.21
    return total - discount
```

### After (v18)
```python
from typing import Optional

def calculate_total(
    self,
    include_tax: bool = True,
    discount: Optional[float] = None,
) -> float:
    discount = discount or 0.0
    total = sum(self.mapped('amount'))
    if include_tax:
        total *= 1.21
    return total - discount
```

## Security Rule Updates

### Before (v17)
```xml
<field name="domain_force">[
    ('company_id', 'in', company_ids)
]</field>
```

### After (v18)
```xml
<field name="domain_force">[
    ('company_id', 'in', allowed_company_ids)
]</field>
```

## Migration Checklist

### For Multi-Company Models
- [ ] Add `_check_company_auto = True` to model definition
- [ ] Add `check_company=True` to relevant Many2one fields
- [ ] Remove manual company validation constraints
- [ ] Update record rules to use `allowed_company_ids`

### For SQL Queries
- [ ] Import `from odoo.tools import SQL`
- [ ] Replace raw SQL strings with `SQL()` builder
- [ ] Use `SQL.identifier()` for table/column names
- [ ] Test all queries work correctly

### For Methods (Recommended)
- [ ] Add type hints to method parameters
- [ ] Add return type annotations
- [ ] Import `from typing import Optional, Any` as needed

### Testing
- [ ] Test multi-company scenarios
- [ ] Test company switching
- [ ] Verify SQL queries execute correctly
- [ ] Test with Python type checker (optional)

## Backward Compatibility

If supporting both v17 and v18:

```python
# Check for SQL builder availability
try:
    from odoo.tools import SQL
    HAS_SQL = True
except ImportError:
    HAS_SQL = False

def _execute_query(self):
    if HAS_SQL:
        query = SQL("SELECT * FROM %s WHERE id = %s",
                   SQL.identifier(self._table), self.id)
    else:
        query = "SELECT * FROM %s WHERE id = %%s" % self._table
        query = query, (self.id,)
    # Handle execution...
```

## Common Migration Issues

### Issue: company_id required for _check_company_auto
```
ValidationError: company_id is required when _check_company_auto is True
```
**Fix**: Ensure `company_id` field has `required=True`.

### Issue: SQL identifier error
```
AttributeError: 'str' object has no attribute 'as_string'
```
**Fix**: Use `SQL.identifier()` for table names, not raw strings.

### Issue: Type hint import error
```
ImportError: cannot import name 'Optional' from 'typing'
```
**Fix**: Ensure Python 3.10+ is used, or use `from typing import Optional`.
