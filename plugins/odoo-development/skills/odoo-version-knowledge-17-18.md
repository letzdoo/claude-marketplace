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
| Controllers | `request.not_found()` must be **raised**, not returned | **High** - Update all controllers |
| Multi-Company | `_check_company_auto` recommended (already available in v17, not new) | Low - optional clean-up |
| Relations | `check_company=True` recommended (already available in v17) | Low - optional clean-up |
| SQL | `SQL()` builder recommended (already available in v17) | Low - optional clean-up |
| Access checks | `check_access_rights()`/`check_access_rule()` deprecated -> `check_access()`/`has_access()` | Medium |
| Type Hints | Recommended for methods | Low - Add gradually |
| Security | Enhanced company isolation | Medium - Review rules |

## Multi-Company Framework

### Note
`_check_company_auto` and `check_company=True` exist in both v17 and v18; replacing manual constraints is a clean-up you can do in either version.

### Before (manual constraint)
```python
class MyModel(models.Model):
    _name = 'my.model'

    company_id = fields.Many2one('res.company')
    partner_id = fields.Many2one('res.partner')

    # Manual company validation (do not name it _check_company:
    # that would override BaseModel._check_company)
    @api.constrains('partner_id', 'company_id')
    def _check_partner_company(self):
        for record in self:
            if record.partner_id.company_id and \
               record.partner_id.company_id != record.company_id:
                raise ValidationError("Partner company mismatch!")
```

### After (automatic, v17 and v18)
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

## HTTP Controllers: request.not_found() Must Be Raised

### The Breaking Change
In Odoo 18, `request.not_found()` changed from **returning** a response to **raising** an exception. This is a critical breaking change affecting all HTTP controllers.

### Before (v17 and earlier)
```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    @http.route('/my_module/record/<int:record_id>', type='http', auth='user')
    def get_record(self, record_id):
        """Get record by ID."""
        record = request.env['my.model'].browse(record_id)
        if not record.exists():
            return request.not_found()  # RETURN in v17

        return request.render('my_module.record_detail', {
            'record': record,
        })
```

### After (v18)
```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    @http.route('/my_module/record/<int:record_id>', type='http', auth='user')
    def get_record(self, record_id):
        """Get record by ID."""
        record = request.env['my.model'].browse(record_id)
        if not record.exists():
            raise request.not_found()  # RAISE in v18

        return request.render('my_module.record_detail', {
            'record': record,
        })
```

### Migration Pattern

```python
# WRONG in v18 - This will cause errors
if not record.exists():
    return request.not_found()

# CORRECT in v18 - Must raise the exception
if not record.exists():
    raise request.not_found()
```

### API Endpoints Pattern
```python
class APIController(http.Controller):

    @http.route('/api/v1/records/<int:id>', type='http', auth='user',
                methods=['GET'], csrf=False)
    def get_record(self, id):
        """REST API endpoint with proper error handling."""
        record = request.env['my.model'].browse(id)
        if not record.exists():
            raise request.not_found()  # v18: Must raise

        return request.make_response(
            json.dumps({
                'status': 'success',
                'data': {
                    'id': record.id,
                    'name': record.name,
                },
            }),
            headers=[('Content-Type', 'application/json')]
        )
```

### Website Controllers Pattern
```python
class WebsiteController(http.Controller):

    @http.route('/shop/product/<int:product_id>', type='http',
                auth='public', website=True)
    def product_detail(self, product_id, **kw):
        """Website product page."""
        product = request.env['product.template'].browse(product_id)
        if not product.exists() or not product.website_published:
            raise request.not_found()  # v18: Must raise

        return request.render('website_sale.product', {
            'product': product,
        })
```

### File Download Pattern
```python
@http.route('/download/file/<int:attachment_id>', type='http', auth='user')
def download_file(self, attachment_id):
    """Download file with proper error handling."""
    attachment = request.env['ir.attachment'].browse(attachment_id)
    if not attachment.exists():
        raise request.not_found()  # v18: Must raise

    return request.make_response(
        base64.b64decode(attachment.datas),
        headers=[
            ('Content-Type', attachment.mimetype or 'application/octet-stream'),
            ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
        ]
    )
```

### Why This Change?

This change aligns with Python exception handling best practices:
- Exceptions for exceptional conditions (404 is an exceptional flow)
- Clearer control flow - no need to check return values
- Better error propagation through the request handling stack
- Consistent with other Odoo exception patterns

## Record Rules: company_ids (unchanged)

The record rule eval context is the same in v17 and v18: `user`, `time`, `company_ids`, `company_id`. `allowed_company_ids` is NOT defined there; a rule using it fails validation.

### v17 / v18 Record Rule Pattern
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        ('company_id', 'in', company_ids)
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

## SQL() Builder (available since v17)

### Before (string SQL)
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

### After (v17 and v18) - Recommended
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

## Official guideline deltas 17.0 -> 18.0

Only the official-guideline rules (Odoo `skills/`, verified against both sources) that change between the two versions:

| Topic | 17.0 | 18.0 |
|-------|------|------|
| Route `auth` values | `user`, `public`, `none` | adds `bearer` (no `bearer_scope`) |
| Single-dict `@api.model` create | logs a WARNING | DeprecationWarning |
| Translation API | `_()` frame-based, `_lt` | adds `self.env._` and `LazyTranslate` (`_`/`_lt` still work) |
| Restricted `odoo.tools.misc.pickle` | exists | removed |
| JS HTML helpers | `htmlEscape`/`markup` (`@odoo/owl`), `escape` (`@web/core/utils/strings`) | adds `@web/core/utils/html` (`htmlEscape`, `isHtmlEmpty`, `setElementContent`) |
| Imported TestCase class in a test file | collected again (runs twice) | skipped |
| Inherited `test_*` methods | collected | not collected unless `allow_inherited_tests_method = True` |
| `SavepointCase` | removed (already gone in 17.0) | removed (use `TransactionCase`) |

Unchanged (despite claims elsewhere; for rule eval context, `SQL` and `_check_company_auto`/`check_company` see the sections above): `_read_group(domain, groupby, aggregates)`, `_sql_constraints`, route types `http`/`json`, QWeb `t-out` (`t-esc` alias, `t-raw` deprecated), default test tags `{'standard', 'at_install'}`, Owl without `computed`, `patch(obj, ext)`.

## Migration Checklist

- [ ] **CRITICAL**: Change all `return request.not_found()` to `raise request.not_found()`
- [ ] Add `_check_company_auto = True` to multi-company models (optional, already possible in v17)
- [ ] Add `check_company=True` to relational fields (optional, already possible in v17)
- [ ] Keep record rules on `company_ids` (do NOT use `allowed_company_ids`)
- [ ] Replace `check_access_rights()`/`check_access_rule()` with `check_access()`/`has_access()`
- [ ] Start migrating raw SQL to `SQL()` builder
- [ ] Add type hints to new/modified methods
- [ ] Review and test multi-company scenarios
- [ ] Update index definitions for search fields

## Common Migration Errors

### Error: Controller returns None or unexpected response
**Symptom**: Controllers that previously worked now return empty responses or cause errors
**Fix**: Change `return request.not_found()` to `raise request.not_found()`

```python
# WRONG - v17 pattern that breaks in v18
if not record.exists():
    return request.not_found()

# CORRECT - v18 pattern
if not record.exists():
    raise request.not_found()
```

### Error: `ValidationError: check_company failed`
**Fix**: Ensure related records belong to same company or add `check_company=True`

### Warning: `String SQL queries are discouraged`
**Fix**: Migrate to `SQL()` builder: `from odoo.tools import SQL`

### Error: Company isolation violations
**Fix**: Add proper `_check_company_auto` and check that record rules use `company_ids`

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
# Manual style (works in v17 and v18)
class MyModelManual(models.Model):
    _name = 'my.model'

    company_id = fields.Many2one('res.company')
    partner_id = fields.Many2one('res.partner')

    @api.constrains('partner_id')
    def _check_partner_company(self):
        for record in self:
            if record.partner_id.company_id:
                if record.partner_id.company_id != record.company_id:
                    raise ValidationError("Company mismatch")


# Automatic style (available in v17 and v18)
class MyModelAuto(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
    # No manual constraint - handled automatically
```
