# Odoo 17.0 Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 17.0 ORM PATTERNS                                                      ║
║  attrs REMOVED, use @api.model_create_multi (single-dict create warns)       ║
║  VERIFY: https://github.com/odoo/odoo/tree/17.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Patterns

### Key Characteristics
| Feature | Odoo 17.0 Pattern |
|---------|-------------------|
| attrs in views | **REMOVED** - must use conditional attributes |
| Create method | `@api.model_create_multi` (single-dict `@api.model` create still works but logs a warning) |
| X2many commands | `Command` class (recommended) |
| Change tracking | `tracking=True` |
| OWL | Version 2.x (enhanced) |
| Python version | 3.10+ |

## BREAKING: attrs Removed

```xml
<!-- THIS WILL BREAK IN v17 -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- v17 REQUIRED syntax -->
<field name="partner_id"
       invisible="state == 'draft'"/>
```

## create_multi Expected

```python
# v16 style - still works in v17, but logs a WARNING
# ("... is not overriding the create method in batch"):
@api.model
def create(self, vals):
    return super().create(vals)

# v17 correct form:
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        ...
    return super().create(vals_list)
```

A single-dict `@api.model` create is wrapped by the ORM and logs a warning in 17.0. Do not use it.

## Model Definition

```python
from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'

    name = fields.Char(
        string='Name',
        required=True,
        index='trigram',  # v17: index type specification
        tracking=True,
    )

    code = fields.Char(
        index=True,
        copy=False,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, index=True)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], default='0', index=True)

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Date fields
    date = fields.Date(default=fields.Date.context_today)
    date_deadline = fields.Date(index=True)

    # Relational fields
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        tracking=True,
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

    line_count = fields.Integer(
        compute='_compute_line_count',
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )

    # Binary and HTML fields
    attachment = fields.Binary(attachment=True)
    description = fields.Html(sanitize=True)
    note = fields.Text()
```

## CRUD Methods (v17 Patterns)

```python
@api.model_create_multi
def create(self, vals_list):
    """Batch create with @api.model_create_multi (v17 standard)"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        if 'company_id' not in vals:
            vals['company_id'] = self.env.company.id

    records = super().create(vals_list)

    # Post-creation logic
    for record in records:
        record.message_post(body=_("Record created."))

    return records

def write(self, vals):
    """Write with state validation"""
    if 'state' in vals:
        if vals['state'] == 'confirmed':
            for record in self:
                if not record.line_ids:
                    raise UserError(
                        _("Record '%s' must have at least one line.", record.name)
                    )

    result = super().write(vals)

    # Track specific field changes
    if 'partner_id' in vals:
        self._log_partner_change()

    return result

def unlink(self):
    """Delete with state check"""
    for record in self:
        if record.state not in ('draft', 'cancelled'):
            raise UserError(_(
                "Cannot delete '%(name)s' (state: %(state)s). Only draft or cancelled records can be deleted.",
                name=record.name, state=record.state,
            ))
    return super().unlink()

def copy(self, default=None):
    """Copy with name suffix"""
    self.ensure_one()
    default = dict(default or {})
    if 'name' not in default:
        default['name'] = _("%s (copy)", self.name)
    default['state'] = 'draft'
    return super().copy(default)
```

## XML Views (v17 Syntax)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View -->
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <!-- v17: Use Python expressions, NOT attrs -->
                    <button name="action_confirm" type="object"
                            string="Confirm" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_start" type="object"
                            string="Start"
                            invisible="state != 'confirmed'"/>
                    <button name="action_done" type="object"
                            string="Mark Done"
                            invisible="state != 'in_progress'"/>
                    <button name="action_cancel" type="object"
                            string="Cancel"
                            invisible="state in ('done', 'cancelled')"/>
                    <button name="action_draft" type="object"
                            string="Reset to Draft"
                            invisible="state != 'cancelled'"/>

                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,in_progress,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_lines" type="object"
                                class="oe_stat_button" icon="fa-list"
                                invisible="line_count == 0">
                            <field name="line_count" widget="statinfo"
                                   string="Lines"/>
                        </button>
                    </div>

                    <widget name="web_ribbon" title="Archived"
                            invisible="active"/>

                    <div class="oe_title">
                        <label for="name"/>
                        <h1>
                            <field name="name" placeholder="Enter name..."
                                   readonly="state == 'done'"/>
                        </h1>
                    </div>

                    <group>
                        <group string="General">
                            <field name="code" readonly="state != 'draft'"/>
                            <field name="partner_id"
                                   readonly="state == 'done'"
                                   required="state == 'confirmed'"/>
                            <field name="user_id"/>
                            <field name="priority" widget="priority"/>
                        </group>
                        <group string="Dates">
                            <field name="date"/>
                            <field name="date_deadline"
                                   invisible="state == 'draft'"/>
                            <field name="company_id"
                                   groups="base.group_multi_company"
                                   readonly="state != 'draft'"/>
                        </group>
                    </group>

                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids"
                                   readonly="state == 'done'">
                                <tree editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="product_id"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="amount" sum="Total"/>
                                </tree>
                                <form>
                                    <group>
                                        <field name="product_id"/>
                                        <field name="name"/>
                                        <field name="quantity"/>
                                        <field name="price_unit"/>
                                        <field name="amount"/>
                                    </group>
                                </form>
                            </field>
                            <group class="oe_subtotal_footer">
                                <field name="total_amount" class="oe_subtotal_footer_separator"/>
                            </group>
                        </page>
                        <page string="Tags" name="tags">
                            <field name="tag_ids" widget="many2many_tags"
                                   options="{'color_field': 'color'}"/>
                        </page>
                        <page string="Notes" name="notes"
                              invisible="state == 'draft'">
                            <field name="description"
                                   placeholder="Description..."
                                   readonly="state == 'done'"/>
                            <field name="note"
                                   placeholder="Internal notes..."/>
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

    <!-- Tree View -->
    <record id="view_my_model_tree" model="ir.ui.view">
        <field name="name">my.model.tree</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <tree decoration-danger="state == 'cancelled'"
                  decoration-success="state == 'done'"
                  decoration-warning="date_deadline and date_deadline &lt; current_date and state not in ('done', 'cancelled')">
                <field name="sequence" widget="handle"/>
                <field name="name"/>
                <field name="code"/>
                <field name="partner_id"/>
                <field name="date"/>
                <field name="date_deadline" optional="show"/>
                <field name="total_amount" sum="Total"/>
                <field name="state" widget="badge"
                       decoration-success="state == 'done'"
                       decoration-warning="state == 'in_progress'"
                       decoration-info="state == 'confirmed'"
                       decoration-danger="state == 'cancelled'"/>
                <field name="company_id" groups="base.group_multi_company" optional="hide"/>
            </tree>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_my_model_search" model="ir.ui.view">
        <field name="name">my.model.search</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <search>
                <field name="name" filter_domain="['|', ('name', 'ilike', self), ('code', 'ilike', self)]"/>
                <field name="partner_id"/>
                <field name="user_id"/>
                <separator/>
                <filter name="filter_my" string="My Records"
                        domain="[('user_id', '=', uid)]"/>
                <filter name="filter_draft" string="Draft"
                        domain="[('state', '=', 'draft')]"/>
                <filter name="filter_confirmed" string="Confirmed"
                        domain="[('state', '=', 'confirmed')]"/>
                <filter name="filter_done" string="Done"
                        domain="[('state', '=', 'done')]"/>
                <separator/>
                <filter name="filter_overdue" string="Overdue"
                        domain="[('date_deadline', '&lt;', context_today().strftime('%Y-%m-%d')), ('state', 'not in', ('done', 'cancelled'))]"/>
                <separator/>
                <filter name="filter_archived" string="Archived"
                        domain="[('active', '=', False)]"/>
                <group expand="0" string="Group By">
                    <filter name="groupby_state" string="State"
                            context="{'group_by': 'state'}"/>
                    <filter name="groupby_partner" string="Partner"
                            context="{'group_by': 'partner_id'}"/>
                    <filter name="groupby_user" string="Responsible"
                            context="{'group_by': 'user_id'}"/>
                    <filter name="groupby_date" string="Date"
                            context="{'group_by': 'date:month'}"/>
                </group>
            </search>
        </field>
    </record>
</odoo>
```

## Computed Fields

```python
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))

@api.depends('line_ids')
def _compute_line_count(self):
    for record in self:
        record.line_count = len(record.line_ids)

# Computed with conditional logic
is_overdue = fields.Boolean(
    compute='_compute_is_overdue',
    search='_search_is_overdue',
    store=True,
)

@api.depends('date_deadline', 'state')
def _compute_is_overdue(self):
    today = fields.Date.context_today(self)
    for record in self:
        record.is_overdue = (
            record.date_deadline
            and record.date_deadline < today
            and record.state not in ('done', 'cancelled')
        )

def _search_is_overdue(self, operator, value):
    today = fields.Date.context_today(self)
    if (operator == '=' and value) or (operator == '!=' and not value):
        return [
            ('date_deadline', '<', today),
            ('state', 'not in', ('done', 'cancelled')),
        ]
    return ['|', ('date_deadline', '>=', today), ('date_deadline', '=', False)]
```

## Action Methods

```python
def action_confirm(self):
    """Confirm records - validate before state change"""
    for record in self.filtered(lambda r: r.state == 'draft'):
        if not record.line_ids:
            raise UserError(_("Add at least one line to confirm '%s'.", record.name))
    self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})

def action_start(self):
    """Start work on records"""
    self.filtered(lambda r: r.state == 'confirmed').write({'state': 'in_progress'})

def action_done(self):
    """Mark records as done"""
    self.filtered(lambda r: r.state == 'in_progress').write({'state': 'done'})

def action_cancel(self):
    """Cancel records"""
    self.filtered(lambda r: r.state not in ('done', 'cancelled')).write({'state': 'cancelled'})

def action_draft(self):
    """Reset to draft"""
    self.filtered(lambda r: r.state == 'cancelled').write({'state': 'draft'})

def action_view_lines(self):
    """View lines action"""
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

## Additional Rules from Odoo's Official Guidelines (verified for 17.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 17.0 source; master-only APIs are translated to the 17.0 equivalent or marked as not available.

### Batching: one ORM call per collection

No `search`, `search_count`, `_read_group` or `create` inside a loop over records. Aggregate with the 17.0 `_read_group(domain, groupby, aggregates)`, which returns a **list of tuples**:

```python
# WRONG: one query per partner
for partner in partners:
    partner.x_order_count = self.env['sale.order'].search_count([('partner_id', '=', partner.id)])

# RIGHT (17.0): one grouped query
counts = dict(self.env['sale.order']._read_group(
    [('partner_id', 'in', partners.ids)], ['partner_id'], ['__count'],
))
for partner in partners:
    partner.x_order_count = counts.get(partner, 0)

totals = dict(self.env['sale.order']._read_group(
    [('state', '=', 'sale')], ['partner_id'], ['amount_total:sum'],
))  # {res.partner record: sum}
```

Group keys of many2one groupbys are records. The public `read_group(domain, fields, groupby)` (list of dicts) remains for the UI. Iterate recordsets (do not `browse(id)` in a loop) so prefetching works, and put conditions in the domain rather than in `filtered()`.

### Recordset helpers

`filtered`, `mapped`, `sorted` and `grouped` exist in 17.0. `records.grouped('state')` (or a callable) returns `{key: recordset}` with a shared prefetch set and no SQL. Use `if records:`, not `if len(records):`. Use `ensure_one()` before reading fields on what must be a single record; `action_*` methods called from buttons should start with it.

### Constraints and indexes (17.0 form)

```python
_sql_constraints = [
    ('code_company_uniq', 'UNIQUE(code, company_id)', 'Code must be unique per company.'),
]
code = fields.Char(index=True)            # btree
ref = fields.Char(index='btree_not_null') # most values NULL
name = fields.Char(index='trigram')       # ilike searches

def init(self):
    # multi-column index (models.Index does not exist in 17.0)
    # from odoo.tools.sql import create_index
    create_index(self._cr, 'my_model_company_date_idx', self._table, ['company_id', 'date'])
```

Use `index=` only on fields that are searched and selective. `@api.onchange` is UI-only; enforce invariants with `@api.constrains` or `_sql_constraints`. `models.Constraint`, `models.Index` and `models.UniqueIndex` are master-only.

### Translations (17.0 API)

```python
from odoo import _, _lt

raise UserError(_("Order %s cannot be confirmed.", order.name))            # positional
raise UserError(_("%(name)s has %(count)s lines", name=n, count=c))       # named
LABEL = _lt("Archived")                                                  # module/class level
```

Translate only static literals and pass the values as arguments (never `_("...%s") % x` or f-strings). `_()` escapes the translation when an argument is `Markup`. There is no `self.env._` and no `LazyTranslate` in 17.0. Lists are not formatted per language automatically; use `odoo.tools.misc.format_list(env, items)`. Field values are translated with `translate=True`.

### Domains

Combine domains with `odoo.osv.expression.AND([...])` / `expression.OR([...])`; never hand-build prefix lists or concatenate user input onto a security domain. `odoo.fields.Domain` does not exist in 17.0.

### Context and `default_` keys

The context is a frozendict; change it with `with_context(...)`. `default_get` reads every `default_<field>` key in the context, so a stray `default_state` meant for one model leaks into `create` of child models created in the same context. Prefix custom context keys with the module name.

### Related fields through x2many

A `related='line_ids.product_id'` path takes the **first** record at each x2many hop and silently ignores the others. Use a compute instead. Related fields are computed as superuser by default (`related_sudo=True`).

### Savepoints and commits

```python
try:
    with self.env.cr.savepoint():   # savepoint(flush=True) flushes before and clears on rollback
        record._do_risky_thing()
except UserError:
    ...
```

Catch specific exceptions. Never call `cr.commit()` / `cr.rollback()` on a cursor you did not open yourself.

### Reserved fields

`active` (archive with `action_archive()` / `action_unarchive()`), `state`, `parent_id` + `parent_path` with `_parent_store = True`, `company_id` with `_check_company_auto = True` and `check_company=True` on relational fields (all exist in 17.0). A field and a method cannot share a name. `_inherits` delegates fields, not methods.

### View inheritance anchors

Anchor on names, never on position. `<field name="x" position="after"/>` matches the **first** `<field name="x">` anywhere in the parent arch (name only). Other tags match the first node whose attributes all equal the spec's. An `xpath` takes its first match. Inheriting views reuse the parent xml id prefix (`<model>_view_form` -> `..._view_form_inherit_<module>`); use `mode="primary"` for a new primary view.

### QWeb reports

- `t-lang` is only valid on a node that also has `t-call`; anywhere else it raises `SyntaxError` at compile time. Translate a part by moving it into its own template and calling it with `t-call` + `t-lang`.
- A custom `report.<report_name>` model with `_get_report_values(self, docids, data=None)` replaces the defaults, so it must return `doc_ids`, `doc_model` and `docs` itself:

```python
class ReportMyModel(models.AbstractModel):
    _name = 'report.my_module.report_my_model'
    _description = 'My Model Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['my.model'].browse(docids)
        return {'doc_ids': docids, 'doc_model': 'my.model', 'docs': docs, 'data': data}
```

## v17 Best Practices

1. **NO attrs** - Always use Python expression attributes
2. **@api.model_create_multi** - Always use for create methods
3. **Use Command class** - For all x2many operations
4. **Index important fields** - Use `index=True` or `index='trigram'`
5. **Type-aware filtering** - Use `filtered()` with lambdas

## Migration Notes to v18

When upgrading from v17 to v18:

1. **check_access_rights()/check_access_rule()** - Deprecated in v18 -> `check_access()` / `has_access()`
2. **Translations** - v18 adds `self.env._` and `LazyTranslate` (`_` / `_lt` keep working)
3. **Single-dict create** - Warning in v17 becomes a DeprecationWarning in v18
4. **Type hints recommended** - Python 3.10+ features

```python
# Already available in v17 (not v18 additions):
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # exists in v17

    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # exists in v17
    )
# from odoo.tools import SQL  -> SQL builder exists in v17
```
