# Odoo OWL Guide: 18.0 → 19.0 (Owl 2.x in both)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  OWL GUIDE: 18.0 → 19.0                                                      ║
║  Both versions ship Owl 2 (19.0: Owl 2.8.4). No Owl 3 migration.             ║
║  Verified against the 18.0 and 19.0 (final) source trees.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
> Includes rules from Odoo's official skill library (odoo/odoo skills/, branch 20.0), verified against the 18.0 and 19.0 source.

## Changes Summary

| Feature | v18 | v19 |
|---------|-----|-----|
| Owl version | 2.x | 2.8.4 (`addons/web/static/lib/owl/owl.js`) |
| Component API, hooks, props validation | Owl 2 | Owl 2 (unchanged) |
| `@web/core/utils/html` helpers | `htmlEscape`, `setElementContent`, `isHtmlEmpty` | + `htmlJoin`, `htmlSprintf`, `htmlReplace`/`htmlReplaceAll`, `htmlFormatList`, `htmlTrim`, `isMarkup`, `createElementWithContent`, `createDocumentFragmentFromContent` |
| `setInnerHtml` | not available (use `setElementContent`) | not available (use `setElementContent`) |
| `markup` as tagged template escaping placeholders (``markup`<b>${name}</b>` ``) | yes | yes |
| `patch(objToPatch, extension)` with `super` | yes | yes |
| Owl `computed` | not available (derive values with getters) | not available (derive values with getters) |
| User info | `user` from `@web/core/user` (no `user` service) | same |
| Assets | organize `static/src` by feature; declare in manifest `assets` key | same |

The sections below are style recommendations (JSDoc, cleanup, defaultProps); all of them
already work in v18.

## Reactivity of Set/Map

### Recreating the Set (unnecessary)
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

### Direct mutation (works in Owl 2, i.e. v18 and v19)
```javascript
setup() {
    this.state = useState({
        items: [],
        selectedIds: new Set(),  // Owl 2 reactivity tracks Set/Map mutations
    });
}

toggleSelect(id) {
    if (this.state.selectedIds.has(id)) {
        this.state.selectedIds.delete(id);
    } else {
        this.state.selectedIds.add(id);
    }
    // No need to recreate Set
}
```

## Props Validation

### Basic props
```javascript
static props = {
    recordId: { type: Number, optional: true },
    onConfirm: { type: Function, optional: true },
};
```

### With JSDoc, `validate` and `defaultProps` (Owl 2, v18 and v19)
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

### Minimal version (v18 and v19)

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

### Extended version with JSDoc and cleanup (v18 and v19)

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
// Optional callback prop (v18 and v19)
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

## Optional Style Checklist

- [ ] Add JSDoc type annotations where they help
- [ ] Define `static props` (with `optional: true` where needed)
- [ ] Implement proper cleanup in `onWillUnmount`
- [ ] Use `static defaultProps` for optional props
- [ ] Mutate reactive Set/Map directly (no copies needed)

## Common Issues

### Issue: Set/Map not updating UI
Owl 2 (v18 and v19) tracks Set/Map mutations inside `useState`; recreating the Set is
not needed. If the UI does not update, check that the Set lives inside the reactive
state object and is not a copy taken before `useState`.

### Issue: Missing type annotations
**Fix**: Add JSDoc for all methods, state, and props

### Issue: Uncancelled requests on unmount
**Fix**: Use AbortController and cleanup in onWillUnmount
