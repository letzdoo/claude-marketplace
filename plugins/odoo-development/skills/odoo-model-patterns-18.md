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
- **Type Hints**: Recommended (will be mandatory in v19)
- **SQL Builder**: Use `SQL()` for raw SQL (mandatory in v19)
- **Company Check**: Use `_check_company_auto = True`
- **Decorators**: `@api.model_create_multi` mandatory

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

    def copy(self, default: Optional[dict] = None) -> 'MyModel':
        """Custom copy with name suffix."""
        default = dict(default or {})
        default.setdefault('name', _("%s (Copy)", self.name))
        return super().copy(default)

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
    @api.model
    def _name_search(
        self,
        name: str = '',
        domain: Optional[list] = None,
        operator: str = 'ilike',
        limit: int = 100,
        order: Optional[str] = None,
    ):
        """Extended name search."""
        domain = domain or []
        if name:
            domain = ['|', ('name', operator, name), ('sequence', operator, name)] + domain
        return self._search(domain, limit=limit, order=order)

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
            'view_mode': 'tree,form',
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

## v18 Checklist

- [ ] Use `_check_company_auto = True` for multi-company models
- [ ] Add `check_company=True` to relational fields
- [ ] Use `@api.model_create_multi` for create methods
- [ ] Use `SQL()` builder for raw SQL queries
- [ ] Add type hints (recommended, mandatory in v19)
- [ ] Use `Command` class for x2many operations
- [ ] Use direct `invisible`/`readonly` in views (not `attrs`)

## AI Agent Instructions (v18)

When generating Odoo 18.0 models:

1. **ALWAYS** use `_check_company_auto = True` for multi-company
2. **ALWAYS** use `@api.model_create_multi` for create
3. **USE** `check_company=True` on relational fields
4. **USE** `SQL()` builder for raw SQL (prepare for v19)
5. **ADD** type hints where appropriate (prepare for v19)
6. **USE** `Command` class for x2many operations
7. **USE** `tracking=True` for audited fields
