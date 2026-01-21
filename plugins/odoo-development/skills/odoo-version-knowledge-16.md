# Odoo 16.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 16.0 KNOWLEDGE BASE                                                    ║
║  Command class introduced, attrs deprecated, OWL 2.x                         ║
║  Released: October 2022                                                      ║
║  VERIFY: https://github.com/odoo/odoo/tree/16.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Release Date | October 2022 |
| Python | 3.8, 3.9, 3.10 |
| PostgreSQL | 12, 13, 14 |
| Frontend | OWL 2.x |
| Support | Community: Active, Enterprise: Active |

## Key Changes from v15

### Command Class Introduced
```python
from odoo.fields import Command

# NEW v16 syntax
line_ids = [
    Command.create({'name': 'Line 1'}),
    Command.update(id, {'name': 'Updated'}),
    Command.delete(id),
    Command.link(id),
    Command.clear(),
    Command.set([id1, id2]),
]

# Old tuple syntax still works
line_ids = [(0, 0, {'name': 'Line 1'})]
```

### attrs DEPRECATED
```xml
<!-- DEPRECATED in v16 (still works but warns) -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- v16 RECOMMENDED -->
<field name="partner_id"
       invisible="state == 'draft'"/>
```

### OWL 2.x
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: [], loading: true });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.data = await this.orm.searchRead(
            "my.model",
            [],
            ["name", "state"]
        );
        this.state.loading = false;
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

## Key Features

### New in Odoo 16
- OWL 2.x framework
- Command class for x2many
- Improved Knowledge app
- Enhanced Spreadsheet
- Better project management
- WhatsApp integration (Enterprise)

### Technical Stack
- Python 3.8+ (3.10 recommended)
- PostgreSQL 12+
- OWL 2.x framework
- ES modules

## Version-Specific Patterns

### Model Definition
```python
from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True, index=True)

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    partner_id = fields.Many2one(
        'res.partner',
        domain="[('company_id', 'in', [company_id, False])]",
    )

    line_ids = fields.One2many(
        'my.model.line',
        'model_id',
        copy=True,
    )
```

### Using Command Class
```python
from odoo.fields import Command

def create_with_lines(self):
    return self.env['my.model'].create({
        'name': 'New Record',
        'line_ids': [
            Command.create({'name': 'Line 1', 'quantity': 1}),
            Command.create({'name': 'Line 2', 'quantity': 2}),
        ],
    })

def update_lines(self):
    self.write({
        'line_ids': [
            Command.update(self.line_ids[0].id, {'quantity': 5}),
            Command.create({'name': 'New Line'}),
            Command.delete(self.line_ids[-1].id),
        ],
    })

def manage_tags(self):
    # Many2many operations
    self.write({
        'tag_ids': [
            Command.link(tag.id),      # Add existing
            Command.unlink(tag.id),    # Remove (M2M only)
            Command.set([id1, id2]),   # Replace all
            Command.clear(),           # Remove all
        ],
    })
```

### CRUD Methods
```python
@api.model_create_multi
def create(self, vals_list):
    """Batch create - recommended in v16"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)
```

### XML Views (Transition Period)
```xml
<!-- v16 supports both syntaxes -->

<!-- OLD (deprecated, still works) -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- NEW (recommended) -->
<field name="partner_id"
       invisible="state == 'draft'"
       readonly="state == 'done'"
       required="state == 'confirmed'"/>

<!-- Buttons -->
<button name="action_confirm" type="object" string="Confirm"
        invisible="state != 'draft'"/>
```

## OWL 2.x Patterns

### Component with Services
```javascript
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
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");

        this.state = useState({
            data: [],
            loading: true,
            error: null,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state"],
                { limit: 100 }
            );
        } catch (error) {
            this.state.error = error.message;
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
```

### OWL Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="my-component">
            <t t-if="state.loading">
                <div class="text-center p-4">
                    <i class="fa fa-spinner fa-spin fa-2x"/>
                </div>
            </t>
            <t t-elif="state.error">
                <div class="alert alert-danger" t-esc="state.error"/>
            </t>
            <t t-else="">
                <div class="list-group">
                    <t t-foreach="state.data" t-as="item" t-key="item.id">
                        <a class="list-group-item list-group-item-action"
                           t-on-click="() => this.onItemClick(item)">
                            <span t-esc="item.name"/>
                            <span class="badge" t-esc="item.state"/>
                        </a>
                    </t>
                </div>
            </t>
        </div>
    </t>
</templates>
```

## Migration from v15

### Mandatory Changes
- None strictly required (v15 code works)

### Recommended Changes
1. Start using Command class
2. Migrate attrs to conditional attributes
3. Update OWL components to 2.x

### Code Migration
```python
# v15 → v16 changes

# 1. Use Command class (recommended)
# Before
line_ids = [(0, 0, {'name': 'Test'})]

# After
from odoo.fields import Command
line_ids = [Command.create({'name': 'Test'})]

# 2. Use model_create_multi
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

### View Migration
```xml
<!-- v15 → v16 -->

<!-- Before (v15) -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- After (v16) -->
<field name="partner_id"
       invisible="state == 'draft'"/>
```

## Preparing for v17 Upgrade

### Critical: attrs REMOVED in v17
```xml
<!-- THIS BREAKS IN v17 -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- MIGRATE NOW for v17 compatibility -->
<field name="partner_id"
       invisible="state == 'draft'"/>
```

### Critical: create_multi MANDATORY in v17
```python
# v16: Optional but recommended
# v17: MANDATORY

@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

## Best Practices for v16

1. **Use Command class** - For x2many operations
2. **Start migrating attrs** - Use conditional attributes
3. **Use @api.model_create_multi** - Prepare for v17
4. **Build with OWL 2.x** - For new frontend components
5. **Index important fields** - `index=True` on search fields

## Manifest Structure

```python
{
    'name': 'My Module',
    'version': '16.0.1.0.0',
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
            'my_module/static/src/**/*.js',
            'my_module/static/src/**/*.xml',
            'my_module/static/src/**/*.scss',
        ],
    },
    'installable': True,
    'application': False,
}
```

## Common Issues

### attrs Deprecation Warning
```
DeprecationWarning: attrs is deprecated, use invisible/readonly/required attributes
```
Solution: Migrate to conditional attributes

### Command Import
```
ImportError: cannot import name 'Command' from 'odoo.fields'
```
Solution: Ensure you're on v16+; use tuple syntax for v15
