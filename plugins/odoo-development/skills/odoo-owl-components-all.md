# Odoo OWL Components - Core Concepts (All Versions)

This document covers OWL component concepts that are consistent across all Odoo versions. For version-specific implementation details, see the version-specific files.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  OWL VERSION MAPPING                                                         ║
║  • Odoo 15.0: OWL 1.x                                                        ║
║  • Odoo 16.0-18.0: OWL 2.x                                                   ║
║  • Odoo 19.0+: OWL 3.x                                                       ║
║  ALWAYS use the correct OWL version patterns for your target Odoo version!  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## OWL Component Architecture

### Component Lifecycle

All OWL versions follow a similar lifecycle pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Construction → 2. willStart → 3. Render → 4. Mounted       │
│                                                                 │
│  Updates: willUpdateProps → willRender → Rendered → willPatch  │
│                                                                 │
│  Cleanup: willUnmount → willDestroy                            │
└─────────────────────────────────────────────────────────────────┘
```

### Core Concepts

1. **Components**: Self-contained UI units with template, logic, and state
2. **Templates**: QWeb XML templates defining the UI structure
3. **State**: Reactive data that triggers re-renders when changed
4. **Props**: Data passed from parent to child components
5. **Hooks**: Lifecycle callbacks and service access
6. **Services**: Shared functionality (ORM, notifications, actions)

## Component Types in Odoo

### Client Actions
Full-page components triggered by menu actions or programmatic navigation.

Use cases:
- Dashboards
- Custom wizards
- Standalone applications
- Configuration pages

### Field Widgets
Components that render and edit field values in forms and lists.

Use cases:
- Custom field displays
- Complex input components
- Field-specific interactions

### Systray Items
Small components in the top navigation bar.

Use cases:
- Notifications
- Quick actions
- Status indicators
- Menu dropdowns

### View Components
Components that render entire view types (form, list, kanban).

Use cases:
- Custom view types
- View extensions
- Specialized displays

### Dialog Components
Modal components for user interactions.

Use cases:
- Confirmations
- Form popups
- Wizards
- Alerts

## Odoo Services Reference

### ORM Service
Access to database operations:
- `searchRead`: Search and read records
- `read`: Read specific records
- `create`: Create new records
- `write`: Update records
- `unlink`: Delete records
- `call`: Call model methods

### Action Service
Navigation and action execution:
- `doAction`: Execute window/server/client actions
- `switchView`: Change current view
- Navigate between records

### Notification Service
User feedback:
- Success messages
- Warning messages
- Error messages
- Sticky notifications
- Button notifications

### Dialog Service
Modal interactions:
- Confirmation dialogs
- Custom dialogs
- Alert dialogs

### RPC Service
Low-level server communication:
- Direct controller calls
- Custom endpoints
- File uploads

## Template Concepts

### QWeb Directives

| Directive | Purpose |
|-----------|---------|
| `t-if` / `t-elif` / `t-else` | Conditional rendering |
| `t-foreach` / `t-as` / `t-key` | Iteration |
| `t-esc` | Text output (escaped) |
| `t-out` | Raw HTML output |
| `t-att-*` | Dynamic attribute |
| `t-attf-*` | Formatted attribute |
| `t-on-*` | Event handlers |
| `t-ref` | Element reference |
| `t-slot` | Slot definition |
| `t-set-slot` | Slot content |
| `t-component` | Dynamic component |
| `t-props` | Props spreading |

### Event Handling

```xml
<!-- Click event -->
<button t-on-click="onButtonClick">Click</button>

<!-- With parameter -->
<button t-on-click="() => this.onSelect(item.id)">Select</button>

<!-- Prevent default -->
<a t-on-click.prevent="onLinkClick">Link</a>

<!-- Stop propagation -->
<div t-on-click.stop="onDivClick">Div</div>
```

### Conditional Classes

```xml
<!-- Dynamic class -->
<div t-att-class="state.active ? 'active' : ''"/>

<!-- Multiple conditions -->
<div t-attf-class="base-class {{ state.type }} {{ state.active ? 'active' : '' }}"/>

<!-- Object syntax (OWL 2+) -->
<div t-att-class="{ active: state.active, hidden: !state.visible }"/>
```

## Registry System

Odoo uses registries to organize components:

| Registry | Purpose |
|----------|---------|
| `actions` | Client action components |
| `fields` | Field widget components |
| `systray` | Systray item components |
| `views` | View type components |
| `services` | Service providers |
| `main_components` | Root-level components |

## State Management

### Local State
Component-specific reactive state:
- Use for UI-only state
- Triggers re-render on change
- Not shared between components

### Props
Parent-to-child data flow:
- Immutable in child
- Triggers update on change
- Define type validation

### Services
Shared application state:
- Global accessibility
- Business logic encapsulation
- Singleton pattern

## Common Patterns

### Loading States
```
1. Initialize with loading: true
2. Fetch data in willStart/onMounted
3. Set loading: false when complete
4. Show spinner while loading
5. Show content when loaded
```

### Error Handling
```
1. Wrap async operations in try/catch
2. Update error state on failure
3. Show error message to user
4. Provide retry option
5. Log errors for debugging
```

### Form Handling
```
1. Initialize form state
2. Bind inputs to state
3. Validate on change/blur
4. Submit to server
5. Handle response/errors
```

## Asset Organization

### Static File Structure

```
module_name/
└── static/
    └── src/
        ├── components/
        │   ├── component_name/
        │   │   ├── component_name.js
        │   │   ├── component_name.xml
        │   │   └── component_name.scss
        │   └── ...
        ├── fields/
        ├── views/
        └── ...
```

### Manifest Assets

```python
'assets': {
    'web.assets_backend': [
        # JavaScript
        'module_name/static/src/**/*.js',
        # Templates
        'module_name/static/src/**/*.xml',
        # Styles
        'module_name/static/src/**/*.scss',
    ],
    'web.assets_frontend': [
        # Website components
    ],
},
```

## Debugging Tips

1. **Use browser devtools**: Inspect component tree
2. **Console logging**: Log state changes
3. **OWL devtools**: Browser extension for OWL debugging
4. **Network tab**: Monitor RPC calls
5. **Error boundaries**: Catch and display errors

## Performance Best Practices

1. **Minimize re-renders**: Use shouldUpdate when needed
2. **Lazy loading**: Load data on demand
3. **Pagination**: Limit data fetching
4. **Debouncing**: Delay rapid user inputs
5. **Memoization**: Cache computed values

## Testing Components

### Unit Testing
- Test component logic in isolation
- Mock services and dependencies
- Verify state changes

### Integration Testing
- Test component interactions
- Verify RPC calls
- Check DOM updates

### Tour Testing
- End-to-end user flows
- Automated UI testing
- Regression testing

---

**Note**: This document covers concepts that apply to all versions. For version-specific syntax and patterns, refer to the appropriate version-specific file (e.g., `odoo-owl-components-18.md`).
