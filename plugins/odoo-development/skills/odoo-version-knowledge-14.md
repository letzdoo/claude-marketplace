# Odoo 14.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 14.0 KNOWLEDGE BASE                                                    ║
║  Last LTS with @api.multi and track_visibility                               ║
║  Released: October 2020                                                      ║
║  VERIFY: https://github.com/odoo/odoo/tree/14.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Release Date | October 2020 |
| Python | 3.6, 3.7, 3.8 |
| PostgreSQL | 10, 11, 12 |
| Frontend | Legacy JS + QWeb |
| OWL | Not available |
| Support | Community: Ongoing, Enterprise: Extended |

## Key Features

### New in Odoo 14
- Improved performance
- Enhanced reporting
- Better mobile experience
- Website improvements
- Accounting enhancements
- Manufacturing improvements

### Technical Stack
- Python 3.6+ (3.8 recommended)
- PostgreSQL 10+
- Werkzeug 0.16
- Jinja2 2.10
- lxml 4.2

## Deprecated Features (Still Working)

### @api.multi Decorator
```python
# DEPRECATED but works in v14
@api.multi
def action_confirm(self):
    for record in self:
        pass

# PREFERRED (implicit multi)
def action_confirm(self):
    for record in self:
        pass
```

### track_visibility
```python
# DEPRECATED but works in v14
state = fields.Selection(..., track_visibility='onchange')

# PREFERRED
state = fields.Selection(..., tracking=True)
```

## Version-Specific Patterns

### Field Definitions
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)

    # track_visibility still works
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], track_visibility='onchange')  # or tracking=True

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
```

### X2many Commands (Tuple Syntax)
```python
# Standard v14 tuple syntax
def create_with_lines(self):
    self.env['my.model'].create({
        'name': 'Test',
        'line_ids': [
            (0, 0, {'name': 'Line 1'}),  # Create
            (1, id, {'name': 'Updated'}), # Update
            (2, id, 0),                   # Delete
            (4, id, 0),                   # Link
            (5, 0, 0),                    # Clear
            (6, 0, [id1, id2]),           # Replace
        ],
    })
```

### attrs in Views
```xml
<!-- v14: Full attrs support -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'required': [('state', '=', 'confirmed')],
               'readonly': [('state', '=', 'done')]}"/>

<button name="action_confirm"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

### Create Method
```python
# v14: Single record create is standard
@api.model
def create(self, vals):
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super(MyModel, self).create(vals)
```

## Frontend Development

### Legacy JavaScript
```javascript
odoo.define('my_module.MyWidget', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');

    var MyWidget = Widget.extend({
        template: 'my_module.MyWidget',
        events: {
            'click .btn-confirm': '_onClickConfirm',
        },

        init: function (parent, options) {
            this._super(parent);
            this.options = options || {};
        },

        start: function () {
            return this._super.apply(this, arguments);
        },

        _onClickConfirm: function (ev) {
            ev.preventDefault();
            // Handle click
        },
    });

    core.action_registry.add('my_module.my_action', MyWidget);

    return MyWidget;
});
```

### QWeb Templates
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyWidget">
        <div class="my-widget">
            <button class="btn btn-primary btn-confirm">
                Confirm
            </button>
        </div>
    </t>
</templates>
```

## Security Configuration

### Access Rights (CSV)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_manager,1,1,1,1
```

### Record Rules
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'child_of', [user.company_id.id])
    ]</field>
</record>
```

## Manifest Structure

```python
{
    'name': 'My Module',
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'summary': 'Module summary',
    'description': """
Module Description
==================
Long description here.
    """,
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        # Order matters!
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/my_model_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## Migration from v13

### Key Changes from v13 to v14
1. Python 3.6+ required (no more Python 2)
2. Performance improvements
3. Improved mail templates
4. Better search panels

### Deprecated in v14
- `@api.multi` (use implicit iteration)
- `track_visibility` (use `tracking=True`)
- `oldname` parameter (use direct migration)

## Preparing for v15 Upgrade

### Code Changes Needed
```python
# 1. Remove @api.multi decorators
# Before (v14)
@api.multi
def action_confirm(self):
    pass

# After (v15)
def action_confirm(self):
    pass

# 2. Replace track_visibility
# Before
state = fields.Selection(..., track_visibility='onchange')

# After
state = fields.Selection(..., tracking=True)
```

### View Changes Needed
- No immediate view changes required for v15
- Consider using `tracking=True` in fields

## Best Practices for v14

1. **Use tracking=True** instead of track_visibility
2. **Don't use @api.multi** explicitly
3. **Use self.env.company** instead of self.env.user.company_id
4. **Test with Python 3.8** for forward compatibility
5. **Document deprecated patterns** in your code

## Common Issues

### Performance
- Use `search_read()` instead of `search()` + `read()`
- Use stored computed fields when possible
- Index frequently searched fields

### Multi-company
```python
company_id = fields.Many2one(
    'res.company',
    default=lambda self: self.env.company,
)

# Domain for related records
partner_id = fields.Many2one(
    'res.partner',
    domain="[('company_id', 'in', [company_id, False])]",
)
```
