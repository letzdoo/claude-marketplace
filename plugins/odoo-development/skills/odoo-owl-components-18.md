# Odoo OWL Components - Version 18.0 (OWL 2.x)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 18.0 OWL 2.x COMPONENT PATTERNS                                        ║
║  This file contains ONLY Odoo 18.0 OWL patterns.                             ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 18.0 OWL Requirements

- **OWL Version**: 2.x (enhanced)
- **Module System**: ES modules with `/** @odoo-module **/`
- **Props**: Optional but recommended

## Basic Component Structure

```javascript
/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
        mode: { type: String, optional: true },
    };

    setup() {
        // Services
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.user = useService("user");

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
                "my.model",
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
            res_model: "my.model",
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

// Register as client action
registry.category("actions").add("my_module.my_component", MyComponent);
```

## Template Structure (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="o_my_component">
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

            <!-- Data loaded -->
            <t t-else="">
                <div class="o_content">
                    <!-- Header -->
                    <div class="o_header d-flex justify-content-between mb-3">
                        <h2>My Component</h2>
                        <button class="btn btn-primary"
                                t-on-click="onButtonClick">
                            Action
                        </button>
                    </div>

                    <!-- List -->
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
                                        <td>
                                            <span t-attf-class="badge bg-{{ item.state === 'done' ? 'success' : 'secondary' }}">
                                                <t t-esc="item.state"/>
                                            </span>
                                        </td>
                                        <td t-esc="item.amount"/>
                                    </tr>
                                </t>
                            </tbody>
                        </table>
                    </t>

                    <!-- Empty state -->
                    <t t-else="">
                        <div class="o_nocontent_help text-center p-4">
                            <p class="o_view_nocontent_smiling_face">
                                No records found
                            </p>
                        </div>
                    </t>
                </div>

                <!-- Input with ref -->
                <input t-ref="input" type="text" class="form-control"/>
            </t>
        </div>
    </t>
</templates>
```

## Component Types

### Client Action

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class DashboardAction extends Component {
    static template = "my_module.DashboardAction";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ stats: {} });

        onWillStart(async () => {
            this.state.stats = await this.orm.call(
                "my.model",
                "get_dashboard_stats",
                []
            );
        });
    }
}

// Register as action
registry.category("actions").add("my_module.dashboard", DashboardAction);
```

Action XML:
```xml
<record id="action_dashboard" model="ir.actions.client">
    <field name="name">Dashboard</field>
    <field name="tag">my_module.dashboard</field>
</record>
```

### Field Widget

```javascript
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class MyFieldWidget extends Component {
    static template = "my_module.MyFieldWidget";
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

registry.category("fields").add("my_field_widget", {
    component: MyFieldWidget,
    supportedTypes: ["char"],
});
```

### Systray Item

```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class MySystrayItem extends Component {
    static template = "my_module.MySystrayItem";

    setup() {
        this.notification = useService("notification");
        this.state = useState({ count: 0 });
    }

    onClick() {
        this.notification.add("Systray clicked!", { type: "info" });
    }
}

export const systrayItem = {
    Component: MySystrayItem,
};

registry.category("systray").add("my_module.MySystrayItem", systrayItem, { sequence: 100 });
```

### Dialog Component

```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";

export class MyDialog extends Component {
    static template = "my_module.MyDialog";
    static components = { Dialog };
    static props = {
        close: Function,
        title: { type: String, optional: true },
        onConfirm: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({ value: "" });
    }

    onConfirm() {
        if (this.props.onConfirm) {
            this.props.onConfirm(this.state.value);
        }
        this.props.close();
    }
}
```

Dialog template:
```xml
<t t-name="my_module.MyDialog">
    <Dialog title="props.title or 'My Dialog'">
        <div class="p-3">
            <input type="text" class="form-control"
                   t-model="state.value"
                   placeholder="Enter value..."/>
        </div>
        <t t-set-slot="footer">
            <button class="btn btn-secondary" t-on-click="props.close">
                Cancel
            </button>
            <button class="btn btn-primary" t-on-click="onConfirm">
                Confirm
            </button>
        </t>
    </Dialog>
</t>
```

## OWL Hooks Reference

### Lifecycle Hooks

```javascript
import {
    onWillStart,    // Before first render (async)
    onMounted,      // After mounted to DOM
    onWillUpdateProps, // Before props update
    onWillRender,   // Before each render
    onRendered,     // After each render
    onWillUnmount,  // Before unmount
    onWillDestroy,  // Before destroy
    onError,        // Error handling
} from "@odoo/owl";

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

    onError((error) => {
        console.error("Component error:", error);
    });
}
```

### State and Reactivity

```javascript
import { useState, useRef, reactive } from "@odoo/owl";

setup() {
    // Reactive state
    this.state = useState({
        count: 0,
        items: [],
    });

    // DOM refs
    this.inputRef = useRef("myInput");

    // Reactive object
    this.data = reactive({ value: 0 });
}

// Access ref in methods
onButtonClick() {
    const input = this.inputRef.el;
    input.focus();
}
```

## Services Reference

### ORM Service

```javascript
const orm = useService("orm");

// Search and read
const records = await orm.searchRead("res.partner", [["is_company", "=", true]], ["name", "email"]);

// Read single record
const record = await orm.read("res.partner", [1], ["name"]);

// Create
const id = await orm.create("res.partner", { name: "New Partner" });

// Write
await orm.write("res.partner", [1], { name: "Updated" });

// Unlink
await orm.unlink("res.partner", [1]);

// Call method
const result = await orm.call("res.partner", "custom_method", [[1, 2]], { arg: "value" });

// Search count
const count = await orm.searchCount("res.partner", []);
```

### Action Service

```javascript
const action = useService("action");

// Open form view
await action.doAction({
    type: "ir.actions.act_window",
    res_model: "res.partner",
    res_id: 1,
    views: [[false, "form"]],
    target: "current",
});

// Open list view
await action.doAction({
    type: "ir.actions.act_window",
    res_model: "res.partner",
    views: [[false, "list"], [false, "form"]],
    target: "current",
});

// Execute server action
await action.doAction(actionId);
```

### Notification Service

```javascript
const notification = useService("notification");

// Simple notification
notification.add("Operation successful", { type: "success" });

// With title and options
notification.add("Record created", {
    title: "Success",
    type: "success",
    sticky: false,
    buttons: [
        {
            name: "View",
            onClick: () => this.viewRecord(),
        },
    ],
});

// Types: success, warning, danger, info
```

### Dialog Service

```javascript
const dialog = useService("dialog");

// Confirmation dialog
dialog.add(ConfirmationDialog, {
    title: "Confirm Action",
    body: "Are you sure?",
    confirm: () => this.doAction(),
    cancel: () => {},
});
```

## Manifest Assets (v18)

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/**/*.js',
        'my_module/static/src/**/*.xml',
        'my_module/static/src/**/*.scss',
    ],
    'web.assets_frontend': [
        # For website components
    ],
},
```

## v18 OWL Checklist

- [ ] Use `/** @odoo-module **/` directive
- [ ] Import from `@odoo/owl`
- [ ] Use `useService()` for services
- [ ] Register in appropriate registry
- [ ] Static props definition (optional but recommended)
- [ ] Proper lifecycle hooks usage
- [ ] Include in manifest assets

## AI Agent Instructions (v18 OWL)

When generating Odoo 18.0 OWL components:

1. **ALWAYS** start with `/** @odoo-module **/`
2. **USE** ES module imports from `@odoo/owl`
3. **USE** `useService()` hook for services
4. **REGISTER** components in appropriate registry
5. **DEFINE** static props (recommended)
6. **USE** proper lifecycle hooks
7. **INCLUDE** in manifest assets
