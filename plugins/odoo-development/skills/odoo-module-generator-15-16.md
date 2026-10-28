# Odoo Module Migration Guide: 15.0 → 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODULE MIGRATION: 15.0 → 16.0                                               ║
║  OWL 2.x, XML templates in JS bundles, attrs and Command unchanged           ║
║  VERIFY: https://github.com/odoo/odoo/tree/16.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Migration Overview

| Aspect | v15 | v16 |
|--------|-----|-----|
| X2many commands | Command class (or tuples) | Command class (or tuples) |
| attrs in views | Full support | Full support (direct `invisible="expr"` only from 17.0) |
| OWL | 1.x | 2.x |
| Python (minimum) | 3.7 | 3.7 |
| create method | @api.model_create_multi (single-dict @api.model silently wrapped) | @api.model_create_multi (single-dict @api.model warns) |
| XML templates in assets | `web.assets_qweb` | inside JS bundles (`web.assets_backend`, ...) |
| `t-lang` without `t-call` | silently ignored | SyntaxError |
| `index=` | bool only | + `'btree_not_null'`, `'trigram'` |

## Key Changes

### 1. Command Class for X2many (unchanged: available since 15.0)

```python
# Tuple syntax (works in 15.0 and 16.0):
line_ids = [
    (0, 0, {'name': 'Line 1'}),      # Create
    (1, line_id, {'name': 'Updated'}), # Update
    (2, line_id, 0),                  # Delete
    (4, line_id, 0),                  # Link
    (5, 0, 0),                        # Clear
    (6, 0, [id1, id2]),               # Replace
]

# Command class (15.0 and 16.0, RECOMMENDED):
from odoo import Command

line_ids = [
    Command.create({'name': 'Line 1'}),      # Create
    Command.update(line_id, {'name': 'Updated'}), # Update
    Command.delete(line_id),                 # Delete
    Command.link(line_id),                   # Link
    Command.clear(),                         # Clear
    Command.set([id1, id2]),                 # Replace
]
```

### 2. attrs stays (no change in 16.0)

```xml
<!-- 15.0 and 16.0: attrs is the correct syntax -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'required': [('state', '=', 'confirmed')],
               'readonly': [('state', '=', 'done')]}"/>
```

A direct `invisible="state == 'draft'"` is NOT evaluated as a record condition in 16.0; direct expressions
replace `attrs` only in 17.0.

### 3. OWL 1.x → 2.x

```javascript
// v15 OWL 1.x:
/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
const { Component, useState } = owl;
const { onMounted } = owl.hooks;

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
        ],
        'web.assets_qweb': [
            'my_module/static/src/xml/**/*',
        ],
    },
}

# v16 - XML templates move into the JS bundle, update version
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

    @api.model_create_multi  # also the right form in 15.0
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
        return super().create(vals_list)

    def create_with_lines(self):
        return self.env['my.model'].create({
            'name': 'Test',
            'line_ids': [
                (0, 0, {'name': 'Line 1'}),  # Command.create(...) also works in 15.0
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

<!-- v16: identical - keep attrs. Python-expression attributes
     (invisible="state != 'draft'") only work from 17.0. -->
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

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

const { Component } = owl;
const { useState, onWillStart } = owl.hooks;

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
- [ ] (Optional) Use `Command` instead of tuples (already possible in 15.0)
- [ ] Use `@api.model_create_multi` for create methods (single-dict form warns in 16.0)
- [ ] Replace `sudo(user)` with `with_user(user)`
- [ ] Consider `index='trigram'` / `'btree_not_null'` where useful

### View / QWeb Changes
- [ ] Keep `attrs=` (no change needed in 16.0)
- [ ] Move `t-lang` onto `t-call` nodes (SyntaxError otherwise in 16.0)

### OWL Changes
- [ ] Replace `owl` / `owl.hooks` globals by imports from `@odoo/owl`
- [ ] Update OWL imports from `@odoo/owl`
- [ ] Add `static template` and `static props`
- [ ] Use arrow functions in t-on-click: `t-on-click="() => this.method(arg)"`

### Manifest Changes
- [ ] Update version to `16.0.x.x.x`
- [ ] Move XML template entries from `web.assets_qweb` into `web.assets_backend`

## attrs Conversion Reference (for the later 17.0 migration, not for 16.0)

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

### ImportError: cannot import 'Command'
**Cause**: Only on 14.0 or older (`Command` exists in 15.0 and 16.0)
**Solution**: `from odoo import Command`

### OWL Import Errors
**Cause**: Using the Owl 1 globals (`owl`, `owl.hooks`) in 16.0
**Solution**: `import { Component, useState } from "@odoo/owl"`

## Official guideline deltas 15.0 -> 16.0

| Topic | 15.0 | 16.0 |
|---|---|---|
| route override without `@http.route` | URL silently dropped | auto-decorated + warning (still re-decorate) |
| test fixtures | `TransactionCase`, `TransactionCaseWithUserDemo`, `HttpCaseWithUserDemo`, `new_test_user` | + `BaseCommon`, `BaseUsersCommon` (`user_internal`, `user_portal`) |

Unchanged: no `base` injection into an empty `depends` (declare `['base']`), `license` default `LGPL-3`,
`auto_install` list must be a subset of `depends`, `assets` key, no `<asset>` XML tag,
`security/ir.model.access.csv`, default test tags `standard` + `at_install` (post-install needs
`@tagged('post_install', '-at_install')`), imported TestCase classes and inherited `test_*` methods are collected,
`--test-tags /module:Class`.
