# Common Module Templates

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMMON MODULE TEMPLATES                                                     ║
║  Ready-to-use templates for extending popular Odoo apps                      ║
║  Patterns are for v18 - adjust for other versions per version guides         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Template Index

| Target App | Template | Common Use Cases |
|------------|----------|------------------|
| Sale | sale_extension | Custom fields, workflows, reports |
| Stock | stock_extension | Warehouse operations, tracking |
| HR | hr_extension | Employee data, custom leaves |
| CRM | crm_extension | Lead scoring, custom stages |
| Accounting | account_extension | Custom reports, fiscal positions |
| Website | website_extension | Pages, snippets, themes |
| Project | project_extension | Task types, time tracking |

## Sale Extension Template (v18)

### Manifest
```python
# __manifest__.py
{
    'name': 'Sale Extension',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Custom sale order enhancements',
    'description': """
Sale Extension
==============
Extends sale orders with custom functionality.
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['sale', 'sale_management'],
    'data': [
        'security/sale_extension_security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/menuitems.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### Model Extension
```python
# models/sale_order.py
from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Custom fields
    x_custom_reference = fields.Char(
        string='Custom Reference',
        tracking=True,
        copy=False,
    )

    x_approval_required = fields.Boolean(
        string='Requires Approval',
        compute='_compute_approval_required',
        store=True,
    )

    x_approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        tracking=True,
    )

    x_approval_date = fields.Datetime(
        string='Approval Date',
    )

    # Computed field
    @api.depends('amount_total')
    def _compute_approval_required(self):
        approval_threshold = float(
            self.env['ir.config_parameter'].sudo().get_param(
                'sale_extension.approval_threshold', '10000'
            )
        )
        for order in self:
            order.x_approval_required = order.amount_total > approval_threshold

    # Action methods
    def action_request_approval(self):
        """Request approval for high-value orders"""
        for order in self:
            if not order.x_approval_required:
                raise UserError(_("This order does not require approval."))
            # Send notification to managers
            order.message_post(
                body=_("Approval requested for order %s") % order.name,
                subtype_xmlid='mail.mt_note',
            )

    def action_approve(self):
        """Approve the order"""
        self.write({
            'x_approved_by': self.env.user.id,
            'x_approval_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_("Order approved by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_note',
        )
```

### View Extension
```xml
<!-- views/sale_order_views.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_order_form_inherit" model="ir.ui.view">
        <field name="name">sale.order.form.inherit.extension</field>
        <field name="model">sale.order</field>
        <field name="inherit_id" ref="sale.view_order_form"/>
        <field name="arch" type="xml">
            <!-- Add custom reference field -->
            <field name="client_order_ref" position="after">
                <field name="x_custom_reference"/>
            </field>

            <!-- Add approval fields in a new group -->
            <xpath expr="//group[@name='sale_info']" position="inside">
                <field name="x_approval_required" invisible="not x_approval_required"/>
                <field name="x_approved_by" invisible="not x_approved_by"/>
                <field name="x_approval_date" invisible="not x_approval_date"/>
            </xpath>

            <!-- Add approval button in header -->
            <xpath expr="//button[@name='action_confirm']" position="before">
                <button name="action_request_approval"
                        type="object"
                        string="Request Approval"
                        class="btn-secondary"
                        invisible="not x_approval_required or x_approved_by or state != 'draft'"
                        groups="sale_extension.group_sale_user"/>
                <button name="action_approve"
                        type="object"
                        string="Approve"
                        class="btn-primary"
                        invisible="not x_approval_required or x_approved_by or state != 'draft'"
                        groups="sale_extension.group_sale_manager"/>
            </xpath>
        </field>
    </record>

    <!-- Tree view extension -->
    <record id="view_order_tree_inherit" model="ir.ui.view">
        <field name="name">sale.order.tree.inherit.extension</field>
        <field name="model">sale.order</field>
        <field name="inherit_id" ref="sale.view_order_tree"/>
        <field name="arch" type="xml">
            <field name="state" position="before">
                <field name="x_approval_required" optional="hide"/>
            </field>
        </field>
    </record>
</odoo>
```

### Security
```xml
<!-- security/sale_extension_security.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="group_sale_user" model="res.groups">
        <field name="name">Sale Extension User</field>
        <field name="category_id" ref="base.module_category_sales"/>
        <field name="implied_ids" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
    </record>

    <record id="group_sale_manager" model="res.groups">
        <field name="name">Sale Extension Manager</field>
        <field name="category_id" ref="base.module_category_sales"/>
        <field name="implied_ids" eval="[(4, ref('group_sale_user'))]"/>
    </record>
</odoo>
```

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

---

## Stock Extension Template (v18)

### Model Extension
```python
# models/stock_picking.py
from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    x_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Delivery Vehicle',
        check_company=True,
        tracking=True,
    )

    x_driver_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        check_company=True,
        tracking=True,
    )

    x_delivery_notes = fields.Text(
        string='Delivery Notes',
    )

    x_signature = fields.Binary(
        string='Recipient Signature',
        attachment=True,
    )

    x_signed_by = fields.Char(
        string='Signed By',
    )

    x_signed_date = fields.Datetime(
        string='Signature Date',
    )

    def action_record_signature(self):
        """Open wizard to record delivery signature"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Record Signature'),
            'res_model': 'stock.picking.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_picking_id': self.id},
        }
```

### Wizard for Signature
```python
# wizard/signature_wizard.py
from odoo import models, fields, api


class StockPickingSignatureWizard(models.TransientModel):
    _name = 'stock.picking.signature.wizard'
    _description = 'Delivery Signature Wizard'

    picking_id = fields.Many2one(
        'stock.picking',
        required=True,
    )

    signature = fields.Binary(
        string='Signature',
        required=True,
    )

    signed_by = fields.Char(
        string='Recipient Name',
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        self.picking_id.write({
            'x_signature': self.signature,
            'x_signed_by': self.signed_by,
            'x_signed_date': fields.Datetime.now(),
        })
        return {'type': 'ir.actions.act_window_close'}
```

---

## HR Extension Template (v18)

### New Model
```python
# models/hr_skill.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployeeSkill(models.Model):
    _name = 'hr.employee.skill'
    _description = 'Employee Skill'
    _check_company_auto = True
    _order = 'employee_id, skill_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade',
        index=True,
    )

    company_id = fields.Many2one(
        related='employee_id.company_id',
        store=True,
    )

    skill_id = fields.Many2one(
        'hr.skill.type',
        string='Skill',
        required=True,
        check_company=True,
    )

    level = fields.Selection([
        ('1', 'Beginner'),
        ('2', 'Intermediate'),
        ('3', 'Advanced'),
        ('4', 'Expert'),
    ], string='Level', required=True, default='1')

    certified = fields.Boolean(
        string='Certified',
    )

    certification_date = fields.Date(
        string='Certification Date',
    )

    expiry_date = fields.Date(
        string='Expiry Date',
    )

    notes = fields.Text(
        string='Notes',
    )

    _sql_constraints = [
        ('employee_skill_unique',
         'unique(employee_id, skill_id)',
         'An employee can only have one entry per skill!'),
    ]

    @api.constrains('certification_date', 'expiry_date')
    def _check_dates(self):
        for record in self:
            if record.certification_date and record.expiry_date:
                if record.certification_date > record.expiry_date:
                    raise ValidationError(
                        _("Expiry date must be after certification date.")
                    )


class HrSkillType(models.Model):
    _name = 'hr.skill.type'
    _description = 'Skill Type'
    _check_company_auto = True

    name = fields.Char(
        required=True,
        index=True,
    )

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    category = fields.Selection([
        ('technical', 'Technical'),
        ('soft', 'Soft Skills'),
        ('language', 'Language'),
        ('certification', 'Certification'),
    ], string='Category', required=True, default='technical')

    description = fields.Text()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    skill_ids = fields.One2many(
        'hr.employee.skill',
        'employee_id',
        string='Skills',
    )

    skill_count = fields.Integer(
        compute='_compute_skill_count',
    )

    @api.depends('skill_ids')
    def _compute_skill_count(self):
        for employee in self:
            employee.skill_count = len(employee.skill_ids)
```

---

## CRM Extension Template (v18)

### Lead Scoring Model
```python
# models/crm_lead.py
from odoo import models, fields, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_score = fields.Integer(
        string='Lead Score',
        compute='_compute_score',
        store=True,
        tracking=True,
    )

    x_score_breakdown = fields.Text(
        string='Score Breakdown',
        compute='_compute_score',
        store=True,
    )

    x_temperature = fields.Selection([
        ('cold', 'Cold'),
        ('warm', 'Warm'),
        ('hot', 'Hot'),
    ], string='Temperature', compute='_compute_temperature', store=True)

    x_last_activity_days = fields.Integer(
        string='Days Since Last Activity',
        compute='_compute_last_activity',
    )

    @api.depends(
        'email_from', 'phone', 'partner_id', 'expected_revenue',
        'tag_ids', 'probability', 'activity_ids'
    )
    def _compute_score(self):
        for lead in self:
            score = 0
            breakdown = []

            # Email provided: +10
            if lead.email_from:
                score += 10
                breakdown.append("Email: +10")

            # Phone provided: +10
            if lead.phone:
                score += 10
                breakdown.append("Phone: +10")

            # Linked to partner: +15
            if lead.partner_id:
                score += 15
                breakdown.append("Partner linked: +15")

            # Expected revenue > 0: +20
            if lead.expected_revenue and lead.expected_revenue > 0:
                score += 20
                breakdown.append("Revenue expected: +20")

            # Probability > 50%: +25
            if lead.probability and lead.probability > 50:
                score += 25
                breakdown.append("High probability: +25")

            # Has activities: +10
            if lead.activity_ids:
                score += 10
                breakdown.append("Has activities: +10")

            lead.x_score = score
            lead.x_score_breakdown = "\n".join(breakdown) if breakdown else "No score factors"

    @api.depends('x_score')
    def _compute_temperature(self):
        for lead in self:
            if lead.x_score >= 60:
                lead.x_temperature = 'hot'
            elif lead.x_score >= 30:
                lead.x_temperature = 'warm'
            else:
                lead.x_temperature = 'cold'

    def _compute_last_activity(self):
        today = fields.Date.today()
        for lead in self:
            if lead.date_last_stage_update:
                delta = today - lead.date_last_stage_update
                lead.x_last_activity_days = delta.days
            else:
                lead.x_last_activity_days = 0
```

---

## Project Extension Template (v18)

### Task Priority and Effort
```python
# models/project_task.py
from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_effort_estimate = fields.Float(
        string='Effort Estimate (hours)',
        tracking=True,
    )

    x_actual_effort = fields.Float(
        string='Actual Effort (hours)',
        compute='_compute_actual_effort',
        store=True,
    )

    x_effort_variance = fields.Float(
        string='Effort Variance',
        compute='_compute_effort_variance',
        store=True,
    )

    x_complexity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Complexity', default='medium', tracking=True)

    x_risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Risk Level', default='low', tracking=True)

    x_blockers = fields.Text(
        string='Blockers',
    )

    x_definition_of_done = fields.Html(
        string='Definition of Done',
    )

    @api.depends('timesheet_ids.unit_amount')
    def _compute_actual_effort(self):
        for task in self:
            task.x_actual_effort = sum(task.timesheet_ids.mapped('unit_amount'))

    @api.depends('x_effort_estimate', 'x_actual_effort')
    def _compute_effort_variance(self):
        for task in self:
            if task.x_effort_estimate:
                task.x_effort_variance = task.x_actual_effort - task.x_effort_estimate
            else:
                task.x_effort_variance = 0
```

---

## Website Extension Template (v18)

### Custom Page Controller
```python
# controllers/main.py
from odoo import http
from odoo.http import request


class WebsiteExtension(http.Controller):

    @http.route(['/custom/page'], type='http', auth='public', website=True)
    def custom_page(self, **kwargs):
        """Render custom page"""
        values = {
            'page_title': 'Custom Page',
            'records': request.env['my.model'].sudo().search(
                [('is_published', '=', True)],
                limit=20,
            ),
        }
        return request.render('website_extension.custom_page_template', values)

    @http.route(['/custom/api/data'], type='json', auth='public', website=True)
    def get_data(self, **kwargs):
        """JSON API endpoint"""
        records = request.env['my.model'].sudo().search_read(
            [('is_published', '=', True)],
            ['name', 'description'],
            limit=10,
        )
        return {'success': True, 'data': records}
```

### Website Template
```xml
<!-- views/templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="custom_page_template" name="Custom Page">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">
                <section class="s_text_block pt48 pb48">
                    <div class="container">
                        <h1 t-esc="page_title"/>
                        <div class="row">
                            <t t-foreach="records" t-as="record">
                                <div class="col-md-4 mb-4">
                                    <div class="card">
                                        <div class="card-body">
                                            <h5 class="card-title" t-esc="record.name"/>
                                            <p class="card-text" t-esc="record.description"/>
                                        </div>
                                    </div>
                                </div>
                            </t>
                        </div>
                    </div>
                </section>
            </div>
        </t>
    </template>
</odoo>
```

---

## Usage Instructions for Agents

When generating a module that extends a common app:

1. **Identify the target app** (sale, stock, hr, crm, project, website, account)
2. **Load this template file** as a reference
3. **Load the version-specific files** for your target version
4. **Adapt the template** to the specific requirements
5. **Apply version-specific patterns** (attrs, Command class, etc.)

### Example Agent Request
```json
{
  "action": "generate",
  "params": {
    "module_name": "sale_approval",
    "module_description": "Sale order approval workflow",
    "odoo_version": "18.0",
    "target_apps": ["sale"],
    "template_base": "sale_extension",
    "custom_features": [
      "approval_threshold_config",
      "manager_approval",
      "email_notifications"
    ]
  }
}
```
