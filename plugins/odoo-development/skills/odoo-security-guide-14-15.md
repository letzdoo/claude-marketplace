# Odoo Security Guide - Migration 14.0 → 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: ODOO 14.0 → 15.0 SECURITY                                  ║
║  Use this guide when upgrading security code from v14 to v15.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
> Includes rules from Odoo's official skill library (odoo/odoo skills/, branch 20.0), verified against the 14.0 and 15.0 source.

## Overview of Security Changes

| Component | v14 | v15 | Migration Required |
|-----------|-----|-----|-------------------|
| @api.multi | Removed (since 13.0) | Removed | Only for code ported from <= 12.0 |
| Field tracking | `tracking` (`track_visibility` legacy, warns) | same | Clean-up recommended |
| Server QWeb output (XSS sink) | `t-esc` (escapes) / `t-raw` (only raw directive); no `t-out` | `t-out` escapes but prints `Markup` values raw; `t-esc` alias; `t-raw` deprecated (still renders raw) - audit `Markup(...)` built from user input | Recommended |
| x2many commands (also payloads under `sudo()`) | tuples | `Command.create/update/link/set...` or tuples - same `_allow_sudo_commands` rule | Optional |
| Python | 3.6+ | 3.7+ | Check compatibility |
| Chatter widgets | Legacy | Simplified | Recommended |

## Legacy Clean-up (not 14 -> 15 changes)

### 1. @api.multi Decorator (already removed in 14.0)

**<= 12.0 code (fails in 14.0 and 15.0):**
```python
@api.multi
def action_confirm(self):
    for record in self:
        record.state = 'confirmed'
```

**14.0 and 15.0 (no decorator):**
```python
def action_confirm(self):
    for record in self:
        record.state = 'confirmed'
```

### 2. track_visibility → tracking

`mail.thread` in 14.0 and 15.0 accepts only `tracking` as a field parameter; `track_visibility` is still tracked but logs "unknown parameter". Clean up in 14.0 already.

**Legacy (warns in 14 and 15):**
```python
name = fields.Char(string='Name', track_visibility='onchange')
state = fields.Selection([...], track_visibility='always')
partner_id = fields.Many2one('res.partner', track_visibility='onchange')
```

**14.0 and 15.0:**
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

**Legacy (<= 12.0 style; `@api.multi` fails in 14.0):**
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

**14.0 and 15.0:**
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

### Other Unchanged Security Rules

Unchanged in both: `sudo(user)` deprecated (use `with_user`), `_allow_sudo_commands`, `related_sudo=True` default, no `odoo.tools.SQL` (`_search()` -> `Query.select('"t"."c"')`, identifiers via `psycopg2.sql`), `odoo.osv.expression.AND/OR`, RPC guard `check_method_name` (no `@api.private`), route `auth` user/public/none and `type` http/json, CSRF on non-safe `http` methods, `_()` does not escape, Owl 1.4.11 (no `markup`/`htmlEscape`), `fields.NO_ACCESS`, `odoo.tools.file_open`, restricted `odoo.tools.misc.pickle`, `odoo.tools.consteq`, `ir.model.access` + `ir.rule` (no `base.group_everyone`, eval context `user`/`time`/`company_ids`/`company_id`).

## Migration Checklist

- [ ] Remove leftover `@api.multi` (only in code ported from <= 12.0; it fails in 14.0 too)
- [ ] Replace `track_visibility` with `tracking=True` (valid since 14.0)
- [ ] Review `t-raw` usages; move to `t-out` with sanitized/`Markup` values
- [ ] Update Python version to 3.7+
- [ ] Update chatter widgets (optional but recommended)
- [ ] Test all methods that had `@api.multi`
- [ ] Verify tracking works on mail.thread models

## Common Mistakes

### 1. Leaving @api.multi

**Wrong (AttributeError in 14.0 and 15.0):**
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
# Legacy: still tracked in 14/15, but each logs "unknown parameter 'track_visibility'"
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
- `addons/mail/models/mail_thread.py` - Field tracking implementation (`_valid_field_parameter`, `_get_tracked_fields`)
