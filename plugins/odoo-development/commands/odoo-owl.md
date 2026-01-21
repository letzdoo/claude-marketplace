---
name: odoo-owl
description: Generate OWL components for Odoo frontend. Use when user asks to "create owl component", "add widget", "frontend component", "client action".
arguments:
  - name: type
    description: Component type (widget, action, systray, dialog)
    required: false
  - name: name
    description: Component name
    required: false
  - name: version
    description: Target Odoo version
    required: false
input_examples:
  - description: "Create custom widget for Odoo 18"
    arguments:
      type: "widget"
      name: "status_indicator"
      version: "18.0"
  - description: "Generate systray component"
    arguments:
      type: "systray"
      name: "notification_bell"
      version: "17.0"
  - description: "Create client action dialog"
    arguments:
      type: "dialog"
      name: "confirm_action"
---

# /odoo-owl Command

Generate OWL components for Odoo frontend development.

## CRITICAL: OWL VERSION REQUIREMENT

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  OWL versions are COMPLETELY DIFFERENT between Odoo versions!                ║
║                                                                              ║
║  - Odoo 14: NO OWL (use legacy JavaScript)                                   ║
║  - Odoo 15: OWL 1.x (odoo.define syntax)                                     ║
║  - Odoo 16-18: OWL 2.x (ES modules)                                          ║
║  - Odoo 19+: OWL 3.x (ES modules, strict props)                              ║
║                                                                              ║
║  Using wrong OWL version WILL cause JavaScript errors.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Execution Flow

### Step 1: Determine Version

```
What Odoo version are you targeting?
- 14.0 (Legacy JS, no OWL)
- 15.0 (OWL 1.x)
- 16.0-18.0 (OWL 2.x)
- 19.0 (OWL 3.x)
```

### Step 2: Load Version-Specific Skill

```
Read: odoo-development/skills/odoo-owl-components-{version}.md
```

### Step 3: Gather Component Information

- Component type (widget, action, systray, dialog, field)
- Component name
- Required services
- State requirements

### Step 4: Generate Component

## Component Types

### Widget
Custom UI element that can be embedded in views.

### Client Action
Full-page components registered in action registry.

### Systray Item
Icons in the top-right system tray.

### Dialog
Modal dialog components.

### Field Widget
Custom field rendering in forms/lists.

## Output Format

### Odoo 15 (OWL 1.x)
```
static/src/js/{component_name}.js
static/src/xml/{component_name}.xml
static/src/scss/{component_name}.scss
```

### Odoo 16-18 (OWL 2.x)
```
static/src/components/{component_name}/{component_name}.js
static/src/components/{component_name}/{component_name}.xml
static/src/components/{component_name}/{component_name}.scss
```

### Odoo 19 (OWL 3.x)
```
static/src/components/{component_name}/{component_name}.js
static/src/components/{component_name}/{component_name}.xml
static/src/components/{component_name}/{component_name}.scss
```

## Version-Specific Templates

### OWL 1.x (Odoo 15)
```javascript
odoo.define('{module_name}.{ComponentName}', function (require) {
    "use strict";

    const { Component } = owl;
    const { useState } = owl.hooks;
    const { registry } = require("@web/core/registry");

    class {ComponentName} extends Component {
        setup() {
            this.state = useState({ value: 0 });
        }
    }
    {ComponentName}.template = "{module_name}.{ComponentName}";

    registry.category("actions").add("{action_name}", {ComponentName});

    return {ComponentName};
});
```

### OWL 2.x (Odoo 16-18)
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";
    static props = {
        // Optional in OWL 2.x
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, data: [] });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        // Load data using ORM
    }
}

registry.category("actions").add("{action_name}", {ComponentName});
```

### OWL 3.x (Odoo 19)
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";
    static props = {
        // REQUIRED in OWL 3.x
        recordId: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, data: [] });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        // Load data using ORM
    }
}

registry.category("actions").add("{action_name}", {ComponentName});
```

## Manifest Assets

### Odoo 15+
```python
'assets': {
    'web.assets_backend': [
        '{module_name}/static/src/**/*.js',
        '{module_name}/static/src/**/*.xml',
        '{module_name}/static/src/**/*.scss',
    ],
},
```

## Common Services

| Service | Usage |
|---------|-------|
| `orm` | Database operations |
| `action` | Navigation |
| `notification` | User notifications |
| `dialog` | Modal dialogs |
| `user` | Current user info |
| `company` | Company info |
| `rpc` | Low-level RPC calls |

## Example Usage

```
# Generate client action
/odoo-owl action DashboardComponent

# Generate field widget
/odoo-owl widget CustomFieldWidget 18.0

# Interactive
/odoo-owl
```

## AI Agent Instructions

1. **CRITICAL**: Determine Odoo version first
2. **LOAD**: Version-specific OWL skill
3. **VERIFY**: OWL version matches Odoo version
4. **GENERATE**: Version-appropriate component code
5. **INCLUDE**: Template XML and SCSS
6. **UPDATE**: Manifest assets section
