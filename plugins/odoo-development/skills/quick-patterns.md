# Quick Patterns - 80% of Common Tasks

> Copy-paste ready. For complex patterns, use `Read` on specific skill files.

## Model
```python
from odoo import api, fields, models

class MyModel(models.Model):
    _name = 'my.module.model'
    _description = 'My Model'
    _inherit = ['mail.thread']
    _order = 'sequence, id'
```

## Fields
```python
# Basic
name = fields.Char(required=True)
active = fields.Boolean(default=True)
sequence = fields.Integer(default=10)
amount = fields.Float(digits=(16, 2))
description = fields.Text()
date = fields.Date(default=fields.Date.today)
state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')

# Relational
partner_id = fields.Many2one('res.partner', ondelete='cascade')
tag_ids = fields.Many2many('my.tag')
line_ids = fields.One2many('my.line', 'parent_id')
company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
```

## Computed
```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for rec in self:
        rec.total = sum(rec.line_ids.mapped('amount'))
```

## Onchange
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.phone = self.partner_id.phone
```

## Constraints
```python
# SQL
_sql_constraints = [('name_unique', 'UNIQUE(name)', 'Name must be unique')]

# Python
@api.constrains('amount')
def _check_amount(self):
    for rec in self:
        if rec.amount < 0:
            raise ValidationError("Amount cannot be negative")
```

## CRUD Override
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)

def write(self, vals):
    if 'state' in vals:
        self._check_state_transition(vals['state'])
    return super().write(vals)

def unlink(self):
    if any(rec.state == 'done' for rec in self):
        raise UserError("Cannot delete done records")
    return super().unlink()
```

## Form View
```xml
<form>
    <header>
        <button name="action_confirm" string="Confirm" type="object" class="oe_highlight" invisible="state != 'draft'"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group><group><field name="name"/><field name="partner_id"/></group>
        <group><field name="date"/><field name="amount"/></group></group>
        <notebook><page string="Lines"><field name="line_ids"/></page></notebook>
    </sheet>
    <div class="oe_chatter"><field name="message_ids"/></div>
</form>
```

## Tree View
```xml
<tree><field name="name"/><field name="partner_id"/><field name="amount"/><field name="state" widget="badge"/></tree>
```

## Search View
```xml
<search><field name="name"/><field name="partner_id"/>
<filter name="draft" string="Draft" domain="[('state', '=', 'draft')]"/>
<group expand="0" string="Group By"><filter name="group_partner" string="Partner" context="{'group_by': 'partner_id'}"/></group>
</search>
```

## Action
```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Records</field>
    <field name="res_model">my.module.model</field>
    <field name="view_mode">tree,form</field>
</record>
```

## Menu
```xml
<menuitem id="menu_root" name="My App" web_icon="my_module,static/description/icon.png"/>
<menuitem id="menu_main" name="Records" parent="menu_root" action="action_my_model"/>
```

## Security (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_module_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_module_model,my_module.group_manager,1,1,1,1
```

## Manifest
```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Short description',
    'depends': ['base', 'mail'],
    'data': ['security/ir.model.access.csv', 'views/my_model_views.xml'],
    'installable': True,
    'license': 'LGPL-3',
}
```

## Version Visibility
```xml
<!-- v17+: direct --> <field name="x" invisible="state != 'draft'"/>
<!-- v14-16: attrs --> <field name="x" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

---
**Need more?** Read specific skill file from `SKILL.md`
