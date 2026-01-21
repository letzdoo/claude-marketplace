# Odoo Security Guide - Migration 14.0 → 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: ODOO 14.0 → 15.0 SECURITY                                  ║
║  Use this guide when upgrading security code from v14 to v15.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview of Security Changes

| Component | v14 | v15 | Migration Required |
|-----------|-----|-----|-------------------|
| @api.multi | Deprecated | **Removed** | **REQUIRED** |
| Field tracking | `track_visibility` | `tracking` | **REQUIRED** |
| Python | 3.6+ | 3.8+ | Check compatibility |
| Chatter widgets | Legacy | Simplified | Recommended |

## Breaking Changes

### 1. @api.multi Decorator REMOVED

**v14 (deprecated but works):**
```python
@api.multi
def action_confirm(self):
    for record in self:
        record.state = 'confirmed'
```

**v15 (no decorator needed):**
```python
def action_confirm(self):
    for record in self:
        record.state = 'confirmed'
```

### 2. track_visibility → tracking

**v14:**
```python
name = fields.Char(string='Name', track_visibility='onchange')
state = fields.Selection([...], track_visibility='always')
partner_id = fields.Many2one('res.partner', track_visibility='onchange')
```

**v15:**
```python
name = fields.Char(string='Name', tracking=True)
state = fields.Selection([...], tracking=True)
partner_id = fields.Many2one('res.partner', tracking=True)
```

**Note:** `tracking=True` replaces both `track_visibility='onchange'` and `track_visibility='always'`. The distinction is no longer needed.

## Migration Script

```python
import re

def migrate_track_visibility(python_content):
    """Convert track_visibility to tracking."""
    # Replace track_visibility='onchange' with tracking=True
    content = re.sub(
        r"track_visibility=['\"]onchange['\"]",
        "tracking=True",
        python_content
    )
    # Replace track_visibility='always' with tracking=True
    content = re.sub(
        r"track_visibility=['\"]always['\"]",
        "tracking=True",
        content
    )
    return content

def remove_api_multi(python_content):
    """Remove @api.multi decorators."""
    # Remove @api.multi line
    content = re.sub(r"^\s*@api\.multi\s*\n", "", python_content, flags=re.MULTILINE)
    return content
```

## Detailed Migration Examples

### Model with Tracking

**v14:**
```python
from odoo import api, fields, models

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft', track_visibility='always')
    partner_id = fields.Many2one('res.partner', track_visibility='onchange')
    amount = fields.Float(track_visibility='onchange')

    @api.multi
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    @api.multi
    def action_send_email(self):
        for record in self:
            record._send_notification()
```

**v15:**
```python
from odoo import api, fields, models

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft', tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
    amount = fields.Float(tracking=True)

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    def action_send_email(self):
        for record in self:
            record._send_notification()
```

### Chatter Widget Updates

**v14:**
```xml
<div class="oe_chatter">
    <field name="message_follower_ids" widget="mail_followers"/>
    <field name="activity_ids" widget="mail_activity"/>
    <field name="message_ids" widget="mail_thread"/>
</div>
```

**v15:**
```xml
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```

**Note:** The widget attributes are optional in v15 as Odoo auto-detects the correct widget.

## No Change Required

### Security Groups
```xml
<!-- Same in v14 and v15 -->
<record id="group_user" model="res.groups">
    <field name="name">User</field>
    <field name="implied_ids" eval="[(4, ref('other_group'))]"/>
</record>
```

### Access Rights
```csv
# Same format in v14 and v15
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

### Record Rules
```xml
<!-- Same syntax in v14 and v15 -->
<record id="rule_company" model="ir.rule">
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

### View attrs Syntax
```xml
<!-- Same in v14 and v15 -->
<field name="notes" attrs="{'invisible': [('state', '=', 'draft')]}"/>
```

### Field Groups
```python
# Same in v14 and v15
notes = fields.Text(groups='my_module.group_manager')
```

## Migration Checklist

- [ ] **CRITICAL**: Remove ALL `@api.multi` decorators
- [ ] **CRITICAL**: Replace `track_visibility` with `tracking=True`
- [ ] Update Python version to 3.8+
- [ ] Update chatter widgets (optional but recommended)
- [ ] Test all methods that had `@api.multi`
- [ ] Verify tracking works on mail.thread models

## Common Mistakes

### 1. Leaving @api.multi

**Wrong (will cause errors in v15):**
```python
@api.multi
def my_method(self):
    pass
```

**Correct:**
```python
def my_method(self):
    pass
```

### 2. Using Old track_visibility Values

**Wrong:**
```python
# These won't work in v15
name = fields.Char(track_visibility='onchange')
state = fields.Selection([...], track_visibility='always')
```

**Correct:**
```python
name = fields.Char(tracking=True)
state = fields.Selection([...], tracking=True)
```

## Testing After Migration

```python
def test_tracking(self):
    """Test that field tracking works after migration."""
    record = self.env['my.model'].create({'name': 'Test'})

    # Update tracked field
    record.write({'name': 'Updated'})

    # Check that message was created
    messages = record.message_ids.filtered(
        lambda m: m.tracking_value_ids
    )
    self.assertTrue(messages, "Tracking message should be created")
```

## GitHub Reference

- `odoo/api.py` - Decorator changes
- `odoo/models.py` - Field tracking implementation
