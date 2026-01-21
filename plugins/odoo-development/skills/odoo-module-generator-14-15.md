# Odoo Module Migration Guide: 14.0 → 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODULE MIGRATION: 14.0 → 15.0                                               ║
║  @api.multi removed, tracking=True standardized, OWL 1.x introduced          ║
║  VERIFY: https://github.com/odoo/odoo/tree/15.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Migration Overview

| Aspect | v14 | v15 |
|--------|-----|-----|
| @api.multi | Deprecated (works) | REMOVED |
| track_visibility | Deprecated (works) | Deprecated (warns) |
| tracking=True | Supported | Standard |
| OWL | Not available | OWL 1.x |
| Python | 3.6-3.8 | 3.7-3.9 |

## Breaking Changes

### 1. @api.multi REMOVED

```python
# v14 (works but deprecated):
from odoo import models, api

class MyModel(models.Model):
    _name = 'my.model'

    @api.multi
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
        return True

# v15 (REQUIRED):
from odoo import models

class MyModel(models.Model):
    _name = 'my.model'

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
        return True
```

### 2. track_visibility → tracking

```python
# v14 (works):
state = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
], track_visibility='onchange')

name = fields.Char(track_visibility='always')

# v15 (RECOMMENDED):
state = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
], tracking=True)

name = fields.Char(tracking=True)
```

## Manifest Changes

```python
# v14
{
    'name': 'My Module',
    'version': '14.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
}

# v15 - Add assets bundle
{
    'name': 'My Module',
    'version': '15.0.1.0.0',
    'depends': ['base', 'mail', 'web'],  # Add 'web' for OWL
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/**/*',
            'my_module/static/src/xml/**/*',
            'my_module/static/src/scss/**/*',
        ],
    },
}
```

## Model Migration

### Complete Model Example

```python
# v14 Model:
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, track_visibility='always')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', track_visibility='onchange')

    partner_id = fields.Many2one('res.partner')
    line_ids = fields.One2many('my.model.line', 'model_id')

    @api.multi
    def action_confirm(self):
        for record in self:
            if not record.line_ids:
                raise UserError(_("Add at least one line."))
            record.state = 'confirmed'
        return True

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        return True

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        return super(MyModel, self).create(vals)

# v15 Model:
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)

    partner_id = fields.Many2one('res.partner')
    line_ids = fields.One2many('my.model.line', 'model_id')

    def action_confirm(self):  # No @api.multi
        for record in self:
            if not record.line_ids:
                raise UserError(_("Add at least one line."))
            record.state = 'confirmed'
        return True

    def action_done(self):  # No @api.multi
        self.write({'state': 'done'})
        return True

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        return super().create(vals)  # Python 3 style super()
```

## View Changes

Views remain largely compatible. No mandatory changes required.

```xml
<!-- v14/v15: Views are compatible -->
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                attrs="{'invisible': [('state', '!=', 'draft')]}"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <field name="name"/>
            <field name="partner_id"/>
        </group>
        <notebook>
            <page string="Lines">
                <field name="line_ids">
                    <tree editable="bottom">
                        <field name="name"/>
                        <field name="quantity"/>
                    </tree>
                </field>
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

## Frontend Migration

### Legacy JavaScript (v14) → OWL 1.x (v15)

```javascript
// v14 Legacy Widget:
odoo.define('my_module.MyWidget', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');

    var MyWidget = Widget.extend({
        template: 'my_module.MyWidget',
        events: {
            'click .btn-action': '_onClickAction',
        },

        init: function (parent, options) {
            this._super(parent);
            this.data = [];
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._loadData();
            });
        },

        _loadData: function () {
            var self = this;
            return this._rpc({
                model: 'my.model',
                method: 'search_read',
                args: [[], ['name', 'state']],
            }).then(function (result) {
                self.data = result;
                self.renderElement();
            });
        },

        _onClickAction: function (ev) {
            ev.preventDefault();
            // Handle action
        },
    });

    core.action_registry.add('my_module.my_action', MyWidget);
    return MyWidget;
});

// v15 OWL 1.x Component:
/** @odoo-module **/

const { Component, useState, onMounted } = owl;
const { useService } = require('@web/core/utils/hooks');
const { registry } = require('@web/core/registry');

class MyComponent extends Component {
    setup() {
        this.state = useState({
            data: [],
            loading: true,
        });
        this.orm = useService('orm');

        onMounted(async () => {
            await this.loadData();
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

    onClickAction(item) {
        // Handle action
    }
}

MyComponent.template = 'my_module.MyComponent';

registry.category('actions').add('my_module.my_action', MyComponent);
```

### QWeb Template Migration

```xml
<!-- v14 Legacy QWeb -->
<t t-name="my_module.MyWidget">
    <div class="my-widget">
        <t t-foreach="widget.data" t-as="item">
            <div class="item" t-att-data-id="item.id">
                <span t-esc="item.name"/>
            </div>
        </t>
    </div>
</t>

<!-- v15 OWL QWeb -->
<t t-name="my_module.MyComponent" owl="1">
    <div class="my-component">
        <t t-if="state.loading">
            <div class="loading">Loading...</div>
        </t>
        <t t-else="">
            <t t-foreach="state.data" t-as="item" t-key="item.id">
                <div class="item" t-on-click="() => this.onClickAction(item)">
                    <span t-esc="item.name"/>
                </div>
            </t>
        </t>
    </div>
</t>
```

## Migration Checklist

### Code Changes
- [ ] Remove all `@api.multi` decorators
- [ ] Replace `track_visibility='onchange'` with `tracking=True`
- [ ] Replace `track_visibility='always'` with `tracking=True`
- [ ] Update `super()` calls to Python 3 style (remove class/self)
- [ ] Update Python version to 3.7+ if needed

### Manifest Changes
- [ ] Update version to `15.0.x.x.x`
- [ ] Add `assets` bundle for JS/CSS/XML
- [ ] Add `'web'` to depends if using OWL

### Optional Improvements
- [ ] Consider `@api.model_create_multi` for batch creates
- [ ] Consider migrating legacy JS widgets to OWL
- [ ] Add `mail.activity.mixin` for activity support

## Search and Replace Patterns

```bash
# Find @api.multi decorators
grep -r "@api.multi" --include="*.py"

# Find track_visibility usage
grep -r "track_visibility" --include="*.py"

# Find old super() patterns
grep -r "super(.*self)" --include="*.py"
```

## Testing

1. **Test all methods** - Ensure no @api.multi errors
2. **Test mail tracking** - Verify tracking=True works
3. **Test create operations** - Ensure create methods work
4. **Test frontend** - If migrating to OWL, test components

## Common Issues

### AttributeError: 'api' object has no attribute 'multi'
**Cause**: @api.multi used in v15
**Solution**: Remove all @api.multi decorators

### DeprecationWarning: track_visibility is deprecated
**Cause**: track_visibility still used
**Solution**: Replace with tracking=True

### ImportError: cannot import name 'Component' from 'owl'
**Cause**: Wrong OWL import for v15
**Solution**: Use `const { Component } = owl;`
