# Configuration Settings Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  CONFIGURATION SETTINGS PATTERNS                                             ║
║  Module settings, res.config.settings, and system parameters                 ║
║  Use for user-configurable options and feature toggles                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Basic Settings Model

### Inherit res.config.settings
```python
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Simple config parameter
    my_module_api_key = fields.Char(
        string='API Key',
        config_parameter='my_module.api_key',
    )

    # Boolean setting
    my_module_enable_feature = fields.Boolean(
        string='Enable Feature X',
        config_parameter='my_module.enable_feature',
    )

    # Selection setting
    my_module_mode = fields.Selection([
        ('basic', 'Basic Mode'),
        ('advanced', 'Advanced Mode'),
    ], string='Operating Mode',
       config_parameter='my_module.mode',
       default='basic')

    # Integer setting
    my_module_max_items = fields.Integer(
        string='Maximum Items',
        config_parameter='my_module.max_items',
        default=100,
    )
```

---

## Company-Specific Settings

### Company Fields (Not Global)
```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Company-specific setting (stored on res.company)
    my_default_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Default Warehouse',
        related='company_id.my_default_warehouse_id',
        readonly=False,
    )

    my_default_journal_id = fields.Many2one(
        'account.journal',
        string='Default Journal',
        related='company_id.my_default_journal_id',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    my_default_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Default Warehouse',
    )

    my_default_journal_id = fields.Many2one(
        'account.journal',
        string='Default Journal',
    )
```

---

## Feature Group Toggle

### Settings that Enable/Disable Features
```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Feature toggle linked to security group
    group_use_advanced_routing = fields.Boolean(
        string='Use Advanced Routing',
        implied_group='my_module.group_advanced_routing',
    )

    group_multi_warehouse = fields.Boolean(
        string='Multi-Warehouse',
        implied_group='stock.group_stock_multi_warehouses',
    )

    # Module toggle (installs module when enabled)
    module_my_optional_feature = fields.Boolean(
        string='Enable Optional Feature',
        help='Installs my_optional_feature module',
    )
```

### Security Group for Feature
```xml
<!-- Security group enabled by setting -->
<record id="group_advanced_routing" model="res.groups">
    <field name="name">Advanced Routing</field>
    <field name="category_id" ref="base.module_category_hidden"/>
    <field name="comment">Users with access to advanced routing features</field>
</record>
```

---

## Settings View

### Settings View Definition
```xml
<record id="res_config_settings_view_form" model="ir.ui.view">
    <field name="name">res.config.settings.view.form.inherit.my_module</field>
    <field name="model">res.config.settings</field>
    <field name="inherit_id" ref="base.res_config_settings_view_form"/>
    <field name="arch" type="xml">
        <xpath expr="//form" position="inside">
            <app data-string="My Module" string="My Module"
                 data-key="my_module" groups="base.group_system">
                <block title="General Settings">
                    <setting string="API Configuration">
                        <div class="text-muted">
                            Configure external API settings
                        </div>
                        <div class="content-group">
                            <div class="row mt-2">
                                <label for="my_module_api_key" class="col-lg-3"/>
                                <field name="my_module_api_key" class="col-lg-9"/>
                            </div>
                        </div>
                    </setting>

                    <setting string="Operating Mode">
                        <div class="text-muted">
                            Select the operating mode for the module
                        </div>
                        <div class="content-group">
                            <div class="row mt-2">
                                <field name="my_module_mode" class="col-lg-6"/>
                            </div>
                        </div>
                    </setting>
                </block>

                <block title="Features">
                    <setting help="Enable advanced features for power users">
                        <field name="group_use_advanced_routing"/>
                        <div invisible="not group_use_advanced_routing"
                             class="content-group mt-2">
                            <div class="row">
                                <label for="my_module_max_items" class="col-lg-4"/>
                                <field name="my_module_max_items" class="col-lg-8"/>
                            </div>
                        </div>
                    </setting>

                    <setting help="Install additional module for extended functionality">
                        <field name="module_my_optional_feature"/>
                    </setting>
                </block>

                <block title="Company Settings"
                       invisible="not company_id">
                    <setting string="Default Warehouse">
                        <div class="content-group">
                            <div class="row mt-2">
                                <label for="my_default_warehouse_id" class="col-lg-4"/>
                                <field name="my_default_warehouse_id" class="col-lg-8"/>
                            </div>
                        </div>
                    </setting>
                </block>
            </app>
        </xpath>
    </field>
</record>
```

---

## Reading Settings in Code

### Using Config Parameters
```python
class MyModel(models.Model):
    _name = 'my.model'

    def _get_api_key(self):
        """Read config parameter."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'my_module.api_key',
            default='',
        )

    def _is_feature_enabled(self):
        """Check if feature is enabled."""
        param = self.env['ir.config_parameter'].sudo().get_param(
            'my_module.enable_feature',
            default='False',
        )
        # Parameters are stored as strings
        return param == 'True'

    def _get_max_items(self):
        """Read integer config."""
        param = self.env['ir.config_parameter'].sudo().get_param(
            'my_module.max_items',
            default='100',
        )
        return int(param)

    def do_something(self):
        """Example using settings."""
        if not self._is_feature_enabled():
            raise UserError("Feature is disabled in settings.")

        api_key = self._get_api_key()
        max_items = self._get_max_items()

        # Use settings...
```

### Reading Company Settings
```python
def _get_default_warehouse(self):
    """Get company default warehouse."""
    company = self.env.company
    return company.my_default_warehouse_id
```

### Checking Group Membership
```python
def has_advanced_access(self):
    """Check if user has advanced access."""
    return self.env.user.has_group('my_module.group_advanced_routing')
```

---

## Settings with Computed Fields

### Computed Settings Field
```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Stored in ir.config_parameter
    my_module_enabled = fields.Boolean(
        config_parameter='my_module.enabled',
    )

    # Computed based on another setting
    my_module_status = fields.Char(
        compute='_compute_status',
    )

    # Count for information display
    record_count = fields.Integer(
        compute='_compute_record_count',
    )

    @api.depends('my_module_enabled')
    def _compute_status(self):
        for record in self:
            record.my_module_status = 'Active' if record.my_module_enabled else 'Inactive'

    def _compute_record_count(self):
        for record in self:
            record.record_count = self.env['my.model'].search_count([])
```

---

## Settings with Actions

### Execute Action from Settings
```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_sync_data(self):
        """Button action in settings."""
        # Perform sync operation
        self.env['my.model'].sync_all()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sync Complete',
                'message': 'Data synchronization completed.',
                'type': 'success',
            }
        }

    def action_open_records(self):
        """Open related records."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Records',
            'res_model': 'my.model',
            'view_mode': 'tree,form',
        }
```

### Action Button in View
```xml
<setting string="Data Synchronization">
    <div class="text-muted">
        Sync data with external system
    </div>
    <div class="content-group mt-2">
        <button name="action_sync_data" type="object"
                string="Sync Now" class="btn-primary"/>
    </div>
</setting>

<setting string="Quick Access">
    <div class="content-group">
        <button name="action_open_records" type="object"
                string="View Records" class="btn-link"
                icon="fa-external-link"/>
    </div>
</setting>
```

---

## Default Values Pattern

### Set Defaults Based on Settings
```python
class MyModel(models.Model):
    _name = 'my.model'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        default=lambda self: self._get_default_warehouse(),
    )

    mode = fields.Selection([
        ('basic', 'Basic'),
        ('advanced', 'Advanced'),
    ], default=lambda self: self._get_default_mode())

    def _get_default_warehouse(self):
        """Get default from company settings."""
        return self.env.company.my_default_warehouse_id

    def _get_default_mode(self):
        """Get default from system settings."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'my_module.mode',
            default='basic',
        )
```

---

## XML Data for Settings

### Default Config Parameters
```xml
<!-- Set default config parameters -->
<record id="config_my_module_enabled" model="ir.config_parameter">
    <field name="key">my_module.enabled</field>
    <field name="value">True</field>
</record>

<record id="config_my_module_mode" model="ir.config_parameter">
    <field name="key">my_module.mode</field>
    <field name="value">basic</field>
</record>

<record id="config_my_module_max_items" model="ir.config_parameter">
    <field name="key">my_module.max_items</field>
    <field name="value">100</field>
</record>
```

---

## Settings Validation

### Validate on Save
```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    my_module_api_url = fields.Char(
        config_parameter='my_module.api_url',
    )

    @api.constrains('my_module_api_url')
    def _check_api_url(self):
        """Validate API URL format."""
        for record in self:
            if record.my_module_api_url:
                if not record.my_module_api_url.startswith('https://'):
                    raise ValidationError("API URL must use HTTPS.")

    def set_values(self):
        """Custom validation before saving."""
        super().set_values()

        # Additional validation
        if self.my_module_enabled and not self.my_module_api_key:
            raise UserError("API Key is required when feature is enabled.")
```

---

## Conditional Settings Display

### Show Settings Based on Other Settings
```xml
<setting string="Enable API Integration">
    <field name="my_module_api_enabled"/>
</setting>

<!-- Only show when API is enabled -->
<setting string="API Configuration"
         invisible="not my_module_api_enabled">
    <div class="content-group">
        <div class="row mt-2">
            <label for="my_module_api_url" class="col-lg-3"/>
            <field name="my_module_api_url" class="col-lg-9"
                   required="my_module_api_enabled"/>
        </div>
        <div class="row mt-2">
            <label for="my_module_api_key" class="col-lg-3"/>
            <field name="my_module_api_key" class="col-lg-9"
                   password="True"
                   required="my_module_api_enabled"/>
        </div>
    </div>
</setting>
```

---

## Menu Access

### Settings Menu Item
```xml
<!-- Menu to open settings -->
<record id="my_module_config_settings_action" model="ir.actions.act_window">
    <field name="name">Settings</field>
    <field name="res_model">res.config.settings</field>
    <field name="view_mode">form</field>
    <field name="target">inline</field>
    <field name="context">{'module': 'my_module'}</field>
</record>

<menuitem id="menu_my_module_configuration"
          name="Configuration"
          parent="menu_my_module_root"
          sequence="100"/>

<menuitem id="menu_my_module_settings"
          name="Settings"
          parent="menu_my_module_configuration"
          action="my_module_config_settings_action"
          groups="base.group_system"/>
```

---

## Best Practices

1. **Use config_parameter** - For global settings stored in ir.config_parameter
2. **Use related company fields** - For company-specific settings
3. **Use implied_group** - For feature toggles that grant permissions
4. **Use module_** prefix - For settings that install modules
5. **Validate settings** - Check values before saving
6. **Provide defaults** - Set sensible default values
7. **Group logically** - Use blocks to organize related settings
8. **Show/hide conditionally** - Use invisible attribute
9. **Document settings** - Use help text and descriptions
10. **Secure sensitive data** - Use password="True" for secrets
