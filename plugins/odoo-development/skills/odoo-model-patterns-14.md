# Odoo 14.0 Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 14.0 ORM PATTERNS                                                      ║
║  No @api.multi (removed in 13.0); tracking=True; model_create_multi          ║
║  VERIFY: https://github.com/odoo/odoo/tree/14.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Patterns

### Key Characteristics
| Feature | Odoo 14.0 Pattern |
|---------|-------------------|
| Multi-record decorator | none (`@api.multi` is removed and fails) |
| Change tracking | `tracking=True` (`track_visibility` still tracked but logs a warning) |
| Create override | `@api.model_create_multi` + `vals_list` |
| X2many commands | Tuple syntax `(0, 0, vals)` |
| attrs in views | Full support |
| Python version | 3.6+ |

## Model Definition

```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _rec_name = 'name'

    # Basic fields
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        tracking=True,  # the valid tracking parameter in 14.0
    )

    # track_visibility='onchange' is legacy: still tracked by mail.thread,
    # but the field setup logs "unknown parameter" - use tracking=True
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

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
    )

    tag_ids = fields.Many2many(
        'my.model.tag',
        'my_model_tag_rel',
        'model_id',
        'tag_id',
        string='Tags',
    )
```

## @api.multi Pattern (Removed)

```python
# v14: @api.multi does NOT exist (removed in 13.0).
# Code still carrying it fails at import:
# AttributeError: module 'odoo.api' has no attribute 'multi'

# @api.multi  # remove this line
def action_confirm(self):
    for record in self:
        if record.state != 'draft':
            raise UserError(_("Only draft records can be confirmed."))
        record.state = 'confirmed'
    return True

# Correct v14 pattern (no decorator needed)
def action_confirm(self):
    for record in self:
        if record.state != 'draft':
            raise UserError(_("Only draft records can be confirmed."))
        record.state = 'confirmed'
    return True
```

## X2many Command Syntax

```python
# v14: Tuple syntax (still works in all versions)
def create_with_lines(self):
    self.env['my.model'].create({
        'name': 'Test',
        'line_ids': [
            (0, 0, {'name': 'Line 1', 'quantity': 1}),  # Create
            (1, line_id, {'quantity': 2}),              # Update
            (2, line_id, 0),                            # Delete
            (3, line_id, 0),                            # Unlink
            (4, line_id, 0),                            # Link
            (5, 0, 0),                                  # Clear all
            (6, 0, [id1, id2]),                         # Replace all
        ],
    })
```

### Command Reference
| Code | Description | Arguments |
|------|-------------|-----------|
| (0, 0, vals) | Create new record | vals dict |
| (1, id, vals) | Update existing | id, vals dict |
| (2, id, 0) | Delete record | id |
| (3, id, 0) | Unlink (M2M only) | id |
| (4, id, 0) | Link existing | id |
| (5, 0, 0) | Clear all | none |
| (6, 0, ids) | Replace all | list of ids |

## CRUD Methods

```python
@api.model_create_multi
def create(self, vals_list):
    """Override create - BaseModel.create is model_create_multi in 14.0"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)

# A legacy `@api.model def create(self, vals)` override is wrapped silently
# (no warning) and loops one record at a time - always use vals_list.

def write(self, vals):
    """Override write"""
    if 'state' in vals and vals['state'] == 'done':
        for record in self:
            if not record.line_ids:
                raise UserError(_("Cannot complete without lines."))
    return super(MyModel, self).write(vals)

def unlink(self):
    """Override unlink"""
    for record in self:
        if record.state == 'done':
            raise UserError(_("Cannot delete completed records."))
    return super(MyModel, self).unlink()

def copy(self, default=None):
    """Override copy - single record"""
    self.ensure_one()
    default = dict(default or {})
    default['name'] = _("%s (copy)") % self.name
    return super(MyModel, self).copy(default)
```

## Computed Fields

```python
# v14 computed field patterns
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True,
)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))

# Inverse method
partner_name = fields.Char(
    compute='_compute_partner_name',
    inverse='_inverse_partner_name',
    store=False,
)

def _compute_partner_name(self):
    for record in self:
        record.partner_name = record.partner_id.name or ''

def _inverse_partner_name(self):
    for record in self:
        if record.partner_id:
            record.partner_id.name = record.partner_name
```

## Constraints

```python
# SQL Constraint
_sql_constraints = [
    ('code_uniq', 'unique(code, company_id)',
     'Code must be unique per company!'),
    ('positive_amount', 'CHECK(amount >= 0)',
     'Amount must be positive!'),
]

# Python Constraint
@api.constrains('date_start', 'date_end')
def _check_dates(self):
    for record in self:
        if record.date_start and record.date_end:
            if record.date_start > record.date_end:
                raise ValidationError(
                    _("End date must be after start date.")
                )
```

- Python invariants belong in `@api.constrains`; `@api.onchange` is UI-only.
- `models.Constraint`/`Index`/`UniqueIndex` do not exist in 14.0: use `_sql_constraints`.
- `index=True` only on searched AND selective fields (boolean only: a plain btree). Multi-column or partial indexes: `def init(self):` with `tools.create_index(self._cr, ...)` or explicit SQL.

## Search and Domain

```python
def action_find_partners(self):
    # Domain operators
    domain = [
        ('customer_rank', '>', 0),
        ('company_id', 'in', [self.company_id.id, False]),
        '|',
        ('name', 'ilike', 'test'),
        ('email', 'ilike', 'test'),
    ]

    partners = self.env['res.partner'].search(
        domain,
        limit=100,
        order='name',
    )
    return partners

# search_read for efficiency
def get_partner_data(self):
    return self.env['res.partner'].search_read(
        [('customer_rank', '>', 0)],
        ['name', 'email', 'phone'],
        limit=50,
    )
```

- Combine domains with `odoo.osv.expression.AND([...])` / `OR([...])`, never by concatenating a user-supplied list onto a security domain (`fields.Domain` is 19.0+).

## XML Views with attrs

```xml
<!-- v14: attrs fully supported -->
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                attrs="{'invisible': [('state', '!=', 'draft')]}"/>
        <button name="action_done" type="object" string="Done"
                attrs="{'invisible': [('state', '!=', 'confirmed')]}"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <field name="name"/>
            <field name="partner_id"
                   attrs="{'required': [('state', '=', 'confirmed')]}"/>
            <field name="amount"
                   attrs="{'readonly': [('state', '=', 'done')]}"/>
        </group>

        <notebook>
            <page string="Lines"
                  attrs="{'invisible': [('state', '=', 'draft')]}">
                <field name="line_ids">
                    <tree editable="bottom">
                        <field name="name"/>
                        <field name="quantity"/>
                        <field name="price"
                               attrs="{'readonly': [('parent.state', '=', 'done')]}"/>
                    </tree>
                </field>
            </page>
        </notebook>
    </sheet>
</form>
```

## Security Configuration

```python
# ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_manager,1,1,1,1
```

```xml
<!-- Record Rules -->
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

## Common Patterns

### Action Return
```python
def action_view_partner(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': _('Partner'),
        'res_model': 'res.partner',
        'res_id': self.partner_id.id,
        'view_mode': 'form',
        'target': 'current',
    }

def action_view_lines(self):
    return {
        'type': 'ir.actions.act_window',
        'name': _('Lines'),
        'res_model': 'my.model.line',
        'view_mode': 'tree,form',
        'domain': [('model_id', '=', self.id)],
        'context': {'default_model_id': self.id},
    }
```

### Wizard Pattern
```python
class MyWizard(models.TransientModel):
    _name = 'my.wizard'
    _description = 'My Wizard'

    partner_id = fields.Many2one('res.partner', required=True)
    note = fields.Text()

    def action_confirm(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['my.model'].browse(active_ids)
        for record in records:
            record.partner_id = self.partner_id
        return {'type': 'ir.actions.act_window_close'}
```

## Additional Rules from Odoo's Official Guidelines (verified for 14.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 14.0 source; master-only APIs are translated to the 14.0 equivalent or marked as not available.

### Batching: no ORM call per record

```python
# WRONG: one search_count / create per record
for order in orders:
    order.line_count = self.env['my.model.line'].search_count([('model_id', '=', order.id)])

# RIGHT (14.0): one read_group; returns a list of dicts, m2o keys are (id, name)
groups = self.env['my.model.line'].read_group(
    [('model_id', 'in', orders.ids)], ['amount:sum'], ['model_id'])
totals = {g['model_id'][0]: g['amount'] for g in groups}
counts = {g['model_id'][0]: g['model_id_count'] for g in groups}
for order in orders:
    order.total = totals.get(order.id, 0.0)

# create in batch
self.env['my.model.line'].create([{'model_id': o.id, 'name': 'X'} for o in orders])
```

- No `_read_group(domain, groupby, aggregates)` in 14.0 (that signature is 17.0+).
- Iterate recordsets (shared prefetch) instead of `browse(id)` in a loop. Put filters in the domain, not in `filtered()`.

### Translations
```python
from odoo import _, _lt

LABEL = _lt("Draft")                                   # module/class level: lazy
raise UserError(_("Order %s cannot be confirmed.", order.name))      # positional
raise UserError(_("%(name)s: %(count)s lines", name=n, count=c))     # named
```
- `_()` formats after the translation lookup (`%` style, positional or named, not both). It does not escape and does not format lists per language.
- `self.env._` and `LazyTranslate` do not exist in 14.0. Never call `_()` at import time. Never format before calling `_()`.

### Grouping, context
- `recordset.grouped()` does not exist: use `odoo.tools.groupby(records, key)` (returns `(key, list)` pairs) or a `defaultdict(lambda: self.env['my.model'])`.
- `default_<field>` keys in the context are used by `default_get` (and by `mail.thread` auto-subscription) for every create on a model with that field. Strip them (`odoo.tools.clean_context`) before creating unrelated records; prefix custom context keys with the module name.

### Fields
- `related` through an x2many takes the first record at each hop and silently truncates. Use a compute instead.
- Related fields are computed as superuser by default (`related_sudo=True`). Set `related_sudo=False` on sensitive chains.
- Reserved fields: `active` (+ `action_archive`/`action_unarchive`), `state`, `parent_id` + `parent_path` (indexed) with `_parent_store = True`, `company_id` with `_check_company_auto = True` and `check_company=True`.
- Reading a field on a multi-record set raises: call `ensure_one()` in `action_*` methods.

### Transactions
- Never `self.env.cr.commit()` / `rollback()` in business code (only in your own cursor, e.g. a cron that processes batches, with a comment explaining why).
- Recover from an expected error with `with self.env.cr.savepoint():` and catch a specific exception. Keep the number of savepoints per transaction small.
- `odoo.http.request` is unbound in crons, RPC, tests and the shell: do not use it in model code.

### View inheritance and reports
- Anchor on names, not positions: `<field name="partner_id" position="after">`. The shorthand `<field name="x">` matches the FIRST field named `x` anywhere in the parent arch (at any depth). Other tags match the first node whose attributes all match. Use an `xpath` when the field appears more than once.
- `t-lang` only takes effect on a node with `t-call`. Without `t-call` it is silently ignored in 14.0 (no error), so the text renders in the current language.
- A custom `report.<report_name>` model with `_get_report_values()` must return `doc_ids`, `doc_model` and `docs` itself. Odoo adds them only when no custom report model exists.

## Migration Notes to v15

When upgrading from v14 to v15:

1. **`@api.multi`** - already absent in 14.0; nothing to do
2. **`track_visibility`** - replace with `tracking=True` (already the valid form in 14.0)
3. **x2many** - `Command` becomes available in 15.0 (tuples keep working)

```python
# v14 and v15
def action_test(self):
    pass

state = fields.Selection(..., tracking=True)
```

## Important v14 Notes

1. **`@api.multi` does not exist** - methods are multi-record by default
2. **Use `tracking=True`** - `track_visibility` still tracks but logs "unknown parameter"
3. **Tuple commands work** - Standard x2many syntax
4. **attrs fully supported** - Use for conditional visibility
5. **Python 3.6+** - f-strings and type hints available
