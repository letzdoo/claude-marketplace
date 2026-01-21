# Sale and CRM Integration Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  SALE & CRM INTEGRATION PATTERNS                                             ║
║  Sales orders, quotations, leads, opportunities, and pipelines               ║
║  Use for sales automation, CRM customization, and order workflows            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Module Setup

### Manifest for Sale Extension
```python
{
    'name': 'My Sale Extension',
    'version': '18.0.1.0.0',
    'depends': ['sale', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_views.xml',
    ],
}
```

### Manifest for CRM Extension
```python
{
    'name': 'My CRM Extension',
    'version': '18.0.1.0.0',
    'depends': ['crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_views.xml',
    ],
}
```

---

## Extending Sale Orders

### Add Custom Fields
```python
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_project_name = fields.Char(string='Project Name')
    x_delivery_priority = fields.Selection([
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ], string='Delivery Priority', default='normal')
    x_internal_notes = fields.Text(string='Internal Notes')
    x_approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
    )
    x_approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
    )
    x_margin_percent = fields.Float(
        string='Margin %',
        compute='_compute_margin_percent',
        store=True,
    )

    @api.depends('margin', 'amount_untaxed')
    def _compute_margin_percent(self):
        for order in self:
            if order.amount_untaxed:
                order.x_margin_percent = (order.margin / order.amount_untaxed) * 100
            else:
                order.x_margin_percent = 0.0
```

### Add Approval Workflow
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('pending_approval', 'Pending Approval'),
        ],
        ondelete={'pending_approval': 'set default'},
    )
    x_requires_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_approval',
    )

    @api.depends('amount_total')
    def _compute_requires_approval(self):
        limit = float(self.env['ir.config_parameter'].sudo().get_param(
            'sale.approval_limit', default='10000'
        ))
        for order in self:
            order.x_requires_approval = order.amount_total > limit

    def action_confirm(self):
        """Override to add approval check."""
        for order in self:
            if order.x_requires_approval and order.state != 'pending_approval':
                order.write({'state': 'pending_approval'})
                order._send_approval_request()
                return True
        return super().action_confirm()

    def action_approve(self):
        """Approve order and continue confirmation."""
        self.write({
            'x_approved_by': self.env.uid,
            'x_approval_date': fields.Datetime.now(),
        })
        return super().action_confirm()

    def _send_approval_request(self):
        """Send approval request notification."""
        template = self.env.ref('my_module.email_template_approval_request')
        template.send_mail(self.id)
```

### Extend Sale Order Lines
```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_delivery_date = fields.Date(string='Requested Delivery')
    x_is_custom = fields.Boolean(string='Custom Product')
    x_technical_notes = fields.Text(string='Technical Notes')
    x_cost_price = fields.Float(
        string='Cost Price',
        compute='_compute_cost_price',
        store=True,
    )
    x_line_margin = fields.Float(
        string='Line Margin',
        compute='_compute_line_margin',
        store=True,
    )

    @api.depends('product_id')
    def _compute_cost_price(self):
        for line in self:
            line.x_cost_price = line.product_id.standard_price

    @api.depends('price_subtotal', 'x_cost_price', 'product_uom_qty')
    def _compute_line_margin(self):
        for line in self:
            cost = line.x_cost_price * line.product_uom_qty
            line.x_line_margin = line.price_subtotal - cost
```

---

## Sale Order Automation

### Auto-Apply Discounts
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_discount(self):
        """Apply partner-specific discount."""
        if self.partner_id and self.partner_id.x_discount_percent:
            for line in self.order_line:
                line.discount = self.partner_id.x_discount_percent


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_discount_percent = fields.Float(string='Default Discount %')
    x_credit_limit = fields.Float(string='Credit Limit')
    x_payment_terms_note = fields.Text(string='Payment Terms Note')
```

### Create Order from Template
```python
class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    x_auto_confirm = fields.Boolean(string='Auto Confirm Orders')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_template_id(self):
        """Apply template and custom logic."""
        result = super()._onchange_sale_order_template_id()

        if self.sale_order_template_id.x_auto_confirm:
            # Schedule auto-confirmation
            self.x_auto_confirm_scheduled = True

        return result
```

---

## CRM Lead/Opportunity Extension

### Extend CRM Lead
```python
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_industry_id = fields.Many2one('res.partner.industry', string='Industry')
    x_budget = fields.Monetary(string='Budget', currency_field='company_currency')
    x_timeline = fields.Selection([
        ('immediate', 'Immediate'),
        ('1_month', '1 Month'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
    ], string='Purchase Timeline')
    x_competitor = fields.Char(string='Main Competitor')
    x_lead_score = fields.Integer(
        string='Lead Score',
        compute='_compute_lead_score',
        store=True,
    )
    x_next_action_date = fields.Date(string='Next Action Date')
    x_lost_reason_details = fields.Text(string='Lost Reason Details')

    @api.depends('expected_revenue', 'probability', 'x_budget', 'x_timeline')
    def _compute_lead_score(self):
        for lead in self:
            score = 0
            # Score based on revenue
            if lead.expected_revenue > 50000:
                score += 30
            elif lead.expected_revenue > 10000:
                score += 20
            elif lead.expected_revenue > 1000:
                score += 10

            # Score based on probability
            score += int(lead.probability * 0.5)

            # Score based on timeline
            timeline_scores = {
                'immediate': 20,
                '1_month': 15,
                '3_months': 10,
                '6_months': 5,
                '1_year': 2,
            }
            score += timeline_scores.get(lead.x_timeline, 0)

            lead.x_lead_score = score
```

### Lead Qualification
```python
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_qualification_status = fields.Selection([
        ('unqualified', 'Unqualified'),
        ('mql', 'Marketing Qualified'),
        ('sql', 'Sales Qualified'),
        ('opportunity', 'Opportunity'),
    ], string='Qualification', default='unqualified')

    def action_qualify_mql(self):
        """Mark as Marketing Qualified Lead."""
        self.write({'x_qualification_status': 'mql'})
        self._schedule_qualification_followup()

    def action_qualify_sql(self):
        """Mark as Sales Qualified Lead."""
        self.write({'x_qualification_status': 'sql'})
        self.activity_schedule(
            'mail.mail_activity_data_call',
            summary='SQL Follow-up Call',
            user_id=self.user_id.id,
        )

    def action_convert_to_opportunity(self):
        """Convert to opportunity with custom logic."""
        self.write({
            'x_qualification_status': 'opportunity',
            'type': 'opportunity',
        })
        return self.action_opportunity_form()
```

### Pipeline Stage Automation
```python
class CrmStage(models.Model):
    _inherit = 'crm.stage'

    x_auto_activity = fields.Boolean(string='Auto Schedule Activity')
    x_activity_type_id = fields.Many2one(
        'mail.activity.type',
        string='Activity Type',
    )
    x_activity_days = fields.Integer(string='Days Until Due', default=3)
    x_email_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
    )


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def write(self, vals):
        """Auto-create activities on stage change."""
        result = super().write(vals)

        if 'stage_id' in vals:
            for lead in self:
                stage = lead.stage_id
                if stage.x_auto_activity and stage.x_activity_type_id:
                    lead.activity_schedule(
                        stage.x_activity_type_id.id,
                        date_deadline=fields.Date.today() + timedelta(
                            days=stage.x_activity_days
                        ),
                    )
                if stage.x_email_template_id:
                    stage.x_email_template_id.send_mail(lead.id)

        return result
```

---

## Quotation Templates

### Custom Quotation Sections
```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_section_type = fields.Selection([
        ('product', 'Product'),
        ('service', 'Service'),
        ('option', 'Optional'),
    ], string='Section Type', default='product')
    x_is_optional = fields.Boolean(string='Optional Item')

    def _get_optional_lines(self):
        """Get optional lines for this order."""
        return self.order_id.order_line.filtered(lambda l: l.x_is_optional)
```

---

## Sales Reports

### Custom Sales Analysis
```python
class SaleReport(models.Model):
    _inherit = 'sale.report'

    x_margin_percent = fields.Float(string='Margin %', readonly=True)
    x_delivery_priority = fields.Selection([
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ], string='Priority', readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['x_margin_percent'] = """
            CASE WHEN s.amount_untaxed > 0
            THEN (s.margin / s.amount_untaxed) * 100
            ELSE 0 END
        """
        res['x_delivery_priority'] = "s.x_delivery_priority"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ", s.x_delivery_priority"
        return res
```

---

## Views

### Sale Order Form Extension
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_order_form_inherit" model="ir.ui.view">
        <field name="name">sale.order.form.inherit</field>
        <field name="model">sale.order</field>
        <field name="inherit_id" ref="sale.view_order_form"/>
        <field name="arch" type="xml">
            <field name="payment_term_id" position="after">
                <field name="x_project_name"/>
                <field name="x_delivery_priority"/>
            </field>

            <xpath expr="//page[@name='other_information']" position="inside">
                <group string="Approval">
                    <field name="x_requires_approval"/>
                    <field name="x_approved_by"
                           invisible="not x_approved_by"/>
                    <field name="x_approval_date"
                           invisible="not x_approval_date"/>
                </group>
            </xpath>

            <xpath expr="//button[@name='action_confirm']" position="before">
                <button name="action_approve"
                        string="Approve"
                        type="object"
                        class="btn-primary"
                        invisible="state != 'pending_approval'"
                        groups="sales_team.group_sale_manager"/>
            </xpath>
        </field>
    </record>
</odoo>
```

### CRM Lead Form Extension
```xml
<record id="crm_lead_view_form_inherit" model="ir.ui.view">
    <field name="name">crm.lead.form.inherit</field>
    <field name="model">crm.lead</field>
    <field name="inherit_id" ref="crm.crm_lead_view_form"/>
    <field name="arch" type="xml">
        <field name="expected_revenue" position="after">
            <field name="x_budget"/>
            <field name="x_timeline"/>
            <field name="x_lead_score" widget="progressbar"/>
        </field>

        <div name="button_box" position="inside">
            <button class="oe_stat_button" type="object"
                    name="action_view_lead_score"
                    icon="fa-star">
                <field string="Score" name="x_lead_score"
                       widget="statinfo"/>
            </button>
        </div>
    </field>
</record>
```

---

## Best Practices

1. **Don't break standard flow** - Extend, don't replace core methods
2. **Use existing fields** - Check if field exists before adding
3. **Respect access rights** - Sales team vs manager permissions
4. **Performance** - Index frequently searched fields
5. **Multi-company** - Filter by company_id
6. **Currency handling** - Use Monetary fields properly
7. **Report integration** - Extend sale.report for analysis
8. **Email templates** - Use standard mail.template
9. **Activity types** - Use existing or create specific ones
10. **Testing** - Test quotation → order → invoice flow
