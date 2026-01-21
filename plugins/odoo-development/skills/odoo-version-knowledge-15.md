# Odoo 15.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 KNOWLEDGE BASE                                                    ║
║  @api.multi removed, OWL 1.x introduced                                      ║
║  Released: October 2021                                                      ║
║  VERIFY: https://github.com/odoo/odoo/tree/15.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Release Date | October 2021 |
| Python | 3.7, 3.8, 3.9 |
| PostgreSQL | 10, 11, 12, 13 |
| Frontend | OWL 1.x introduced |
| Support | Community: Ongoing, Enterprise: Active |

## Breaking Changes from v14

### @api.multi REMOVED
```python
# BREAKS IN v15
@api.multi
def action_confirm(self):
    pass

# v15 REQUIRED
def action_confirm(self):
    for record in self:
        pass
```

### track_visibility Deprecated
```python
# DEPRECATED (still works but warns)
state = fields.Selection(..., track_visibility='onchange')

# v15 CORRECT
state = fields.Selection(..., tracking=True)
```

## Key Features

### New in Odoo 15
- OWL Framework 1.x for frontend
- Enhanced Spreadsheet (Enterprise)
- Knowledge app (Enterprise)
- Improved website builder
- Better appointment scheduling
- Enhanced manufacturing

### Technical Stack
- Python 3.7+ (3.9 recommended)
- PostgreSQL 10+
- OWL 1.x framework
- ES6+ JavaScript

## OWL 1.x Introduction

### Component Structure
```javascript
/** @odoo-module **/

const { Component, useState, onMounted } = owl;
const { useService } = require('@web/core/utils/hooks');

class MyComponent extends Component {
    setup() {
        this.state = useState({
            data: [],
            loading: true,
        });
        this.orm = useService('orm');

        onMounted(() => {
            this.loadData();
        });
    }

    async loadData() {
        this.state.data = await this.orm.searchRead(
            'my.model',
            [],
            ['name', 'state']
        );
        this.state.loading = false;
    }
}

MyComponent.template = 'my_module.MyComponent';
```

### OWL Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent" owl="1">
        <div class="my-component">
            <t t-if="state.loading">
                <div class="loading">Loading...</div>
            </t>
            <t t-else="">
                <t t-foreach="state.data" t-as="item" t-key="item.id">
                    <div class="item" t-esc="item.name"/>
                </t>
            </t>
        </div>
    </t>
</templates>
```

## Version-Specific Patterns

### Model Definition
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)  # Use tracking, not track_visibility

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    line_ids = fields.One2many(
        'my.model.line',
        'model_id',
    )
```

### CRUD Methods
```python
@api.model
def create(self, vals):
    """Single record create - standard pattern"""
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals)

# Optional: model_create_multi for batch operations
@api.model_create_multi
def create(self, vals_list):
    """Batch create - optional but recommended"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)

def write(self, vals):
    """Write - no decorator needed"""
    return super().write(vals)

def unlink(self):
    """Delete - no decorator needed"""
    return super().unlink()
```

### Views with attrs
```xml
<!-- v15: attrs fully supported -->
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                attrs="{'invisible': [('state', '!=', 'draft')]}"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <field name="name"/>
            <field name="partner_id"
                   attrs="{'required': [('state', '=', 'confirmed')]}"/>
        </group>
    </sheet>
</form>
```

## Manifest Structure

```python
{
    'name': 'My Module',
    'version': '15.0.1.0.0',
    'category': 'Tools',
    'summary': 'Module summary',
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/**/*',
            'my_module/static/src/xml/**/*',
            'my_module/static/src/scss/**/*',
        ],
    },
    'installable': True,
    'application': False,
}
```

## Asset Management

### New Asset Bundle System
```python
'assets': {
    'web.assets_backend': [
        # JavaScript
        'my_module/static/src/js/my_component.js',

        # OWL Templates
        'my_module/static/src/xml/my_component.xml',

        # SCSS
        'my_module/static/src/scss/my_component.scss',
    ],
    'web.assets_frontend': [
        'my_module/static/src/js/frontend.js',
    ],
}
```

## Migration from v14

### Mandatory Changes
1. Remove all `@api.multi` decorators
2. Replace `track_visibility` with `tracking=True`
3. Update Python version if needed (3.7+)

### Code Migration
```python
# v14 → v15 changes

# 1. Remove @api.multi
# Before
@api.multi
def action_test(self):
    pass

# After
def action_test(self):
    pass

# 2. Change track_visibility
# Before
state = fields.Selection(..., track_visibility='onchange')

# After
state = fields.Selection(..., tracking=True)

# 3. Use super() without arguments
# Before (Python 2 style, works but outdated)
return super(MyModel, self).create(vals)

# After (Python 3 style)
return super().create(vals)
```

## Preparing for v16 Upgrade

### Upcoming Changes
- Command class for x2many operations
- attrs deprecation begins
- OWL 2.x introduction

### Recommended Actions
1. Start using `@api.model_create_multi`
2. Document attrs usage for future migration
3. Plan OWL component upgrades

```python
# Prepare for v16: Use create_multi
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

## Best Practices for v15

1. **Use tracking=True** - Not track_visibility
2. **No @api.multi** - Methods iterate by default
3. **Consider @api.model_create_multi** - For batch creates
4. **Use OWL for new components** - Legacy JS for maintenance
5. **Use asset bundles** - New asset management system
6. **Python 3 super()** - No need for class/self arguments

## Common Patterns

### Computed Fields
```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

### Onchange
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.contact_id = self.partner_id.child_ids[:1]
```

### Action Return
```python
def action_view_lines(self):
    return {
        'type': 'ir.actions.act_window',
        'name': _('Lines'),
        'res_model': 'my.model.line',
        'view_mode': 'tree,form',
        'domain': [('model_id', '=', self.id)],
    }
```

## Common Issues

### @api.multi Errors
```
AttributeError: 'api' object has no attribute 'multi'
```
Solution: Remove all @api.multi decorators

### track_visibility Warnings
```
DeprecationWarning: track_visibility is deprecated
```
Solution: Replace with `tracking=True`
