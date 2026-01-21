# Odoo Module Migration Guide: 17.0 → 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: Odoo 17.0 → 18.0                                           ║
║  This document covers ONLY changes between these specific versions.          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Component | v17 Status | v18 Status | Action Required |
|-----------|------------|------------|-----------------|
| `_check_company_auto` | Optional | Recommended | Add to models |
| `check_company` on fields | Optional | Recommended | Add to relations |
| `SQL()` builder | New | Recommended | Use for raw SQL |
| Type hints | Optional | Recommended | Add where possible |
| Raw SQL strings | Allowed | Deprecated | Migrate to SQL() |
| Python 3.10 | Required | 3.10+, 3.12 recommended | Verify compatibility |

## NEW: Company Check Automation

### Before (v17)
```python
class MyModel(models.Model):
    _name = 'my.model'

    company_id = fields.Many2one('res.company')
    partner_id = fields.Many2one('res.partner')

    def write(self, vals):
        # Manual company validation
        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.company_id and partner.company_id != self.company_id:
                raise UserError(_("Partner company mismatch."))
        return super().write(vals)
```

### After (v18)
```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # v18: Enable automatic checks

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # v18: Automatic company validation
    )
    # No manual validation needed - framework handles it
```

## NEW: SQL Builder Pattern

### Before (v17 - Raw SQL)
```python
def _get_statistics(self):
    # Vulnerable to SQL injection if not careful
    query = """
        SELECT partner_id, SUM(amount) as total
        FROM %s
        WHERE company_id = %s AND state = '%s'
        GROUP BY partner_id
    """ % (self._table, self.env.company.id, 'confirmed')
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()
```

### After (v18 - SQL Builder)
```python
from odoo.tools import SQL

def _get_statistics(self):
    # Safe, parameterized queries
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

### SQL Builder Reference

```python
from odoo.tools import SQL

# Table/column identifiers (prevents injection)
SQL.identifier('my_table')
SQL.identifier('my_table', 'column_name')

# Raw SQL fragment (use carefully)
SQL('ORDER BY create_date DESC')

# Combining queries
query = SQL(
    "%s UNION %s",
    SQL("SELECT * FROM table1 WHERE id = %s", 1),
    SQL("SELECT * FROM table2 WHERE id = %s", 2),
)

# IN clause with tuple
ids = (1, 2, 3)
query = SQL("SELECT * FROM table WHERE id IN %s", ids)
```

## RECOMMENDED: Type Hints

### Before (v17)
```python
def process_partner(self, partner_id, options=None):
    partner = self.env['res.partner'].browse(partner_id)
    options = options or {}
    return partner.name
```

### After (v18)
```python
from typing import Optional, Any

def process_partner(
    self,
    partner_id: int,
    options: Optional[dict[str, Any]] = None,
) -> str:
    partner = self.env['res.partner'].browse(partner_id)
    options = options or {}
    return partner.name
```

### Common Type Hints

```python
from typing import Optional, Any, Union
from collections.abc import Iterable

# Model methods
def create(self, vals_list: list[dict]) -> 'MyModel': ...
def write(self, vals: dict) -> bool: ...
def unlink(self) -> bool: ...
def copy(self, default: Optional[dict] = None) -> 'MyModel': ...

# Search methods
def search(self, domain: list, limit: Optional[int] = None) -> 'MyModel': ...

# Custom methods
def calculate_total(self, include_tax: bool = True) -> float: ...
def get_partner_data(self) -> dict[str, Any]: ...
```

## Multi-Company Updates

### v18 Multi-Company Pattern

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )

    # Related fields - auto-check company
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,
    )
    product_id = fields.Many2one(
        'product.product',
        check_company=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        check_company=True,
    )
```

### Security Rule Update

```xml
<!-- v18: Use allowed_company_ids -->
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-Company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', allowed_company_ids)
    ]</field>
</record>
```

## OWL Updates (2.x Enhanced)

### Service Access Pattern
```javascript
// v18: Consistent service usage
setup() {
    this.orm = useService("orm");
    this.action = useService("action");
    this.notification = useService("notification");
    this.dialog = useService("dialog");
    this.user = useService("user");
    this.company = useService("company");
}
```

### Enhanced RPC
```javascript
// v18: Enhanced ORM service
const records = await this.orm.searchRead(
    "res.partner",
    [["is_company", "=", true]],
    ["name", "email", "phone"],
    { limit: 100, order: "name ASC" }
);
```

## Manifest Version Update

```python
# v17
'version': '17.0.1.0.0',

# v18
'version': '18.0.1.0.0',
```

## Migration Checklist

### Models (Python)
- [ ] Add `_check_company_auto = True` to multi-company models
- [ ] Add `check_company=True` to relational fields referencing company-specific data
- [ ] Replace raw SQL with `SQL()` builder
- [ ] Add type hints to method signatures
- [ ] Update Python compatibility to 3.10+ (3.12 recommended)
- [ ] Review deprecated method usage

### Views (XML)
- [ ] Verify all views work with new validation
- [ ] Test company switching behavior
- [ ] Verify field visibility with company rules

### Security (XML)
- [ ] Update record rules to use `allowed_company_ids`
- [ ] Test multi-company access scenarios
- [ ] Verify cross-company data isolation

### OWL (JavaScript)
- [ ] Verify service usage patterns
- [ ] Test all client actions
- [ ] Verify RPC calls work correctly

### Manifest
- [ ] Update version from `17.0.x.x.x` to `18.0.x.x.x`
- [ ] Verify all dependencies are v18 compatible
- [ ] Check asset declarations

### Testing
- [ ] Run all tests with v18
- [ ] Test multi-company scenarios
- [ ] Test company switching
- [ ] Verify SQL queries work correctly
- [ ] Performance testing (SQL builder may affect)

## Common Migration Issues

### Issue: Company validation errors
```
ValidationError: Partner's company must match document company.
```
**Solution**: Ensure all relational fields have proper company relationships or set `check_company=False` for cross-company fields.

### Issue: SQL syntax errors
```
ProgrammingError: syntax error at or near "SQL"
```
**Solution**: Ensure SQL() is properly imported from `odoo.tools`.

### Issue: Type hint import errors
```
ImportError: cannot import name 'Optional' from 'typing'
```
**Solution**: Use Python 3.10+ which has built-in support, or import from `typing`.

## Performance Considerations

### SQL Builder Overhead
The SQL() builder adds minimal overhead but provides:
- Automatic SQL injection prevention
- Better query debugging
- Consistent query formatting

### Company Check Performance
`_check_company_auto` adds validation overhead:
- Enable only on models that need it
- Consider disabling for high-volume transient models
- Use `with_context(check_company=False)` for batch operations

## Backward Compatibility Notes

### Keeping v17 Compatibility (Dual Version)
```python
# Works in both v17 and v18
try:
    from odoo.tools import SQL
    HAS_SQL_BUILDER = True
except ImportError:
    HAS_SQL_BUILDER = False

def _execute_query(self, ...):
    if HAS_SQL_BUILDER:
        query = SQL(...)
    else:
        query = "..." % (...)
    self.env.cr.execute(query)
```

**Note**: This is only recommended for modules that must support multiple versions simultaneously.

## GitHub Reference

For official migration notes, consult:
- https://github.com/odoo/odoo/tree/18.0
- Odoo 18.0 release notes
- Community upgrade scripts

---

**IMPORTANT**: v18 changes are mostly additive. Focus on adopting new patterns for better security and maintainability.
