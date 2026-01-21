# Odoo OWL Components - Version 15.0 (OWL 1.x)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 OWL 1.x COMPONENT PATTERNS                                        ║
║  This file contains ONLY Odoo 15.0 OWL patterns.                             ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 15.0 OWL Requirements

- **OWL Version**: 1.x
- **Module System**: `odoo.define()` with require
- **Syntax**: Different from OWL 2.x

## Basic Component Structure (OWL 1.x)

```javascript
odoo.define('{module_name}.{ComponentName}', function (require) {
    "use strict";

    const { Component, useState, useRef } = owl;
    const { onWillStart, onMounted, onWillUnmount } = owl.hooks;
    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');
    const rpc = require('web.rpc');

    class {ComponentName} extends Component {
        setup() {
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
                const data = await rpc.query({
                    model: '{module_name}.{model_name}',
                    method: 'search_read',
                    args: [[], ['name', 'state', 'amount']],
                });
                this.state.data = data;
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
            await this.do_action({
                type: 'ir.actions.act_window',
                res_model: '{module_name}.{model_name}',
                res_id: recordId,
                views: [[false, 'form']],
                target: 'current',
            });
        }
    }

    {ComponentName}.template = '{module_name}.{ComponentName}';

    // Register as action
    core.action_registry.add('{module_name}.{component_name}', {ComponentName});

    return {ComponentName};
});
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
        '{module_name}/static/src/xml/*.xml',
        '{module_name}/static/src/scss/*.scss',
    ],
},
```

## v15 OWL 1.x Checklist

- [ ] Use `odoo.define()` module syntax
- [ ] Import from `owl` and `owl.hooks`
- [ ] Use `require('web.rpc')` for RPC calls
- [ ] Use `core.action_registry.add()` for actions
- [ ] Add `owl="1"` to template root
- [ ] Include in manifest assets

## AI Agent Instructions (v15 OWL)

When generating Odoo 15.0 OWL components:

1. **USE** `odoo.define()` module pattern
2. **USE** `owl.hooks` for lifecycle
3. **USE** `require('web.rpc')` for RPC
4. **USE** `core.action_registry.add()` for registration
5. **ADD** `owl="1"` to template
6. **DO NOT** use ES module imports
7. **DO NOT** use OWL 2.x patterns
