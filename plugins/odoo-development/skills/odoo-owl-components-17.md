# Odoo OWL Components - Version 17.0 (OWL 2.x)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 17.0 OWL 2.x COMPONENT PATTERNS                                        ║
║  This file contains ONLY Odoo 17.0 OWL patterns.                             ║
║  Same as v16 patterns with minor enhancements.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 17.0 OWL Requirements

- **OWL Version**: 2.x (same as v16)
- **Module System**: ES modules with `/** @odoo-module **/`
- **View Integration**: Works with new Python expression visibility

## v17 OWL Enhancements

v17 OWL is essentially the same as v16 with improved:
- Better error handling
- Enhanced service interfaces
- Improved TypeScript definitions

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
        onConfirm: { type: Function, optional: true },
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
            selectedIds: new Set(),
        });

        // Refs
        this.containerRef = useRef("container");

        // Lifecycle
        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            console.log("Component mounted");
        });
    }

    async loadData() {
        try {
            const data = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state", "amount"],
                { order: "create_date DESC", limit: 100 }
            );
            this.state.data = data;
        } catch (error) {
            this.state.error = error.message;
            this.notification.add("Failed to load data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    toggleSelect(id) {
        if (this.state.selectedIds.has(id)) {
            this.state.selectedIds.delete(id);
        } else {
            this.state.selectedIds.add(id);
        }
        // Force reactivity update
        this.state.selectedIds = new Set(this.state.selectedIds);
    }

    async onBulkAction() {
        const ids = Array.from(this.state.selectedIds);
        if (ids.length === 0) {
            this.notification.add("No records selected", { type: "warning" });
            return;
        }

        await this.orm.call("my.model", "action_confirm", [ids]);
        this.notification.add(`${ids.length} records confirmed`, { type: "success" });
        await this.loadData();
    }

    async onRecordClick(record) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "my.model",
            res_id: record.id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

## Template Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div t-ref="container" class="o_my_component p-3">
            <!-- Loading -->
            <t t-if="state.loading">
                <div class="d-flex justify-content-center p-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </t>

            <!-- Error -->
            <t t-elif="state.error">
                <div class="alert alert-danger d-flex align-items-center">
                    <i class="fa fa-exclamation-triangle me-2"/>
                    <span t-esc="state.error"/>
                </div>
            </t>

            <!-- Content -->
            <t t-else="">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h2>Records</h2>
                    <div>
                        <button class="btn btn-outline-secondary me-2"
                                t-on-click="() => this.loadData()">
                            <i class="fa fa-refresh"/>
                        </button>
                        <button class="btn btn-primary"
                                t-att-disabled="state.selectedIds.size === 0"
                                t-on-click="onBulkAction">
                            Confirm Selected (<t t-esc="state.selectedIds.size"/>)
                        </button>
                    </div>
                </div>

                <t t-if="state.data.length">
                    <div class="list-group">
                        <t t-foreach="state.data" t-as="item" t-key="item.id">
                            <div t-attf-class="list-group-item list-group-item-action d-flex justify-content-between align-items-center {{ state.selectedIds.has(item.id) ? 'active' : '' }}">
                                <div class="form-check">
                                    <input type="checkbox" class="form-check-input"
                                           t-att-checked="state.selectedIds.has(item.id)"
                                           t-on-change="() => this.toggleSelect(item.id)"/>
                                </div>
                                <div class="flex-grow-1 ms-3"
                                     t-on-click="() => this.onRecordClick(item)"
                                     style="cursor: pointer;">
                                    <strong t-esc="item.name"/>
                                    <div class="small text-muted">
                                        Amount: <t t-esc="item.amount"/>
                                    </div>
                                </div>
                                <span t-attf-class="badge bg-{{ item.state === 'done' ? 'success' : 'secondary' }}">
                                    <t t-esc="item.state"/>
                                </span>
                            </div>
                        </t>
                    </div>
                </t>

                <t t-else="">
                    <div class="text-center p-5 text-muted">
                        <i class="fa fa-inbox fa-3x mb-3"/>
                        <p>No records found</p>
                    </div>
                </t>
            </t>
        </div>
    </t>
</templates>
```

## Dialog Component (v17)

```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ConfirmDialog extends Component {
    static template = "my_module.ConfirmDialog";
    static components = { Dialog };
    static props = {
        close: Function,
        title: { type: String, optional: true },
        message: { type: String, optional: true },
        onConfirm: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({ processing: false });
    }

    async onConfirm() {
        this.state.processing = true;
        try {
            if (this.props.onConfirm) {
                await this.props.onConfirm();
            }
            this.props.close();
        } finally {
            this.state.processing = false;
        }
    }
}
```

## v17 Checklist

- [ ] Use `/** @odoo-module **/` directive
- [ ] Import from `@odoo/owl`
- [ ] Use `useService()` for all services
- [ ] Define `static props` for validation
- [ ] Use `registry.category().add()` for registration
- [ ] Include in manifest assets

## AI Agent Instructions (v17 OWL)

When generating Odoo 17.0 OWL components:

1. **USE** same patterns as v16 (OWL 2.x)
2. **START** with `/** @odoo-module **/`
3. **IMPORT** from `@odoo/owl`
4. **USE** `useService()` for services
5. **DEFINE** `static props` for type validation
6. Components work with new view Python expressions
