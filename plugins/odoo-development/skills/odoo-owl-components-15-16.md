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
| Module system | `/** @odoo-module **/` (new client) or legacy `odoo.define()` | `/** @odoo-module **/` |
| Owl API | Owl 1.4, globals `owl` / `owl.hooks` | Owl 2.x, `import ... from "@odoo/owl"` |
| Hooks location | `owl.hooks` | Direct from `@odoo/owl` |
| Template declaration | Property on class | `static template` |
| RPC | `useService("orm")` (legacy code: `require('web.rpc')`) | `useService("orm")` |
| Action registration | `registry.category("actions")` (legacy widgets: `core.action_registry`) | `registry.category("actions")` |
| Templates in assets | `web.assets_qweb`, root needs `owl="1"` | JS bundle, no `owl="1"` |

## Complete Migration Example

### Before (OWL 1.x - v15)

```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component } = owl;
const { useState, onWillStart, onMounted } = owl.hooks;

export class MyComponent extends Component {
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
        this.state.records = await this.orm.searchRead("my.model", [], ["name", "state"]);
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

MyComponent.template = "my_module.MyComponent";

registry.category("actions").add("my_module.my_action", MyComponent);
```

Legacy 15.0 code written with `odoo.define()`, `require('web.rpc')` and `core.action_registry` (legacy
widgets) must be rewritten the same way when moving to 16.0.

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
| `const { useState } = owl.hooks;` | `import { useState } from "@odoo/owl";` |
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
- [ ] Move XML templates from `web.assets_qweb` into the JS bundle
- [ ] Update `patch()` calls only if needed (signature unchanged in 16.0)
- [ ] Test all component functionality

## Official guideline deltas 15.0 -> 16.0

| Topic | 15.0 | 16.0 |
|---|---|---|
| Trusted HTML in templates | Owl 1 `t-raw` (raw sink), no `markup()` | `markup()` + `t-out` |
| JS escape helper | none in `@web/core` (underscore `_.escape`) | `escape` in `@web/core/utils/strings` (Owl `htmlEscape` also available) |

Unchanged: no Owl `computed`; `patch(obj, "patch_name", { ... })` with `this._super(...)` (mandatory patch name);
organize code by feature; SCSS conventions (`o_<module>` classes, `$o-...` variables, 4 spaces).

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
