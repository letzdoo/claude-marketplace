# Odoo OWL Components - Version Dispatcher

## CRITICAL: VERSION-SPECIFIC REQUIREMENTS

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ⚠️  MANDATORY VERSION MATCHING ⚠️                                          ║
║                                                                              ║
║   OWL versions are COMPLETELY DIFFERENT between Odoo versions.               ║
║   Using wrong OWL patterns WILL cause JavaScript errors.                     ║
║                                                                              ║
║   - Odoo 14: No OWL (legacy JavaScript)                                      ║
║   - Odoo 15: OWL 1.x                                                         ║
║   - Odoo 16-18: OWL 2.x                                                      ║
║   - Odoo 19+: OWL 3.x                                                        ║
║                                                                              ║
║   BEFORE writing ANY OWL component, identify your Odoo version               ║
║   and load the corresponding file. This is NOT optional.                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Files

| Target Version | OWL Version | File to Use |
|----------------|-------------|-------------|
| Odoo 14.0 | No OWL | `odoo-owl-components-14.md` (legacy JS) |
| Odoo 15.0 | OWL 1.x | `odoo-owl-components-15.md` |
| Odoo 16.0 | OWL 2.x | `odoo-owl-components-16.md` |
| Odoo 17.0 | OWL 2.x | `odoo-owl-components-17.md` |
| Odoo 18.0 | OWL 2.x | `odoo-owl-components-18.md` |
| Odoo 19.0 | OWL 3.x | `odoo-owl-components-19.md` |
| All versions | Concepts | `odoo-owl-components-all.md` |

## Migration Guides

| Migration Path | File |
|----------------|------|
| 14.0 → 15.0 | `odoo-owl-components-14-15.md` (Legacy to OWL 1.x) |
| 15.0 → 16.0 | `odoo-owl-components-15-16.md` (OWL 1.x to 2.x) |
| 16.0 → 17.0 | `odoo-owl-components-16-17.md` (OWL 2.x refinements) |
| 17.0 → 18.0 | `odoo-owl-components-17-18.md` (OWL 2.x refinements) |
| 18.0 → 19.0 | `odoo-owl-components-18-19.md` (OWL 2.x to 3.x) |

## Quick Reference: OWL Changes by Version

### Odoo 14 (No OWL)
```javascript
// Legacy jQuery-based
odoo.define('module.widget', function (require) {
    var Widget = require('web.Widget');
    var MyWidget = Widget.extend({
        template: 'MyTemplate',
        start: function() {
            return this._super.apply(this, arguments);
        },
    });
    return MyWidget;
});
```

### Odoo 15 (OWL 1.x)
```javascript
odoo.define('module.Component', function (require) {
    const { Component } = owl;
    const { useState } = owl.hooks;

    class MyComponent extends Component {
        setup() {
            this.state = useState({ count: 0 });
        }
    }
    MyComponent.template = 'module.MyComponent';
    return MyComponent;
});
```

### Odoo 16-18 (OWL 2.x)
```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "module.MyComponent";
    setup() {
        this.state = useState({ count: 0 });
    }
}
registry.category("actions").add("my_action", MyComponent);
```

### Odoo 19+ (OWL 3.x)
```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "module.MyComponent";
    static props = {
        // Explicit prop types required
    };
    setup() {
        this.state = useState({ count: 0 });
    }
}
```

## Key Differences

| Feature | OWL 1.x | OWL 2.x | OWL 3.x |
|---------|---------|---------|---------|
| Module system | `odoo.define` | ES modules | ES modules |
| Import syntax | `require()` | `import` | `import` |
| Hooks | `owl.hooks` | Direct import | Direct import |
| Template | Property | Static property | Static property |
| Props | Implicit | Optional | Required |

## OWL Detection in Existing Code

| Indicator | Version |
|-----------|---------|
| `odoo.define()` | 14 (legacy) or 15 (OWL 1.x) |
| `require('web.Widget')` | 14 (legacy) |
| `const { Component } = owl` | 15 (OWL 1.x) |
| `/** @odoo-module **/` | 16+ (OWL 2.x+) |
| `import { Component }` | 16+ (OWL 2.x+) |
| `static props = {}` required | 19+ (OWL 3.x) |

## Common OWL Patterns

### Registries
- `actions` - Client actions
- `fields` - Field widgets
- `views` - View types
- `systray` - Systray items
- `main_components` - Main UI components

### Services
- `orm` - Database operations
- `action` - Navigation
- `notification` - User notifications
- `dialog` - Modal dialogs
- `user` - Current user info
- `company` - Current company

---

**REMINDER**: OWL versions are NOT backwards compatible. Always verify your Odoo version before implementing OWL components.
