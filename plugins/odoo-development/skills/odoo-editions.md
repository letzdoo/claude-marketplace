# Odoo Editions: Community vs Enterprise

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO EDITIONS REFERENCE                                                     ║
║  Understanding differences between Community and Enterprise editions         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Edition Overview

| Aspect | Community | Enterprise |
|--------|-----------|------------|
| License | LGPL-3 | Odoo Enterprise License |
| Source | Open source | Proprietary |
| Repository | github.com/odoo/odoo | github.com/odoo/enterprise |
| Cost | Free | Subscription-based |
| Apps | Core apps | Core + Enterprise apps |

## GitHub Repositories

### Community Edition
```
https://github.com/odoo/odoo
```
Contains all core functionality and Community apps.

### Enterprise Edition
```
https://github.com/odoo/enterprise
```
Requires Enterprise license to access. Contains additional apps and features.

## App Availability by Edition

### Community Apps (Free)
| Category | Apps |
|----------|------|
| Sales | CRM, Sales, Point of Sale |
| Inventory | Inventory, Purchase |
| Accounting | Invoicing (basic) |
| Website | Website Builder, eCommerce (basic) |
| HR | Employees, Recruitment, Time Off |
| Manufacturing | MRP (basic) |
| Project | Project, Timesheet |
| Marketing | Email Marketing, Events |

### Enterprise-Only Apps
| Category | Apps |
|----------|------|
| Accounting | Full Accounting, Assets, Consolidation |
| Sales | Subscriptions, Rental |
| HR | Appraisals, Referrals, Payroll |
| Manufacturing | PLM, Quality, MRP II |
| Inventory | Barcode, IoT |
| Field Service | Field Service, Planning |
| Marketing | Marketing Automation, Social Marketing |
| Studio | Odoo Studio (customization tool) |
| Documents | Document Management |
| Sign | Electronic Signatures |
| Helpdesk | Helpdesk |

## Development Considerations

### Developing for Community Edition

```python
# Your module depends only on Community apps
{
    'depends': ['base', 'mail', 'sale', 'stock'],
    # All these are Community apps
}
```

Your module can be:
- Open source (LGPL-3)
- Sold commercially
- Used by anyone

### Developing for Enterprise Edition

```python
# If your module depends on Enterprise apps
{
    'depends': ['helpdesk', 'planning', 'documents'],
    # These are Enterprise-only apps
}
```

Your module:
- Requires Enterprise license to use
- Cannot be open source (incompatible license)
- Can only be used by Enterprise customers

### Hybrid Modules (Both Editions)

```python
# Main module (Community-compatible)
{
    'name': 'My Module',
    'depends': ['base', 'sale'],
}

# Optional Enterprise extension
# my_module_enterprise/__manifest__.py
{
    'name': 'My Module - Enterprise',
    'depends': ['my_module', 'helpdesk'],
    'auto_install': True,  # Auto-install if helpdesk is available
}
```

## Feature Detection Pattern

```python
# Check if Enterprise module is installed
def _has_enterprise_feature(self):
    return 'helpdesk' in self.env.registry._init_modules

# Conditional import
try:
    from odoo.addons.helpdesk.models import helpdesk_ticket
    HAS_HELPDESK = True
except ImportError:
    HAS_HELPDESK = False

# Feature flag in model
class MyModel(models.Model):
    _name = 'my.model'

    # Only add field if Enterprise module available
    helpdesk_ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string='Helpdesk Ticket',
    ) if 'helpdesk' in dir() else None
```

## Views with Edition-Specific Elements

```xml
<!-- Use groups to hide Enterprise features -->
<field name="helpdesk_ticket_id"
       groups="helpdesk.group_helpdesk_user"/>

<!-- The field will be hidden if helpdesk module is not installed -->
```

## Key Technical Differences

### Studio Module (Enterprise)
- Allows non-developers to customize
- Creates custom models and fields
- Generates XML views automatically
- Stored in `ir.model.data` with special prefixes

### Barcode Module (Enterprise)
- Hardware barcode scanner support
- Inventory operations via barcode
- Dedicated mobile interface

### IoT Module (Enterprise)
- Internet of Things integration
- Hardware device support
- Real-time data collection

## Module Licensing

### Community-Compatible (LGPL-3)
```python
{
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'stock'],  # Community only
}
```

### Enterprise-Dependent (OPL-1)
```python
{
    'license': 'OPL-1',  # Odoo Proprietary License
    'depends': ['helpdesk'],  # Enterprise app
}
```

## Best Practices for Edition Compatibility

### 1. Prefer Community Dependencies
If possible, depend only on Community apps for wider compatibility.

### 2. Use Conditional Features
```python
class MyModel(models.Model):
    _name = 'my.model'

    def _get_available_integrations(self):
        integrations = ['email', 'sms']
        if self.env['ir.module.module'].search([
            ('name', '=', 'helpdesk'),
            ('state', '=', 'installed')
        ]):
            integrations.append('helpdesk')
        return integrations
```

### 3. Separate Enterprise Extensions
```
my_module/              # Community core
my_module_helpdesk/     # Enterprise integration
my_module_planning/     # Enterprise integration
```

### 4. Document Edition Requirements
```python
{
    'description': """
My Module
=========

**Community Features:**
- Feature A
- Feature B

**Enterprise Features (requires Enterprise apps):**
- Helpdesk integration (requires helpdesk)
- Planning integration (requires planning)
    """,
}
```

## AI Agent Instructions

When generating modules:

1. **ASK** which edition the user targets
2. **DEFAULT** to Community-compatible unless specified
3. **WARN** if depending on Enterprise-only apps
4. **SEPARATE** Enterprise features into optional modules
5. **DOCUMENT** edition requirements clearly
6. **USE** appropriate license (LGPL-3 or OPL-1)
