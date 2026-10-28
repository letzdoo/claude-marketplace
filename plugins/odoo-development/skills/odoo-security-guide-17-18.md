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
| Multi-company rules | `company_ids` | `company_ids` (unchanged; `allowed_company_ids` is not in the rule eval context) | No |
| Company check | `_check_company_auto` available | same | No (optional clean-up) |
| Field company | `check_company=True` available | same | No (optional clean-up) |
| Access check API | `check_access_rights()`/`check_access_rule()` | deprecated -> `check_access()`/`has_access()` | Recommended |
| Type hints | Optional | Recommended | Optional |
| SQL queries | `SQL()` builder available | same | No (optional clean-up) |
| View syntax | Direct attributes | Direct attributes | No change |

## Breaking Changes

### None - v17 to v18 is mostly additive

The v17 to v18 migration for security is relatively smooth. Most changes are new features/improvements rather than breaking changes.

## Recommended Migrations

### 1. Multi-Company Record Rules (no change)

The rule eval context is `user`, `time`, `company_ids`, `company_id` in both v17 and v18. Do NOT replace `company_ids` with `allowed_company_ids`: it is not defined in rule domains and the rule fails validation on install.

**v17 and v18 Pattern:**
```xml
<record id="rule_model_company" model="ir.rule">
    <field name="name">Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <!-- No groups => global rule ('global' is computed, do not set it) -->
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

### 2. Model Company Validation (available in both versions)

`_check_company_auto` and `check_company=True` already exist in v17; this is an optional clean-up.

**Manual pattern:**
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

    # Do not name it _check_company: that overrides BaseModel._check_company
    @api.constrains('partner_id', 'company_id')
    def _check_partner_company(self):
        for record in self:
            if record.partner_id.company_id and record.partner_id.company_id != record.company_id:
                raise ValidationError(_("Partner company mismatch"))
```

**Automatic pattern (v17 and v18):**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True  # available since before v17

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # replaces the manual constraint (v17 and v18)
    )
    # No need for manual _check_company constraint
```

**Migration Steps:**
1. Add `_check_company_auto = True` to model class
2. Add `check_company=True` to relational fields
3. Remove the manual company constraint methods
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

### 4. SQL Builder for Raw Queries (available in both versions)

**Plain parameterized pattern (safe in v17 and v18):**
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

**SQL builder pattern (v17 and v18):**
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
<field name="secret" groups="my_module.group_manager"/>
<button name="action" invisible="state != 'draft'" groups="my_module.group_manager"/>
```

### Field Groups
```python
# Same syntax in v17 and v18
internal_notes = fields.Text(groups='my_module.group_manager')
```

## Official guideline deltas 17.0 -> 18.0

Only the official-guideline security rules (Odoo `skills/`, verified against both sources) that change between the two versions:

| Topic | 17.0 | 18.0 |
|-------|------|------|
| Route `auth` values | `user`, `public`, `none` | adds `bearer` (no `bearer_scope`) |
| Restricted `odoo.tools.misc.pickle` | exists (still prefer JSON) | removed |
| JS HTML helpers | `htmlEscape`/`markup` from `@odoo/owl`, `escape` from `@web/core/utils/strings` | adds `@web/core/utils/html` (`htmlEscape`, `isHtmlEmpty`, `setElementContent`) |

Unchanged in both: `sudo(flag)`/`with_user`, `_allow_sudo_commands`, `related_sudo=True` default, `odoo.osv.expression.AND/OR`, RPC guard (`_` prefix, `@api.private`), route types `http`/`json` and CSRF behaviour, QWeb `t-out` (`t-esc` alias, `t-raw` deprecated), `fields.NO_ACCESS`, `file_open` confinement, `consteq`, `ir.model.access` + `ir.rule` semantics, no `base.group_everyone`. (SQL builder and rule eval context: see Overview and section 1.)

## Migration Checklist

- [ ] Keep record rules on `company_ids` (never `allowed_company_ids`)
- [ ] Replace `check_access_rights()`/`check_access_rule()` with `check_access()`/`has_access()`
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

    # _check_company_auto and check_company work the same in v17 and v18
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
    # No manual constraint needed for v17 compatibility
```

## GitHub Reference

Check these files in the Odoo repository for v18 patterns:

- `odoo/models.py` - `_check_company_auto` implementation
- `odoo/fields.py` - `check_company` parameter
- `odoo/tools/sql.py` - `SQL` builder class
- `odoo/addons/base/models/ir_rule.py` - `_eval_context()` (user, time, company_ids, company_id)
