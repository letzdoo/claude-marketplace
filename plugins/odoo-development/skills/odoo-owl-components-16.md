# Odoo OWL Components - Version 16.0 (OWL 2.x)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 16.0 OWL 2.x COMPONENT PATTERNS                                        ║
║  This file contains ONLY Odoo 16.0 OWL patterns.                             ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 16.0 OWL Requirements

- **OWL Version**: 2.x (initial)
- **Module System**: ES modules with `/** @odoo-module **/`
- **Breaking**: Complete rewrite from OWL 1.x

## IMPORTANT: OWL 1.x → 2.x Changes

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  BREAKING CHANGES from v15:                                                  ║
║  • No more odoo.define() - use ES modules                                    ║
║  • No more require() - use import                                            ║
║  • Hooks imported directly from @odoo/owl                                    ║
║  • Services accessed via useService()                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Basic Component Structure (OWL 2.x)

```javascript
/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";
    static props = {
        recordId: { type: Number, optional: true },
        mode: { type: String, optional: true },
    };

    setup() {
        // Services
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

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
            this.inputRef.el?.focus();
        });
    }

    async loadData() {
        try {
            const data = await this.orm.searchRead(
                "{module_name}.{model_name}",
                [],
                ["name", "state", "amount"]
            );
            this.state.data = data;
        } catch (error) {
            this.state.error = error.message;
            this.notification.add("Failed to load data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    onButtonClick() {
        this.notification.add("Button clicked!", { type: "success" });
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

// Register as client action
registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

## Template Structure (OWL 2.x)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="{module_name}.{ComponentName}">
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

## ORM Service (OWL 2.x)

```javascript
const orm = useService("orm");

// Search and read
const records = await orm.searchRead(
    "res.partner",
    [["is_company", "=", true]],
    ["name", "email"]
);

// Read
const record = await orm.read("res.partner", [1], ["name"]);

// Create
const id = await orm.create("res.partner", { name: "New Partner" });

// Write
await orm.write("res.partner", [1], { name: "Updated" });

// Unlink
await orm.unlink("res.partner", [1]);

// Call method
const result = await orm.call(
    "res.partner",
    "custom_method",
    [[1, 2]],
    { arg: "value" }
);

// Search count
const count = await orm.searchCount("res.partner", []);
```

## Field Widget (OWL 2.x)

```javascript
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class {WidgetName} extends Component {
    static template = "{module_name}.{WidgetName}";
    static props = {
        ...standardFieldProps,
    };

    get formattedValue() {
        return this.props.record.data[this.props.name] || "";
    }

    onChange(ev) {
        this.props.record.update({ [this.props.name]: ev.target.value });
    }
}

registry.category("fields").add("{widget_name}", {
    component: {WidgetName},
    supportedTypes: ["char"],
});
```

## Systray Item (OWL 2.x)

```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class {SystrayName} extends Component {
    static template = "{module_name}.{SystrayName}";

    setup() {
        this.notification = useService("notification");
        this.state = useState({ count: 0 });
    }

    onClick() {
        this.notification.add("Systray clicked!", { type: "info" });
    }
}

export const systrayItem = {
    Component: {SystrayName},
};

registry.category("systray").add("{module_name}.{SystrayName}", systrayItem, { sequence: 100 });
```

## Manifest Assets (v16)

```python
'assets': {
    'web.assets_backend': [
        '{module_name}/static/src/**/*.js',
        '{module_name}/static/src/**/*.xml',
        '{module_name}/static/src/**/*.scss',
    ],
},
```

## v16 OWL 2.x Checklist

- [ ] Use `/** @odoo-module **/` directive
- [ ] Import from `@odoo/owl`
- [ ] Use `useService()` for services
- [ ] Use `registry.category().add()` for registration
- [ ] Define `static template` and `static props`
- [ ] Use direct lifecycle hooks (not from `owl.hooks`)
- [ ] Include in manifest assets

## AI Agent Instructions (v16 OWL)

When generating Odoo 16.0 OWL components:

1. **START** with `/** @odoo-module **/`
2. **IMPORT** from `@odoo/owl` directly
3. **USE** `useService()` for orm, action, notification
4. **USE** `registry.category().add()` for registration
5. **DEFINE** `static template` and `static props`
6. **DO NOT** use `odoo.define()`
7. **DO NOT** use `require()`
