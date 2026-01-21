# Purchase and Procurement Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PURCHASE & PROCUREMENT PATTERNS                                             ║
║  Purchase orders, vendor management, and procurement workflows               ║
║  Use for purchasing automation, vendor portals, and supply chain             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Module Setup

### Manifest Dependencies
```python
{
    'name': 'My Purchase Module',
    'version': '18.0.1.0.0',
    'depends': ['purchase'],  # Core purchase
    # Optional: 'purchase_stock', 'purchase_requisition'
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_views.xml',
    ],
}
```

---

## Extending Purchase Orders

### Add Custom Fields
```python
from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_project_id = fields.Many2one('project.project', string='Project')
    x_department_id = fields.Many2one('hr.department', string='Department')
    x_priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='normal')
    x_approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    x_approval_date = fields.Datetime(string='Approval Date', readonly=True)
    x_budget_code = fields.Char(string='Budget Code')
    x_internal_notes = fields.Text(string='Internal Notes')

    x_total_weight = fields.Float(
        string='Total Weight',
        compute='_compute_total_weight',
        store=True,
    )

    @api.depends('order_line.x_weight')
    def _compute_total_weight(self):
        for order in self:
            order.x_total_weight = sum(order.order_line.mapped('x_weight'))
```

### Purchase Approval Workflow
```python
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

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
            'purchase.approval_limit', default='5000'
        ))
        for order in self:
            order.x_requires_approval = order.amount_total > limit

    def button_confirm(self):
        """Override to add approval check."""
        for order in self:
            if order.x_requires_approval and order.state != 'pending_approval':
                order.write({'state': 'pending_approval'})
                order._send_approval_request()
                return True
        return super().button_confirm()

    def action_approve(self):
        """Approve and confirm order."""
        self.write({
            'x_approved_by': self.env.uid,
            'x_approval_date': fields.Datetime.now(),
        })
        return super().button_confirm()

    def _send_approval_request(self):
        """Notify approvers."""
        template = self.env.ref('my_module.email_template_po_approval')
        approvers = self.env.ref('purchase.group_purchase_manager').users
        for approver in approvers:
            template.with_context(approver=approver).send_mail(self.id)
```

### Purchase Order Lines
```python
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_weight = fields.Float(string='Weight (kg)')
    x_delivery_date = fields.Date(string='Requested Delivery')
    x_internal_ref = fields.Char(string='Internal Reference')
    x_is_urgent = fields.Boolean(string='Urgent')

    @api.onchange('product_id')
    def _onchange_product_weight(self):
        if self.product_id:
            self.x_weight = self.product_id.weight * self.product_qty
```

---

## Vendor Management

### Extend Vendor (Partner)
```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_vendor_code = fields.Char(string='Vendor Code')
    x_vendor_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Below Average'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent'),
    ], string='Vendor Rating')
    x_payment_terms_note = fields.Text(string='Payment Terms Note')
    x_min_order_amount = fields.Monetary(string='Minimum Order Amount')
    x_lead_time = fields.Integer(string='Default Lead Time (days)')
    x_certified = fields.Boolean(string='Certified Vendor')
    x_certification_expiry = fields.Date(string='Certification Expiry')

    x_purchase_count = fields.Integer(
        string='Purchase Orders',
        compute='_compute_purchase_stats',
    )
    x_total_purchased = fields.Monetary(
        string='Total Purchased',
        compute='_compute_purchase_stats',
    )

    def _compute_purchase_stats(self):
        for partner in self:
            orders = self.env['purchase.order'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['purchase', 'done']),
            ])
            partner.x_purchase_count = len(orders)
            partner.x_total_purchased = sum(orders.mapped('amount_total'))
```

### Vendor Evaluation
```python
class VendorEvaluation(models.Model):
    _name = 'vendor.evaluation'
    _description = 'Vendor Evaluation'
    _inherit = ['mail.thread']

    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True,
        domain=[('supplier_rank', '>', 0)],
    )
    evaluation_date = fields.Date(
        string='Evaluation Date',
        default=fields.Date.today,
    )
    evaluator_id = fields.Many2one(
        'res.users',
        string='Evaluator',
        default=lambda self: self.env.user,
    )

    # Criteria scores (1-5)
    quality_score = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
    ], string='Quality')
    delivery_score = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
    ], string='Delivery')
    price_score = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
    ], string='Price')
    service_score = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
    ], string='Service')

    overall_score = fields.Float(
        string='Overall Score',
        compute='_compute_overall_score',
        store=True,
    )
    notes = fields.Text(string='Notes')

    @api.depends('quality_score', 'delivery_score', 'price_score', 'service_score')
    def _compute_overall_score(self):
        for eval in self:
            scores = [
                int(eval.quality_score or 0),
                int(eval.delivery_score or 0),
                int(eval.price_score or 0),
                int(eval.service_score or 0),
            ]
            valid_scores = [s for s in scores if s > 0]
            eval.overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    def action_update_vendor_rating(self):
        """Update vendor's rating based on evaluations."""
        for eval in self:
            if eval.overall_score >= 4.5:
                rating = '5'
            elif eval.overall_score >= 3.5:
                rating = '4'
            elif eval.overall_score >= 2.5:
                rating = '3'
            elif eval.overall_score >= 1.5:
                rating = '2'
            else:
                rating = '1'
            eval.partner_id.x_vendor_rating = rating
```

---

## Purchase Requisitions

### Extend Requisition
```python
class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    x_department_id = fields.Many2one('hr.department', string='Department')
    x_budget_id = fields.Many2one('account.budget', string='Budget')
    x_justification = fields.Text(string='Business Justification')

    def action_create_rfq_for_vendors(self, vendor_ids):
        """Create RFQs for multiple vendors."""
        for vendor_id in vendor_ids:
            self._create_rfq(vendor_id)

    def _create_rfq(self, vendor_id):
        """Create single RFQ from requisition."""
        return self.env['purchase.order'].create({
            'partner_id': vendor_id,
            'requisition_id': self.id,
            'origin': self.name,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom_id.id,
                'price_unit': 0,  # To be filled by vendor
            }) for line in self.line_ids],
        })
```

---

## Automated Purchasing

### Auto-Reorder Rules
```python
class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    x_preferred_vendor_id = fields.Many2one(
        'res.partner',
        string='Preferred Vendor',
        domain=[('supplier_rank', '>', 0)],
    )
    x_auto_create_po = fields.Boolean(
        string='Auto Create PO',
        default=False,
    )

    def _get_procurement_vendor(self):
        """Get vendor for procurement."""
        if self.x_preferred_vendor_id:
            return self.x_preferred_vendor_id
        # Fall back to product's default vendor
        return self.product_id.seller_ids[:1].partner_id


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        """Extend scheduler to handle auto PO creation."""
        result = super()._run_scheduler_tasks(use_new_cursor, company_id)

        # Process auto-reorder points
        orderpoints = self.env['stock.warehouse.orderpoint'].search([
            ('x_auto_create_po', '=', True),
        ])

        for op in orderpoints:
            if op.qty_to_order > 0:
                op._create_auto_purchase_order()

        return result
```

### Scheduled Purchase Creation
```python
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _cron_create_recurring_orders(self):
        """Create recurring purchase orders."""
        templates = self.env['purchase.order.template'].search([
            ('active', '=', True),
            ('next_order_date', '<=', fields.Date.today()),
        ])

        for template in templates:
            order = template._create_order()
            template._update_next_date()

            if template.auto_confirm:
                order.button_confirm()
```

---

## Views

### Purchase Order Form Extension
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="purchase_order_form_inherit" model="ir.ui.view">
        <field name="name">purchase.order.form.inherit</field>
        <field name="model">purchase.order</field>
        <field name="inherit_id" ref="purchase.purchase_order_form"/>
        <field name="arch" type="xml">
            <field name="partner_ref" position="after">
                <field name="x_priority"/>
                <field name="x_department_id"/>
            </field>

            <xpath expr="//page[@name='products']" position="after">
                <page string="Approval" name="approval"
                      invisible="not x_requires_approval">
                    <group>
                        <group>
                            <field name="x_requires_approval"/>
                            <field name="x_approved_by"/>
                            <field name="x_approval_date"/>
                        </group>
                        <group>
                            <field name="x_budget_code"/>
                        </group>
                    </group>
                    <field name="x_internal_notes" placeholder="Internal notes..."/>
                </page>
            </xpath>

            <xpath expr="//button[@name='button_confirm']" position="before">
                <button name="action_approve"
                        string="Approve"
                        type="object"
                        class="btn-primary"
                        invisible="state != 'pending_approval'"
                        groups="purchase.group_purchase_manager"/>
            </xpath>
        </field>
    </record>
</odoo>
```

### Vendor Form Extension
```xml
<record id="view_partner_form_purchase_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.purchase.inherit</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//page[@name='sales_purchases']" position="inside">
            <group string="Vendor Details" invisible="supplier_rank == 0">
                <group>
                    <field name="x_vendor_code"/>
                    <field name="x_vendor_rating"/>
                    <field name="x_certified"/>
                </group>
                <group>
                    <field name="x_min_order_amount"/>
                    <field name="x_lead_time"/>
                    <field name="x_certification_expiry"
                           invisible="not x_certified"/>
                </group>
            </group>
        </xpath>

        <div name="button_box" position="inside">
            <button class="oe_stat_button" type="action"
                    name="%(purchase.action_purchase_order_report_all)d"
                    icon="fa-shopping-cart"
                    invisible="supplier_rank == 0">
                <field string="Purchases" name="x_purchase_count" widget="statinfo"/>
            </button>
        </div>
    </field>
</record>
```

---

## Reports

### Purchase Analysis Extension
```python
class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    x_department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    x_priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', readonly=True)

    def _select(self):
        return super()._select() + ", po.x_department_id, po.x_priority"

    def _group_by(self):
        return super()._group_by() + ", po.x_department_id, po.x_priority"
```

---

## Best Practices

1. **Vendor management** - Track ratings, certifications, lead times
2. **Approval workflows** - Amount-based approval for cost control
3. **Budget integration** - Link POs to budgets/cost centers
4. **Multi-company** - Handle inter-company purchases
5. **Receipt tracking** - Monitor delivery performance
6. **Price history** - Track vendor price changes
7. **Lead time accuracy** - Compare promised vs actual
8. **Blanket orders** - Use purchase agreements for contracts
9. **RFQ process** - Competitive bidding for large purchases
10. **Integration** - Connect with inventory, accounting, projects
