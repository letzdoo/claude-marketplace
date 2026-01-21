# Odoo 14.0 Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 14.0 ORM PATTERNS                                                      ║
║  Last version with @api.multi and track_visibility                           ║
║  VERIFY: https://github.com/odoo/odoo/tree/14.0/odoo/models.py               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Patterns

### Key Characteristics
| Feature | Odoo 14.0 Pattern |
|---------|-------------------|
| Multi-record decorator | `@api.multi` (deprecated but works) |
| Change tracking | `track_visibility='onchange'` |
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
        tracking=True,  # New way (works in 14.0)
    )

    # Old tracking syntax (deprecated but works)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', track_visibility='onchange')  # Old way

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

## @api.multi Pattern (Deprecated)

```python
# v14: @api.multi still works but is deprecated
# It's the implicit default for methods

@api.multi  # Deprecated - remove this decorator
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
@api.model
def create(self, vals):
    """Override create - note: not create_multi yet"""
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super(MyModel, self).create(vals)

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

## Migration Notes to v15

When upgrading from v14 to v15:

1. **Remove @api.multi** - No longer needed
2. **Replace track_visibility** - Use `tracking=True` instead
3. **Update create()** - Consider `@api.model_create_multi` (optional in v15)

```python
# v14
@api.multi
def action_test(self):
    pass

state = fields.Selection(..., track_visibility='onchange')

# v15
def action_test(self):
    pass

state = fields.Selection(..., tracking=True)
```

## Important v14 Notes

1. **@api.multi is implicit** - Don't use it explicitly
2. **track_visibility works** - But tracking=True is preferred
3. **Tuple commands work** - Standard x2many syntax
4. **attrs fully supported** - Use for conditional visibility
5. **Python 3.6+** - f-strings and type hints available
