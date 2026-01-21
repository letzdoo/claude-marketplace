# Dashboard and KPI Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  DASHBOARD & KPI PATTERNS                                                    ║
║  Analytics views, KPI displays, and business intelligence                    ║
║  Use for data visualization and executive dashboards                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Dashboard Model (Pivot/Graph Base)

### Analytics Model for Reporting
```python
from odoo import api, fields, models, tools


class SaleAnalysis(models.Model):
    _name = 'sale.analysis'
    _description = 'Sales Analysis'
    _auto = False  # No table created - it's a database view
    _order = 'date desc'

    # Dimension fields
    date = fields.Date(string='Date', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    categ_id = fields.Many2one('product.category', string='Category', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sale', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True)

    # Measure fields
    order_count = fields.Integer(string='# Orders', readonly=True)
    product_qty = fields.Float(string='Qty Sold', readonly=True)
    price_subtotal = fields.Float(string='Untaxed Total', readonly=True)
    price_total = fields.Float(string='Total', readonly=True)

    def init(self):
        """Create database view for analysis."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () as id,
                    so.date_order::date as date,
                    so.partner_id,
                    sol.product_id,
                    pt.categ_id,
                    so.user_id,
                    so.company_id,
                    so.state,
                    COUNT(DISTINCT so.id) as order_count,
                    SUM(sol.product_uom_qty) as product_qty,
                    SUM(sol.price_subtotal) as price_subtotal,
                    SUM(sol.price_total) as price_total
                FROM sale_order so
                JOIN sale_order_line sol ON sol.order_id = so.id
                JOIN product_product pp ON pp.id = sol.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                GROUP BY
                    so.date_order::date,
                    so.partner_id,
                    sol.product_id,
                    pt.categ_id,
                    so.user_id,
                    so.company_id,
                    so.state
            )
        """ % self._table)
```

---

## Dashboard Views

### Pivot View
```xml
<record id="sale_analysis_view_pivot" model="ir.ui.view">
    <field name="name">sale.analysis.pivot</field>
    <field name="model">sale.analysis</field>
    <field name="arch" type="xml">
        <pivot string="Sales Analysis" display_quantity="true">
            <field name="date" type="row" interval="month"/>
            <field name="categ_id" type="row"/>
            <field name="user_id" type="col"/>
            <field name="price_total" type="measure"/>
            <field name="product_qty" type="measure"/>
            <field name="order_count" type="measure"/>
        </pivot>
    </field>
</record>
```

### Graph View
```xml
<record id="sale_analysis_view_graph" model="ir.ui.view">
    <field name="name">sale.analysis.graph</field>
    <field name="model">sale.analysis</field>
    <field name="arch" type="xml">
        <graph string="Sales Analysis" type="bar" stacked="True">
            <field name="date" type="row" interval="month"/>
            <field name="price_total" type="measure"/>
        </graph>
    </field>
</record>

<!-- Line Chart -->
<record id="sale_analysis_view_graph_line" model="ir.ui.view">
    <field name="name">sale.analysis.graph.line</field>
    <field name="model">sale.analysis</field>
    <field name="arch" type="xml">
        <graph string="Sales Trend" type="line">
            <field name="date" type="row" interval="day"/>
            <field name="price_total" type="measure"/>
        </graph>
    </field>
</record>

<!-- Pie Chart -->
<record id="sale_analysis_view_graph_pie" model="ir.ui.view">
    <field name="name">sale.analysis.graph.pie</field>
    <field name="model">sale.analysis</field>
    <field name="arch" type="xml">
        <graph string="Sales by Category" type="pie">
            <field name="categ_id" type="row"/>
            <field name="price_total" type="measure"/>
        </graph>
    </field>
</record>
```

### Dashboard Action
```xml
<record id="action_sale_analysis" model="ir.actions.act_window">
    <field name="name">Sales Analysis</field>
    <field name="res_model">sale.analysis</field>
    <field name="view_mode">graph,pivot</field>
    <field name="context">{
        'search_default_current_month': 1,
        'group_by': ['date:month'],
    }</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            No data to display
        </p>
    </field>
</record>
```

---

## KPI Stat Buttons

### Button Box Pattern
```python
class Partner(models.Model):
    _inherit = 'res.partner'

    # KPI counters
    sale_order_count = fields.Integer(
        compute='_compute_sale_count',
        string='Sales',
    )
    sale_total = fields.Monetary(
        compute='_compute_sale_count',
        string='Total Sales',
    )
    invoice_count = fields.Integer(
        compute='_compute_invoice_count',
        string='Invoices',
    )
    open_invoice_amount = fields.Monetary(
        compute='_compute_invoice_count',
        string='Due Amount',
    )

    def _compute_sale_count(self):
        for partner in self:
            orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done']),
            ])
            partner.sale_order_count = len(orders)
            partner.sale_total = sum(orders.mapped('amount_total'))

    def _compute_invoice_count(self):
        for partner in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
            ])
            partner.invoice_count = len(invoices)
            partner.open_invoice_amount = sum(
                inv.amount_residual
                for inv in invoices
                if inv.payment_state != 'paid'
            )

    def action_view_sales(self):
        """Open related sales."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
        }

    def action_view_invoices(self):
        """Open related invoices."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [
                ('partner_id', '=', self.id),
                ('move_type', '=', 'out_invoice'),
            ],
        }
```

### Button Box View
```xml
<form>
    <sheet>
        <div class="oe_button_box" name="button_box">
            <!-- Sales stat button -->
            <button name="action_view_sales" type="object"
                    class="oe_stat_button" icon="fa-dollar">
                <div class="o_field_widget o_stat_info">
                    <span class="o_stat_value">
                        <field name="sale_order_count"/>
                    </span>
                    <span class="o_stat_text">Sales</span>
                </div>
                <div class="o_stat_info" invisible="not sale_total">
                    <span class="o_stat_value">
                        <field name="sale_total" widget="monetary"/>
                    </span>
                </div>
            </button>

            <!-- Invoice stat button -->
            <button name="action_view_invoices" type="object"
                    class="oe_stat_button" icon="fa-book"
                    invisible="invoice_count == 0">
                <div class="o_field_widget o_stat_info">
                    <span class="o_stat_value">
                        <field name="invoice_count"/>
                    </span>
                    <span class="o_stat_text">Invoices</span>
                </div>
            </button>

            <!-- Alert indicator -->
            <button name="action_view_open_invoices" type="object"
                    class="oe_stat_button" icon="fa-exclamation-triangle"
                    invisible="open_invoice_amount == 0">
                <div class="o_stat_info text-danger">
                    <span class="o_stat_value">
                        <field name="open_invoice_amount" widget="monetary"/>
                    </span>
                    <span class="o_stat_text">Due</span>
                </div>
            </button>
        </div>
    </sheet>
</form>
```

---

## OWL Dashboard Component

### Dashboard Action (v16+)
```javascript
/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class MyDashboard extends Component {
    static template = "my_module.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            kpis: {},
            loading: true,
        });

        onWillStart(async () => {
            await this.loadKPIs();
        });
    }

    async loadKPIs() {
        this.state.loading = true;
        try {
            this.state.kpis = await this.orm.call(
                "my.dashboard",
                "get_dashboard_data",
                []
            );
        } finally {
            this.state.loading = false;
        }
    }

    openAction(action) {
        this.action.doAction(action);
    }
}

registry.category("actions").add("my_module.dashboard", MyDashboard);
```

### Dashboard Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.Dashboard">
        <div class="o_my_dashboard container-fluid">
            <div class="row mt-4">
                <!-- KPI Cards -->
                <div class="col-lg-3 col-md-6 mb-4">
                    <div class="card bg-primary text-white h-100"
                         t-on-click="() => this.openAction('sale.action_orders')">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-white-50">Sales</h6>
                                    <h2 t-esc="state.kpis.sale_count || 0"/>
                                </div>
                                <i class="fa fa-shopping-cart fa-3x opacity-50"/>
                            </div>
                        </div>
                        <div class="card-footer bg-transparent border-0">
                            <small>This Month: <t t-esc="state.kpis.sale_amount || 0"/></small>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6 mb-4">
                    <div class="card bg-success text-white h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-white-50">Revenue</h6>
                                    <h2 t-esc="state.kpis.revenue || 0"/>
                                </div>
                                <i class="fa fa-dollar fa-3x opacity-50"/>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6 mb-4">
                    <div class="card bg-warning text-dark h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6>Pending</h6>
                                    <h2 t-esc="state.kpis.pending_count || 0"/>
                                </div>
                                <i class="fa fa-clock-o fa-3x opacity-50"/>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6 mb-4">
                    <div class="card bg-danger text-white h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-white-50">Overdue</h6>
                                    <h2 t-esc="state.kpis.overdue_count || 0"/>
                                </div>
                                <i class="fa fa-exclamation-triangle fa-3x opacity-50"/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chart Area -->
            <div class="row">
                <div class="col-lg-8 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Sales Trend</h5>
                        </div>
                        <div class="card-body">
                            <!-- Embed graph view or custom chart -->
                            <div id="sales_chart" style="height: 300px;"/>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Top Products</h5>
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                <t t-foreach="state.kpis.top_products || []" t-as="product">
                                    <li class="list-group-item d-flex justify-content-between">
                                        <span t-esc="product.name"/>
                                        <span class="badge bg-primary rounded-pill"
                                              t-esc="product.count"/>
                                    </li>
                                </t>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</templates>
```

### Dashboard Data Provider
```python
class MyDashboard(models.TransientModel):
    _name = 'my.dashboard'
    _description = 'Dashboard Data Provider'

    @api.model
    def get_dashboard_data(self):
        """Return KPI data for dashboard."""
        today = fields.Date.today()
        month_start = today.replace(day=1)

        # Sales KPIs
        sales = self.env['sale.order'].search([
            ('date_order', '>=', month_start),
            ('state', 'in', ['sale', 'done']),
        ])

        # Pending orders
        pending = self.env['sale.order'].search_count([
            ('state', '=', 'draft'),
        ])

        # Overdue invoices
        overdue = self.env['account.move'].search_count([
            ('move_type', '=', 'out_invoice'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '<', today),
        ])

        # Top products
        top_products = self._get_top_products(limit=5)

        return {
            'sale_count': len(sales),
            'sale_amount': sum(sales.mapped('amount_total')),
            'revenue': self._get_revenue(),
            'pending_count': pending,
            'overdue_count': overdue,
            'top_products': top_products,
        }

    def _get_top_products(self, limit=5):
        """Get top selling products."""
        query = """
            SELECT pp.id, pt.name, SUM(sol.product_uom_qty) as qty
            FROM sale_order_line sol
            JOIN product_product pp ON pp.id = sol.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN sale_order so ON so.id = sol.order_id
            WHERE so.state IN ('sale', 'done')
            AND so.date_order >= %s
            GROUP BY pp.id, pt.name
            ORDER BY qty DESC
            LIMIT %s
        """
        month_start = fields.Date.today().replace(day=1)
        self.env.cr.execute(query, (month_start, limit))

        return [
            {'id': row[0], 'name': row[1], 'count': int(row[2])}
            for row in self.env.cr.fetchall()
        ]

    def _get_revenue(self):
        """Calculate monthly revenue."""
        month_start = fields.Date.today().replace(day=1)
        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', month_start),
        ])
        return sum(invoices.mapped('amount_total'))
```

---

## Search Filters for Dashboard

### Search View with Defaults
```xml
<record id="sale_analysis_view_search" model="ir.ui.view">
    <field name="name">sale.analysis.search</field>
    <field name="model">sale.analysis</field>
    <field name="arch" type="xml">
        <search>
            <!-- Filters -->
            <filter name="current_month" string="This Month"
                    domain="[('date', '>=', (context_today() - relativedelta(day=1)).strftime('%Y-%m-%d'))]"/>
            <filter name="current_quarter" string="This Quarter"
                    domain="[('date', '>=', (context_today() - relativedelta(months=(context_today().month - 1) % 3, day=1)).strftime('%Y-%m-%d'))]"/>
            <filter name="current_year" string="This Year"
                    domain="[('date', '>=', (context_today()).strftime('%Y-01-01'))]"/>
            <separator/>
            <filter name="confirmed" string="Confirmed"
                    domain="[('state', '=', 'sale')]"/>

            <!-- Group By -->
            <group expand="1" string="Group By">
                <filter name="group_by_date" string="Date"
                        context="{'group_by': 'date:month'}"/>
                <filter name="group_by_partner" string="Customer"
                        context="{'group_by': 'partner_id'}"/>
                <filter name="group_by_product" string="Product"
                        context="{'group_by': 'product_id'}"/>
                <filter name="group_by_category" string="Category"
                        context="{'group_by': 'categ_id'}"/>
                <filter name="group_by_user" string="Salesperson"
                        context="{'group_by': 'user_id'}"/>
            </group>
        </search>
    </field>
</record>
```

---

## Cohort View (Enterprise)

### Cohort Analysis
```xml
<record id="sale_analysis_view_cohort" model="ir.ui.view">
    <field name="name">sale.analysis.cohort</field>
    <field name="model">sale.analysis</field>
    <field name="arch" type="xml">
        <cohort string="Sales Cohort"
                date_start="date"
                date_stop="date"
                interval="month"
                measure="price_total"/>
    </field>
</record>
```

---

## Best Practices

1. **Use database views** - _auto=False for aggregated models
2. **Index key columns** - Add indexes to frequently filtered fields
3. **Pre-aggregate** - Calculate totals in SQL, not Python
4. **Cache expensive** - Use Redis/Memcached for heavy queries
5. **Limit date ranges** - Default to current month/quarter
6. **Add search filters** - Make it easy to drill down
7. **Use measures wisely** - Choose meaningful KPIs
8. **Refresh async** - Use background jobs for heavy data
9. **Mobile friendly** - Design for responsive display
10. **Test performance** - Verify with production data volumes
