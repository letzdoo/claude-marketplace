# Odoo OWL Components - Version 19.0 (OWL 3.x)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 19.0 OWL 3.x COMPONENT PATTERNS                                        ║
║  This file contains ONLY Odoo 19.0 OWL patterns.                             ║
║  DO NOT use these patterns for other versions.                               ║
║  Note: v19 is in development - patterns may change.                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 19.0 OWL Requirements

- **OWL Version**: 3.x (new version)
- **Module System**: ES modules with `/** @odoo-module **/`
- **Breaking**: Some changes from OWL 2.x

## OWL 2.x → 3.x Changes

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  KEY CHANGES in OWL 3.x:                                                     ║
║  • Enhanced reactivity system                                                ║
║  • Improved props validation                                                 ║
║  • Better TypeScript support                                                 ║
║  • Refined lifecycle hooks                                                   ║
║  • Performance improvements                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Basic Component Structure (OWL 3.x)

```javascript
/** @odoo-module **/

import {
    Component,
    useState,
    useRef,
    onWillStart,
    onMounted,
    onWillUnmount,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * @typedef {Object} MyComponentProps
 * @property {number} [recordId]
 * @property {string} [mode]
 * @property {Function} [onSelect]
 */

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    /** @type {MyComponentProps} */
    static props = {
        recordId: { type: Number, optional: true },
        mode: { type: String, optional: true },
        onSelect: { type: Function, optional: true },
    };

    static defaultProps = {
        mode: "view",
    };

    setup() {
        // Services with typed access
        /** @type {import("@web/core/orm_service").ORM} */
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.user = useService("user");
        this.company = useService("company");

        // Reactive state
        this.state = useState({
            /** @type {Array<Object>} */
            data: [],
            /** @type {boolean} */
            loading: true,
            /** @type {string|null} */
            error: null,
            /** @type {number|null} */
            selectedId: null,
            /** @type {Object} */
            filters: {
                state: null,
                search: "",
            },
        });

        // Refs
        this.containerRef = useRef("container");
        this.searchRef = useRef("search");

        // Cleanup function
        this._cleanup = null;

        // Lifecycle
        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            this._setupEventListeners();
            this.searchRef.el?.focus();
        });

        onWillUnmount(() => {
            this._cleanup?.();
        });
    }

    _setupEventListeners() {
        const handler = (e) => {
            if (e.key === "Escape") {
                this.state.selectedId = null;
            }
        };
        document.addEventListener("keydown", handler);
        this._cleanup = () => document.removeEventListener("keydown", handler);
    }

    /**
     * Load data from server
     * @returns {Promise<void>}
     */
    async loadData() {
        this.state.loading = true;
        this.state.error = null;

        try {
            const domain = this._buildDomain();
            const data = await this.orm.searchRead(
                "my.model",
                domain,
                ["name", "state", "amount", "partner_id"],
                {
                    order: "create_date DESC",
                    limit: 100,
                }
            );
            this.state.data = data;
        } catch (error) {
            this.state.error = error.message || "Failed to load data";
            this.notification.add(this.state.error, {
                type: "danger",
                sticky: true,
            });
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Build search domain from filters
     * @returns {Array}
     */
    _buildDomain() {
        const domain = [];
        if (this.state.filters.state) {
            domain.push(["state", "=", this.state.filters.state]);
        }
        if (this.state.filters.search) {
            domain.push(["name", "ilike", this.state.filters.search]);
        }
        return domain;
    }

    /**
     * Handle item selection
     * @param {Object} item
     */
    onItemSelect(item) {
        this.state.selectedId = item.id;
        if (this.props.onSelect) {
            this.props.onSelect(item.id);
        }
    }

    /**
     * Open record in form view
     * @param {number} id
     */
    async openRecord(id) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "my.model",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    /**
     * Handle search input
     * @param {Event} ev
     */
    onSearchInput(ev) {
        this.state.filters.search = ev.target.value;
        // Debounced reload would be better in production
        this.loadData();
    }

    /**
     * Handle filter change
     * @param {string|null} state
     */
    onFilterChange(state) {
        this.state.filters.state = state;
        this.loadData();
    }

    /**
     * Refresh data
     */
    async onRefresh() {
        await this.loadData();
        this.notification.add("Data refreshed", { type: "success" });
    }
}

// Register as client action
registry.category("actions").add("my_module.my_component", MyComponent);
```

## Template Structure (OWL 3.x)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div t-ref="container" class="o_my_component d-flex flex-column h-100">
            <!-- Header -->
            <div class="o_cp_top p-3 border-bottom bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">Records</h4>
                    <div class="d-flex gap-2">
                        <button class="btn btn-outline-secondary btn-sm"
                                t-on-click="onRefresh"
                                t-att-disabled="state.loading">
                            <i t-attf-class="fa fa-refresh {{ state.loading ? 'fa-spin' : '' }}"/>
                        </button>
                    </div>
                </div>

                <!-- Filters -->
                <div class="d-flex gap-3 mt-3">
                    <div class="flex-grow-1">
                        <input t-ref="search"
                               type="search"
                               class="form-control form-control-sm"
                               placeholder="Search..."
                               t-att-value="state.filters.search"
                               t-on-input="onSearchInput"/>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button t-attf-class="btn {{ !state.filters.state ? 'btn-primary' : 'btn-outline-primary' }}"
                                t-on-click="() => this.onFilterChange(null)">All</button>
                        <button t-attf-class="btn {{ state.filters.state === 'draft' ? 'btn-primary' : 'btn-outline-primary' }}"
                                t-on-click="() => this.onFilterChange('draft')">Draft</button>
                        <button t-attf-class="btn {{ state.filters.state === 'confirmed' ? 'btn-primary' : 'btn-outline-primary' }}"
                                t-on-click="() => this.onFilterChange('confirmed')">Confirmed</button>
                    </div>
                </div>
            </div>

            <!-- Content -->
            <div class="flex-grow-1 overflow-auto p-3">
                <!-- Loading -->
                <t t-if="state.loading">
                    <div class="d-flex justify-content-center align-items-center h-100">
                        <div class="spinner-border text-primary" role="status"/>
                    </div>
                </t>

                <!-- Error -->
                <t t-elif="state.error">
                    <div class="alert alert-danger m-3">
                        <div class="d-flex align-items-center">
                            <i class="fa fa-exclamation-circle fa-2x me-3"/>
                            <div>
                                <strong>Error loading data</strong>
                                <p class="mb-0 mt-1" t-esc="state.error"/>
                            </div>
                        </div>
                        <button class="btn btn-outline-danger btn-sm mt-3"
                                t-on-click="onRefresh">
                            Try Again
                        </button>
                    </div>
                </t>

                <!-- Data -->
                <t t-elif="state.data.length">
                    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
                        <t t-foreach="state.data" t-as="item" t-key="item.id">
                            <div class="col">
                                <div t-attf-class="card h-100 {{ item.id === state.selectedId ? 'border-primary shadow' : '' }}"
                                     t-on-click="() => this.onItemSelect(item)"
                                     style="cursor: pointer;">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-start">
                                            <h5 class="card-title mb-1" t-esc="item.name"/>
                                            <span t-attf-class="badge bg-{{ item.state === 'done' ? 'success' : item.state === 'cancelled' ? 'danger' : 'secondary' }}">
                                                <t t-esc="item.state"/>
                                            </span>
                                        </div>
                                        <p class="card-text text-muted small">
                                            Amount: <strong t-esc="item.amount"/>
                                        </p>
                                        <t t-if="item.partner_id">
                                            <p class="card-text small">
                                                Partner: <t t-esc="item.partner_id[1]"/>
                                            </p>
                                        </t>
                                    </div>
                                    <div class="card-footer bg-transparent">
                                        <button class="btn btn-sm btn-outline-primary w-100"
                                                t-on-click.stop="() => this.openRecord(item.id)">
                                            <i class="fa fa-external-link me-1"/>
                                            Open
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </t>
                    </div>
                </t>

                <!-- Empty -->
                <t t-else="">
                    <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted">
                        <i class="fa fa-inbox fa-4x mb-3"/>
                        <h5>No Records Found</h5>
                        <p>Try adjusting your search or filters</p>
                    </div>
                </t>
            </div>
        </div>
    </t>
</templates>
```

## Field Widget (OWL 3.x)

```javascript
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class CustomFieldWidget extends Component {
    static template = "my_module.CustomFieldWidget";
    static props = {
        ...standardFieldProps,
        customOption: { type: String, optional: true },
    };

    /** @returns {string} */
    get formattedValue() {
        const value = this.props.record.data[this.props.name];
        if (!value) return "";
        // Custom formatting
        return `★ ${value}`;
    }

    /** @returns {boolean} */
    get isReadonly() {
        return this.props.readonly || !this.props.record.isEditable;
    }

    /**
     * @param {Event} ev
     */
    onChange(ev) {
        if (this.isReadonly) return;
        this.props.record.update({ [this.props.name]: ev.target.value });
    }
}

registry.category("fields").add("custom_widget", {
    component: CustomFieldWidget,
    supportedTypes: ["char", "text"],
    extractProps: ({ attrs }) => ({
        customOption: attrs.custom_option,
    }),
});
```

## v19 OWL 3.x Checklist

- [ ] Use `/** @odoo-module **/` directive
- [ ] Import from `@odoo/owl`
- [ ] Add JSDoc type annotations
- [ ] Define comprehensive `static props`
- [ ] Use `static defaultProps` where needed
- [ ] Handle cleanup in `onWillUnmount`
- [ ] Use proper TypeScript-compatible patterns
- [ ] Include in manifest assets

## AI Agent Instructions (v19 OWL)

When generating Odoo 19.0 OWL components:

1. **USE** `/** @odoo-module **/`
2. **IMPORT** from `@odoo/owl`
3. **ADD** JSDoc type annotations
4. **DEFINE** comprehensive `static props`
5. **HANDLE** cleanup in `onWillUnmount`
6. **USE** OWL 3.x enhanced patterns
7. **DO NOT** use OWL 2.x deprecated patterns
