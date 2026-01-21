# Odoo 17.0 Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 17.0 ORM PATTERNS                                                      ║
║  attrs REMOVED, @api.model_create_multi mandatory                            ║
║  VERIFY: https://github.com/odoo/odoo/tree/17.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Patterns

### Key Characteristics
| Feature | Odoo 17.0 Pattern |
|---------|-------------------|
| attrs in views | **REMOVED** - must use conditional attributes |
| Create method | `@api.model_create_multi` **MANDATORY** |
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

## BREAKING: create_multi Mandatory

```python
# v16 (optional):
@api.model
def create(self, vals):
    return super().create(vals)

# v17 (MANDATORY):
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

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
    """MANDATORY: @api.model_create_multi in v17"""
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
                        _("Record '%s' must have at least one line.") % record.name
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
            raise UserError(
                _("Cannot delete '%s' (state: %s). Only draft or cancelled records can be deleted.")
                % (record.name, record.state)
            )
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
            raise UserError(_("Add at least one line to confirm '%s'.") % record.name)
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

## v17 Best Practices

1. **NO attrs** - Always use Python expression attributes
2. **@api.model_create_multi** - Always use for create methods
3. **Use Command class** - For all x2many operations
4. **Index important fields** - Use `index=True` or `index='trigram'`
5. **Type-aware filtering** - Use `filtered()` with lambdas

## Migration Notes to v18

When upgrading from v17 to v18:

1. **_check_company_auto** - New pattern for multi-company
2. **check_company=True** - On relational fields
3. **SQL() builder** - For raw SQL queries
4. **Type hints recommended** - Python 3.10+ features

```python
# v18 additions
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # v18 pattern

    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # v18 pattern
    )
```
