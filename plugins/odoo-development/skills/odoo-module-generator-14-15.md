# Odoo Module Migration Guide: 14.0 → 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODULE MIGRATION: 14.0 → 15.0                                               ║
║  assets manifest key, Command, t-out, ES-module web client (Owl 1.4.11)      ║
║  VERIFY: https://github.com/odoo/odoo/tree/15.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Migration Overview

| Aspect | v14 | v15 |
|--------|-----|-----|
| @api.multi | Removed (since 13.0) | Removed |
| track_visibility | Legacy (tracked, logs "unknown parameter") | Same as 14 |
| tracking=True | Valid parameter | Valid parameter |
| OWL | Owl 1.4.11 (legacy widgets dominate) | Owl 1.4.11 + new ES-module web client |
| Manifest assets | no `assets` key: inherit `web.assets_backend`/`web.assets_frontend` templates in an XML data file; JS QWeb in `'qweb'` | `assets` key; JS/SCSS in `web.assets_backend`, client QWeb XML in `web.assets_qweb` |
| Python | 3.6+ | 3.7+ |

## Legacy Clean-up (already needed in 14.0)

### 1. @api.multi (removed in 13.0)

```python
# <= 12.0 code (fails in 14.0 and 15.0):
from odoo import models, api

class MyModel(models.Model):
    _name = 'my.model'

    @api.multi
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
        return True

# 14.0 and 15.0:
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
# Legacy (still tracked in 14.0 and 15.0, logs "unknown parameter"):
state = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
], track_visibility='onchange')

name = fields.Char(track_visibility='always')

# 14.0 and 15.0 (valid parameter):
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
            'my_module/static/src/scss/**/*',
        ],
        # 15.0: client-side QWeb templates go in web.assets_qweb
        'web.assets_qweb': [
            'my_module/static/src/xml/**/*',
        ],
    },
}
```

## Model Migration

### Complete Model Example

```python
# Legacy model (<= 12.0 style - @api.multi fails in 14.0; track_visibility warns):
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

# 14.0 / 15.0 Model:
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

    @api.model_create_multi  # BaseModel.create is model_create_multi in 14.0 and 15.0
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        return super().create(vals_list)  # Python 3 style super()
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

### Legacy JavaScript (v14) → ES-module Owl 1.4.11 component (v15)

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

// v15 Owl 1.4.11 Component (ES module, new web client):
/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

const { Component, useState } = owl;
const { onMounted } = owl.hooks;  // Owl 1: lifecycle hooks live in owl.hooks

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

## Official guideline deltas 14.0 -> 15.0

Generator-relevant rows of the verified official-guideline matrix that change between 14.0 and 15.0 and are not covered above (manifest assets and Python: see Migration Overview):

| Topic | 14.0 | 15.0 |
|-------|------|------|
| `Command` import | absent (tuples) | `from odoo import Command` |
| server QWeb templates | `t-esc` / `t-raw`; no `t-out` | `t-out` (`t-esc` alias, `t-raw` deprecated) |
| test base class with class fixtures | `SavepointCase` | `TransactionCase` (`SavepointCase` deprecated alias) |
| JS module format / patching | `odoo.define(...)`, `.include()` | `/** @odoo-module **/` imports; `patch(obj, name, ext)` with `this._super` |

Unchanged in both: no `base` injection for empty `depends`, `license` default `LGPL-3`, `auto_install` list must be a subset of `depends`, no `<asset>` XML tag, default test tags `standard` + `at_install` (post-install = `@tagged('post_install', '-at_install')`), imported test classes and inherited `test_*` methods are collected again, `--test-tags /my_module:TestClass`.

## Migration Checklist

### Code Changes
- [ ] Remove leftover `@api.multi` (only in code ported from <= 12.0; fails in 14.0 too)
- [ ] Replace `track_visibility='onchange'` with `tracking=True` (valid since 14.0)
- [ ] Replace `track_visibility='always'` with `tracking=True`
- [ ] Update `super()` calls to Python 3 style (remove class/self)
- [ ] Update Python version to 3.7+ if needed
- [ ] Rename `SavepointCase` test classes to `TransactionCase`

### Manifest Changes
- [ ] Update version to `15.0.x.x.x`
- [ ] Move asset XML templates and the `'qweb'` key to the `assets` key (`web.assets_backend`, `web.assets_qweb`)
- [ ] Add `'web'` to depends if using web client code

### Optional Improvements
- [ ] Use `@api.model_create_multi` for create overrides (already available in 14.0)
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

### AttributeError: module 'odoo.api' has no attribute 'multi'
**Cause**: @api.multi used (fails in 14.0 and 15.0)
**Solution**: Remove all @api.multi decorators

### Warning: Field ...: unknown parameter 'track_visibility'
**Cause**: track_visibility still used (same warning in 14.0)
**Solution**: Replace with tracking=True

### ImportError: cannot import name 'Component' from 'owl'
**Cause**: Wrong OWL import for v15
**Solution**: Use `const { Component } = owl;` and `const { onMounted } = owl.hooks;`
