# Odoo OWL Migration Guide: 17.0 → 18.0 (OWL 2.x Enhanced)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  OWL MIGRATION GUIDE: 17.0 → 18.0                                            ║
║  Minor updates - OWL 2.x remains the same with enhancements.                 ║
║  Focus on service improvements and best practices.                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview

The OWL framework in Odoo 18.0 is the same version (2.x) as in Odoo 17.0, with minor enhancements and new services.

## Changes Summary

| Feature | v17 | v18 |
|---------|-----|-----|
| OWL Version | 2.x, no `computed` (use getters / `useState`) | 2.x (enhanced), still no `computed` |
| Services | Standard | Additional services |
| Props validation | Recommended | Recommended |
| Type hints (JSDoc) | Optional | Recommended |

## New/Enhanced Services in v18

### Company Service
```javascript
// v18: New company service
setup() {
    this.company = useService("company");
    // Access current company info
    const currentCompany = this.company.currentCompany;
    const allowedCompanies = this.company.allowedCompanies;
}
```

### Enhanced ORM Service
```javascript
// v18: Enhanced ORM with better options
const records = await this.orm.searchRead(
    "my.model",
    domain,
    fields,
    {
        limit: 100,
        offset: 0,
        order: "create_date DESC",
        context: { ...this.user.context },
    }
);
```

### Enhanced Notification Service
```javascript
// v18: More notification options
this.notification.add("Operation successful", {
    type: "success",
    sticky: false,
    buttons: [
        {
            name: "Undo",
            onClick: () => this.undoAction(),
            primary: true,
        },
        {
            name: "View",
            onClick: () => this.viewRecord(),
        },
    ],
});
```

## Best Practices for v18

### Add JSDoc Type Annotations
```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * @typedef {Object} MyComponentProps
 * @property {number} [recordId]
 * @property {Function} [onConfirm]
 */

export class MyComponent extends Component {
    /** @type {string} */
    static template = "my_module.MyComponent";

    /** @type {MyComponentProps} */
    static props = {
        recordId: { type: Number, optional: true },
        onConfirm: { type: Function, optional: true },
    };

    setup() {
        /** @type {import("@web/core/orm_service").ORM} */
        this.orm = useService("orm");
    }
}
```

### Use Static Props Validation
```javascript
static props = {
    // Required props
    recordId: { type: Number },

    // Optional props with defaults
    mode: { type: String, optional: true },

    // Function props
    onConfirm: { type: Function, optional: true },

    // Array/Object props
    items: { type: Array, optional: true },
    config: { type: Object, optional: true },

    // Union types
    value: { type: [String, Number], optional: true },
};

static defaultProps = {
    mode: "view",
    items: [],
};
```

### Cleanup in onWillUnmount
```javascript
setup() {
    this._cleanup = null;

    onMounted(() => {
        const handler = (e) => this.handleKeydown(e);
        document.addEventListener("keydown", handler);
        this._cleanup = () => document.removeEventListener("keydown", handler);
    });

    onWillUnmount(() => {
        this._cleanup?.();
    });
}
```

## Official guideline deltas 17.0 -> 18.0

Only the official-guideline web rules (Odoo `skills/`, verified against both sources) that change between the two versions:

| Topic | 17.0 | 18.0 |
|-------|------|------|
| HTML helpers | `htmlEscape`/`markup` from `@odoo/owl`, `escape` from `@web/core/utils/strings`; no `@web/core/utils/html` | adds `@web/core/utils/html`: `htmlEscape` (keeps `Markup` values), `isHtmlEmpty`, `setElementContent` (sets `innerHTML` only for `markup()` values, otherwise `textContent`) |

Unchanged in both: `patch(target, extension)` with `super`, organize code by feature, SCSS `o_<module>` classes and assets via the manifest `assets` key.

## Migration Checklist

- [ ] Add JSDoc type annotations (recommended)
- [ ] Add comprehensive `static props` validation
- [ ] Add `static defaultProps` where needed
- [ ] Use new company service if needed
- [ ] Add cleanup logic in `onWillUnmount`
- [ ] Test with new view Python expressions

## No Breaking Changes

v17 OWL components work in v18 without modification. The changes are additive and follow enhanced best practices.
