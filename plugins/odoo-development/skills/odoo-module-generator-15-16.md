# Odoo Module Migration Guide: 15.0 → 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODULE MIGRATION: 15.0 → 16.0                                               ║
║  Command class introduced, attrs deprecated, OWL 2.x                         ║
║  VERIFY: https://github.com/odoo/odoo/tree/16.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Migration Overview

| Aspect | v15 | v16 |
|--------|-----|-----|
| X2many commands | Tuple syntax | Command class (recommended) |
| attrs in views | Full support | DEPRECATED (warns) |
| OWL | 1.x | 2.x |
| Python | 3.7-3.9 | 3.8-3.10 |
| create method | @api.model | @api.model_create_multi recommended |

## Key Changes

### 1. Command Class for X2many

```python
# v15 Tuple syntax (still works in v16):
line_ids = [
    (0, 0, {'name': 'Line 1'}),      # Create
    (1, line_id, {'name': 'Updated'}), # Update
    (2, line_id, 0),                  # Delete
    (4, line_id, 0),                  # Link
    (5, 0, 0),                        # Clear
    (6, 0, [id1, id2]),               # Replace
]

# v16 Command class (RECOMMENDED):
from odoo.fields import Command

line_ids = [
    Command.create({'name': 'Line 1'}),      # Create
    Command.update(line_id, {'name': 'Updated'}), # Update
    Command.delete(line_id),                 # Delete
    Command.link(line_id),                   # Link
    Command.clear(),                         # Clear
    Command.set([id1, id2]),                 # Replace
]
```

### 2. attrs DEPRECATED

```xml
<!-- v15 (full support): -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'required': [('state', '=', 'confirmed')],
               'readonly': [('state', '=', 'done')]}"/>

<!-- v16 (RECOMMENDED - prepare for v17): -->
<field name="partner_id"
       invisible="state == 'draft'"
       required="state == 'confirmed'"
       readonly="state == 'done'"/>
```

### 3. OWL 1.x → 2.x

```javascript
// v15 OWL 1.x:
/** @odoo-module **/
const { Component, useState, onMounted } = owl;
const { useService } = require('@web/core/utils/hooks');
const { registry } = require('@web/core/registry');

class MyComponent extends Component {
    setup() {
        this.state = useState({ data: [] });
        this.orm = useService('orm');
        onMounted(() => this.loadData());
    }
}
MyComponent.template = 'my_module.MyComponent';

// v16 OWL 2.x:
/** @odoo-module **/
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({ data: [] });
        this.orm = useService("orm");
        onMounted(() => this.loadData());
    }
}
```

## Manifest Changes

```python
# v15
{
    'name': 'My Module',
    'version': '15.0.1.0.0',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/**/*',
            'my_module/static/src/xml/**/*',
        ],
    },
}

# v16 - Same structure, update version
{
    'name': 'My Module',
    'version': '16.0.1.0.0',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/**/*.js',
            'my_module/static/src/**/*.xml',
            'my_module/static/src/**/*.scss',
        ],
    },
}
```

## Model Migration

### Complete Model Example

```python
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

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        return super().create(vals)

    def create_with_lines(self):
        return self.env['my.model'].create({
            'name': 'Test',
            'line_ids': [
                (0, 0, {'name': 'Line 1'}),
                (0, 0, {'name': 'Line 2'}),
            ],
        })

# v16 Model:
from odoo import models, fields, api, _
from odoo.fields import Command
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
    ], default='draft', tracking=True, index=True)  # Add index

    partner_id = fields.Many2one('res.partner')
    line_ids = fields.One2many('my.model.line', 'model_id')

    @api.model_create_multi  # Recommended in v16
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        return super().create(vals_list)

    def create_with_lines(self):
        return self.env['my.model'].create({
            'name': 'Test',
            'line_ids': [
                Command.create({'name': 'Line 1'}),
                Command.create({'name': 'Line 2'}),
            ],
        })
```

## View Migration

### Form View

```xml
<!-- v15 (with attrs): -->
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
                   attrs="{'required': [('state', '=', 'confirmed')],
                           'readonly': [('state', '=', 'done')]}"/>
        </group>
        <notebook>
            <page string="Lines"
                  attrs="{'invisible': [('state', '=', 'draft')]}">
                <field name="line_ids"/>
            </page>
        </notebook>
    </sheet>
</form>

<!-- v16 (with Python expressions - RECOMMENDED): -->
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                invisible="state != 'draft'"/>
        <button name="action_done" type="object" string="Done"
                invisible="state != 'confirmed'"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <field name="name"/>
            <field name="partner_id"
                   required="state == 'confirmed'"
                   readonly="state == 'done'"/>
        </group>
        <notebook>
            <page string="Lines"
                  invisible="state == 'draft'">
                <field name="line_ids"/>
            </page>
        </notebook>
    </sheet>
</form>
```

### Tree View with Decorations

```xml
<!-- v16: Enhanced tree decorations -->
<tree decoration-danger="state == 'cancelled'"
      decoration-success="state == 'done'"
      decoration-warning="is_overdue">
    <field name="name"/>
    <field name="state" widget="badge"
           decoration-success="state == 'done'"
           decoration-info="state == 'confirmed'"/>
</tree>
```

## OWL Migration (1.x → 2.x)

### Component Migration

```javascript
// v15 OWL 1.x:
/** @odoo-module **/

const { Component, useState, onWillStart, onMounted } = owl;
const { useService } = require('@web/core/utils/hooks');
const { registry } = require('@web/core/registry');

class MyComponent extends Component {
    setup() {
        this.state = useState({
            data: [],
            loading: true,
        });
        this.orm = useService('orm');

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.data = await this.orm.searchRead(
            'my.model', [], ['name', 'state']
        );
        this.state.loading = false;
    }
}

MyComponent.template = 'my_module.MyComponent';
registry.category('actions').add('my_module.my_action', MyComponent);

// v16 OWL 2.x:
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
    };

    setup() {
        this.state = useState({
            data: [],
            loading: true,
        });
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "my.model", [], ["name", "state"],
                { limit: 100 }
            );
        } catch (error) {
            this.notification.add("Failed to load data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onItemClick(item) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "my.model",
            res_id: item.id,
            views: [[false, "form"]],
        });
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

### Template Changes

```xml
<!-- v15 OWL 1.x template: -->
<t t-name="my_module.MyComponent" owl="1">
    <div class="my-component">
        <t t-if="state.loading">
            <div>Loading...</div>
        </t>
        <t t-else="">
            <t t-foreach="state.data" t-as="item" t-key="item.id">
                <div t-on-click="onItemClick(item)" t-esc="item.name"/>
            </t>
        </t>
    </div>
</t>

<!-- v16 OWL 2.x template: -->
<t t-name="my_module.MyComponent">
    <div class="my-component">
        <t t-if="state.loading">
            <div class="text-center p-4">
                <i class="fa fa-spinner fa-spin"/>
            </div>
        </t>
        <t t-else="">
            <div class="list-group">
                <t t-foreach="state.data" t-as="item" t-key="item.id">
                    <a class="list-group-item list-group-item-action"
                       t-on-click="() => this.onItemClick(item)">
                        <span t-esc="item.name"/>
                    </a>
                </t>
            </div>
        </t>
    </div>
</t>
```

## Migration Checklist

### Code Changes
- [ ] Add `from odoo.fields import Command` where needed
- [ ] Replace tuple x2many commands with Command class
- [ ] Consider `@api.model_create_multi` for create methods
- [ ] Add `index=True` to frequently searched fields

### View Changes
- [ ] Replace `attrs=` with Python expression attributes
- [ ] Convert invisible/required/readonly domains to expressions
- [ ] Update page visibility conditions

### OWL Changes
- [ ] Change `require()` to ES `import`
- [ ] Update OWL imports from `@odoo/owl`
- [ ] Add `static template` and `static props`
- [ ] Use arrow functions in t-on-click: `t-on-click="() => this.method(arg)"`

### Manifest Changes
- [ ] Update version to `16.0.x.x.x`
- [ ] Update asset glob patterns if needed

## attrs Conversion Reference

| attrs | Python Expression |
|-------|-------------------|
| `[('state', '=', 'draft')]` | `state == 'draft'` |
| `[('state', '!=', 'draft')]` | `state != 'draft'` |
| `[('state', 'in', ['a', 'b'])]` | `state in ('a', 'b')` |
| `[('state', 'not in', ['a', 'b'])]` | `state not in ('a', 'b')` |
| `[('count', '>', 0)]` | `count > 0` |
| `[('count', '>=', 5)]` | `count >= 5` |
| `[('active', '=', True)]` | `active` |
| `[('active', '=', False)]` | `not active` |
| `['|', ('a', '=', 1), ('b', '=', 2)]` | `a == 1 or b == 2` |
| `['&', ('a', '=', 1), ('b', '=', 2)]` | `a == 1 and b == 2` |

## Common Issues

### DeprecationWarning: attrs is deprecated
**Cause**: Using attrs in v16
**Solution**: Migrate to Python expression attributes

### ImportError: cannot import 'Command'
**Cause**: Using Command in v15
**Solution**: Ensure you're on v16; use tuple syntax for v15

### OWL Import Errors
**Cause**: Using old require() syntax in v16
**Solution**: Use ES `import` statements
