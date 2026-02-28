# Mail and Notification Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MAIL & NOTIFICATION PATTERNS                                                ║
║  Email templates, chatter integration, and activity management               ║
║  Use for automated emails, discussions, and workflow notifications           ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Mail Mixin Integration

### Adding Chatter to Model
```python
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned To',
        tracking=True,
    )
    description = fields.Html(string='Description')
```

### View with Chatter
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="my_model_view_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form string="My Model">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="state"/>
                        <field name="partner_id"/>
                        <field name="user_id"/>
                    </group>
                    <notebook>
                        <page string="Description">
                            <field name="description"/>
                        </page>
                    </notebook>
                </sheet>
                <!-- Chatter -->
                <chatter/>
            </form>
        </field>
    </record>
</odoo>
```

---

## Email Templates

### Template Syntax Evolution (Odoo 15+)

Starting with Odoo 15, email templates migrated from Jinja2 (Mako-style) syntax to QWeb rendering. This brought significant syntax changes and improvements:

**Before Odoo 15 (Jinja2/Mako syntax):**
```xml
<record id="email_template_example" model="mail.template">
    <field name="name">Example Template</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="subject">Order ${object.name} - ${object.state}</field>
    <field name="body_html" type="html">
<![CDATA[
<p>Dear ${object.student_id.name},</p>
<p>Your order ${object.name} is now ${object.state}.</p>
<p>Amount: ${object.amount_total}</p>
]]>
    </field>
</record>
```

**Odoo 15+ (QWeb syntax):**
```xml
<record id="email_template_example" model="mail.template">
    <field name="name">Example Template</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="subject"><t t-out="object.name"/> - <t t-out="object.state"/></field>
    <field name="body_html" type="html">
<![CDATA[
<p>Dear <t t-out="object.student_id.name"/>,</p>
<p>Your order <t t-out="object.name"/> is now <t t-out="object.state"/>.</p>
<p>Amount: <t t-out="object.amount_total"/></p>
]]>
    </field>
</record>
```

**Key Changes:**
- **Syntax**: `${expression}` → `<t t-out="expression"/>`
- **Default behavior**: `t-out` escapes HTML by default (like old `t-esc`)
- **Raw HTML**: Use `t-out` with `Markup` objects for safe unescaped rendering
- **Conditionals**: `% if` → `<t t-if="condition">`
- **Loops**: `% for` → `<t t-foreach="items" t-as="item">`

**The t-out Directive:**
The `t-out` directive was introduced in Odoo 15 as a unified replacement for:
- `t-esc` (HTML-escaped output) - deprecated but still works
- `t-raw` (unescaped output) - deprecated but still works

`t-out` escapes by default but accepts `Markup` objects for safe HTML rendering, providing better security while maintaining flexibility.

**Migration Checklist:**
- Replace `${object.field}` with `<t t-out="object.field"/>`
- Replace `${object.field or ''}` with `<t t-out="object.field or ''"/>`
- Convert `% if` blocks to `<t t-if="condition">`
- Convert `% for` loops to `<t t-foreach="items" t-as="item">`
- Update any raw HTML rendering to use `Markup` objects with `t-out`

### Basic Email Template
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="email_template_my_model_confirm" model="mail.template">
        <field name="name">My Model: Confirmation</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="subject">{{ object.name }} - Confirmed</field>
        <field name="email_from">{{ (object.company_id.email or user.email) }}</field>
        <field name="email_to">{{ object.partner_id.email }}</field>
        <field name="body_html" type="html">
<![CDATA[
<div style="margin: 0px; padding: 0px;">
    <p style="margin: 0px; padding: 0px; font-size: 13px;">
        Dear {{ object.partner_id.name }},
    </p>
    <br/>
    <p>
        Your request <strong>{{ object.name }}</strong> has been confirmed.
    </p>
    <br/>
    <p>
        <strong>Details:</strong>
    </p>
    <ul>
        <li>Reference: {{ object.name }}</li>
        <li>Date: {{ object.create_date.strftime('%Y-%m-%d') }}</li>
        <li>Status: {{ object.state }}</li>
    </ul>
    <br/>
    <p>
        Best regards,<br/>
        {{ object.company_id.name }}
    </p>
</div>
]]>
        </field>
        <field name="auto_delete" eval="True"/>
    </record>
</odoo>
```

### Template with Attachments
```xml
<record id="email_template_with_report" model="mail.template">
    <field name="name">My Model: Send Report</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="subject">Report: {{ object.name }}</field>
    <field name="email_from">{{ user.email }}</field>
    <field name="email_to">{{ object.partner_id.email }}</field>
    <field name="body_html" type="html">
<![CDATA[
<p>Please find attached the report for {{ object.name }}.</p>
]]>
    </field>
    <!-- Attach PDF report -->
    <field name="report_template_id" ref="my_module.report_my_model"/>
    <field name="report_name">Report_{{ object.name }}</field>
</record>
```

### Dynamic Template (Python)
```python
def _get_email_template_body(self) -> str:
    """Generate dynamic email body."""
    lines_html = ""
    for line in self.line_ids:
        lines_html += f"""
        <tr>
            <td>{line.name}</td>
            <td style="text-align: right;">{line.quantity}</td>
            <td style="text-align: right;">{line.price_unit:.2f}</td>
        </tr>
        """

    return f"""
    <p>Dear {self.partner_id.name},</p>
    <table border="1" cellpadding="5">
        <thead>
            <tr>
                <th>Description</th>
                <th>Qty</th>
                <th>Price</th>
            </tr>
        </thead>
        <tbody>
            {lines_html}
        </tbody>
    </table>
    <p>Total: {self.amount_total:.2f}</p>
    """
```

---

## Sending Emails

### Using Template
```python
def action_send_email(self) -> dict:
    """Send email using template."""
    self.ensure_one()

    template = self.env.ref('my_module.email_template_my_model_confirm')
    template.send_mail(self.id, force_send=True)

    return True
```

### Open Email Composer
```python
def action_send_email_wizard(self) -> dict:
    """Open email composer with template."""
    self.ensure_one()

    template = self.env.ref('my_module.email_template_my_model_confirm')

    return {
        'type': 'ir.actions.act_window',
        'name': 'Send Email',
        'res_model': 'mail.compose.message',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_model': self._name,
            'default_res_ids': self.ids,
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
        },
    }
```

### Send Without Template
```python
def action_notify_partner(self) -> None:
    """Send email without template."""
    self.ensure_one()

    mail_values = {
        'subject': f'Update: {self.name}',
        'body_html': f'<p>Your record {self.name} has been updated.</p>',
        'email_from': self.env.company.email or self.env.user.email,
        'email_to': self.partner_id.email,
        'model': self._name,
        'res_id': self.id,
    }

    mail = self.env['mail.mail'].sudo().create(mail_values)
    mail.send()
```

### Batch Email
```python
def action_send_batch_emails(self) -> None:
    """Send emails to multiple records."""
    template = self.env.ref('my_module.email_template_my_model_confirm')

    for record in self:
        if record.partner_id.email:
            template.send_mail(record.id, force_send=False)

    # Process mail queue
    self.env['mail.mail'].sudo().process_email_queue()
```

---

## Message Posting

### Post Simple Message
```python
def action_post_note(self) -> None:
    """Post internal note."""
    self.ensure_one()

    self.message_post(
        body="This is an internal note.",
        message_type='comment',
        subtype_xmlid='mail.mt_note',
    )
```

### Post with Tracking
```python
def action_confirm(self) -> None:
    """Confirm and post message."""
    self.ensure_one()

    old_state = self.state
    self.write({'state': 'confirmed'})

    # Post message with details
    self.message_post(
        body=f"Record confirmed. State changed from {old_state} to confirmed.",
        message_type='notification',
        subtype_xmlid='mail.mt_comment',
    )
```

### Post with Attachments
```python
def action_post_with_attachment(self) -> None:
    """Post message with file attachment."""
    self.ensure_one()

    attachment = self.env['ir.attachment'].create({
        'name': 'document.pdf',
        'type': 'binary',
        'datas': self.document_file,  # base64 encoded
        'res_model': self._name,
        'res_id': self.id,
    })

    self.message_post(
        body="Document attached for review.",
        attachment_ids=[attachment.id],
    )
```

### Post from Template
```python
def action_post_from_template(self) -> None:
    """Post message using template."""
    self.ensure_one()

    template = self.env.ref('my_module.email_template_my_model_confirm')

    self.message_post_with_source(
        source_ref=template,
        subtype_xmlid='mail.mt_comment',
    )
```

---

## Followers and Subscriptions

### Add Followers
```python
def action_add_followers(self) -> None:
    """Add partners as followers."""
    self.ensure_one()

    partners_to_add = self.team_id.member_ids.mapped('partner_id')
    self.message_subscribe(partner_ids=partners_to_add.ids)
```

### Remove Followers
```python
def action_remove_follower(self, partner_id: int) -> None:
    """Remove specific follower."""
    self.ensure_one()
    self.message_unsubscribe(partner_ids=[partner_id])
```

### Custom Subtypes
```xml
<!-- data/mail_subtype.xml -->
<odoo>
    <!-- Subtype for confirmed notifications -->
    <record id="mt_my_model_confirmed" model="mail.message.subtype">
        <field name="name">Confirmed</field>
        <field name="res_model">my.model</field>
        <field name="default" eval="True"/>
        <field name="description">Record has been confirmed</field>
    </record>

    <!-- Subtype for assignment -->
    <record id="mt_my_model_assigned" model="mail.message.subtype">
        <field name="name">Assigned</field>
        <field name="res_model">my.model</field>
        <field name="default" eval="False"/>
        <field name="description">Record has been assigned</field>
    </record>
</odoo>
```

### Use Custom Subtype
```python
def action_confirm(self) -> None:
    """Confirm with custom notification."""
    self.ensure_one()
    self.write({'state': 'confirmed'})

    self.message_post(
        body="Record confirmed.",
        subtype_xmlid='my_module.mt_my_model_confirmed',
    )
```

---

## Activities

### Schedule Activity
```python
def action_schedule_followup(self) -> None:
    """Schedule follow-up activity."""
    self.ensure_one()

    self.activity_schedule(
        'mail.mail_activity_data_todo',
        date_deadline=fields.Date.today() + timedelta(days=7),
        summary='Follow up with customer',
        note='Check if customer needs assistance.',
        user_id=self.user_id.id,
    )
```

### Schedule with Feedback
```python
def action_request_approval(self) -> None:
    """Request approval via activity."""
    self.ensure_one()

    activity_type = self.env.ref('mail.mail_activity_data_todo')

    self.activity_schedule(
        activity_type_id=activity_type.id,
        date_deadline=fields.Date.today() + timedelta(days=3),
        summary='Approval Required',
        note=f'Please review and approve: {self.name}',
        user_id=self.env.ref('base.user_admin').id,
    )
```

### Mark Activity Done
```python
def action_mark_activity_done(self) -> None:
    """Mark all activities as done."""
    self.ensure_one()

    activities = self.activity_ids.filtered(
        lambda a: a.activity_type_id.name == 'To Do'
    )
    activities.action_feedback(feedback='Completed by workflow.')
```

### Custom Activity Type
```xml
<!-- data/mail_activity_type.xml -->
<odoo>
    <record id="mail_activity_type_review" model="mail.activity.type">
        <field name="name">Review Required</field>
        <field name="summary">Review this record</field>
        <field name="res_model">my.model</field>
        <field name="icon">fa-check-square</field>
        <field name="delay_count">3</field>
        <field name="delay_unit">days</field>
        <field name="default_user_id" ref="base.user_admin"/>
    </record>
</odoo>
```

---

## Automated Notifications

### On State Change (Automated Action)
```xml
<record id="automation_notify_on_confirm" model="base.automation">
    <field name="name">Notify on Confirmation</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="trigger">on_write</field>
    <field name="trigger_field_ids" eval="[(6, 0, [ref('field_my_model__state')])]"/>
    <field name="filter_domain">[('state', '=', 'confirmed')]</field>
    <field name="state">code</field>
    <field name="code">
template = env.ref('my_module.email_template_my_model_confirm')
for record in records:
    if record.partner_id.email:
        template.send_mail(record.id)
    </field>
</record>
```

### Override Tracking (Python)
```python
def _track_subtype(self, init_values) -> str:
    """Return subtype for tracking notifications."""
    self.ensure_one()

    if 'state' in init_values:
        if self.state == 'confirmed':
            return self.env.ref('my_module.mt_my_model_confirmed')
        elif self.state == 'done':
            return self.env.ref('my_module.mt_my_model_done')

    return super()._track_subtype(init_values)
```

### Custom Notification Logic
```python
def _notify_get_recipients(self, message, msg_vals, **kwargs):
    """Override to customize notification recipients."""
    recipients = super()._notify_get_recipients(message, msg_vals, **kwargs)

    # Add manager to important notifications
    if self.state == 'confirmed' and self.amount_total > 10000:
        manager = self.env.ref('my_module.group_manager').users
        for user in manager:
            if user.partner_id.id not in [r['id'] for r in recipients]:
                recipients.append({
                    'id': user.partner_id.id,
                    'active': True,
                    'share': False,
                    'notif': 'email',
                    'type': 'user',
                })

    return recipients
```

---

## In-App Notifications

### Display Notification
```python
def action_with_notification(self) -> dict:
    """Action with success notification."""
    self.ensure_one()

    # Do something
    self.write({'state': 'done'})

    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Success',
            'message': f'{self.name} has been processed.',
            'type': 'success',  # success, warning, danger, info
            'sticky': False,
            'next': {'type': 'ir.actions.act_window_close'},
        }
    }
```

### Notification with Link
```python
def action_notify_with_link(self) -> dict:
    """Notification with clickable link."""
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Record Created',
            'message': 'Click to view the new record.',
            'type': 'success',
            'links': [{
                'label': self.name,
                'url': f'/web#id={self.id}&model={self._name}&view_type=form',
            }],
        }
    }
```

---

## Bus Notifications (Real-time)

### Send Bus Notification
```python
def action_notify_users(self) -> None:
    """Send real-time notification via bus."""
    self.ensure_one()

    # Notify specific user
    self.env['bus.bus']._sendone(
        self.user_id.partner_id,
        'simple_notification',
        {
            'title': 'New Assignment',
            'message': f'You have been assigned to {self.name}',
            'type': 'info',
            'sticky': False,
        }
    )
```

### Broadcast to Channel
```python
def action_broadcast(self) -> None:
    """Broadcast to all users in group."""
    channel = f'my_module_{self.env.company.id}'

    self.env['bus.bus']._sendone(
        channel,
        'my_module/notification',
        {
            'record_id': self.id,
            'message': f'Record {self.name} updated',
        }
    )
```

---

## Best Practices

1. **Use templates** - Define email templates in XML for maintainability
2. **Handle missing emails** - Always check `partner_id.email` before sending
3. **Use queues** - Set `force_send=False` for batch operations
4. **Track important fields** - Add `tracking=True` to key fields
5. **Custom subtypes** - Create subtypes for different notification types
6. **Activity scheduling** - Use activities for task management
7. **Follower management** - Auto-subscribe relevant parties
8. **Test email rendering** - Verify templates render correctly

---

## Manifest Dependencies

```python
{
    'depends': [
        'mail',  # Required for mail.thread
    ],
    'data': [
        'data/mail_template.xml',
        'data/mail_subtype.xml',
        'data/mail_activity_type.xml',
        'views/my_model_views.xml',
    ],
}
```
