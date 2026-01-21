# Odoo Version Knowledge: 17 to 18 Migration

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  VERSION MIGRATION: 17.0 → 18.0                                              ║
║  Critical changes, breaking changes, and migration patterns                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Category | Change | Impact |
|----------|--------|--------|
| Multi-Company | `_check_company_auto` recommended | High - Review all models |
| Relations | `check_company=True` recommended | High - Update Many2one fields |
| SQL | `SQL()` builder recommended | Medium - Update raw queries |
| Type Hints | Recommended for methods | Low - Add gradually |
| Security | Enhanced company isolation | Medium - Review rules |

## Multi-Company Framework

### The Big Change
v18 introduces stricter multi-company validation with automatic checking.

### Before (v17)
```python
class MyModel(models.Model):
    _name = 'my.model'

    company_id = fields.Many2one('res.company')
    partner_id = fields.Many2one('res.partner')

    # Manual company validation
    @api.constrains('partner_id', 'company_id')
    def _check_company(self):
        for record in self:
            if record.partner_id.company_id and \
               record.partner_id.company_id != record.company_id:
                raise ValidationError("Partner company mismatch!")
```

### After (v18)
```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # Enable automatic checking

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
    # No manual constraint needed - automatic validation
```

### _check_company_auto Behavior
```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # Validates on write()

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )

    # All these fields will be checked against company_id
    partner_id = fields.Many2one('res.partner', check_company=True)
    warehouse_id = fields.Many2one('stock.warehouse', check_company=True)
    account_id = fields.Many2one('account.account', check_company=True)
```

## Record Rules: allowed_company_ids

### v18 Record Rule Pattern
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        ('company_id', 'in', allowed_company_ids)
    ]</field>
</record>
```

### Multi-Company Field Pattern
```python
# Required pattern for v18 multi-company models
company_id = fields.Many2one(
    'res.company',
    string='Company',
    required=True,
    readonly=True,
    default=lambda self: self.env.company,
    index=True,
)
```

## SQL() Builder Introduction

### Before (v17)
```python
# String SQL - works but discouraged
self.env.cr.execute("""
    SELECT id, name, amount
    FROM my_model
    WHERE state = %s AND company_id = %s
    ORDER BY date DESC
    LIMIT %s
""", ('confirmed', self.env.company.id, 100))
```

### After (v18) - Recommended
```python
from odoo.tools import SQL

# SQL() builder - recommended
self.env.cr.execute(SQL(
    """
    SELECT id, name, amount
    FROM my_model
    WHERE state = %s AND company_id = %s
    ORDER BY date DESC
    LIMIT %s
    """,
    'confirmed', self.env.company.id, 100
))

# With named placeholders
self.env.cr.execute(SQL(
    """
    UPDATE my_model
    SET state = %(state)s, write_date = %(now)s
    WHERE id IN %(ids)s
    """,
    state='done',
    now=fields.Datetime.now(),
    ids=tuple(self.ids)
))
```

### SQL Builder Features
```python
from odoo.tools import SQL

# Composable queries
base_query = SQL("SELECT * FROM my_model WHERE active = %s", True)
filtered_query = SQL(
    "%s AND company_id = %s",
    base_query, self.env.company.id
)

# Safe table/column names
table = SQL.identifier('my_model')
column = SQL.identifier('state')
query = SQL("SELECT %s FROM %s", column, table)
```

## Type Hints (Recommended)

### v18 Recommended Style
```python
from typing import Optional
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True

    name: str = fields.Char(required=True)
    active: bool = fields.Boolean(default=True)
    amount: float = fields.Float()
    company_id = fields.Many2one('res.company', required=True)

    def action_confirm(self) -> bool:
        """Confirm the record."""
        for record in self:
            record.state = 'confirmed'
        return True

    def action_get_partner(self) -> Optional['res.partner']:
        """Get related partner or None."""
        self.ensure_one()
        return self.partner_id or None

    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> 'MyModel':
        return super().create(vals_list)
```

## Enhanced Indexing

### Trigram Index for Search
```python
# v18 improved index types
name = fields.Char(index='trigram')  # For ILIKE searches
code = fields.Char(index='btree_not_null')  # Exclude NULLs
date = fields.Date(index=True)  # Standard btree
```

## OWL 2.x Improvements

### Service Usage Pattern
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class MyComponent extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ records: [], loading: true });

        onWillStart(async () => {
            await this.loadRecords();
        });
    }

    async loadRecords() {
        try {
            const records = await this.orm.searchRead(
                "my.model",
                [["company_id", "in", this.env.companyIds]],  // v18 pattern
                ["name", "state"]
            );
            this.state.records = records;
        } catch (error) {
            this.notification.add("Error loading records", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }
}
```

## GitHub Verification URLs

```
# Multi-company changes
https://raw.githubusercontent.com/odoo/odoo/18.0/odoo/models.py
# Search for _check_company_auto

# SQL builder
https://raw.githubusercontent.com/odoo/odoo/18.0/odoo/tools/sql.py

# Sale order (reference implementation)
https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order.py
```

## Migration Checklist

- [ ] Add `_check_company_auto = True` to multi-company models
- [ ] Add `check_company=True` to relational fields
- [ ] Update record rules to use `allowed_company_ids`
- [ ] Start migrating raw SQL to `SQL()` builder
- [ ] Add type hints to new/modified methods
- [ ] Review and test multi-company scenarios
- [ ] Update index definitions for search fields

## Common Migration Errors

### Error: `ValidationError: check_company failed`
**Fix**: Ensure related records belong to same company or add `check_company=True`

### Warning: `String SQL queries are discouraged`
**Fix**: Migrate to `SQL()` builder: `from odoo.tools import SQL`

### Error: Company isolation violations
**Fix**: Add proper `_check_company_auto` and update record rules

## Multi-Company Testing

```python
def test_multi_company_isolation(self):
    """Test company isolation in v18"""
    company2 = self.env['res.company'].create({'name': 'Company 2'})

    # Create user in company2
    user_c2 = self.env['res.users'].create({
        'name': 'User C2',
        'login': 'user_c2',
        'company_id': company2.id,
        'company_ids': [(6, 0, [company2.id])],
    })

    # Record in main company
    record = self.env['my.model'].create({
        'name': 'Test',
        'company_id': self.env.company.id,
    })

    # User in company2 should NOT see it
    visible = self.env['my.model'].with_user(user_c2).search([])
    self.assertNotIn(record.id, visible.ids)
```

## Comparison: v17 vs v18 Model

```python
# v17 Style
class MyModelV17(models.Model):
    _name = 'my.model'

    company_id = fields.Many2one('res.company')
    partner_id = fields.Many2one('res.partner')

    @api.constrains('partner_id')
    def _check_company(self):
        for record in self:
            if record.partner_id.company_id:
                if record.partner_id.company_id != record.company_id:
                    raise ValidationError("Company mismatch")


# v18 Style
class MyModelV18(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
    # No manual constraint - handled automatically
```
