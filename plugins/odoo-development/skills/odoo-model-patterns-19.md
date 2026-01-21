# Odoo 19.0 Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 19.0 ORM PATTERNS                                                      ║
║  Type hints mandatory, SQL() required, OWL 3.x                               ║
║  WARNING: v19 is in development - patterns may change                        ║
║  VERIFY: https://github.com/odoo/odoo/tree/master/odoo/models.py             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Patterns

### Key Characteristics
| Feature | Odoo 19.0 Pattern |
|---------|-------------------|
| Type hints | **MANDATORY** for public methods |
| Raw SQL | **SQL() required** - string queries deprecated |
| X2many commands | `Command` class |
| Multi-company | `_check_company_auto` + `check_company=True` |
| OWL | Version 3.x |
| Python version | 3.12+ |

## BREAKING: Type Hints Mandatory

```python
# v18 (optional):
def action_confirm(self):
    pass

# v19 (MANDATORY):
def action_confirm(self) -> bool:
    return True

# Full type hints example
def create_record(self, name: str, partner_id: int | None = None) -> 'MyModel':
    return self.create({'name': name, 'partner_id': partner_id})
```

## BREAKING: SQL() Builder Required

```python
from odoo.tools import SQL

# v18 (deprecated string queries):
self.env.cr.execute("SELECT id FROM my_model WHERE state = %s", ['draft'])

# v19 (REQUIRED SQL() builder):
self.env.cr.execute(SQL(
    "SELECT id FROM my_model WHERE state = %s",
    'draft'
))

# Complex query
self.env.cr.execute(SQL(
    """
    SELECT m.id, m.name, COUNT(l.id) as line_count
    FROM my_model m
    LEFT JOIN my_model_line l ON l.model_id = m.id
    WHERE m.state = %s AND m.company_id = %s
    GROUP BY m.id, m.name
    HAVING COUNT(l.id) > %s
    """,
    'confirmed', self.env.company.id, 0
))
```

## Model Definition

```python
from __future__ import annotations
from typing import TYPE_CHECKING

from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL
import logging

if TYPE_CHECKING:
    from odoo.addons.base.models.res_partner import Partner
    from odoo.addons.base.models.res_company import Company

_logger = logging.getLogger(__name__)


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'
    _check_company_auto = True  # v19: Auto company check

    # String fields
    name: str = fields.Char(
        string='Name',
        required=True,
        index='trigram',
        tracking=True,
    )

    code: str = fields.Char(
        index=True,
        copy=False,
    )

    # Selection field
    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, index=True)

    priority: str = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], default='0', index=True)

    # Integer/Float fields
    sequence: int = fields.Integer(default=10)
    quantity: float = fields.Float(digits='Product Unit of Measure')

    # Boolean
    active: bool = fields.Boolean(default=True)

    # Date fields
    date: fields.Date = fields.Date(default=fields.Date.context_today)
    date_deadline: fields.Date = fields.Date(index=True)

    # Relational fields with company check
    company_id: Company = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    user_id: models.Model = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True,  # v19: Enforce company
    )

    partner_id: Partner = fields.Many2one(
        'res.partner',
        tracking=True,
        check_company=True,  # v19: Enforce company
    )

    line_ids: models.Model = fields.One2many(
        'my.model.line',
        'model_id',
        copy=True,
    )

    tag_ids: models.Model = fields.Many2many('my.model.tag')

    # Monetary fields
    total_amount: float = fields.Monetary(
        compute='_compute_total',
        store=True,
        currency_field='currency_id',
    )

    currency_id: models.Model = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )

    # Computed count
    line_count: int = fields.Integer(
        compute='_compute_line_count',
    )

    # HTML/Text
    description: str = fields.Html(sanitize=True)
    note: str = fields.Text()
```

## CRUD Methods with Type Hints

```python
@api.model_create_multi
def create(self, vals_list: list[dict]) -> 'MyModel':
    """Create records with auto-generated code.

    Args:
        vals_list: List of value dictionaries

    Returns:
        Created records
    """
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        if 'company_id' not in vals:
            vals['company_id'] = self.env.company.id

    records = super().create(vals_list)

    for record in records:
        record.message_post(body=_("Record created."))

    return records

def write(self, vals: dict) -> bool:
    """Update records with validation.

    Args:
        vals: Values to update

    Returns:
        True on success
    """
    if 'state' in vals and vals['state'] == 'confirmed':
        for record in self:
            if not record.line_ids:
                raise UserError(
                    _("Record '%s' must have at least one line.") % record.name
                )

    return super().write(vals)

def unlink(self) -> bool:
    """Delete records with state check.

    Returns:
        True on success

    Raises:
        UserError: If record is not draft or cancelled
    """
    for record in self:
        if record.state not in ('draft', 'cancelled'):
            raise UserError(
                _("Cannot delete '%s'. Only draft or cancelled records can be deleted.")
                % record.name
            )
    return super().unlink()

def copy(self, default: dict | None = None) -> 'MyModel':
    """Copy record with name suffix.

    Args:
        default: Override values for copy

    Returns:
        New copied record
    """
    self.ensure_one()
    default = dict(default or {})
    if 'name' not in default:
        default['name'] = _("%s (copy)", self.name)
    default['state'] = 'draft'
    return super().copy(default)
```

## Computed Fields with Types

```python
@api.depends('line_ids.amount')
def _compute_total(self) -> None:
    """Compute total amount from lines."""
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))

@api.depends('line_ids')
def _compute_line_count(self) -> None:
    """Compute number of lines."""
    for record in self:
        record.line_count = len(record.line_ids)

# Computed with search
is_overdue: bool = fields.Boolean(
    compute='_compute_is_overdue',
    search='_search_is_overdue',
    store=True,
)

@api.depends('date_deadline', 'state')
def _compute_is_overdue(self) -> None:
    """Compute overdue status."""
    today = fields.Date.context_today(self)
    for record in self:
        record.is_overdue = (
            record.date_deadline
            and record.date_deadline < today
            and record.state not in ('done', 'cancelled')
        )

def _search_is_overdue(self, operator: str, value: bool) -> list:
    """Search implementation for is_overdue.

    Args:
        operator: Search operator
        value: Search value

    Returns:
        Search domain
    """
    today = fields.Date.context_today(self)
    if (operator == '=' and value) or (operator == '!=' and not value):
        return [
            ('date_deadline', '<', today),
            ('state', 'not in', ('done', 'cancelled')),
        ]
    return ['|', ('date_deadline', '>=', today), ('date_deadline', '=', False)]
```

## SQL Queries with SQL() Builder

```python
def get_summary_data(self) -> list[dict]:
    """Get summary data using SQL() builder.

    Returns:
        List of summary dictionaries
    """
    self.env.cr.execute(SQL(
        """
        SELECT
            state,
            COUNT(*) as count,
            SUM(total_amount) as total
        FROM my_model
        WHERE company_id = %s
        GROUP BY state
        ORDER BY count DESC
        """,
        self.env.company.id
    ))
    return self.env.cr.dictfetchall()

def find_duplicates(self, name: str) -> list[int]:
    """Find records with similar names.

    Args:
        name: Name to search

    Returns:
        List of record IDs
    """
    self.env.cr.execute(SQL(
        """
        SELECT id FROM my_model
        WHERE company_id = %s
        AND name ILIKE %s
        AND id != %s
        """,
        self.env.company.id,
        f'%{name}%',
        self.id or 0
    ))
    return [row[0] for row in self.env.cr.fetchall()]

def bulk_update_state(self, state: str, record_ids: list[int]) -> int:
    """Bulk update state using raw SQL.

    Args:
        state: New state value
        record_ids: Record IDs to update

    Returns:
        Number of updated records
    """
    if not record_ids:
        return 0

    self.env.cr.execute(SQL(
        """
        UPDATE my_model
        SET state = %s, write_date = NOW(), write_uid = %s
        WHERE id = ANY(%s)
        AND company_id = %s
        """,
        state,
        self.env.uid,
        record_ids,
        self.env.company.id
    ))

    # Invalidate cache for updated records
    self.browse(record_ids).invalidate_recordset()

    return self.env.cr.rowcount
```

## Action Methods with Types

```python
def action_confirm(self) -> bool:
    """Confirm records.

    Returns:
        True on success

    Raises:
        UserError: If validation fails
    """
    for record in self.filtered(lambda r: r.state == 'draft'):
        if not record.line_ids:
            raise UserError(_("Add at least one line to confirm '%s'.") % record.name)

    self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})
    return True

def action_start(self) -> bool:
    """Start work on records."""
    self.filtered(lambda r: r.state == 'confirmed').write({'state': 'in_progress'})
    return True

def action_done(self) -> bool:
    """Mark records as done."""
    self.filtered(lambda r: r.state == 'in_progress').write({'state': 'done'})
    return True

def action_cancel(self) -> bool:
    """Cancel records."""
    self.filtered(lambda r: r.state not in ('done', 'cancelled')).write({'state': 'cancelled'})
    return True

def action_draft(self) -> bool:
    """Reset to draft."""
    self.filtered(lambda r: r.state == 'cancelled').write({'state': 'draft'})
    return True

def action_view_lines(self) -> dict:
    """Return action to view lines.

    Returns:
        Action dictionary
    """
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': _('Lines'),
        'res_model': 'my.model.line',
        'view_mode': 'tree,form',
        'domain': [('model_id', '=', self.id)],
        'context': {'default_model_id': self.id},
    }
```

## Constraints with Types

```python
_sql_constraints = [
    ('code_company_uniq', 'unique(code, company_id)',
     'Code must be unique per company!'),
    ('positive_quantity', 'CHECK(quantity >= 0)',
     'Quantity must be positive!'),
]

@api.constrains('date', 'date_deadline')
def _check_dates(self) -> None:
    """Validate date order.

    Raises:
        ValidationError: If dates are invalid
    """
    for record in self:
        if record.date and record.date_deadline:
            if record.date > record.date_deadline:
                raise ValidationError(
                    _("Deadline must be after start date for '%s'.") % record.name
                )

@api.constrains('line_ids')
def _check_lines(self) -> None:
    """Validate lines have positive amounts.

    Raises:
        ValidationError: If any line has invalid amount
    """
    for record in self:
        for line in record.line_ids:
            if line.amount < 0:
                raise ValidationError(
                    _("Line '%s' cannot have negative amount.") % line.name
                )
```

## XML Views (v19)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" type="object"
                            string="Confirm" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_start" type="object"
                            string="Start"
                            invisible="state != 'confirmed'"/>
                    <button name="action_done" type="object"
                            string="Done"
                            invisible="state != 'in_progress'"/>
                    <button name="action_cancel" type="object"
                            string="Cancel"
                            invisible="state in ('done', 'cancelled')"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" readonly="state == 'done'"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="partner_id"
                                   readonly="state == 'done'"
                                   required="state == 'confirmed'"/>
                            <field name="date"/>
                        </group>
                        <group>
                            <field name="total_amount"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines">
                            <field name="line_ids" readonly="state == 'done'"/>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
```

## v19 Best Practices

1. **Type hints on all public methods** - Mandatory for code quality
2. **Use SQL() builder** - Never use string SQL queries
3. **_check_company_auto = True** - On multi-company models
4. **check_company=True** - On relational fields
5. **Use OWL 3.x patterns** - For frontend components
6. **from __future__ import annotations** - For forward references

## Type Hint Reference

```python
# Import types
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from odoo.addons.base.models.res_partner import Partner

# Method signatures
def method_name(self, param: str, optional: int | None = None) -> bool:
    pass

# Return types
def returns_recordset(self) -> 'MyModel':
    pass

def returns_list(self) -> list[dict[str, Any]]:
    pass

def returns_dict(self) -> dict[str, str | int]:
    pass
```
