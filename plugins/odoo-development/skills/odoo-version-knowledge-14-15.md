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
| API | `@api.multi` already removed in 13.0 (fails in 14 and 15) | Only for code ported from <= 12.0 |
| Fields | `track_visibility` legacy in both 14 and 15 (`tracking=True` is the valid parameter in both) | Low - clean up |
| Frontend | Owl 1.4.11 in both; 15.0 adds the ES-module web client (`/** @odoo-module **/`, `@web/core/...`) | High for JS |
| Assets | manifest `assets` key (absent in 14.0) replaces XML templates inheriting `web.assets_*` and the `'qweb'` key; JS QWeb XML goes in `web.assets_qweb` | Medium - Update manifests |
| Python | 3.6+ (14.0) -> 3.7+ (15.0) | Low - Check compatibility |

## Legacy Clean-up: @api.multi

**Not a 14 -> 15 change**: `@api.multi` does not exist in 14.0 either (removed in 13.0). The example below only applies to code ported from 12.0 or older.

### Before (<= 12.0, fails in 14.0 and 15.0)
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

### After (14.0 and 15.0)
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

## Field Tracking Clean-up

`mail.thread` behaves the same in 14.0 and 15.0: only `tracking` is a valid field parameter; `track_visibility` is still tracked but logs "unknown parameter". Do this clean-up in 14.0 already.

### Legacy (logs a warning in 14 and 15)
```python
name = fields.Char(track_visibility='onchange')
state = fields.Selection([...], track_visibility='always')
partner_id = fields.Many2one('res.partner', track_visibility='onchange')
```

### Correct (14.0 and 15.0)
```python
name = fields.Char(tracking=True)
state = fields.Selection([...], tracking=True)
partner_id = fields.Many2one('res.partner', tracking=True)
```

### Migration Notes
- `track_visibility='onchange'` → `tracking=True`
- `track_visibility='always'` → `tracking=True`
- `track_visibility=False` → Remove or `tracking=False`

## New Web Client (v15)

Owl 1.4.11 ships in both 14.0 and 15.0. What 15.0 adds is the new ES-module web client (`/** @odoo-module **/`, `import ... from "@web/core/..."`, services, registries), alongside legacy JS. In 15.0, Owl hooks such as `onMounted` come from `owl.hooks`.

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
| `@api.multi` | Removed already in 13.0 | No decorator needed |
| `@api.one` | Removed already in 13.0 | Use loop in method |
| `track_visibility` | Legacy in 14 and 15 (warning) | `tracking=True` |
| `qweb` in manifest | Deprecated | Use `assets` |
| `website_published` | Deprecated | `is_published` |

## GitHub Verification URLs

```
# v14 reference
https://raw.githubusercontent.com/odoo/odoo/14.0/odoo/api.py

# v15 reference
https://raw.githubusercontent.com/odoo/odoo/15.0/odoo/api.py

# Compare sale.order between versions
https://raw.githubusercontent.com/odoo/odoo/14.0/addons/sale/models/sale_order.py
https://raw.githubusercontent.com/odoo/odoo/15.0/addons/sale/models/sale_order.py
```

## Official guideline deltas 14.0 -> 15.0

Rows of the verified official-guideline matrix that change between 14.0 and 15.0 and are not covered above (assets and Python: see Breaking Changes Summary):

| Topic | 14.0 | 15.0 |
|-------|------|------|
| `Command` class | absent (tuples `(0, 0, vals)`...) | `from odoo import Command` (tuples still work) |
| server QWeb output | no `t-out`; `t-esc` escapes, `t-raw` prints raw | `t-out` (escapes, Markup passes); `t-esc` = alias; `t-raw` deprecated |
| class-level test fixtures | `SavepointCase` (`TransactionCase` has no `cls.env`) | `TransactionCase` (`SavepointCase` is a deprecated alias) |
| JS patching | legacy `.include()` / `.extend()` | `patch(obj, name, ext)` with `this._super` |

Unchanged in both: no `grouped()`, no `odoo.tools.SQL`, no `fields.Domain`, no `@api.private` (RPC guard `check_method_name`), route `auth` user/public/none and `type` http/json, Owl 1.4.11 without `markup`/`htmlEscape`, `t-lang` without `t-call` silently ignored, `read_group(domain, fields, groupby)` returning dicts, `_sql_constraints`, boolean `index`, no `base` injection in `depends`, default test tags `standard` + `at_install`, `_allow_sudo_commands`, restricted `odoo.tools.misc.pickle`.

## Migration Checklist

- [ ] Remove leftover `@api.multi`/`@api.one` (only in code ported from <= 12.0)
- [ ] Replace `track_visibility` with `tracking` (already valid in 14.0)
- [ ] Update manifest `qweb` and XML asset templates to `assets`
- [ ] Optionally switch x2many tuples to `Command` (15.0+)
- [ ] Server QWeb: prefer `t-out`; `t-raw` is deprecated in 15.0
- [ ] Verify field tracking still works
- [ ] Update Python compatibility (3.7+)
- [ ] Consider the new ES-module web client for new frontend code

## Common Migration Errors

### Error: `AttributeError: module 'odoo.api' has no attribute 'multi'`
**Fix**: Remove `@api.multi` decorator (raised in 14.0 too)

### Warning: `Field ...: unknown parameter 'track_visibility'`
**Fix**: Replace with `tracking=True` (same warning in 14.0)

### Error: `qweb key not supported in manifest`
**Fix**: Move to `assets.web.assets_qweb`
