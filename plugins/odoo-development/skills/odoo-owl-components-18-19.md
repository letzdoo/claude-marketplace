# Odoo OWL Migration Guide: 18.0 → 19.0 (OWL 2.x → 3.x)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  OWL MIGRATION GUIDE: 2.x → 3.x                                              ║
║  This is a significant update with enhanced patterns.                        ║
║  Note: v19 is in development - patterns may change.                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Changes Summary

| Feature | OWL 2.x (v18) | OWL 3.x (v19) |
|---------|---------------|---------------|
| Reactivity | Standard | Enhanced |
| Props validation | Runtime | Enhanced + TypeScript-like |
| Type annotations | JSDoc optional | JSDoc recommended |
| Error boundaries | Basic | Enhanced |
| Performance | Good | Improved |

## Enhanced Reactivity in OWL 3.x

### Before (OWL 2.x)
```javascript
setup() {
    this.state = useState({
        items: [],
        selectedIds: new Set(),
    });
}

toggleSelect(id) {
    if (this.state.selectedIds.has(id)) {
        this.state.selectedIds.delete(id);
    } else {
        this.state.selectedIds.add(id);
    }
    // Force reactivity update for Set
    this.state.selectedIds = new Set(this.state.selectedIds);
}
```

### After (OWL 3.x)
```javascript
setup() {
    this.state = useState({
        items: [],
        selectedIds: new Set(),  // Sets are now fully reactive
    });
}

toggleSelect(id) {
    // Direct mutation works with enhanced reactivity
    if (this.state.selectedIds.has(id)) {
        this.state.selectedIds.delete(id);
    } else {
        this.state.selectedIds.add(id);
    }
    // No need to recreate Set
}
```

## Enhanced Props Validation

### Before (OWL 2.x)
```javascript
static props = {
    recordId: { type: Number, optional: true },
    onConfirm: { type: Function, optional: true },
};
```

### After (OWL 3.x)
```javascript
/**
 * @typedef {Object} MyComponentProps
 * @property {number} [recordId]
 * @property {(id: number) => void} [onConfirm]
 * @property {'view' | 'edit'} [mode]
 */

static props = {
    recordId: { type: Number, optional: true },
    onConfirm: { type: Function, optional: true },
    mode: {
        type: String,
        optional: true,
        validate: (value) => ['view', 'edit'].includes(value),
    },
};

static defaultProps = {
    mode: 'view',
};
```

## Complete Migration Example

### Before (OWL 2.x - v18)

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
        this.state = useState({
            data: [],
            loading: true,
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
                ["name", "state"]
            );
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

### After (OWL 3.x - v19)

```javascript
/** @odoo-module **/

import {
    Component,
    useState,
    onWillStart,
    onMounted,
    onWillUnmount,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * @typedef {Object} MyComponentProps
 * @property {number} [recordId] - Optional record ID to load
 * @property {(data: Array) => void} [onDataLoad] - Callback when data loads
 */

/**
 * @typedef {Object} MyComponentState
 * @property {Array<Object>} data
 * @property {boolean} loading
 * @property {string|null} error
 */

export class MyComponent extends Component {
    /** @type {string} */
    static template = "my_module.MyComponent";

    /** @type {MyComponentProps} */
    static props = {
        recordId: { type: Number, optional: true },
        onDataLoad: { type: Function, optional: true },
    };

    setup() {
        /** @type {import("@web/core/orm_service").ORM} */
        this.orm = useService("orm");
        this.notification = useService("notification");

        /** @type {MyComponentState} */
        this.state = useState({
            data: [],
            loading: true,
            error: null,
        });

        // Cleanup function reference
        this._abortController = null;

        onWillStart(async () => {
            await this.loadData();
        });

        onWillUnmount(() => {
            // Cancel pending requests
            this._abortController?.abort();
        });
    }

    /**
     * Load data from server
     * @returns {Promise<void>}
     */
    async loadData() {
        this._abortController = new AbortController();

        try {
            const data = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state"],
                { order: "create_date DESC" }
            );

            this.state.data = data;
            this.state.error = null;

            // Call callback if provided
            this.props.onDataLoad?.(data);
        } catch (error) {
            if (error.name !== 'AbortError') {
                this.state.error = error.message;
                this.notification.add("Failed to load data", { type: "danger" });
            }
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Handle item click
     * @param {Object} item
     */
    onItemClick(item) {
        console.log("Item clicked:", item.id);
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

## Key Differences

### 1. Enhanced Type Annotations
- More comprehensive JSDoc
- Function parameter types
- Return type annotations

### 2. Better Error Handling
- AbortController for cancellation
- Proper cleanup in onWillUnmount
- Error state management

### 3. Props Callback Pattern
```javascript
// v19: Better callback props pattern
static props = {
    onSelect: {
        type: Function,
        optional: true,
    },
};

// Usage with null-safe call
this.props.onSelect?.(selectedId);
```

### 4. State Type Definition
```javascript
/**
 * @typedef {Object} ComponentState
 * @property {Array<Object>} items
 * @property {boolean} loading
 * @property {number|null} selectedId
 */

/** @type {ComponentState} */
this.state = useState({...});
```

## Migration Checklist

- [ ] Add comprehensive JSDoc type annotations
- [ ] Define type for component props (`@typedef`)
- [ ] Define type for component state (`@typedef`)
- [ ] Add return types to all methods
- [ ] Add parameter types to all methods
- [ ] Implement proper cleanup in `onWillUnmount`
- [ ] Use AbortController for cancellable requests
- [ ] Update Set/Map usage (now fully reactive)
- [ ] Add validation functions to props where needed
- [ ] Use `static defaultProps` for optional props

## Common Migration Issues

### Issue: Set/Map not updating UI
**v18**: Required recreating Set/Map for reactivity
**v19**: Direct mutations work, no workaround needed

### Issue: Missing type annotations
**Fix**: Add JSDoc for all methods, state, and props

### Issue: Uncancelled requests on unmount
**Fix**: Use AbortController and cleanup in onWillUnmount
