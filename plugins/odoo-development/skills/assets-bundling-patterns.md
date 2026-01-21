# Assets Bundling Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ASSETS BUNDLING PATTERNS                                                    ║
║  JavaScript, CSS, and SCSS asset management                                  ║
║  Use for frontend customization and OWL component registration               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Asset Bundles Overview

### Main Bundles
| Bundle | Used In | Purpose |
|--------|---------|---------|
| `web.assets_backend` | Backend UI | JS/CSS for Odoo backend |
| `web.assets_frontend` | Website | JS/CSS for public website |
| `web.assets_common` | Both | Shared resources |
| `web.assets_qweb` | Both | QWeb templates |
| `point_of_sale.assets` | POS | Point of Sale |

---

## Manifest Asset Declaration

### Basic Assets in __manifest__.py
```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'assets': {
        # Backend assets
        'web.assets_backend': [
            'my_module/static/src/js/**/*.js',
            'my_module/static/src/css/**/*.css',
            'my_module/static/src/scss/**/*.scss',
            'my_module/static/src/xml/**/*.xml',
        ],

        # Website/frontend assets
        'web.assets_frontend': [
            'my_module/static/src/frontend/js/*.js',
            'my_module/static/src/frontend/css/*.css',
        ],

        # QWeb templates for OWL components
        'web.assets_qweb': [
            'my_module/static/src/xml/*.xml',
        ],
    },
}
```

### Odoo 16+ Asset Declaration
```python
{
    'assets': {
        'web.assets_backend': [
            # Include specific files
            'my_module/static/src/js/my_component.js',

            # Include all files with glob pattern
            'my_module/static/src/**/*.js',
            'my_module/static/src/**/*.xml',
            'my_module/static/src/**/*.scss',

            # Prepend (load before others)
            ('prepend', 'my_module/static/src/js/early_load.js'),

            # After specific file
            ('after', 'web/static/src/core/main.js', 'my_module/static/src/js/after_main.js'),

            # Before specific file
            ('before', 'web/static/src/core/main.js', 'my_module/static/src/js/before_main.js'),

            # Replace existing file
            ('replace', 'other_module/static/src/js/old.js', 'my_module/static/src/js/new.js'),

            # Remove file
            ('remove', 'other_module/static/src/js/unwanted.js'),
        ],
    },
}
```

---

## Directory Structure

### Recommended Layout
```
my_module/
├── static/
│   ├── description/
│   │   └── icon.png          # Module icon (256x256)
│   └── src/
│       ├── js/               # JavaScript files
│       │   ├── my_widget.js
│       │   └── my_component.js
│       ├── css/              # Plain CSS
│       │   └── my_styles.css
│       ├── scss/             # SCSS files
│       │   └── my_styles.scss
│       ├── xml/              # QWeb templates
│       │   └── my_templates.xml
│       ├── img/              # Images
│       │   └── logo.png
│       └── fonts/            # Custom fonts
│           └── custom.woff2
```

---

## JavaScript Patterns

### ES6 Module (Odoo 14+)
```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        // Component setup
    }
}

// Register component
registry.category("actions").add("my_module.my_action", MyComponent);
```

### Service Registration
```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";

const myService = {
    dependencies: ["orm", "notification"],

    start(env, { orm, notification }) {
        return {
            async doSomething(recordId) {
                const result = await orm.call("my.model", "my_method", [recordId]);
                notification.add("Done!", { type: "success" });
                return result;
            },
        };
    },
};

registry.category("services").add("myService", myService);
```

### Widget Extension
```javascript
/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    setup() {
        super.setup();
        // Additional setup
    },

    async onRecordSaved(record) {
        await super.onRecordSaved(record);
        // Custom logic after save
        console.log("Record saved:", record.resId);
    },
});
```

---

## CSS/SCSS Patterns

### Basic SCSS
```scss
// my_module/static/src/scss/my_styles.scss

// Use Odoo variables
@import "bootstrap/scss/functions";
@import "bootstrap/scss/variables";

// Module namespace
.o_my_module {
    // Component styles
    .my-card {
        border-radius: $border-radius;
        padding: $spacer;
        background: $white;
        box-shadow: $box-shadow-sm;

        &-header {
            font-weight: $font-weight-bold;
            border-bottom: 1px solid $border-color;
        }

        &-body {
            padding: $spacer;
        }
    }

    // Form customization
    .o_form_view {
        .my-custom-field {
            background-color: $light;
        }
    }

    // Kanban customization
    .o_kanban_view {
        .o_kanban_record {
            &.my-highlight {
                border-left: 3px solid $primary;
            }
        }
    }
}
```

### Dark Mode Support
```scss
// Support dark mode (Odoo 16+)
.o_my_module {
    .my-component {
        background: var(--o-view-background-color);
        color: var(--o-main-text-color);
        border-color: var(--o-color-border);
    }
}

// Or using media query
@media (prefers-color-scheme: dark) {
    .o_my_module {
        .my-component {
            background: #1e1e1e;
        }
    }
}

// Using Odoo's dark mode class
html.dark {
    .o_my_module {
        .my-component {
            background: #2d2d2d;
        }
    }
}
```

---

## QWeb Templates

### OWL Component Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">

    <t t-name="my_module.MyComponent">
        <div class="o_my_module my-component">
            <div class="my-component-header">
                <h3 t-esc="props.title"/>
            </div>
            <div class="my-component-body">
                <t t-if="state.loading">
                    <span class="fa fa-spinner fa-spin"/> Loading...
                </t>
                <t t-else="">
                    <t t-foreach="state.items" t-as="item" t-key="item.id">
                        <div class="item" t-on-click="() => this.onItemClick(item)">
                            <t t-esc="item.name"/>
                        </div>
                    </t>
                </t>
            </div>
            <div class="my-component-footer">
                <button class="btn btn-primary" t-on-click="onSave">
                    Save
                </button>
            </div>
        </div>
    </t>

</templates>
```

### Extending Existing Templates
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">

    <!-- Extend kanban record -->
    <t t-inherit="web.KanbanRecord" t-inherit-mode="extension">
        <xpath expr="//div[hasclass('o_kanban_record_bottom')]" position="inside">
            <t t-if="props.record.resModel === 'my.model'">
                <div class="my-custom-info">
                    <span t-esc="record.my_field.value"/>
                </div>
            </t>
        </xpath>
    </t>

</templates>
```

---

## Legacy JavaScript (pre-Odoo 14)

### AMD Module Pattern
```javascript
odoo.define('my_module.my_widget', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');
    var _t = core._t;

    var MyWidget = Widget.extend({
        template: 'my_module.MyWidgetTemplate',
        events: {
            'click .my-button': '_onButtonClick',
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.options = options || {};
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._renderContent();
            });
        },

        _onButtonClick: function (ev) {
            ev.preventDefault();
            // Handle click
        },

        _renderContent: function () {
            // Render logic
        },
    });

    return MyWidget;
});
```

---

## Asset Compilation

### Debug Mode Assets
```python
# In development, assets are not minified
# Enable debug mode: ?debug=assets

# Or in URL: /web?debug=1
# Or in URL: /web?debug=assets (assets only)
```

### Force Asset Regeneration
```python
# Clear assets cache
def clear_assets_cache(self):
    """Clear compiled assets."""
    self.env['ir.qweb'].clear_caches()

    # Delete asset bundles
    attachments = self.env['ir.attachment'].search([
        ('name', 'ilike', 'web.assets'),
    ])
    attachments.unlink()
```

---

## External Libraries

### Include External Library
```python
{
    'assets': {
        'web.assets_backend': [
            # Include from CDN (not recommended)
            # Better: download and put in static/lib/

            # Local library
            'my_module/static/lib/chart.js/chart.min.js',
            'my_module/static/lib/chart.js/chart.min.css',

            # Then your code that uses it
            'my_module/static/src/js/my_chart.js',
        ],
    },
}
```

### Library Wrapper
```javascript
/** @odoo-module **/

// Wrap external library for Odoo
import { loadJS, loadCSS } from "@web/core/assets";

export async function loadChartJS() {
    await loadJS("/my_module/static/lib/chart.js/chart.min.js");
    return window.Chart;
}

// Usage in component
import { loadChartJS } from "./chart_loader";

class ChartComponent extends Component {
    async setup() {
        this.Chart = await loadChartJS();
    }
}
```

---

## Lazy Loading

### Load Assets On Demand
```javascript
/** @odoo-module **/

import { loadJS, loadCSS } from "@web/core/assets";

export class LazyComponent extends Component {
    static template = "my_module.LazyComponent";

    async setup() {
        // Load heavy library only when needed
        if (this.props.needsChart) {
            await loadJS("/my_module/static/lib/heavy-lib.js");
            await loadCSS("/my_module/static/lib/heavy-lib.css");
        }
    }
}
```

---

## Version-Specific Patterns

### Odoo 17+ (ES Modules)
```javascript
/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ModernComponent extends Component {
    static template = "my_module.ModernComponent";
    static props = {
        recordId: { type: Number },
        onSave: { type: Function, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: null });

        onMounted(() => {
            this.loadData();
        });
    }

    async loadData() {
        this.state.data = await this.orm.read(
            "my.model",
            [this.props.recordId],
            ["name", "value"]
        );
    }
}
```

### Odoo 14-16 (Transition Period)
```javascript
/** @odoo-module **/

// May need to import from different paths
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

// Or legacy compatibility
const { Component } = owl;
```

---

## Testing Assets

### QUnit Tests
```javascript
/** @odoo-module **/

import { getFixture, mount } from "@web/../tests/helpers/utils";
import { MyComponent } from "@my_module/js/my_component";

QUnit.module("MyComponent", (hooks) => {
    let target;

    hooks.beforeEach(() => {
        target = getFixture();
    });

    QUnit.test("renders correctly", async (assert) => {
        await mount(MyComponent, target, {
            props: { title: "Test" },
        });

        assert.containsOnce(target, ".my-component");
        assert.strictEqual(
            target.querySelector(".my-component-header h3").textContent,
            "Test"
        );
    });
});
```

---

## Best Practices

1. **Use namespaced classes** - Prefix with `.o_my_module`
2. **Follow directory structure** - Consistent file organization
3. **Use SCSS variables** - Leverage Bootstrap/Odoo variables
4. **Minimize bundle size** - Only include what's needed
5. **Lazy load heavy libs** - Don't slow initial load
6. **Support dark mode** - Use CSS variables
7. **Test with debug=assets** - Catch compilation errors
8. **Version compatibility** - Check asset syntax for version
9. **Document dependencies** - Note external libraries
10. **Clean up on uninstall** - Remove generated assets
