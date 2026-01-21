# Odoo OWL Migration Guide: 15.0 → 16.0 (OWL 1.x → 2.x)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  OWL MIGRATION GUIDE: 1.x → 2.x                                              ║
║  This is a MAJOR breaking change migration.                                  ║
║  All OWL components must be rewritten.                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Feature | OWL 1.x (v15) | OWL 2.x (v16) |
|---------|---------------|---------------|
| Module system | `odoo.define()` | ES modules `/** @odoo-module **/` |
| Imports | `require()` | `import` statements |
| Hooks location | `owl.hooks` | Direct from `@odoo/owl` |
| Template declaration | Property on class | `static template` |
| RPC | `require('web.rpc')` | `useService("orm")` |
| Action registration | `core.action_registry` | `registry.category("actions")` |

## Complete Migration Example

### Before (OWL 1.x - v15)

```javascript
odoo.define('my_module.MyComponent', function (require) {
    "use strict";

    const { Component, useState } = owl;
    const { onWillStart, onMounted } = owl.hooks;
    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');
    const rpc = require('web.rpc');

    class MyComponent extends Component {
        setup() {
            this.state = useState({
                records: [],
                loading: true,
            });

            onWillStart(async () => {
                await this.loadRecords();
            });

            onMounted(() => {
                console.log("Component mounted");
            });
        }

        async loadRecords() {
            const records = await rpc.query({
                model: 'my.model',
                method: 'search_read',
                args: [[], ['name', 'state']],
            });
            this.state.records = records;
            this.state.loading = false;
        }

        async onRecordClick(id) {
            await this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'my.model',
                res_id: id,
                views: [[false, 'form']],
                target: 'current',
            });
        }
    }

    MyComponent.template = 'my_module.MyComponent';

    core.action_registry.add('my_module.my_action', MyComponent);

    return MyComponent;
});
```

### After (OWL 2.x - v16)

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            records: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadRecords();
        });

        onMounted(() => {
            console.log("Component mounted");
        });
    }

    async loadRecords() {
        const records = await this.orm.searchRead(
            "my.model",
            [],
            ["name", "state"]
        );
        this.state.records = records;
        this.state.loading = false;
    }

    async onRecordClick(id) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "my.model",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

## Template Migration

### Before (OWL 1.x)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent" owl="1">
        <div class="o_my_component">
            <t t-if="state.loading">Loading...</t>
            <t t-else="">
                <t t-foreach="state.records" t-as="record" t-key="record.id">
                    <div t-on-click="() => this.onRecordClick(record.id)">
                        <t t-esc="record.name"/>
                    </div>
                </t>
            </t>
        </div>
    </t>
</templates>
```

### After (OWL 2.x)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="o_my_component">
            <t t-if="state.loading">Loading...</t>
            <t t-else="">
                <t t-foreach="state.records" t-as="record" t-key="record.id">
                    <div t-on-click="() => this.onRecordClick(record.id)">
                        <t t-esc="record.name"/>
                    </div>
                </t>
            </t>
        </div>
    </t>
</templates>
```

**Note**: Remove `owl="1"` attribute from template root.

## Import Mapping

| OWL 1.x | OWL 2.x |
|---------|---------|
| `const { Component } = owl;` | `import { Component } from "@odoo/owl";` |
| `const { useState } = owl;` | `import { useState } from "@odoo/owl";` |
| `const { onWillStart } = owl.hooks;` | `import { onWillStart } from "@odoo/owl";` |
| `const rpc = require('web.rpc');` | `this.orm = useService("orm");` |
| `const core = require('web.core');` | `import { registry } from "@web/core/registry";` |

## RPC Method Migration

| OWL 1.x RPC | OWL 2.x ORM Service |
|-------------|---------------------|
| `rpc.query({ model, method: 'search_read', args })` | `this.orm.searchRead(model, domain, fields)` |
| `rpc.query({ model, method: 'read', args })` | `this.orm.read(model, ids, fields)` |
| `rpc.query({ model, method: 'create', args })` | `this.orm.create(model, vals)` |
| `rpc.query({ model, method: 'write', args })` | `this.orm.write(model, ids, vals)` |
| `rpc.query({ model, method: 'unlink', args })` | `this.orm.unlink(model, ids)` |
| `rpc.query({ model, method, args, kwargs })` | `this.orm.call(model, method, args, kwargs)` |

## Registration Migration

| OWL 1.x | OWL 2.x |
|---------|---------|
| `core.action_registry.add(key, Component)` | `registry.category("actions").add(key, Component)` |
| `fieldRegistry.add(key, Component)` | `registry.category("fields").add(key, {...})` |
| `widgetRegistry.add(key, Component)` | Depends on widget type |

## Migration Checklist

- [ ] Replace `odoo.define()` with `/** @odoo-module **/`
- [ ] Convert `require()` to `import` statements
- [ ] Import hooks directly from `@odoo/owl` (not `owl.hooks`)
- [ ] Add `static template` to class
- [ ] Replace `rpc.query()` with `useService("orm")` methods
- [ ] Replace `core.action_registry` with `registry.category("actions")`
- [ ] Remove `owl="1"` from templates
- [ ] Update manifest assets to use glob patterns
- [ ] Test all component functionality

## Common Migration Errors

### Error: odoo.define is not defined
**Cause**: Using old module syntax
**Fix**: Replace with ES module syntax

### Error: owl is not defined
**Cause**: Importing from global `owl`
**Fix**: Import from `@odoo/owl`

### Error: rpc is not defined
**Cause**: Using `require('web.rpc')`
**Fix**: Use `useService("orm")` instead
