# Odoo 15.0 Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 ORM PATTERNS                                                      ║
║  tracking=True, Command class available, create via model_create_multi       ║
║  VERIFY: https://github.com/odoo/odoo/tree/15.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Patterns

### Key Characteristics
| Feature | Odoo 15.0 Pattern |
|---------|-------------------|
| Multi-record decorator | REMOVED - methods iterate by default |
| Change tracking | `tracking=True` (track_visibility deprecated) |
| X2many commands | `Command` class (`from odoo import Command`); tuples `(0, 0, vals)` still valid |
| create override | `@api.model_create_multi` (base `create` uses it) |
| attrs in views | Full support |
| OWL | Owl 1.4 (also shipped in 14.0) |
| Python version | 3.7+ |

## Breaking Changes from v14

```python
# @api.multi does not exist (already absent in 14.0) - old code like this fails:
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

- `related` through an x2many silently uses only the FIRST record of that x2many.
- `related` is computed as superuser by default: `related_sudo=False` on sensitive chains.
- Monetary: `currency_field` defaults to `currency_id`.
- Reserved fields: `active` (archive with `action_archive()` / `action_unarchive()`), `state`, `parent_id` + `parent_path = fields.Char(index=True)` with `_parent_store = True`, `company_id` with `_check_company_auto = True` and `check_company=True` on relational fields.
- `_inherits` delegates fields only, not methods.

## CRUD Methods

```python
# Base create() is @api.model_create_multi in 15.0; override it the same way.
# (@api.model def create(self, vals) still works: silently wrapped, no warning,
#  but then creates one by one.)
@api.model_create_multi
def create(self, vals_list):
    """Batch create - accepts a dict or a list of dicts from callers"""
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

def init(self):
    # multi-column index (no models.Index in 15.0; from odoo import tools)
    tools.create_index(self._cr, 'my_model_company_state_index', self._table, ['company_id', 'state'])
```

`index=True` on a field creates a plain btree index; only index fields that are searched AND selective. `@api.onchange` is UI-only: invariants belong in `@api.constrains` or `_sql_constraints`.

## X2many Operations

`Command` exists in 15.0 (`from odoo import Command`): `Command.create(vals)`, `Command.update(id, vals)`,
`Command.delete(id)`, `Command.unlink(id)`, `Command.link(id)`, `Command.clear()`, `Command.set(ids)`.
The tuple forms below are equivalent and still accepted.

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

View inheritance: anchor on names, not positions. `<field name="x" position="after">` matches the FIRST `field` named `x` at any depth; other tags match the first node whose attributes all match. Use `xpath` for ambiguous targets; never re-add a field that already exists.

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

## Additional Rules from Odoo's Official Guidelines (verified for 15.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 15.0 source; master-only APIs are translated to the 15.0 equivalent or marked as not available.

### Batching: no ORM call per record

No `search`, `search_count`, `read_group` or `create` inside a loop over records. Aggregate once with
`read_group` (15.0 has no `_read_group(domain, groupby, aggregates)` tuple API):

```python
# One query for all orders instead of search_count/sum per order
groups = self.env['my.model.line'].read_group(
    [('model_id', 'in', self.ids)],
    ['amount:sum'],          # 'field:agg' or 'name:agg(field)'
    ['model_id'],
    lazy=False,
)
totals = {g['model_id'][0]: g['amount'] for g in groups}   # m2o group value = (id, name)
counts = {g['model_id'][0]: g['__count'] for g in groups}  # lazy=True would give 'model_id_count'
for record in self:
    record.total_amount = totals.get(record.id, 0.0)
```

- Iterate the recordset (prefetch works); `browse(id)` inside a loop prefetches only that id.
- Put conditions into the search domain instead of `filtered()` after a broad search.
- Create in batch: `self.env['my.model.line'].create([vals1, vals2, ...])`.

### Translations

```python
from odoo import _, _lt

LABEL = _lt("Pending")                                  # module/class level: lazy
raise UserError(_("Record %s cannot be confirmed.", record.display_name))
raise UserError(_("%(name)s exceeds %(limit)s.", name=record.name, limit=limit))
```

- Translate only literal strings; pass values as arguments (never format before calling `_()`).
- 15.0 has no `self.env._` and no `LazyTranslate`; `_()` finds the language through the caller frame (`self.env`).
- `_()` does not escape Markup arguments in 15.0 and does not format lists per language.
- Field values: `translate=True` on the field.

### Domains, grouping, context

```python
from odoo.osv import expression
domain = expression.AND([[('company_id', 'in', self.env.companies.ids)], extra_domain])
domain = expression.OR([domain_a, domain_b])

from odoo.tools import groupby
for partner, lines in groupby(lines, key=lambda l: l.partner_id):   # lines is a list
    lines = self.env['my.model.line'].concat(*lines)
```

- No `fields.Domain`, no `recordset.grouped()` in 15.0.
- `with_context()` returns a new env (frozendict). Prefix custom keys with the module name. A `default_<field>`
  key in the context is applied by `default_get` to EVERY model created in that context: strip it with
  `odoo.tools.misc.clean_context(self.env.context)` before creating unrelated records.
- `if records:` instead of `if len(records):`. Reading a field on a multi-record set raises `Expected singleton`: use `ensure_one()` in `action_*` methods.

### Transactions

- Never `self.env.cr.commit()` / `rollback()` on the request/cron cursor unless you own the cursor; justify every commit.
- Catch specific exceptions; recover with `with self.env.cr.savepoint():` (flushes before and after; keep the number of savepoints per transaction low).
- No `odoo.http.request` in model code: it is unbound in crons, RPC, tests and shell.

### QWeb, reports

- `t-lang` is only effective on a node with `t-call`; on other nodes 15.0 silently ignores it (no error). Translate a block by extracting it into a template and calling it with `t-lang`.
- A custom `_get_report_values()` (model `report.<report_name>`) must itself return `docs`, `doc_ids` and `doc_model`; the defaults are only provided when no such model exists.

## v15 Best Practices

1. **Use tracking=True** instead of track_visibility
2. **Remove @api.multi** - methods iterate by default
3. **Use @api.model_create_multi** for every create override (see CRUD Methods)
4. **Use super() without arguments** - Python 3 style
5. **Leverage OWL 1.x** for custom frontend components

## Migration Notes to v16

When upgrading from v15 to v16:

1. **`Command` is already available in 15.0** - prefer `Command.create()` over tuples now
2. **`attrs` stays valid in 16.0** - direct `invisible="expr"` modifiers only arrive in 17.0
3. **OWL 2.x** - Major frontend update
4. **`index=`** gains `'trigram'` / `'btree_not_null'` in 16.0

```python
# 15.0 and 16.0: Command class (preferred)
from odoo import Command
line_ids = [Command.create({'name': 'Test'})]
```
