# Odoo Version Knowledge: 14 to 15 Migration

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  VERSION MIGRATION: 14.0 → 15.0                                              ║
║  Critical changes, breaking changes, and migration patterns                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Category | Change | Impact |
|----------|--------|--------|
| API | `@api.multi` REMOVED | High - Update all methods |
| Fields | `track_visibility` deprecated | Medium - Use `tracking` |
| OWL | OWL 1.x introduced | High - New frontend framework |
| Assets | `assets_backend` pattern change | Medium - Update manifests |
| Python | Python 3.8+ required | Low - Check compatibility |

## Critical Migration: @api.multi Removal

**The most significant breaking change in v15**

### Before (v14)
```python
from odoo import api, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
        return True

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})
```

### After (v15)
```python
from odoo import api, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            order.state = 'sale'
        return True

    def action_cancel(self):
        return self.write({'state': 'cancel'})
```

### Migration Script
```python
# Find and remove @api.multi
import re

def migrate_api_multi(content):
    # Remove @api.multi decorator lines
    content = re.sub(r'\n\s*@api\.multi\n', '\n', content)
    return content
```

## Field Tracking Migration

### Before (v14)
```python
name = fields.Char(track_visibility='onchange')
state = fields.Selection([...], track_visibility='always')
partner_id = fields.Many2one('res.partner', track_visibility='onchange')
```

### After (v15)
```python
name = fields.Char(tracking=True)
state = fields.Selection([...], tracking=True)
partner_id = fields.Many2one('res.partner', tracking=True)
```

### Migration Notes
- `track_visibility='onchange'` → `tracking=True`
- `track_visibility='always'` → `tracking=True`
- `track_visibility=False` → Remove or `tracking=False`

## OWL Introduction (v15)

v15 introduces OWL 1.x as the new frontend framework alongside legacy JS.

### Legacy Widget (v14)
```javascript
odoo.define('my_module.MyWidget', function (require) {
    var Widget = require('web.Widget');

    var MyWidget = Widget.extend({
        template: 'my_module.MyTemplate',
        events: {
            'click .my-button': '_onClick',
        },
        start: function () {
            return this._super.apply(this, arguments);
        },
        _onClick: function () {
            this.do_action({type: 'ir.actions.act_window'});
        },
    });

    return MyWidget;
});
```

### OWL 1.x Component (v15)
```javascript
/** @odoo-module **/

const { Component } = owl;
const { xml } = owl.tags;

class MyComponent extends Component {
    static template = xml`
        <div class="my-component">
            <button t-on-click="onClick">Click Me</button>
        </div>
    `;

    onClick() {
        this.env.services.action.doAction({type: 'ir.actions.act_window'});
    }
}
```

## Asset Bundle Changes

### Before (v14 manifest)
```python
'qweb': [
    'static/src/xml/my_templates.xml',
],
```

### After (v15 manifest)
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/my_component.js',
        'my_module/static/src/scss/my_styles.scss',
    ],
    'web.assets_qweb': [
        'my_module/static/src/xml/my_templates.xml',
    ],
},
```

## Removed/Deprecated Features

| Feature | Status | Replacement |
|---------|--------|-------------|
| `@api.multi` | REMOVED | No decorator needed |
| `@api.one` | REMOVED | Use loop in method |
| `track_visibility` | Deprecated | `tracking=True` |
| `qweb` in manifest | Deprecated | Use `assets` |
| `website_published` | Deprecated | `is_published` |

## GitHub Verification URLs

```
# v14 reference
https://raw.githubusercontent.com/odoo/odoo/14.0/odoo/api.py

# v15 reference (note: @api.multi removed)
https://raw.githubusercontent.com/odoo/odoo/15.0/odoo/api.py

# Compare sale.order between versions
https://raw.githubusercontent.com/odoo/odoo/14.0/addons/sale/models/sale_order.py
https://raw.githubusercontent.com/odoo/odoo/15.0/addons/sale/models/sale_order.py
```

## Migration Checklist

- [ ] Remove all `@api.multi` decorators
- [ ] Remove all `@api.one` decorators (rewrite logic)
- [ ] Replace `track_visibility` with `tracking`
- [ ] Update manifest `qweb` to `assets`
- [ ] Test all button actions work without decorators
- [ ] Verify field tracking still works
- [ ] Update Python compatibility (3.8+)
- [ ] Consider OWL for new frontend components

## Common Migration Errors

### Error: `AttributeError: module 'odoo.api' has no attribute 'multi'`
**Fix**: Remove `@api.multi` decorator

### Error: `Unknown field 'track_visibility'`
**Fix**: Replace with `tracking=True`

### Error: `qweb key not supported in manifest`
**Fix**: Move to `assets.web.assets_qweb`
