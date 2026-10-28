# Odoo Model Patterns - Version 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 18.0 MODEL PATTERNS                                                    ║
║  This file contains ONLY Odoo 18.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 18.0 Requirements

- **Python**: 3.10+ required, 3.12 recommended
- **Type Hints**: Optional (not enforced in v18 or v19)
- **SQL Builder**: Use `SQL()` for raw SQL (plain `cr.execute(str, params)` still works)
- **Company Check**: Use `_check_company_auto = True`
- **Decorators**: `@api.model_create_multi` + `def create(self, vals_list)` (`@api.model` on create still works but emits a DeprecationWarning); callers may still pass a single dict

## Model Definition (v18)

```python
# -*- coding: utf-8 -*-
from typing import Optional
from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL


class MyModel(models.Model):
    _name = 'my_module.my_model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # v18: Enable automatic company check
    _check_company_auto = True

    # === BASIC FIELDS === #
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(string='Description')

    # === RELATIONAL FIELDS === #
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        tracking=True,
        check_company=True,  # v18: Check company consistency
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True,
    )
    line_ids = fields.One2many(
        comodel_name='my_module.my_model.line',
        inverse_name='parent_id',
        string='Lines',
        copy=True,
    )
    tag_ids = fields.Many2many(
        comodel_name='my_module.tag',
        string='Tags',
    )

    # === SELECTION FIELDS === #
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )

    # === MONETARY FIELDS === #
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
    )

    # === COMPUTED FIELDS === #
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
    )
    display_name = fields.Char(
        compute='_compute_display_name',
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self) -> None:
        """Compute total from lines."""
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    @api.depends('name', 'sequence')
    def _compute_display_name(self) -> None:
        """Compute display name."""
        for record in self:
            record.display_name = f"[{record.sequence}] {record.name or ''}"

    # === CONSTRAINTS === #
    # Invariants belong in @api.constrains or _sql_constraints; @api.onchange is UI-only.
    # 18.0: models.Constraint does not exist, use _sql_constraints.
    @api.constrains('amount')
    def _check_amount(self) -> None:
        """Validate amount is positive."""
        for record in self:
            if record.amount < 0:
                raise ValidationError(_("Amount must be positive."))

    _sql_constraints = [
        ('name_uniq', 'unique(company_id, name)', 'Name must be unique per company!'),
    ]

    # === CRUD METHODS === #
    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> 'MyModel':
        """Override create to add sequence."""
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'my_module.my_model'
                ) or _('New')
        return super().create(vals_list)

    def write(self, vals: dict) -> bool:
        """Override write with validation."""
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if not record.line_ids:
                    raise UserError(_("Cannot complete without lines."))
        return super().write(vals)

    def unlink(self) -> bool:
        """Prevent deletion of confirmed records."""
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_("Cannot delete confirmed records."))
        return super().unlink()

    def copy_data(self, default: Optional[dict] = None) -> list[dict]:
        """Custom copy with name suffix.

        v18: copy() works on multi-record sets and calls copy_data(), which
        returns one vals dict per record - override copy_data, not copy.
        """
        vals_list = super().copy_data(default=default)
        if default and 'name' in default:
            return vals_list
        return [
            dict(vals, name=self.env._("%s (Copy)", record.name))
            for record, vals in zip(self, vals_list)
        ]

    # === x2many OPERATIONS - Use Command class === #
    def action_add_line(self) -> None:
        """Add a new line using Command."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New Line', 'amount': 0}),
            ]
        })

    def action_update_lines(self) -> None:
        """Command class operations reference."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New'}),         # 0: Create new
                Command.update(1, {'name': 'Updated'}),  # 1: Update existing
                Command.delete(2),                       # 2: Delete from DB
                Command.unlink(3),                       # 3: Remove relation
                Command.link(4),                         # 4: Link existing
                Command.clear(),                         # 5: Clear all
                Command.set([5, 6, 7]),                  # 6: Replace with IDs
            ]
        })

    # === ACTION METHODS === #
    def action_confirm(self) -> None:
        """Confirm records."""
        self.write({'state': 'confirmed'})

    def action_done(self) -> None:
        """Mark as done."""
        self.write({'state': 'done'})

    def action_cancel(self) -> None:
        """Cancel records."""
        self.write({'state': 'cancelled'})

    def action_draft(self) -> None:
        """Reset to draft."""
        self.write({'state': 'draft'})

    # === SEARCH METHODS === #
    # v18: name_search() searches on display_name; customize the search with
    # _rec_names_search or by overriding _search_display_name(operator, value).
    _rec_names_search = ['name', 'description']

    # === SQL OPERATIONS (v18 pattern) === #
    def _get_report_data(self) -> list[dict]:
        """Use SQL builder for complex queries."""
        query = SQL(
            """
            SELECT
                m.id,
                m.name,
                m.state,
                SUM(l.amount) as total
            FROM %s m
            LEFT JOIN %s l ON l.parent_id = m.id
            WHERE m.company_id IN %s
            GROUP BY m.id, m.name, m.state
            ORDER BY m.create_date DESC
            """,
            SQL.identifier(self._table),
            SQL.identifier('my_module_my_model_line'),
            tuple(self.env.companies.ids),
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    # === ONCHANGE METHODS === #
    @api.onchange('partner_id')
    def _onchange_partner_id(self) -> None:
        """Update user when partner changes."""
        if self.partner_id and self.partner_id.user_id:
            self.user_id = self.partner_id.user_id
```

## Line Model (v18)

```python
class MyModelLine(models.Model):
    _name = 'my_module.my_model.line'
    _description = 'My Model Line'
    _order = 'sequence, id'

    _check_company_auto = True

    parent_id = fields.Many2one(
        comodel_name='my_module.my_model',
        string='Parent',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        related='parent_id.company_id',
        store=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Description', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        check_company=True,
    )
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    amount = fields.Float(
        string='Amount',
        compute='_compute_amount',
        store=True,
    )

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self) -> None:
        for line in self:
            line.amount = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self) -> None:
        if self.product_id:
            self.name = self.product_id.display_name
            self.price_unit = self.product_id.lst_price
```

## Inheritance Patterns (v18)

### Classical Inheritance (Extension)

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_field = fields.Char(string='Custom Field')
    my_model_ids = fields.One2many(
        comodel_name='my_module.my_model',
        inverse_name='partner_id',
        string='Related Records',
    )

    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> 'ResPartner':
        """Extend create with custom logic."""
        records = super().create(vals_list)
        for record in records:
            if record.custom_field:
                record._process_custom_field()
        return records

    def _process_custom_field(self) -> None:
        """Custom processing logic."""
        pass
```

### Delegation Inheritance

`_inherits` delegates fields (as related fields), not methods.

```python
class ExtendedModel(models.Model):
    _name = 'my_module.extended_model'
    _inherits = {'my_module.my_model': 'base_id'}
    _description = 'Extended Model'

    base_id = fields.Many2one(
        comodel_name='my_module.my_model',
        required=True,
        ondelete='cascade',
        auto_join=True,
    )
    extra_field = fields.Char(string='Extra Field')
```

### Abstract Model (Mixin)

```python
class ApprovalMixin(models.AbstractModel):
    _name = 'my_module.approval.mixin'
    _description = 'Approval Mixin'

    approval_state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
        tracking=True,
    )
    approved_by = fields.Many2one(
        comodel_name='res.users',
        string='Approved By',
    )
    approval_date = fields.Datetime(string='Approval Date')

    def action_approve(self) -> None:
        self.write({
            'approval_state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })

    def action_reject(self) -> None:
        self.write({
            'approval_state': 'rejected',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })
```

## Transient Model (Wizard) - v18

```python
class MyWizard(models.TransientModel):
    _name = 'my_module.wizard'
    _description = 'My Wizard'

    def _default_record_ids(self) -> 'MyModel':
        return self.env['my_module.my_model'].browse(
            self._context.get('active_ids', [])
        )

    record_ids = fields.Many2many(
        comodel_name='my_module.my_model',
        string='Records',
        default=_default_record_ids,
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
    )
    note = fields.Text(string='Note')

    def action_confirm(self) -> dict:
        """Execute wizard action."""
        self.ensure_one()
        self.record_ids.write({
            'state': 'confirmed',
        })
        return {'type': 'ir.actions.act_window_close'}

    def action_confirm_and_view(self) -> dict:
        """Execute and return action to view records."""
        self.action_confirm()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'my_module.my_model',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.record_ids.ids)],
            'target': 'current',
        }
```

## v18 Specific Features

### Type Hints (Recommended)

```python
from typing import Optional, Any

def custom_method(
    self,
    partner_id: int,
    options: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    """Method with type hints."""
    options = options or {}
    # ...
    return []
```

### SQL Builder Pattern

```python
from odoo.tools import SQL

def _execute_query(self) -> list[dict]:
    """Use SQL() for safe query building."""
    query = SQL(
        """
        SELECT id, name, amount
        FROM %s
        WHERE company_id = %s
          AND state = %s
        ORDER BY %s
        """,
        SQL.identifier(self._table),
        self.env.company.id,
        'confirmed',
        SQL('create_date DESC'),
    )
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()
```

### Company Check Auto

```python
class MyModel(models.Model):
    _name = 'my_module.my_model'
    _check_company_auto = True  # v18: Enable automatic checks

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # Will be auto-validated
    )
```

## v18 Decorator Reference

| Decorator | Usage |
|-----------|-------|
| `@api.model` | Class-level method, no recordset |
| `@api.model_create_multi` | Create method (mandatory) |
| `@api.depends(*fields)` | Compute dependency |
| `@api.constrains(*fields)` | Validation constraint |
| `@api.onchange(*fields)` | UI change handler |
| `@api.depends_context(*keys)` | Context-dependent compute |
| `@api.autovacuum` | Scheduled cleanup |

## Additional Rules from Odoo's Official Guidelines (verified for 18.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 18.0 source; master-only APIs are translated to their 18.0 equivalent or marked as not available.

### Batching: one ORM call per collection

No `search`, `search_count`, `_read_group`, `create` or `browse(id)` inside a loop over records. Aggregate with `_read_group(domain, groupby, aggregates)`, which returns a list of tuples (relational group keys come back as recordsets):

```python
# Totals per order in ONE query
totals = dict(self.env['sale.order.line']._read_group(
    [('order_id', 'in', orders.ids)],
    groupby=['order_id'],
    aggregates=['price_subtotal:sum'],
))
for order in orders:
    total = totals.get(order, 0.0)  # keys are sale.order records

# Count per partner
counts = dict(self.env['my_module.my_model']._read_group(
    [('partner_id', 'in', partners.ids)], ['partner_id'], ['__count'],
))
```

`read_group(domain, fields, groupby, ...)` (list of dicts) still exists in 18 for the web client; use `_read_group` in Python code. Put conditions into the domain instead of `filtered()` on large sets, iterate whole recordsets (prefetch) instead of `browse(id)` one by one, and create records in batch: `Model.create([vals1, vals2])`.

### ORM rules in 18.0

| Rule | 18.0 form |
|------|-----------|
| Indexes | field `index=True` (`'btree'`), `'btree_not_null'` (mostly-NULL columns), `'trigram'` (ilike search); only on searched AND selective fields. Multi-column: override `init()` and call `odoo.tools.sql.create_index(self.env.cr, name, self._table, ['col_a', 'col_b'])` |
| Translation | `self.env._("Order %s confirmed", order.name)` or `_("...", arg)`; pass arguments to `_()`, never format before/after the lookup; module level: `_lt = LazyTranslate(__name__)` then `LABEL = _lt("Label")`; lists are not formatted per language in 18 -> `odoo.tools.format_list(self.env, names)` |
| Domains | `from odoo.osv import expression`; `expression.AND([d1, d2])`, `expression.OR([...])`; never hand-build prefix lists |
| Grouping in memory | `records.grouped('partner_id')` -> `{partner: recordset}` (same prefetch set) |
| Context | `with_context(key=...)` (frozendict); prefix custom keys with the module name; a stray `default_<field>` key in the context is applied by every `create` on any model that has that field |
| Related through x2many | `related='line_ids.product_id'` follows only the FIRST line; use a compute for "all lines" |
| Savepoints | `with self.env.cr.savepoint():` around code whose failure must not break the transaction; catch specific exceptions |
| Commit | never `self.env.cr.commit()`/`rollback()` unless you opened the cursor yourself; tests forbid it |
| Reserved fields | `active` (archive with `action_archive()`/`action_unarchive()`), `state`, `parent_id` + `parent_path` (indexed) with `_parent_store = True`, `company_id` with `_check_company_auto` + `check_company=True`; keep `_log_access` on TransientModel |
| `request` in models | do not use `odoo.http.request` in model code (unbound in crons, RPC, tests, shell) |
| Public methods | prefix internal methods with `_` or decorate with `@api.private`; classmethods are RPC-callable in 18 unless prefixed with `_` |

### Views, reports, QWeb

- Inheritance anchors on names, never on position: `<field name="partner_id" position="after">` matches the first `field` with that name at any depth; other tags match the first node carrying all the given attributes; use `xpath` when that is ambiguous.
- Inheriting view: same xml id prefix, name `<model>.view.<type>.inherit.<detail>`; `mode="primary"` for a separate variant; do not re-add fields that the parent already shows.
- `t-lang` is only valid on a node with `t-call`; anywhere else the template compile raises `SyntaxError`.
- A custom report model `report.<report_name>` must return `doc_ids`, `doc_model` and `docs` itself from `_get_report_values(docids, data)`; the defaults are only added when no such model exists:

```python
class ReportMyModel(models.AbstractModel):
    _name = 'report.my_module.report_my_model'
    _description = 'My Model Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['my_module.my_model'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'my_module.my_model',
            'docs': docs,
            'totals': dict(self.env['my_module.my_model.line']._read_group(
                [('parent_id', 'in', docs.ids)], ['parent_id'], ['amount:sum'],
            )),
        }
```

## v18 Checklist

- [ ] Use `_check_company_auto = True` for multi-company models
- [ ] Add `check_company=True` to relational fields
- [ ] Use `@api.model_create_multi` for create methods
- [ ] Use `SQL()` builder for raw SQL queries
- [ ] No ORM calls inside loops (`_read_group` for aggregates)
- [ ] Use `Command` class for x2many operations
- [ ] Use direct `invisible`/`readonly` in views (not `attrs`)

## AI Agent Instructions (v18)

When generating Odoo 18.0 models:

1. **ALWAYS** use `_check_company_auto = True` for multi-company
2. **ALWAYS** use `@api.model_create_multi` for create
3. **USE** `check_company=True` on relational fields
4. **USE** `SQL()` builder for raw SQL
5. **ADD** type hints where they help readability (optional)
6. **USE** `Command` class for x2many operations
7. **USE** `tracking=True` for audited fields
