# Odoo 15.0 Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 ORM PATTERNS                                                      ║
║  @api.multi removed, tracking=True standardized, OWL 1.x introduced          ║
║  VERIFY: https://github.com/odoo/odoo/tree/15.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Patterns

### Key Characteristics
| Feature | Odoo 15.0 Pattern |
|---------|-------------------|
| Multi-record decorator | REMOVED - methods iterate by default |
| Change tracking | `tracking=True` (track_visibility deprecated) |
| X2many commands | Tuple syntax `(0, 0, vals)` |
| attrs in views | Full support |
| OWL | Version 1.x introduced |
| Python version | 3.7+ |

## Breaking Changes from v14

```python
# REMOVED in v15 - @api.multi
# v14 (deprecated):
@api.multi
def action_test(self):
    pass

# v15 (correct):
def action_test(self):
    for record in self:
        pass

# DEPRECATED in v15 - track_visibility
# v14:
state = fields.Selection(..., track_visibility='onchange')

# v15:
state = fields.Selection(..., tracking=True)
```

## Model Definition

```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # Basic fields with tracking
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        tracking=True,  # v15 standard
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)  # Use tracking, not track_visibility

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Date fields
    date = fields.Date(default=fields.Date.context_today)
    datetime = fields.Datetime(default=fields.Datetime.now)

    # Relational fields
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain="[('company_id', 'in', [company_id, False])]",
    )

    line_ids = fields.One2many(
        'my.model.line',
        'model_id',
        string='Lines',
        copy=True,
    )

    tag_ids = fields.Many2many(
        'my.model.tag',
        string='Tags',
    )

    # Computed fields
    line_count = fields.Integer(
        compute='_compute_line_count',
        string='Line Count',
    )

    total_amount = fields.Monetary(
        compute='_compute_total',
        store=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )
```

## CRUD Methods

```python
@api.model
def create(self, vals):
    """Single record create - standard in v15"""
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals)

# Optional: model_create_multi for batch operations
@api.model_create_multi
def create(self, vals_list):
    """Batch create - optional in v15, recommended for performance"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)

def write(self, vals):
    """Multi-record write"""
    if 'state' in vals and vals['state'] == 'done':
        for record in self:
            if not record.line_ids:
                raise UserError(_("Cannot complete without lines."))
    return super().write(vals)

def unlink(self):
    """Multi-record delete"""
    if any(record.state == 'done' for record in self):
        raise UserError(_("Cannot delete completed records."))
    return super().unlink()

def copy(self, default=None):
    """Copy single record"""
    self.ensure_one()
    default = dict(default or {})
    default['name'] = _("%s (copy)") % self.name
    return super().copy(default)
```

## Computed Fields

```python
@api.depends('line_ids', 'line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))

@api.depends('line_ids')
def _compute_line_count(self):
    for record in self:
        record.line_count = len(record.line_ids)

# Search computed field
is_overdue = fields.Boolean(
    compute='_compute_is_overdue',
    search='_search_is_overdue',
)

def _compute_is_overdue(self):
    today = fields.Date.context_today(self)
    for record in self:
        record.is_overdue = record.date_due and record.date_due < today

def _search_is_overdue(self, operator, value):
    today = fields.Date.context_today(self)
    if (operator == '=' and value) or (operator == '!=' and not value):
        return [('date_due', '<', today)]
    return [('date_due', '>=', today)]
```

## Onchange and Constraints

```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    """Update fields when partner changes"""
    if self.partner_id:
        self.delivery_address_id = self.partner_id.address_get(['delivery'])['delivery']

@api.constrains('date_start', 'date_end')
def _check_dates(self):
    for record in self:
        if record.date_start and record.date_end:
            if record.date_start > record.date_end:
                raise ValidationError(
                    _("End date must be after start date.")
                )

_sql_constraints = [
    ('code_uniq', 'unique(code, company_id)',
     'Code must be unique per company!'),
    ('positive_amount', 'CHECK(amount >= 0)',
     'Amount must be positive!'),
]
```

## X2many Operations

```python
def create_with_lines(self):
    """Create record with one2many lines using tuple syntax"""
    return self.env['my.model'].create({
        'name': 'New Record',
        'line_ids': [
            (0, 0, {'name': 'Line 1', 'quantity': 1, 'price': 10.0}),
            (0, 0, {'name': 'Line 2', 'quantity': 2, 'price': 20.0}),
        ],
    })

def update_lines(self):
    """Update one2many lines"""
    self.write({
        'line_ids': [
            (1, self.line_ids[0].id, {'quantity': 5}),  # Update first line
            (0, 0, {'name': 'New Line', 'quantity': 1}),  # Add new line
            (2, self.line_ids[-1].id, 0),  # Delete last line
        ],
    })

def replace_lines(self):
    """Replace all lines"""
    new_line_ids = self.env['my.model.line'].create([
        {'name': 'A', 'quantity': 1},
        {'name': 'B', 'quantity': 2},
    ])
    self.write({
        'line_ids': [(6, 0, new_line_ids.ids)],
    })
```

## XML Views with attrs

```xml
<!-- v15: attrs fully supported -->
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                class="btn-primary"
                attrs="{'invisible': [('state', '!=', 'draft')]}"/>
        <button name="action_done" type="object" string="Mark Done"
                attrs="{'invisible': [('state', '!=', 'confirmed')]}"/>
        <button name="action_cancel" type="object" string="Cancel"
                attrs="{'invisible': [('state', '=', 'done')]}"/>
        <field name="state" widget="statusbar"
               statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1>
                <field name="name" placeholder="Name"/>
            </h1>
        </div>
        <group>
            <group>
                <field name="partner_id"/>
                <field name="date"/>
                <field name="company_id" groups="base.group_multi_company"/>
            </group>
            <group>
                <field name="total_amount"/>
                <field name="currency_id" invisible="1"/>
            </group>
        </group>

        <notebook>
            <page string="Lines" name="lines">
                <field name="line_ids"
                       attrs="{'readonly': [('state', '=', 'done')]}">
                    <tree editable="bottom">
                        <field name="sequence" widget="handle"/>
                        <field name="name"/>
                        <field name="quantity"/>
                        <field name="price"/>
                        <field name="amount" sum="Total"/>
                    </tree>
                </field>
            </page>
            <page string="Notes" name="notes"
                  attrs="{'invisible': [('state', '=', 'draft')]}">
                <field name="note" placeholder="Internal notes..."/>
            </page>
        </notebook>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

## Search and Actions

```python
def action_search_partners(self):
    """Search with domain"""
    domain = [
        ('customer_rank', '>', 0),
        ('company_id', 'in', [self.company_id.id, False]),
    ]
    return self.env['res.partner'].search(domain, limit=100)

def action_view_record(self):
    """Return action to view single record"""
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': self.name,
        'res_model': self._name,
        'res_id': self.id,
        'view_mode': 'form',
        'target': 'current',
    }

def action_view_lines(self):
    """Return action to view related records"""
    return {
        'type': 'ir.actions.act_window',
        'name': _('Lines'),
        'res_model': 'my.model.line',
        'view_mode': 'tree,form',
        'domain': [('model_id', '=', self.id)],
        'context': {
            'default_model_id': self.id,
            'create': self.state != 'done',
        },
    }
```

## Cron Jobs

```python
@api.model
def _cron_process_records(self):
    """Scheduled action - process pending records"""
    records = self.search([
        ('state', '=', 'confirmed'),
        ('date', '<=', fields.Date.today()),
    ])
    for record in records:
        try:
            record.action_done()
        except Exception as e:
            _logger.error("Failed to process %s: %s", record.name, e)
```

## Mail Integration

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def action_send_notification(self):
        """Post message to chatter"""
        self.message_post(
            body=_("Record has been confirmed."),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )

    def action_schedule_activity(self):
        """Schedule follow-up activity"""
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            date_deadline=fields.Date.add(fields.Date.today(), days=7),
            summary=_("Follow up on %s") % self.name,
        )
```

## v15 Best Practices

1. **Use tracking=True** instead of track_visibility
2. **Remove @api.multi** - methods iterate by default
3. **Consider @api.model_create_multi** for batch creates
4. **Use super() without arguments** - Python 3 style
5. **Leverage OWL 1.x** for custom frontend components

## Migration Notes to v16

When upgrading from v15 to v16:

1. **Command class available** - Can use `Command.create()` instead of tuples
2. **attrs deprecation begins** - Start planning migration
3. **OWL 2.x** - Major frontend update

```python
# v15: Tuple syntax
line_ids = [(0, 0, {'name': 'Test'})]

# v16: Command class (preferred)
from odoo.fields import Command
line_ids = [Command.create({'name': 'Test'})]
```
