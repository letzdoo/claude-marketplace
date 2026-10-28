# Odoo OWL Components - Version 15.0 (OWL 1.x)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 OWL 1.x COMPONENT PATTERNS                                        ║
║  This file contains ONLY Odoo 15.0 OWL patterns.                             ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 15.0 OWL Requirements

- **OWL Version**: 1.4 (`addons/web/static/lib/owl/owl.js`)
- **Module System**: `/** @odoo-module **/` ES modules (used by the new `@web/core` client); legacy `odoo.define()` still works for legacy widgets
- **Owl API**: globals `owl` / `owl.hooks` (no `@odoo/owl` import in 15.0)
- **Syntax**: Different from OWL 2.x

## Basic Component Structure (OWL 1.x)

```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component } = owl;
const { useState, useRef, onWillStart, onMounted } = owl.hooks;

export class {ComponentName} extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        // State
        this.state = useState({
            data: [],
            loading: true,
            error: null,
        });

        // Refs
        this.inputRef = useRef("input");

        // Lifecycle
        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            if (this.inputRef.el) {
                this.inputRef.el.focus();
            }
        });
    }

    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "{module_name}.{model_name}", [], ["name", "state", "amount"]
            );
        } catch (error) {
            this.state.error = error.message;
        } finally {
            this.state.loading = false;
        }
    }

    onButtonClick() {
        console.log("Button clicked");
    }

    async onRecordSelect(recordId) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "{module_name}.{model_name}",
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

{ComponentName}.template = "{module_name}.{ComponentName}";

// Register as client action (new web client registry)
registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

## Template Structure (OWL 1.x)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="{module_name}.{ComponentName}" owl="1">
        <div class="o_{component_name}">
            <!-- Loading state -->
            <t t-if="state.loading">
                <div class="o_loading text-center p-4">
                    <i class="fa fa-spinner fa-spin fa-2x"/>
                    <p>Loading...</p>
                </div>
            </t>

            <!-- Error state -->
            <t t-elif="state.error">
                <div class="alert alert-danger">
                    <t t-esc="state.error"/>
                </div>
            </t>

            <!-- Content -->
            <t t-else="">
                <div class="o_content">
                    <div class="o_header d-flex justify-content-between mb-3">
                        <h2>My Component</h2>
                        <button class="btn btn-primary" t-on-click="onButtonClick">
                            Action
                        </button>
                    </div>

                    <t t-if="state.data.length">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>State</th>
                                    <th>Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-foreach="state.data" t-as="item" t-key="item.id">
                                    <tr t-on-click="() => this.onRecordSelect(item.id)"
                                        class="cursor-pointer">
                                        <td t-esc="item.name"/>
                                        <td t-esc="item.state"/>
                                        <td t-esc="item.amount"/>
                                    </tr>
                                </t>
                            </tbody>
                        </table>
                    </t>

                    <t t-else="">
                        <div class="o_nocontent_help text-center p-4">
                            <p>No records found</p>
                        </div>
                    </t>
                </div>

                <input t-ref="input" type="text" class="form-control mt-3"/>
            </t>
        </div>
    </t>
</templates>
```

## OWL 1.x Hooks

```javascript
const { Component, useState, useRef } = owl;
const {
    onWillStart,     // Before first render (async)
    onMounted,       // After mounted to DOM
    onWillUpdateProps, // Before props update
    onWillUnmount,   // Before unmount
    onWillPatch,     // Before DOM patch
    onPatched,       // After DOM patch
} = owl.hooks;

setup() {
    onWillStart(async () => {
        // Async initialization
        await this.loadData();
    });

    onMounted(() => {
        // DOM is available
        console.log("Component mounted");
    });

    onWillUnmount(() => {
        // Cleanup
        console.log("Component will unmount");
    });
}
```

## RPC Service (OWL 1.x)

```javascript
const rpc = require('web.rpc');

// Search and read
const records = await rpc.query({
    model: 'res.partner',
    method: 'search_read',
    args: [[['is_company', '=', true]], ['name', 'email']],
});

// Call custom method
const result = await rpc.query({
    model: 'res.partner',
    method: 'custom_method',
    args: [[1, 2, 3]],
    kwargs: { arg: 'value' },
});

// Create record
const id = await rpc.query({
    model: 'res.partner',
    method: 'create',
    args: [{ name: 'New Partner' }],
});
```

## Field Widget (OWL 1.x)

```javascript
odoo.define('{module_name}.{WidgetName}', function (require) {
    "use strict";

    const { Component } = owl;
    const fieldRegistry = require('web.field_registry');
    const AbstractField = require('web.AbstractField');
    const fieldUtils = require('web.field_utils');

    class {WidgetName} extends Component {
        get value() {
            return this.props.value || '';
        }

        onChange(ev) {
            this.trigger('update-value', ev.target.value);
        }
    }

    {WidgetName}.template = '{module_name}.{WidgetName}';

    // Register widget
    fieldRegistry.add('{widget_name}', {WidgetName});

    return {WidgetName};
});
```

## Manifest Assets (v15)

```python
'assets': {
    'web.assets_backend': [
        '{module_name}/static/src/js/*.js',
        '{module_name}/static/src/scss/*.scss',
    ],
    # 15.0: Owl/QWeb XML templates are loaded from web.assets_qweb
    'web.assets_qweb': [
        '{module_name}/static/src/xml/*.xml',
    ],
},
```

Ship assets in the module; third-party libraries unminified under `static/lib/`. Frontend JS/SCSS goes to `web.assets_frontend`.

## Additional Rules from Odoo's Official Guidelines (verified for 15.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 15.0 source; master-only APIs are translated to the 15.0 equivalent or marked as not available.

- **Escaping / XSS**: Owl 1.4 templates escape with `t-esc`; `t-raw` inserts raw HTML and is an XSS sink for anything not built from trusted constants. 15.0 has no Owl `markup()`, no tagged `markup` template and no `@web/core/utils/html` (`htmlEscape`, `setElementContent`, `htmlJoin` arrive in 16.0+/18.0+). In JS, avoid `innerHTML`, `insertAdjacentHTML` and jQuery `.html()` with dynamic values; escape with underscore's `_.escape(value)` when HTML must be built.
- **No Owl `computed`**: does not exist in Owl 1.4; use getters or compute in handlers.
- **`patch`**: `import { patch } from "@web/core/utils/patch";` then `patch(Target.prototype, "my_module.patch_name", { method() { const res = this._super(...arguments); ... return res; } });` - the patch name is mandatory in 15.0. Legacy widgets are extended with `Widget.include({...})`. Patching is the normal extension mechanism in custom addons.
- **Organize by feature**: `static/src/<feature>/<feature>.js|.xml|.scss` rather than one folder per file type.
- **SCSS**: 4-space indent, classes prefixed `o_<module>_...`, Odoo SCSS variables (`$o-...`), no id selectors, no CSS custom properties on `:root`.

## v15 OWL 1.x Checklist

- [ ] Use `/** @odoo-module **/` for new code (legacy `odoo.define()` only when extending legacy widgets)
- [ ] Take Owl APIs from the `owl` / `owl.hooks` globals
- [ ] Use `useService("orm")` / `useService("action")` in new-client components
- [ ] Register client actions with `registry.category("actions").add()`
- [ ] Add `owl="1"` to template root
- [ ] Include JS/SCSS in `web.assets_backend`, XML in `web.assets_qweb`

## AI Agent Instructions (v15 OWL)

When generating Odoo 15.0 OWL components:

1. **USE** `/** @odoo-module **/` ES modules (legacy `odoo.define()` only for legacy widgets)
2. **USE** `owl.hooks` for lifecycle
3. **USE** `useService("orm")` for RPC in new-client components (`require('web.rpc')` only in legacy code)
4. **USE** `registry.category("actions").add()` for client-action registration
5. **ADD** `owl="1"` to template
6. **DO NOT** import from `@odoo/owl` (Owl 2.x / 16.0+)
7. **DO NOT** use OWL 2.x patterns (`markup()`, `static template` with `@odoo/owl` imports)
