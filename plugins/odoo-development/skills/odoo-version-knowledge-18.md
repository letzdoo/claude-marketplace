# Odoo Version Knowledge - Version 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 18.0 VERSION KNOWLEDGE                                                 ║
║  Release: October 2024                                                       ║
║  Python: 3.10+ required, 3.12 recommended                                    ║
║  OWL: 2.x (enhanced)                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 18.0 Overview

Odoo 18.0 is a refinement release focusing on:
- Multi-company improvements with automatic validation
- SQL security enhancements with SQL() builder
- Type hint preparation for v19 mandatory adoption
- Performance optimizations

## New Features in v18

### _check_company_auto
Automatic company consistency validation (not new in 18, still the recommended pattern):

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
```

### SQL() Builder
Safe SQL query construction:

```python
from odoo.tools import SQL

query = SQL(
    "SELECT * FROM %s WHERE company_id = %s",
    SQL.identifier(self._table),
    self.env.company.id,
)
```

`_search()` returns a `Query`; select from it with `query.select(SQL(...))`. Same API in master.

### Type Hints (Optional)
```python
def calculate_total(self, include_tax: bool = True) -> float:
    return sum(self.mapped('amount'))
```

### company_ids in Record Rules
Rule domains are evaluated with `user`, `time`, `company_ids` and `company_id`
(`odoo/addons/base/models/ir_rule.py`, `_eval_context`). `allowed_company_ids` is NOT
available there; a rule using it fails at install with "Invalid domain".
```xml
<field name="domain_force">[
    '|', ('company_id', '=', False), ('company_id', 'in', company_ids)
]</field>
```

## Breaking Changes in v18

| Feature | Change | Action Required |
|---------|--------|-----------------|
| `request.not_found()` | Must be **raised**, not returned | Change `return request.not_found()` to `raise request.not_found()` |

### request.not_found() Exception Change
```python
# WRONG in v18 - Do not return
if not record.exists():
    return request.not_found()

# CORRECT in v18 - Must raise
if not record.exists():
    raise request.not_found()
```

## Deprecations in v18

| Feature | Status | Replacement | Deadline |
|---------|--------|-------------|----------|
| Raw SQL strings | Discouraged (still work) | `SQL()` builder | - |
| `check_access_rights()` / `check_access_rule()` / `_filter_access_rules()` | Deprecated (DeprecationWarning) | `check_access()`, `has_access()`, `_filtered_access()` (same in master) | - |
| `@api.model` on `create` | Deprecated (DeprecationWarning) | `@api.model_create_multi` (master converts a single dict silently) | - |
| `group_operator=` field attribute | Deprecated | `aggregator=` | - |
| `_check_recursion()` | Deprecated | `not self._has_cycle()` | - |
| `t-esc` / `t-raw` (server QWeb) | Deprecated (still render: `t-esc` is an escaping alias of `t-out`, `t-raw` renders unescaped; same in master) | `t-out` | - |

## v18 Required Patterns

### Model Definition
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True  # Opt-in company consistency check (available since 14.0)

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
```

### Create Method
```python
@api.model_create_multi
def create(self, vals_list: list[dict]) -> 'MyModel':
    return super().create(vals_list)
```

### View Visibility
```xml
<button name="action_confirm"
        invisible="state != 'draft'"
        readonly="locked"/>
```

## GitHub Verification URLs

Always verify patterns against official source:

| Component | URL |
|-----------|-----|
| Base models | `github.com/odoo/odoo/tree/18.0/odoo/addons/base/models` |
| Web module | `github.com/odoo/odoo/tree/18.0/addons/web` |
| OWL components | `github.com/odoo/odoo/tree/18.0/addons/web/static/src` |
| Mail thread | `github.com/odoo/odoo/tree/18.0/addons/mail/models` |
| Sale module | `github.com/odoo/odoo/tree/18.0/addons/sale/models` |

## v18 Field Patterns

### Standard Fields
```python
name = fields.Char(string='Name', required=True, tracking=True)
active = fields.Boolean(default=True)
sequence = fields.Integer(default=10)
state = fields.Selection([...], default='draft', tracking=True, copy=False)
```

### Relational Fields (Multi-Company)
```python
partner_id = fields.Many2one('res.partner', check_company=True)
product_id = fields.Many2one('product.product', check_company=True)
warehouse_id = fields.Many2one('stock.warehouse', check_company=True)
```

### Monetary Fields
```python
currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
amount = fields.Monetary(currency_field='currency_id')
```

## v18 Security Patterns

Access model: `ir.model.access` + `ir.rule` (master unifies them into `ir.access`, not available in 18).

### Access Rights (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,group_manager,1,1,1,1
```

### Record Rules (Multi-Company)
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-Company</field>
    <field name="model_id" ref="model_my_model"/>
    <!-- no groups = global rule ("global" is computed, do not set it) -->
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

## v18 OWL Patterns

Owl 2.x (master: Owl 3): no `computed`; patching uses `patch(obj, extension)`.

### Component Structure
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = { recordId: { type: Number, optional: true } };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: [], loading: true });
        onWillStart(async () => await this.loadData());
    }

    async loadData() {
        this.state.data = await this.orm.searchRead("my.model", [], ["name"]);
        this.state.loading = false;
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

## Common v18 Patterns

### Computed Fields
```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self) -> None:
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

### Action Methods
```python
def action_confirm(self) -> None:
    self.write({'state': 'confirmed'})

def action_view_records(self) -> dict:
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'my.model',
        'view_mode': 'list,form',  # v18: view type is 'list' (ir.ui.view has no 'tree' type)
        'domain': [('partner_id', '=', self.partner_id.id)],
    }
```

## Additional Rules from Odoo's Official Guidelines (verified for 18.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 18.0 source; master-only APIs are translated to their 18.0 equivalent or marked as not available.

### API availability in 18.0 vs master

| Topic | 18.0 | Master (20.0) |
|-------|------|---------------|
| Combine domains | `odoo.osv.expression.AND/OR/normalize_domain` | `odoo.fields.Domain` (`&`, `|`, `~`) |
| SQL constraints | `_sql_constraints = [(name, sql, message)]` | `models.Constraint(...)`; `_sql_constraints` ignored |
| Multi-column / custom index | `init()` + `odoo.tools.sql.create_index()`; field `index=True/'btree_not_null'/'trigram'` | `models.Index` / `models.UniqueIndex` |
| Aggregation | `_read_group(domain, groupby, aggregates)` -> list of tuples; `read_group()` (dicts) still public | `read_group` deprecated -> `formatted_read_group` |
| Recordset helpers | `filtered`, `mapped`, `sorted`, `grouped`, `filtered_domain` | same |
| RPC guard | blocks `_` names, `@api.private`, unsafe attribute names; classmethods NOT blocked | also blocks classmethods/staticmethods |
| `@api.private` | yes | yes |
| Route `type` | `http`, `json` | `http`, `jsonrpc`, `json2` |
| Route `auth` | `user`, `bearer` (no `bearer_scope`), `public`, `none` | + `bearer_scope` |
| Translation | `self.env._("text %s", arg)`, frame-based `_()`, `_lt = LazyTranslate(__name__)` or `from odoo import _lt`; list args NOT formatted per language (use `odoo.tools.format_list`) | list args formatted per language |
| `t-lang` without `t-call` | SyntaxError | SyntaxError |
| Restricted pickle | removed | removed |
| Manifest | no automatic `base` dependency (declare it); `license` defaults to LGPL-3 with warning; `auto_install` may be a list; `assets` key | `base` injected |
| Tests | default tags `standard` + `at_install`; post-install = `@tagged('post_install', '-at_install')`; `BaseCommon` runs as superuser (no independent user/company) | default `post_install`; independent user/company |
| Web HTML helpers | `htmlEscape`, `setElementContent`, `isHtmlEmpty` (`@web/core/utils/html`); Owl `markup` as escaping tagged template | + `htmlJoin`, `setInnerHtml`, ... |

### Master-only things NOT to use in 18.0

`odoo.fields.Domain`, `models.Constraint` / `models.Index` / `models.UniqueIndex`, `ir.access` / `security/ir.access.csv`, `base.group_everyone`, `bearer_scope=`, route types `jsonrpc` / `json2`, `formatted_read_group`, Owl `computed`, `setInnerHtml` / `htmlJoin`, `populate.blueprint`, `--unsafe-policy`, tour step `expectUnloadPage` (not verified for 18).

## v18 Checklist

When developing for Odoo 18.0:

- [ ] **Use `raise request.not_found()` instead of `return request.not_found()`**
- [ ] Use `_check_company_auto = True` for multi-company models
- [ ] Add `check_company=True` to cross-company relational fields
- [ ] Use `SQL()` builder for raw SQL queries
- [ ] Type hints on method signatures are optional
- [ ] Use `@api.model_create_multi` for create methods
- [ ] Use direct `invisible`/`readonly` in views
- [ ] Use `company_ids` in record rules (not `allowed_company_ids`)
- [ ] Include `tracking=True` for audited fields
- [ ] Use OWL 2.x patterns for frontend

## Preparing for v19

Start adopting these patterns now to ease v19 migration:

1. **Type hints**: Add to all method signatures
2. **SQL() builder**: Use for all raw SQL
3. **Company checks**: Use automatic validation
4. **OWL patterns**: Follow current 2.x best practices

---

**Note**: Always verify patterns against the official Odoo 18.0 source code at `github.com/odoo/odoo/tree/18.0`.
