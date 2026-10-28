# Odoo 16.0 Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 16.0 ORM PATTERNS                                                      ║
║  Command class, attrs/states view modifiers, OWL 2.x                         ║
║  VERIFY: https://github.com/odoo/odoo/tree/16.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Patterns

### Key Characteristics
| Feature | Odoo 16.0 Pattern |
|---------|-------------------|
| X2many commands | `Command` class (tuple syntax still works) |
| attrs in views | `attrs` / `states` are the 16.0 syntax (expressions only from 17.0) |
| Change tracking | `tracking=True` |
| OWL | Version 2.x |
| Python version | 3.7 - 3.12 |

## Command Class (available since 15.0)

```python
from odoo import Command   # or: from odoo.fields import Command

# Command class methods
Command.create(values)      # Replaces (0, 0, values)
Command.update(id, values)  # Replaces (1, id, values)
Command.delete(id)          # Replaces (2, id, 0)
Command.unlink(id)          # Replaces (3, id, 0) - M2M only
Command.link(id)            # Replaces (4, id, 0)
Command.clear()             # Replaces (5, 0, 0)
Command.set(ids)            # Replaces (6, 0, ids)
```

## Model Definition

```python
from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        tracking=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, index=True)

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Date fields
    date = fields.Date(default=fields.Date.context_today)
    date_deadline = fields.Date()

    # Relational fields
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )

    partner_id = fields.Many2one(
        'res.partner',
        domain="[('company_id', 'in', [company_id, False])]",
        tracking=True,
    )

    line_ids = fields.One2many(
        'my.model.line',
        'model_id',
        copy=True,
    )

    tag_ids = fields.Many2many('my.model.tag')

    # Computed fields
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

## Using Command Class

```python
def create_with_lines(self):
    """Create record with lines using Command class"""
    return self.env['my.model'].create({
        'name': 'New Record',
        'line_ids': [
            Command.create({'name': 'Line 1', 'quantity': 1, 'price': 10.0}),
            Command.create({'name': 'Line 2', 'quantity': 2, 'price': 20.0}),
        ],
    })

def update_lines(self):
    """Update one2many lines"""
    self.write({
        'line_ids': [
            Command.update(self.line_ids[0].id, {'quantity': 5}),
            Command.create({'name': 'New Line', 'quantity': 1}),
            Command.delete(self.line_ids[-1].id),
        ],
    })

def manage_tags(self):
    """Manage many2many using Command class"""
    tag = self.env['my.model.tag'].create({'name': 'Important'})

    # Link existing tag
    self.write({'tag_ids': [Command.link(tag.id)]})

    # Replace all tags
    self.write({'tag_ids': [Command.set([tag.id])]})

    # Clear all tags
    self.write({'tag_ids': [Command.clear()]})

    # Unlink specific tag
    self.write({'tag_ids': [Command.unlink(tag.id)]})
```

## CRUD Methods

```python
@api.model_create_multi
def create(self, vals_list):
    """Batch create - recommended in v16"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)

def write(self, vals):
    """Multi-record write with Command awareness"""
    result = super().write(vals)
    if 'state' in vals and vals['state'] == 'confirmed':
        for record in self:
            record.message_post(body=_("Record confirmed."))
    return result

def unlink(self):
    """Delete with validation"""
    if any(r.state not in ('draft', 'cancelled') for r in self):
        raise UserError(_("Only draft or cancelled records can be deleted."))
    return super().unlink()
```

A single-dict `@api.model def create(self, vals)` still works in 16.0 but logs a WARNING; never call `create()` per record in a loop.

## XML Views: attrs / states (16.0 syntax)

```xml
<!--
    v16: record-dependent modifiers MUST use attrs (domains) or states.
    invisible="state == 'draft'" is NOT a record condition in 16.0: non-boolean
    values are evaluated with only `context` available (ir_ui_view.py).
    Python expressions on fields are 17.0+.
-->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'required': [('state', '=', 'confirmed')],
               'readonly': [('state', '=', 'done')]}"/>

<!-- Buttons -->
<button name="action_confirm" type="object" string="Confirm"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
<!-- Shorthand: visible only in the listed states -->
<button name="action_confirm" type="object" string="Confirm" states="draft"/>
```

### Complete Form Example

```xml
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                class="btn-primary" states="draft"/>
        <button name="action_done" type="object" string="Mark Done"
                states="confirmed"/>
        <button name="action_cancel" type="object" string="Cancel"
                attrs="{'invisible': [('state', 'in', ('done', 'cancelled'))]}"/>
        <button name="action_draft" type="object" string="Set to Draft"
                states="cancelled"/>
        <field name="state" widget="statusbar"
               statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1>
                <field name="name" placeholder="Name"
                       attrs="{'readonly': [('state', '=', 'done')]}"/>
            </h1>
        </div>
        <group>
            <group>
                <field name="partner_id"
                       attrs="{'readonly': [('state', '=', 'done')]}"/>
                <field name="date"/>
                <field name="date_deadline"
                       attrs="{'invisible': [('state', '=', 'draft')]}"/>
            </group>
            <group>
                <field name="total_amount"/>
                <field name="company_id"
                       groups="base.group_multi_company"
                       attrs="{'readonly': [('state', '!=', 'draft')]}"/>
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
            <page string="Tags" name="tags">
                <field name="tag_ids" widget="many2many_tags"/>
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

## Computed Fields

```python
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))

# With currency
@api.depends('line_ids.price_subtotal', 'currency_id')
def _compute_amount_total(self):
    for record in self:
        record.amount_total = sum(record.line_ids.mapped('price_subtotal'))
```

## Search Methods

```python
def action_search_overdue(self):
    """Search with complex domain"""
    today = fields.Date.today()
    domain = [
        ('state', '=', 'confirmed'),
        ('date_deadline', '<', today),
        ('company_id', '=', self.env.company.id),
    ]
    return self.search(domain, order='date_deadline')

# Simplest in 16.0: declare the searched fields instead of overriding
# _rec_names_search = ['name', 'code']

@api.model  # required: name_search is @api.model in 16.0; without it RPC calls break
def name_search(self, name='', args=None, operator='ilike', limit=100):
    """Enhanced name search"""
    args = args or []
    if name:
        domain = ['|', ('name', operator, name), ('code', operator, name)]
        return self.search(domain + args, limit=limit).name_get()
    return super().name_search(name, args, operator, limit)
```

## Action Methods

```python
def action_confirm(self):
    """Confirm records"""
    for record in self:
        if record.state != 'draft':
            raise UserError(_("Only draft records can be confirmed."))
        if not record.line_ids:
            raise UserError(_("Please add at least one line."))
    self.write({'state': 'confirmed'})

def action_done(self):
    """Mark as done"""
    self.filtered(lambda r: r.state == 'confirmed').write({'state': 'done'})

def action_cancel(self):
    """Cancel records"""
    self.filtered(lambda r: r.state != 'done').write({'state': 'cancelled'})

def action_draft(self):
    """Reset to draft"""
    self.filtered(lambda r: r.state == 'cancelled').write({'state': 'draft'})
```

## Additional Rules from Odoo's Official Guidelines (verified for 16.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 16.0 source; master-only APIs are translated to the 16.0 equivalent or marked as not available.

### Batching: one ORM call per collection
No `search`, `search_count`, `read_group` or `create` inside a loop. Put conditions in the domain instead of `filtered()`. Iterate recordsets (shared prefetch) instead of `browse(id)` per id.

```python
# Aggregate per group - 16.0 API (master's _read_group(domain, groupby, aggregates) does NOT exist)
groups = self.env['my.model.line'].read_group(
    [('model_id', 'in', self.ids)],
    ['amount:sum'],          # fields / aggregates
    ['model_id'],            # groupby
    lazy=False,
)
totals = {g['model_id'][0]: g['amount'] for g in groups}
counts = {g['model_id'][0]: g['__count'] for g in groups}   # lazy=True -> key 'model_id_count'
for record in self:
    record.total_amount = totals.get(record.id, 0.0)
```

### Constraints and indexes
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _sql_constraints = [
        ('code_company_uniq', 'UNIQUE(code, company_id)', 'The code must be unique per company.'),
        ('amount_positive', 'CHECK(amount >= 0)', 'The amount must be positive.'),
    ]

    ref = fields.Char(index='trigram')          # True/'btree', 'btree_not_null', 'trigram'

    def init(self):
        # multi-column index (no models.Index in 16.0)
        tools.create_index(self._cr, 'my_model_company_date_idx', self._table, ['company_id', 'date'])

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(_("Start date must be before end date."))
```
(`from odoo import tools`.) `@api.onchange` is UI only; invariants go into `@api.constrains` or `_sql_constraints`. `models.Constraint/Index/UniqueIndex` do not exist in 16.0.

### Translations
- `from odoo import _, _lt`; no `self.env._` and no `LazyTranslate` in 16.0.
- Pass arguments to `_()`: `_("Order %s confirmed", order.name)` or named `_("%(name)s confirmed", name=order.name)` (args or kwargs, not both). Never format before or after the lookup; prefer `%` over `.format()`.
- `_()` at module/class level evaluates too early: use `_lt("...")`.
- `_()` does not escape Markup args in 16.0; for HTML use `Markup(_("Hello %s")) % value`.
- Field values are translated via `translate=True`, not `_()`.

### Domains, grouping, context
- Combine domains with `from odoo.osv import expression`: `expression.AND([d1, d2])`, `expression.OR([...])`; never hand-build prefix lists or concatenate user input (no `fields.Domain` in 16.0).
- `records.grouped()` does not exist in 16.0: `for key, recs in tools.groupby(records, key=lambda r: r.partner_id)` (returns lists; wrap with `self.browse()`/`concat` if needed) or `tools.partition`.
- `if records:` instead of `len()`; `ensure_one()` before reading a single value; `action_*` methods start with `self.ensure_one()` when they act on one record.
- `with_context()` keys leak: `default_<field>` in context is used by `default_get` of EVERY model created downstream; pop it or use a module-prefixed key.

### Fields
- `related='a_ids.b'` through an x2many takes only the FIRST record of each intermediate x2many (silent truncation); use a compute instead.
- Reserved fields: `active` (archive with `action_archive()`), `state`, `parent_id` + `parent_path` with `_parent_store = True`, `company_id` with `_check_company_auto = True` and `check_company=True` (all exist in 16.0); keep `_log_access` on TransientModel (asserted).

### Transactions
- Never `self.env.cr.commit()` / `rollback()` unless you own the cursor; justify every commit.
- Recover from expected errors with `with self.env.cr.savepoint():` (signature `savepoint(flush=True)`) and catch specific exceptions; avoid hundreds of savepoints in one transaction.
- Don't use `odoo.http.request` in models (unbound in crons, RPC, tests, shell).

### Views, QWeb, reports
- Inheritance: anchor on names, never on position. `<field name="x" position="after">` matches the FIRST `<field name="x">` at any depth; other tags match the first node having all given attributes; use `xpath` for anything more specific. Inheriting view id: `<parent_xmlid>_inherit_<details>`; use `mode="primary"` for a new variant.
- `t-lang` is only valid on a node with `t-call`; elsewhere it raises `SyntaxError` at compile time. To translate a fragment, extract it into a template and `t-call` it with `t-lang`.
- A custom `_get_report_values()` (model `report.<report_name>`) must itself return `doc_ids`, `doc_model` and `docs`; the defaults are only added when no such model exists.

## v16 Best Practices

1. **Use Command class** for x2many operations
2. **Use attrs/states** for record-dependent view modifiers
3. **Use @api.model_create_multi** for create methods
4. **Leverage OWL 2.x** for frontend components
5. **Use index=True** only on fields that are searched AND selective

## Migration Notes to v17

When upgrading from v16 to v17:

1. **attrs/states replaced** - convert domains to Python expressions during the 17.0 migration (not before: expressions do not work as record conditions in 16.0)
2. **Single-dict create** - still only a WARNING in 17.0; use `@api.model_create_multi` anyway
3. **OWL 2.x** - `patch()` signature changes to `patch(obj, ext)` with `super`

```xml
<!-- v16 -->
<field name="x" attrs="{'invisible': [('state', '=', 'draft')]}"/>
<!-- v17 -->
<field name="x" invisible="state == 'draft'"/>
```
