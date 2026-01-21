# Odoo OWL Migration Guide: 16.0 → 17.0 (OWL 2.x Continued)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  OWL MIGRATION GUIDE: 16.0 → 17.0                                            ║
║  OWL 2.x continues with enhancements and best practice refinements           ║
║  VERIFY: https://github.com/odoo/odoo/tree/17.0/addons/web/static/src        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview

Odoo 17.0 continues using OWL 2.x with refinements. The main changes are in best practices, service usage, and component patterns rather than framework version changes.

## Changes Summary

| Feature | v16 (OWL 2.x) | v17 (OWL 2.x enhanced) |
|---------|---------------|------------------------|
| OWL Version | 2.x | 2.x (same) |
| Props validation | Recommended | Strongly recommended |
| Services | Standard | Enhanced patterns |
| Error handling | Basic | Improved patterns |
| TypeScript-like JSDoc | Optional | Recommended |

## No Breaking Changes

OWL components written for v16 will work in v17 without modification. The changes are additive best practices.

## Enhanced Patterns for v17

### Props Validation (Strongly Recommended)

```javascript
// v16: Props optional but recommended
export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
    };
}

// v17: Enhanced props with validation
export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
        mode: {
            type: String,
            optional: true,
            validate: (value) => ["view", "edit", "create"].includes(value),
        },
        onConfirm: { type: Function, optional: true },
        config: { type: Object, optional: true },
    };

    static defaultProps = {
        mode: "view",
        config: {},
    };
}
```

### JSDoc Type Annotations (Recommended)

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * @typedef {Object} MyComponentProps
 * @property {number} [recordId] - Optional record ID
 * @property {'view' | 'edit' | 'create'} [mode] - Component mode
 * @property {Function} [onConfirm] - Callback on confirm
 */

/**
 * @typedef {Object} MyComponentState
 * @property {Array<Object>} data - Loaded records
 * @property {boolean} loading - Loading state
 * @property {string|null} error - Error message
 */

export class MyComponent extends Component {
    /** @type {string} */
    static template = "my_module.MyComponent";

    /** @type {MyComponentProps} */
    static props = {
        recordId: { type: Number, optional: true },
        mode: { type: String, optional: true },
        onConfirm: { type: Function, optional: true },
    };

    static defaultProps = {
        mode: "view",
    };

    setup() {
        /** @type {import("@web/core/orm_service").ORM} */
        this.orm = useService("orm");

        /** @type {MyComponentState} */
        this.state = useState({
            data: [],
            loading: true,
            error: null,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    /**
     * Load data from server
     * @returns {Promise<void>}
     */
    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state"],
                { order: "create_date DESC" }
            );
            this.state.error = null;
        } catch (error) {
            this.state.error = error.message;
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

### Enhanced Service Usage

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        // Core services
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.user = useService("user");
        this.company = useService("company");  // v17: Enhanced company service

        // State management
        this.state = useState({
            data: [],
            loading: true,
            selectedIds: new Set(),
        });

        // Cleanup tracking
        this._cleanup = [];

        onWillStart(async () => {
            await this.loadData();
        });

        onWillUnmount(() => {
            this._cleanup.forEach(fn => fn());
        });
    }

    async loadData() {
        try {
            // v17: Enhanced ORM options
            this.state.data = await this.orm.searchRead(
                "my.model",
                [["company_id", "=", this.company.currentCompany.id]],
                ["name", "state", "partner_id"],
                {
                    limit: 100,
                    offset: 0,
                    order: "create_date DESC",
                    context: { ...this.user.context },
                }
            );
        } catch (error) {
            this.notification.add(error.message || "Failed to load data", {
                type: "danger",
                sticky: false,
            });
        } finally {
            this.state.loading = false;
        }
    }

    async onConfirm(recordId) {
        try {
            await this.orm.call("my.model", "action_confirm", [[recordId]]);
            this.notification.add("Record confirmed successfully", {
                type: "success",
            });
            await this.loadData();
        } catch (error) {
            this.notification.add(error.message, { type: "danger" });
        }
    }

    async openRecord(recordId) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "my.model",
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}
```

### Error Handling Patterns

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");

        this.state = useState({
            data: [],
            loading: true,
            error: null,
        });

        onWillStart(async () => {
            await this.loadDataWithRetry();
        });
    }

    /**
     * Load data with retry logic
     * @param {number} retries - Number of retries
     */
    async loadDataWithRetry(retries = 3) {
        for (let i = 0; i < retries; i++) {
            try {
                this.state.data = await this.orm.searchRead(
                    "my.model",
                    [],
                    ["name", "state"]
                );
                this.state.error = null;
                return;
            } catch (error) {
                if (i === retries - 1) {
                    this.state.error = `Failed after ${retries} attempts: ${error.message}`;
                    this.notification.add(this.state.error, { type: "danger" });
                } else {
                    // Wait before retry
                    await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                }
            }
        }
        this.state.loading = false;
    }

    /**
     * Confirm action with dialog
     * @param {number} recordId
     */
    async confirmWithDialog(recordId) {
        const confirmed = await new Promise((resolve) => {
            this.dialog.add(ConfirmationDialog, {
                title: "Confirm Action",
                body: "Are you sure you want to confirm this record?",
                confirm: () => resolve(true),
                cancel: () => resolve(false),
            });
        });

        if (confirmed) {
            await this.doConfirm(recordId);
        }
    }
}
```

## Component Lifecycle Best Practices

```javascript
/** @odoo-module **/

import {
    Component,
    useState,
    onWillStart,
    onMounted,
    onWillUpdateProps,
    onWillUnmount,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: null, loading: true });

        // Cleanup functions
        this._eventListeners = [];

        // Before first render
        onWillStart(async () => {
            if (this.props.recordId) {
                await this.loadRecord(this.props.recordId);
            }
        });

        // After DOM mounted
        onMounted(() => {
            this.setupEventListeners();
        });

        // When props change
        onWillUpdateProps(async (nextProps) => {
            if (nextProps.recordId !== this.props.recordId) {
                this.state.loading = true;
                await this.loadRecord(nextProps.recordId);
            }
        });

        // Cleanup before unmount
        onWillUnmount(() => {
            this.cleanupEventListeners();
        });
    }

    setupEventListeners() {
        const handleKeydown = (e) => {
            if (e.key === "Escape") {
                this.onCancel();
            }
        };
        document.addEventListener("keydown", handleKeydown);
        this._eventListeners.push(() => {
            document.removeEventListener("keydown", handleKeydown);
        });
    }

    cleanupEventListeners() {
        this._eventListeners.forEach(cleanup => cleanup());
        this._eventListeners = [];
    }

    async loadRecord(recordId) {
        try {
            const [record] = await this.orm.read("my.model", [recordId]);
            this.state.data = record;
        } finally {
            this.state.loading = false;
        }
    }
}
```

## Template Patterns for v17

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="my-component h-100 d-flex flex-column">
            <!-- Loading State -->
            <t t-if="state.loading">
                <div class="d-flex justify-content-center align-items-center h-100">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </t>

            <!-- Error State -->
            <t t-elif="state.error">
                <div class="alert alert-danger m-3" role="alert">
                    <i class="fa fa-exclamation-triangle me-2"/>
                    <span t-esc="state.error"/>
                    <button class="btn btn-sm btn-outline-danger ms-3"
                            t-on-click="() => this.loadDataWithRetry()">
                        Retry
                    </button>
                </div>
            </t>

            <!-- Content -->
            <t t-else="">
                <!-- Toolbar -->
                <div class="d-flex p-2 border-bottom bg-light">
                    <button class="btn btn-primary btn-sm me-2"
                            t-on-click="onCreateNew">
                        <i class="fa fa-plus me-1"/>
                        New
                    </button>
                    <button class="btn btn-secondary btn-sm"
                            t-att-disabled="state.selectedIds.size === 0"
                            t-on-click="onBulkAction">
                        Bulk Action
                        <span t-if="state.selectedIds.size > 0"
                              class="badge bg-primary ms-1"
                              t-esc="state.selectedIds.size"/>
                    </button>
                </div>

                <!-- List -->
                <div class="flex-grow-1 overflow-auto">
                    <t t-if="state.data.length === 0">
                        <div class="text-center text-muted p-5">
                            <i class="fa fa-inbox fa-3x mb-3 d-block"/>
                            No records found
                        </div>
                    </t>
                    <t t-else="">
                        <div class="list-group list-group-flush">
                            <t t-foreach="state.data" t-as="item" t-key="item.id">
                                <div class="list-group-item list-group-item-action d-flex align-items-center"
                                     t-att-class="{ 'active': state.selectedIds.has(item.id) }"
                                     t-on-click="() => this.onItemClick(item)">
                                    <input type="checkbox"
                                           class="form-check-input me-3"
                                           t-att-checked="state.selectedIds.has(item.id)"
                                           t-on-click.stop="() => this.toggleSelection(item.id)"/>
                                    <div class="flex-grow-1">
                                        <div class="fw-bold" t-esc="item.name"/>
                                        <small class="text-muted" t-esc="item.state"/>
                                    </div>
                                    <span t-att-class="'badge ' + this.getStateBadgeClass(item.state)"
                                          t-esc="item.state"/>
                                </div>
                            </t>
                        </div>
                    </t>
                </div>
            </t>
        </div>
    </t>
</templates>
```

## Migration Checklist (v16 → v17)

Since there are no breaking changes, focus on improvements:

- [ ] Add comprehensive JSDoc type annotations
- [ ] Add props validation with validate functions
- [ ] Add static defaultProps where applicable
- [ ] Implement proper cleanup in onWillUnmount
- [ ] Use enhanced service patterns
- [ ] Add error handling with retry logic
- [ ] Update templates with Bootstrap 5 classes

## Best Practices Summary

1. **Always validate props** - Use static props with types and validators
2. **Document with JSDoc** - Add type annotations for better IDE support
3. **Handle errors gracefully** - Show user-friendly messages
4. **Clean up resources** - Remove event listeners in onWillUnmount
5. **Use services correctly** - Leverage company, user, and other services
6. **Follow lifecycle hooks** - Use appropriate hooks for each task
