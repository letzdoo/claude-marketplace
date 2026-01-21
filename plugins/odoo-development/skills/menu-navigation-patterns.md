# Menu and Navigation Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MENU & NAVIGATION PATTERNS                                                  ║
║  Menu structure, navigation, and application organization                    ║
║  Use for module UI organization and user navigation                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Menu Structure Overview

```
Root Menu (App)
├── Category Menu 1
│   ├── Submenu 1.1 → Action
│   └── Submenu 1.2 → Action
├── Category Menu 2
│   ├── Submenu 2.1 → Action
│   └── Submenu 2.2 → Action
└── Configuration
    ├── Settings → Action
    └── Data → Action
```

---

## Basic Menu Definition

### Root Menu (Application)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Root menu (appears in app switcher) -->
    <menuitem id="menu_my_module_root"
              name="My Application"
              web_icon="my_module,static/description/icon.png"
              sequence="10"/>
</odoo>
```

### Category Menus
```xml
<!-- Category under root -->
<menuitem id="menu_my_module_main"
          name="Records"
          parent="menu_my_module_root"
          sequence="10"/>

<menuitem id="menu_my_module_config"
          name="Configuration"
          parent="menu_my_module_root"
          sequence="100"
          groups="base.group_system"/>
```

### Action Menus (Leaf Nodes)
```xml
<!-- Menu with action -->
<menuitem id="menu_my_model"
          name="My Records"
          parent="menu_my_module_main"
          action="action_my_model"
          sequence="10"/>

<menuitem id="menu_my_model_archived"
          name="Archived"
          parent="menu_my_module_main"
          action="action_my_model_archived"
          sequence="20"/>
```

---

## Complete Menu Example

### Full Module Menu Structure
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- ============================================ -->
    <!-- ROOT MENU (Application)                      -->
    <!-- ============================================ -->
    <menuitem id="menu_my_module_root"
              name="My Application"
              web_icon="my_module,static/description/icon.png"
              sequence="50"/>

    <!-- ============================================ -->
    <!-- MAIN MENUS                                   -->
    <!-- ============================================ -->

    <!-- Records Category -->
    <menuitem id="menu_records"
              name="Records"
              parent="menu_my_module_root"
              sequence="10"/>

    <menuitem id="menu_my_model"
              name="All Records"
              parent="menu_records"
              action="action_my_model"
              sequence="10"/>

    <menuitem id="menu_my_model_draft"
              name="Draft"
              parent="menu_records"
              action="action_my_model_draft"
              sequence="20"/>

    <menuitem id="menu_my_model_confirmed"
              name="Confirmed"
              parent="menu_records"
              action="action_my_model_confirmed"
              sequence="30"/>

    <!-- Reports Category -->
    <menuitem id="menu_reports"
              name="Reports"
              parent="menu_my_module_root"
              sequence="50"/>

    <menuitem id="menu_report_analysis"
              name="Analysis"
              parent="menu_reports"
              action="action_report_analysis"
              sequence="10"/>

    <!-- ============================================ -->
    <!-- CONFIGURATION MENUS                          -->
    <!-- ============================================ -->

    <menuitem id="menu_configuration"
              name="Configuration"
              parent="menu_my_module_root"
              sequence="100"
              groups="base.group_system"/>

    <menuitem id="menu_config_settings"
              name="Settings"
              parent="menu_configuration"
              action="action_my_module_config"
              sequence="10"/>

    <menuitem id="menu_config_categories"
              name="Categories"
              parent="menu_configuration"
              action="action_my_category"
              sequence="20"/>

    <menuitem id="menu_config_tags"
              name="Tags"
              parent="menu_configuration"
              action="action_my_tag"
              sequence="30"/>
</odoo>
```

---

## Menu Attributes

### Common Attributes
| Attribute | Description |
|-----------|-------------|
| `id` | Unique XML ID (required) |
| `name` | Display name |
| `parent` | Parent menu XML ID |
| `action` | Action to execute |
| `sequence` | Order (lower = first) |
| `groups` | Security groups (comma-separated) |
| `web_icon` | App icon (root menu only) |
| `active` | Enable/disable menu |

### Sequence Guidelines
| Range | Use For |
|-------|---------|
| 1-20 | Primary menus (most used) |
| 20-50 | Secondary menus |
| 50-80 | Reports and analysis |
| 80-100 | Configuration |

---

## Menu Security

### Restrict by Group
```xml
<!-- Only managers see this menu -->
<menuitem id="menu_sensitive"
          name="Sensitive Data"
          parent="menu_my_module_main"
          action="action_sensitive"
          groups="my_module.group_manager"/>

<!-- Multiple groups (OR) -->
<menuitem id="menu_admin"
          name="Admin"
          parent="menu_my_module_config"
          action="action_admin"
          groups="base.group_system,my_module.group_admin"/>
```

### Hide Menu Conditionally
```xml
<!-- Menu visible based on settings -->
<menuitem id="menu_optional_feature"
          name="Optional Feature"
          parent="menu_my_module_main"
          action="action_optional"
          groups="my_module.group_use_optional_feature"/>
```

---

## Extending Existing Menus

### Add to Existing App
```xml
<!-- Add menu under Sales app -->
<menuitem id="menu_my_sale_extension"
          name="My Extension"
          parent="sale.sale_menu_root"
          action="action_my_sale_extension"
          sequence="50"/>

<!-- Add under Sales > Configuration -->
<menuitem id="menu_my_sale_config"
          name="My Settings"
          parent="sale.menu_sale_config"
          action="action_my_sale_config"
          sequence="100"/>
```

### Common Parent Menus
```xml
<!-- Sales -->
parent="sale.sale_menu_root"
parent="sale.sale_order_menu"
parent="sale.menu_sale_config"

<!-- Purchase -->
parent="purchase.menu_purchase_root"
parent="purchase.menu_purchase_config"

<!-- Inventory -->
parent="stock.menu_stock_root"
parent="stock.menu_stock_config"

<!-- Accounting -->
parent="account.menu_finance"
parent="account.menu_finance_configuration"

<!-- CRM -->
parent="crm.crm_menu_root"
parent="crm.crm_menu_config"

<!-- HR -->
parent="hr.menu_hr_root"
parent="hr.menu_human_resources_configuration"

<!-- Project -->
parent="project.menu_main_pm"
parent="project.menu_project_config"

<!-- Settings (general) -->
parent="base.menu_administration"
```

---

## Menu with Filters

### Pre-filtered Menus
```xml
<!-- Action with domain -->
<record id="action_my_model_draft" model="ir.actions.act_window">
    <field name="name">Draft Records</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
    <field name="domain">[('state', '=', 'draft')]</field>
    <field name="context">{'default_state': 'draft'}</field>
</record>

<menuitem id="menu_my_model_draft"
          name="Draft"
          parent="menu_records"
          action="action_my_model_draft"/>

<!-- Action with search filter -->
<record id="action_my_model_my_records" model="ir.actions.act_window">
    <field name="name">My Records</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
    <field name="context">{'search_default_my_records': 1}</field>
</record>
```

---

## Dynamic Menus

### Create Menu from Python
```python
def _create_dynamic_menu(self, name, parent_id, action_id):
    """Create menu dynamically."""
    return self.env['ir.ui.menu'].create({
        'name': name,
        'parent_id': parent_id,
        'action': f'ir.actions.act_window,{action_id}',
        'sequence': 100,
    })
```

### Update Menu Visibility
```python
def _update_menu_visibility(self):
    """Show/hide menu based on configuration."""
    menu = self.env.ref('my_module.menu_optional_feature')
    config_param = self.env['ir.config_parameter'].sudo()
    show_menu = config_param.get_param('my_module.show_optional', 'False')
    menu.write({'active': show_menu == 'True'})
```

---

## App Icon

### Icon Requirements
- Format: PNG
- Size: 256x256 pixels (recommended)
- Location: `static/description/icon.png`

### Setting App Icon
```xml
<menuitem id="menu_my_module_root"
          name="My Application"
          web_icon="my_module,static/description/icon.png"
          sequence="50"/>
```

---

## Menu Order Patterns

### Standard App Layout
```
1. Main Operations (seq 10-20)
   - All Records
   - My Records
   - To Do / Pending

2. Secondary Operations (seq 30-50)
   - By Category views
   - Filtered views

3. Reports (seq 60-80)
   - Analysis
   - Dashboards

4. Configuration (seq 90-100)
   - Settings
   - Master Data
```

### Example Implementation
```xml
<!-- Main Operations -->
<menuitem id="menu_operations" name="Operations"
          parent="menu_root" sequence="10"/>

<menuitem id="menu_all" name="All Records"
          parent="menu_operations" action="action_all" sequence="10"/>

<menuitem id="menu_my" name="My Records"
          parent="menu_operations" action="action_my" sequence="20"/>

<!-- Reports -->
<menuitem id="menu_reporting" name="Reporting"
          parent="menu_root" sequence="60"/>

<menuitem id="menu_analysis" name="Analysis"
          parent="menu_reporting" action="action_analysis" sequence="10"/>

<!-- Configuration -->
<menuitem id="menu_config" name="Configuration"
          parent="menu_root" sequence="90"
          groups="base.group_system"/>
```

---

## Best Practices

1. **Consistent naming** - Use clear, action-oriented names
2. **Logical grouping** - Group related menus together
3. **Sequence numbers** - Leave gaps (10, 20, 30) for future insertions
4. **Security groups** - Restrict sensitive menus
5. **Configuration last** - Always sequence 90+
6. **App icon** - Always provide for root menu
7. **Extend, don't duplicate** - Add to existing apps when appropriate
8. **Keep it shallow** - Max 3 levels of nesting
9. **Use filters** - Pre-filtered views for common use cases
10. **Test permissions** - Verify menu visibility for different users
