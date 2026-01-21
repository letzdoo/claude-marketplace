# Action Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ACTION PATTERNS                                                             ║
║  Window actions, server actions, client actions, and URL actions             ║
║  Use for navigation, automation, and user interface interactions             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Action Types Overview

| Type | Model | Use Case |
|------|-------|----------|
| Window | `ir.actions.act_window` | Open views (form, tree, kanban) |
| Server | `ir.actions.server` | Execute Python code |
| Client | `ir.actions.client` | JavaScript/OWL actions |
| URL | `ir.actions.act_url` | Open external URLs |
| Report | `ir.actions.report` | Generate PDF reports |

---

## Window Actions

### Basic Window Action (XML)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="action_my_model" model="ir.actions.act_window">
        <field name="name">My Records</field>
        <field name="res_model">my.model</field>
        <field name="view_mode">tree,form,kanban</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first record!
            </p>
        </field>
    </record>
</odoo>
```

### Window Action with Domain and Context
```xml
<record id="action_my_model_active" model="ir.actions.act_window">
    <field name="name">Active Records</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
    <field name="domain">[('state', '=', 'active')]</field>
    <field name="context">{
        'default_state': 'active',
        'search_default_my_filter': 1,
        'group_by': 'category_id',
    }</field>
    <field name="limit">80</field>
</record>
```

### Window Action with Specific Views
```xml
<record id="action_my_model_custom" model="ir.actions.act_window">
    <field name="name">My Records (Custom)</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
    <field name="view_ids" eval="[
        (5, 0, 0),
        (0, 0, {'view_mode': 'tree', 'view_id': ref('my_model_view_tree_custom')}),
        (0, 0, {'view_mode': 'form', 'view_id': ref('my_model_view_form_custom')}),
    ]"/>
</record>
```

### Open Specific Record
```xml
<record id="action_open_partner" model="ir.actions.act_window">
    <field name="name">Partner</field>
    <field name="res_model">res.partner</field>
    <field name="view_mode">form</field>
    <field name="res_id" ref="base.main_partner"/>
    <field name="target">current</field>
</record>
```

### Open as Dialog (Wizard)
```xml
<record id="action_wizard" model="ir.actions.act_window">
    <field name="name">My Wizard</field>
    <field name="res_model">my.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
    <field name="context">{
        'active_id': active_id,
        'active_ids': active_ids,
        'active_model': active_model,
    }</field>
</record>
```

### Target Options
| Target | Effect |
|--------|--------|
| `current` | Replace current view (default) |
| `new` | Open in dialog/popup |
| `inline` | Inline in current form |
| `fullscreen` | Fullscreen mode |
| `main` | Open in main content area |

---

## Window Actions from Python

### Return Action Dictionary
```python
def action_open_related(self):
    """Open related records."""
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': 'Related Records',
        'res_model': 'related.model',
        'view_mode': 'tree,form',
        'domain': [('parent_id', '=', self.id)],
        'context': {
            'default_parent_id': self.id,
        },
    }

def action_open_single(self):
    """Open single record in form view."""
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'my.model',
        'res_id': self.id,
        'view_mode': 'form',
        'target': 'current',
    }

def action_open_wizard(self):
    """Open wizard with context."""
    return {
        'type': 'ir.actions.act_window',
        'name': 'Configure',
        'res_model': 'my.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_record_id': self.id,
            'default_amount': self.amount_total,
        },
    }
```

### Use Existing Action
```python
def action_open_partners(self):
    """Use predefined action."""
    action = self.env.ref('base.action_partner_form').read()[0]
    action['domain'] = [('id', 'in', self.partner_ids.ids)]
    action['context'] = {'default_company_id': self.company_id.id}
    return action
```

---

## Server Actions

### Execute Python Code
```xml
<record id="action_mark_done" model="ir.actions.server">
    <field name="name">Mark as Done</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list,form</field>
    <field name="state">code</field>
    <field name="code">
if records:
    records.write({'state': 'done'})
    </field>
</record>
```

### Server Action with Notification
```xml
<record id="action_process_with_notify" model="ir.actions.server">
    <field name="name">Process Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
count = len(records)
records.action_process()
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Success',
        'message': f'Processed {count} records.',
        'type': 'success',
        'sticky': False,
    }
}
    </field>
</record>
```

### Server Action Opening Window
```xml
<record id="action_open_related" model="ir.actions.server">
    <field name="name">Open Related</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
if records:
    action = {
        'type': 'ir.actions.act_window',
        'name': 'Related Records',
        'res_model': 'related.model',
        'view_mode': 'tree,form',
        'domain': [('parent_id', 'in', records.ids)],
    }
    </field>
</record>
```

### Server Action Types
| State | Description |
|-------|-------------|
| `code` | Execute Python code |
| `object_create` | Create new record |
| `object_write` | Update records |
| `multi` | Execute multiple actions |
| `email` | Send email |
| `sms` | Send SMS |
| `next_activity` | Schedule activity |

---

## Client Actions

### Display Notification
```python
def action_notify(self):
    """Show notification to user."""
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Information',
            'message': 'Operation completed successfully.',
            'type': 'success',  # success, warning, danger, info
            'sticky': False,
            'next': {'type': 'ir.actions.act_window_close'},
        }
    }
```

### Notification with Link
```python
def action_notify_with_link(self):
    """Notification with clickable link."""
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Created',
            'message': 'Record created successfully.',
            'type': 'success',
            'links': [{
                'label': 'View Record',
                'url': f'/web#id={self.id}&model={self._name}&view_type=form',
            }],
        }
    }
```

### Reload Page
```python
def action_reload(self):
    """Reload current view."""
    return {
        'type': 'ir.actions.client',
        'tag': 'reload',
    }
```

### Custom Client Action (OWL)
```xml
<!-- Register client action -->
<record id="action_custom_dashboard" model="ir.actions.client">
    <field name="name">My Dashboard</field>
    <field name="tag">my_module.dashboard</field>
</record>
```

```javascript
/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

class MyDashboard extends Component {
    static template = "my_module.Dashboard";
}

registry.category("actions").add("my_module.dashboard", MyDashboard);
```

---

## URL Actions

### Open External URL
```xml
<record id="action_open_docs" model="ir.actions.act_url">
    <field name="name">Documentation</field>
    <field name="url">https://www.odoo.com/documentation</field>
    <field name="target">new</field>
</record>
```

### Dynamic URL from Python
```python
def action_open_external(self):
    """Open external URL."""
    return {
        'type': 'ir.actions.act_url',
        'url': f'https://example.com/record/{self.external_id}',
        'target': 'new',  # or 'self' for same window
    }

def action_download_file(self):
    """Download file via URL."""
    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content/{attachment.id}?download=true',
        'target': 'self',
    }
```

---

## Action Binding

### Bind to Model (Action Menu)
```xml
<record id="action_batch_update" model="ir.actions.server">
    <field name="name">Batch Update</field>
    <field name="model_id" ref="model_my_model"/>
    <!-- Binding creates "Action" menu entry -->
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list</field>
    <field name="state">code</field>
    <field name="code">records.action_batch_update()</field>
</record>
```

### Binding View Types
| Type | Where Available |
|------|-----------------|
| `list` | Tree/list view only |
| `form` | Form view only |
| `list,form` | Both views |

---

## Close Action

### Close Dialog
```python
def action_close(self):
    """Close dialog/wizard."""
    return {'type': 'ir.actions.act_window_close'}
```

### Close with Notification
```python
def action_save_and_close(self):
    """Save and close with notification."""
    self._do_save()
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Saved',
            'message': 'Changes saved successfully.',
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        }
    }
```

---

## Multi-Action Pattern

### Chain Actions
```python
def action_process_and_open(self):
    """Process then open related view."""
    self._process()

    # Return next action
    return {
        'type': 'ir.actions.act_window',
        'name': 'Processed Records',
        'res_model': 'processed.model',
        'view_mode': 'tree,form',
        'domain': [('source_id', '=', self.id)],
    }
```

### Conditional Actions
```python
def action_smart_open(self):
    """Open appropriate view based on record count."""
    related = self.env['related.model'].search([
        ('parent_id', '=', self.id),
    ])

    if len(related) == 1:
        # Single record - open form
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'related.model',
            'res_id': related.id,
            'view_mode': 'form',
        }
    else:
        # Multiple records - open list
        return {
            'type': 'ir.actions.act_window',
            'name': 'Related Records',
            'res_model': 'related.model',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', related.ids)],
        }
```

---

## Best Practices

1. **Use XML for static actions** - Easier to maintain and override
2. **Use Python for dynamic actions** - When domains/context depend on data
3. **Always set res_model** - Required for window actions
4. **Use context wisely** - Pass defaults and search filters
5. **binding_view_types** - Specify where action appears
6. **target=new for wizards** - Opens as dialog
7. **Return dict, not action record** - More flexible
8. **Handle empty recordsets** - Check before processing
9. **Use notifications** - Give user feedback
10. **Close dialogs properly** - Return act_window_close
