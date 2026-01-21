# Odoo Security Guide - Migration 17.0 → 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: ODOO 17.0 → 18.0 SECURITY                                  ║
║  Use this guide when upgrading security code from v17 to v18.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview of Security Changes

| Component | v17 | v18 | Migration Required |
|-----------|-----|-----|-------------------|
| Multi-company | `company_ids` | `allowed_company_ids` | Recommended |
| Company check | Manual domain | `_check_company_auto` | Recommended |
| Field company | Manual validation | `check_company=True` | Recommended |
| Type hints | Optional | Recommended | Optional |
| SQL queries | Parameterized | `SQL()` builder | Recommended |
| View syntax | Direct attributes | Direct attributes | No change |

## Breaking Changes

### None - v17 to v18 is mostly additive

The v17 to v18 migration for security is relatively smooth. Most changes are new features/improvements rather than breaking changes.

## Recommended Migrations

### 1. Multi-Company Record Rules

**v17 Pattern:**
```xml
<record id="rule_model_company" model="ir.rule">
    <field name="name">Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

**v18 Pattern:**
```xml
<record id="rule_model_company" model="ir.rule">
    <field name="name">Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', allowed_company_ids)
    ]</field>
</record>
```

**Migration Script:**
```python
# Find and replace in XML files
# company_ids → allowed_company_ids (in record rule domains)
```

### 2. Model Company Validation

**v17 Pattern:**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        domain="[('company_id', 'in', [company_id, False])]",
    )

    @api.constrains('partner_id', 'company_id')
    def _check_company(self):
        for record in self:
            if record.partner_id.company_id and record.partner_id.company_id != record.company_id:
                raise ValidationError(_("Partner company mismatch"))
```

**v18 Pattern:**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True  # NEW in v18

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # NEW in v18 - replaces manual constraint
    )
    # No need for manual _check_company constraint
```

**Migration Steps:**
1. Add `_check_company_auto = True` to model class
2. Add `check_company=True` to relational fields
3. Remove manual `_check_company` constraint methods
4. Remove company domain filters (optional, `check_company` handles it)

### 3. Type Hints on Fields

**v17 Pattern:**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner')
    line_ids = fields.One2many('my.model.line', 'parent_id')
    amount = fields.Float()
```

**v18 Pattern:**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name: str = fields.Char(required=True)
    partner_id: int = fields.Many2one('res.partner')
    line_ids: list = fields.One2many('my.model.line', 'parent_id')
    amount: float = fields.Float()
```

**Migration Steps:**
1. Add type hints to all relational fields: `partner_id: int = fields.Many2one(...)`
2. Optionally add to scalar fields: `name: str = fields.Char(...)`

### 4. SQL Builder for Raw Queries

**v17 Pattern:**
```python
def _get_data(self):
    self.env.cr.execute(
        """
        SELECT id, name FROM my_table
        WHERE company_id = %s AND active = %s
        """,
        [self.env.company.id, True]
    )
    return self.env.cr.dictfetchall()
```

**v18 Pattern:**
```python
from odoo.tools import SQL

def _get_data(self):
    query = SQL(
        """
        SELECT id, name FROM %(table)s
        WHERE company_id = %(company_id)s AND active = %(active)s
        """,
        table=SQL.identifier('my_table'),
        company_id=self.env.company.id,
        active=True,
    )
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()
```

**Migration Steps:**
1. Import `SQL` from `odoo.tools`
2. Convert parameterized queries to `SQL()` builder
3. Use `SQL.identifier()` for table/column names

## No Change Required

The following remain the same between v17 and v18:

### Security Groups
```xml
<!-- Same syntax in v17 and v18 -->
<record id="group_custom_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="module_category_custom"/>
</record>
```

### Access Rights (ir.model.access.csv)
```csv
# Same format in v17 and v18
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model.user,model_my_model,my_module.group_user,1,1,1,0
```

### View Security Syntax
```xml
<!-- Same syntax in v17 and v18 -->
<field name="secret" invisible="not user_has_groups('my_module.group_manager')"/>
<button name="action" invisible="state != 'draft'" groups="my_module.group_manager"/>
```

### Field Groups
```python
# Same syntax in v17 and v18
internal_notes = fields.Text(groups='my_module.group_manager')
```

## Migration Checklist

- [ ] Update record rules: `company_ids` → `allowed_company_ids`
- [ ] Add `_check_company_auto = True` to multi-company models
- [ ] Add `check_company=True` to relational fields
- [ ] Remove manual company validation constraints
- [ ] Add type hints to relational fields (recommended)
- [ ] Convert raw SQL to `SQL()` builder (recommended)
- [ ] Test all security rules with different user roles
- [ ] Verify multi-company access works correctly

## Testing After Migration

```python
# Test company validation
def test_company_check(self):
    """Test that _check_company_auto works."""
    company_a = self.env['res.company'].create({'name': 'Company A'})
    company_b = self.env['res.company'].create({'name': 'Company B'})

    partner_a = self.env['res.partner'].create({
        'name': 'Partner A',
        'company_id': company_a.id,
    })

    # This should raise ValidationError with check_company=True
    with self.assertRaises(ValidationError):
        self.env['my.model'].create({
            'name': 'Test',
            'company_id': company_b.id,
            'partner_id': partner_a.id,  # Wrong company
        })
```

## Rollback Considerations

If you need to support both v17 and v18:

```python
# Dual-version compatible code
class MyModel(models.Model):
    _name = 'my.model'

    # _check_company_auto is ignored in v17, works in v18
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)

    # check_company is ignored in v17, works in v18
    partner_id = fields.Many2one('res.partner', check_company=True)

    # Keep manual constraint for v17 compatibility
    @api.constrains('partner_id', 'company_id')
    def _check_company_compat(self):
        # This runs in both versions, but v18 also has automatic check
        for record in self:
            if record.partner_id.company_id:
                if record.partner_id.company_id != record.company_id:
                    raise ValidationError(_("Company mismatch"))
```

## GitHub Reference

Check these files in the Odoo repository for v18 patterns:

- `odoo/models.py` - `_check_company_auto` implementation
- `odoo/fields.py` - `check_company` parameter
- `odoo/tools/sql.py` - `SQL` builder class
- `addons/base/models/ir_rule.py` - `allowed_company_ids` usage
