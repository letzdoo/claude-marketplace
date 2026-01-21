# Odoo Version Knowledge - Version 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 18.0 VERSION KNOWLEDGE                                                 ║
║  Release: October 2024                                                       ║
║  Python: 3.11+ required, 3.12 recommended                                    ║
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
Automatic company consistency validation:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # NEW in v18

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

### Type Hints (Recommended)
```python
def calculate_total(self, include_tax: bool = True) -> float:
    return sum(self.mapped('amount'))
```

### allowed_company_ids in Record Rules
```xml
<field name="domain_force">[
    ('company_id', 'in', allowed_company_ids)
]</field>
```

## Deprecations in v18

| Feature | Status | Replacement | Deadline |
|---------|--------|-------------|----------|
| Raw SQL strings | Deprecated | `SQL()` builder | v19 |
| Methods without type hints | Deprecated | Add type hints | v19 |
| `company_ids` in rules | Deprecated | `allowed_company_ids` | - |

## v18 Required Patterns

### Model Definition
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True  # Required for multi-company

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
    <field name="global" eval="True"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', allowed_company_ids)
    ]</field>
</record>
```

## v18 OWL Patterns

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
        'view_mode': 'tree,form',
        'domain': [('partner_id', '=', self.partner_id.id)],
    }
```

## v18 Checklist

When developing for Odoo 18.0:

- [ ] Use `_check_company_auto = True` for multi-company models
- [ ] Add `check_company=True` to cross-company relational fields
- [ ] Use `SQL()` builder for raw SQL queries
- [ ] Add type hints to method signatures
- [ ] Use `@api.model_create_multi` for create methods
- [ ] Use direct `invisible`/`readonly` in views
- [ ] Use `allowed_company_ids` in record rules
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
