# Report Generation Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  REPORT PATTERNS                                                             ║
║  PDF reports, QWeb templates, and document generation                        ║
║  Use for invoices, delivery slips, quotes, and custom documents              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Report Types

| Type | Use Case | Technology |
|------|----------|------------|
| PDF | Printable documents | QWeb + wkhtmltopdf |
| HTML | Screen display | QWeb |
| Excel | Data export | xlsxwriter/openpyxl |

---

## Basic Report Structure

### File Organization
```
my_module/
├── report/
│   ├── __init__.py
│   ├── my_report.py           # Report logic (optional)
│   └── my_report_templates.xml # QWeb templates
└── __manifest__.py
```

### Manifest Entry
```python
{
    'data': [
        'report/my_report_templates.xml',
    ],
}
```

---

## PDF Report Definition

### Report Action (XML)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Report Action -->
    <record id="report_my_model" model="ir.actions.report">
        <field name="name">My Report</field>
        <field name="model">my.model</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">my_module.report_my_model_document</field>
        <field name="report_file">my_module.report_my_model_document</field>
        <field name="print_report_name">'MyReport - %s' % object.name</field>
        <field name="binding_model_id" ref="model_my_model"/>
        <field name="binding_type">report</field>
        <field name="paperformat_id" ref="base.paperformat_euro"/>
    </record>

    <!-- Report Template -->
    <template id="report_my_model_document">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>
                            <span t-field="doc.name"/>
                        </h2>

                        <div class="row mt-4">
                            <div class="col-6">
                                <strong>Customer:</strong>
                                <span t-field="doc.partner_id.name"/>
                            </div>
                            <div class="col-6 text-end">
                                <strong>Date:</strong>
                                <span t-field="doc.date"/>
                            </div>
                        </div>

                        <table class="table table-sm mt-4">
                            <thead>
                                <tr>
                                    <th>Description</th>
                                    <th class="text-end">Quantity</th>
                                    <th class="text-end">Price</th>
                                    <th class="text-end">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-foreach="doc.line_ids" t-as="line">
                                    <tr>
                                        <td><span t-field="line.name"/></td>
                                        <td class="text-end">
                                            <span t-field="line.quantity"/>
                                        </td>
                                        <td class="text-end">
                                            <span t-field="line.price_unit"
                                                  t-options='{"widget": "monetary",
                                                              "display_currency": doc.currency_id}'/>
                                        </td>
                                        <td class="text-end">
                                            <span t-field="line.subtotal"
                                                  t-options='{"widget": "monetary",
                                                              "display_currency": doc.currency_id}'/>
                                        </td>
                                    </tr>
                                </t>
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="3" class="text-end">
                                        <strong>Total:</strong>
                                    </td>
                                    <td class="text-end">
                                        <strong>
                                            <span t-field="doc.amount_total"
                                                  t-options='{"widget": "monetary",
                                                              "display_currency": doc.currency_id}'/>
                                        </strong>
                                    </td>
                                </tr>
                            </tfoot>
                        </table>

                        <div t-if="doc.notes" class="mt-4">
                            <strong>Notes:</strong>
                            <p t-field="doc.notes"/>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

---

## QWeb Template Syntax

### Basic Output
```xml
<!-- Text content -->
<span t-field="doc.name"/>

<!-- With formatting -->
<span t-field="doc.date" t-options='{"format": "dd/MM/yyyy"}'/>

<!-- Raw output (no escaping) -->
<span t-out="doc.html_content"/>

<!-- Escaped output -->
<span t-esc="doc.description"/>
```

### Field Widgets
```xml
<!-- Monetary -->
<span t-field="doc.amount"
      t-options='{"widget": "monetary",
                  "display_currency": doc.currency_id}'/>

<!-- Date -->
<span t-field="doc.date"
      t-options='{"format": "MMMM dd, yyyy"}'/>

<!-- Float precision -->
<span t-field="doc.quantity"
      t-options='{"precision": 2}'/>

<!-- Duration -->
<span t-field="doc.duration"
      t-options='{"widget": "duration",
                  "unit": "hour"}'/>

<!-- Image -->
<img t-att-src="image_data_uri(doc.image)"
     style="max-width: 200px;"/>

<!-- Barcode -->
<img t-att-src="'/report/barcode/?barcode_type=Code128&amp;value=%s&amp;width=200&amp;height=50' % doc.code"/>
```

### Conditionals
```xml
<!-- If -->
<div t-if="doc.state == 'draft'">
    <span class="badge bg-secondary">Draft</span>
</div>

<!-- If-Else -->
<t t-if="doc.amount > 0">
    <span class="text-success" t-field="doc.amount"/>
</t>
<t t-else="">
    <span class="text-muted">0.00</span>
</t>

<!-- If-Elif-Else -->
<t t-if="doc.state == 'done'">Done</t>
<t t-elif="doc.state == 'cancel'">Cancelled</t>
<t t-else="">In Progress</t>
```

### Loops
```xml
<!-- Basic loop -->
<t t-foreach="doc.line_ids" t-as="line">
    <tr>
        <td t-esc="line.name"/>
        <td t-esc="line.quantity"/>
    </tr>
</t>

<!-- Loop with index -->
<t t-foreach="doc.line_ids" t-as="line">
    <tr>
        <td t-esc="line_index + 1"/>  <!-- 0-based index -->
        <td t-esc="line.name"/>
    </tr>
</t>

<!-- Loop variables -->
<!-- line_index: current index (0-based) -->
<!-- line_first: True if first iteration -->
<!-- line_last: True if last iteration -->
<!-- line_odd: True if odd iteration (1-based) -->
<!-- line_even: True if even iteration -->
<!-- line_size: total items -->
```

### Attributes
```xml
<!-- Dynamic class -->
<tr t-att-class="'table-danger' if line.amount &lt; 0 else ''">

<!-- Dynamic style -->
<span t-att-style="'color: red;' if doc.overdue else ''"/>

<!-- Multiple attributes -->
<div t-attf-class="alert alert-#{doc.state == 'done' and 'success' or 'warning'}"/>
```

### Variables
```xml
<!-- Set variable -->
<t t-set="total" t-value="sum(doc.line_ids.mapped('amount'))"/>
<span t-esc="total"/>

<!-- String formatting -->
<t t-set="title" t-value="'Invoice %s' % doc.name"/>
```

---

## External Layout

### Using Company Header/Footer
```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <!-- Uses company letterhead -->
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Your content here -->
                </div>
            </t>
        </t>
    </t>
</template>
```

### Minimal Layout (No Header/Footer)
```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.basic_layout">
                <div class="page">
                    <!-- Your content here -->
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Custom Report Logic

### Python Report Model
```python
# report/my_report.py
from odoo import api, models


class MyReport(models.AbstractModel):
    _name = 'report.my_module.report_my_model_document'
    _description = 'My Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Prepare report data."""
        docs = self.env['my.model'].browse(docids)

        # Calculate totals
        totals = {
            'amount': sum(docs.mapped('amount_total')),
            'count': len(docs),
        }

        # Get additional data
        categories = docs.mapped('category_id')

        return {
            'doc_ids': docids,
            'doc_model': 'my.model',
            'docs': docs,
            'data': data,
            'totals': totals,
            'categories': categories,
            'company': self.env.company,
            'format_amount': self._format_amount,
        }

    def _format_amount(self, amount, currency):
        """Format amount with currency."""
        return currency.format(amount)
```

### Using Custom Values in Template
```xml
<template id="report_my_model_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Use custom values -->
                    <p>Total Records: <t t-esc="totals['count']"/></p>
                    <p>Grand Total: <t t-esc="format_amount(totals['amount'], doc.currency_id)"/></p>

                    <!-- Access categories -->
                    <ul>
                        <t t-foreach="categories" t-as="cat">
                            <li t-esc="cat.name"/>
                        </t>
                    </ul>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Paper Format

### Define Custom Paper Format
```xml
<record id="paperformat_custom" model="report.paperformat">
    <field name="name">Custom Format</field>
    <field name="default" eval="False"/>
    <field name="format">A4</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">40</field>
    <field name="margin_bottom">20</field>
    <field name="margin_left">7</field>
    <field name="margin_right">7</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">35</field>
    <field name="dpi">90</field>
</record>

<!-- Use in report -->
<record id="report_my_model" model="ir.actions.report">
    <field name="paperformat_id" ref="paperformat_custom"/>
</record>
```

### Standard Paper Formats
- `base.paperformat_euro` - A4 Portrait
- `base.paperformat_us` - Letter Portrait

---

## Print from Python

### Single Record
```python
def action_print(self):
    """Print report for current record."""
    return self.env.ref('my_module.report_my_model').report_action(self)
```

### Multiple Records
```python
def action_print_selected(self):
    """Print report for selected records."""
    return self.env.ref('my_module.report_my_model').report_action(self.ids)
```

### With Custom Data
```python
def action_print_with_data(self):
    """Print with custom parameters."""
    data = {
        'date_from': self.date_from,
        'date_to': self.date_to,
        'include_draft': self.include_draft,
    }
    return self.env.ref('my_module.report_my_model').report_action(
        self, data=data
    )
```

---

## CSS Styling

### Inline Styles
```xml
<style>
    .my-report-table {
        width: 100%;
        border-collapse: collapse;
    }
    .my-report-table th {
        background-color: #f5f5f5;
        border-bottom: 2px solid #333;
    }
    .my-report-table td {
        border-bottom: 1px solid #ddd;
        padding: 8px;
    }
    .page-break {
        page-break-after: always;
    }
</style>
```

### External Stylesheet
```xml
<!-- In manifest assets -->
'assets': {
    'web.report_assets_common': [
        'my_module/static/src/scss/report.scss',
    ],
},
```

---

## Multi-Page Reports

### Page Breaks
```xml
<t t-foreach="docs" t-as="doc">
    <div class="page">
        <!-- Page content -->
    </div>
    <t t-if="not doc_last">
        <div class="page-break"/>
    </t>
</t>
```

### Grouped Reports
```xml
<t t-set="grouped" t-value="docs.grouped('category_id')"/>
<t t-foreach="grouped.items()" t-as="group">
    <div class="page">
        <h2 t-esc="group[0].name or 'Uncategorized'"/>
        <t t-foreach="group[1]" t-as="doc">
            <!-- Document content -->
        </t>
    </div>
</t>
```

---

## Report Inheritance

### Extend Existing Report
```xml
<template id="report_invoice_document_inherit"
          inherit_id="account.report_invoice_document">
    <xpath expr="//div[@name='invoice_address']" position="after">
        <div class="col-6">
            <strong>Custom Field:</strong>
            <span t-field="o.x_custom_field"/>
        </div>
    </xpath>
</template>
```

---

## Best Practices

1. **Use external_layout** for professional documents with company header
2. **Test PDF rendering** - wkhtmltopdf may render differently than browser
3. **Handle empty data** - Use `t-if` to check before displaying
4. **Format currencies properly** - Always use monetary widget with currency
5. **Escape user content** - Use `t-esc` or `t-field` to prevent XSS
6. **Add page breaks** - Use CSS `page-break-after: always` between records
7. **Optimize images** - Resize before including in reports
8. **Test multi-record** - Verify reports work with multiple records
