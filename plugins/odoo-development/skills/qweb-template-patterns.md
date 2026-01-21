# QWeb Template Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  QWEB TEMPLATE PATTERNS                                                      ║
║  QWeb templating language for views, reports, and website pages              ║
║  Use for dynamic HTML generation in Odoo                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## QWeb Directives Overview

| Directive | Purpose |
|-----------|---------|
| `t-if` | Conditional rendering |
| `t-elif` | Else-if condition |
| `t-else` | Else branch |
| `t-foreach` | Loop iteration |
| `t-set` | Variable assignment |
| `t-esc` | Escaped output |
| `t-out` | Output (escaped by default) |
| `t-raw` | Unescaped HTML output |
| `t-call` | Include another template |
| `t-att` | Dynamic attribute |
| `t-attf` | Format string attribute |
| `t-field` | Field rendering |
| `t-options` | Field options |

---

## Conditional Rendering

### Basic If/Else
```xml
<t t-if="record.state == 'draft'">
    <span class="badge bg-secondary">Draft</span>
</t>
<t t-elif="record.state == 'confirmed'">
    <span class="badge bg-primary">Confirmed</span>
</t>
<t t-elif="record.state == 'done'">
    <span class="badge bg-success">Done</span>
</t>
<t t-else="">
    <span class="badge bg-danger">Cancelled</span>
</t>
```

### Conditional on Element
```xml
<div t-if="record.partner_id">
    Partner: <t t-esc="record.partner_id.name"/>
</div>

<span t-if="record.amount > 0" class="text-success">
    <t t-esc="record.amount"/>
</span>
<span t-else="" class="text-danger">No amount</span>
```

### Multiple Conditions
```xml
<t t-if="record.active and record.state == 'confirmed'">
    Active and confirmed
</t>

<t t-if="record.type in ['product', 'service']">
    Valid type
</t>

<t t-if="record.amount >= 1000 or record.is_priority">
    High value or priority
</t>
```

---

## Loops and Iteration

### Basic For Loop
```xml
<t t-foreach="records" t-as="record">
    <div class="record-item">
        <span t-esc="record.name"/>
    </div>
</t>
```

### Loop with Index
```xml
<table>
    <t t-foreach="lines" t-as="line">
        <tr>
            <!-- line_index: 0-based index -->
            <td t-esc="line_index + 1"/>
            <!-- line_value: same as line -->
            <td t-esc="line.name"/>
            <!-- line_size: total count -->
            <td t-if="line_index == line_size - 1">Last item</td>
        </tr>
    </t>
</table>
```

### Loop Variables
| Variable | Description |
|----------|-------------|
| `{name}` | Current item |
| `{name}_index` | 0-based index |
| `{name}_size` | Total count |
| `{name}_first` | True if first |
| `{name}_last` | True if last |
| `{name}_odd` | True if odd index |
| `{name}_even` | True if even index |
| `{name}_value` | Same as {name} |

### Loop with Parity
```xml
<t t-foreach="items" t-as="item">
    <tr t-attf-class="#{item_odd and 'odd' or 'even'}">
        <td t-esc="item.name"/>
    </tr>
</t>
```

### Nested Loops
```xml
<t t-foreach="orders" t-as="order">
    <div class="order">
        <h3 t-esc="order.name"/>
        <t t-foreach="order.line_ids" t-as="line">
            <div class="line">
                <span t-esc="line.product_id.name"/>
                <span t-esc="line.quantity"/>
            </div>
        </t>
    </div>
</t>
```

---

## Variables and Expressions

### Setting Variables
```xml
<!-- Simple assignment -->
<t t-set="total" t-value="0"/>

<!-- Expression assignment -->
<t t-set="total" t-value="sum(line.amount for line in lines)"/>

<!-- Content assignment -->
<t t-set="greeting">
    Hello, <t t-esc="user.name"/>!
</t>
```

### Using Variables
```xml
<t t-set="has_lines" t-value="bool(record.line_ids)"/>

<div t-if="has_lines">
    <t t-set="line_count" t-value="len(record.line_ids)"/>
    <span>Total lines: <t t-esc="line_count"/></span>
</div>
```

### Calculations
```xml
<t t-set="subtotal" t-value="record.quantity * record.price"/>
<t t-set="tax" t-value="subtotal * 0.21"/>
<t t-set="total" t-value="subtotal + tax"/>

<div>
    Subtotal: <t t-esc="subtotal"/>
    Tax: <t t-esc="tax"/>
    Total: <t t-esc="total"/>
</div>
```

---

## Output and Escaping

### Escaped Output (Safe)
```xml
<!-- t-esc escapes HTML characters -->
<span t-esc="record.name"/>

<!-- t-out also escapes by default -->
<span t-out="record.description"/>
```

### Unescaped HTML Output
```xml
<!-- t-raw renders HTML as-is (use carefully!) -->
<div t-raw="record.html_content"/>

<!-- t-out with Markup object -->
<div t-out="record.rendered_html"/>
```

### Field Output (Reports/Website)
```xml
<!-- t-field renders with formatting -->
<span t-field="record.date"/>
<span t-field="record.amount"/>
<span t-field="record.partner_id"/>

<!-- t-field with options -->
<span t-field="record.amount" t-options="{'widget': 'monetary'}"/>
<span t-field="record.date" t-options="{'format': 'dd/MM/yyyy'}"/>
```

---

## Dynamic Attributes

### t-att: Dynamic Attribute Value
```xml
<!-- Single attribute -->
<div t-att-class="record.state"/>
<input t-att-value="record.name"/>
<a t-att-href="record.url"/>

<!-- Conditional attribute -->
<div t-att-class="record.active and 'active' or 'inactive'"/>
```

### t-attf: Format String Attribute
```xml
<!-- String interpolation with #{} -->
<div t-attf-class="card state-#{record.state}"/>
<a t-attf-href="/web#id=#{record.id}&amp;model=my.model"/>

<!-- Combine static and dynamic -->
<div t-attf-class="container #{record.is_important and 'important' or ''}"/>
```

### t-att for Multiple Attributes
```xml
<!-- Dictionary of attributes -->
<div t-att="{'class': 'my-class', 'data-id': record.id}"/>
```

### Conditional Attributes
```xml
<!-- Attribute only if condition true -->
<input type="checkbox" t-att-checked="record.active and 'checked'"/>
<button t-att-disabled="not record.can_edit and 'disabled'"/>

<!-- Class list based on conditions -->
<div t-attf-class="
    card
    #{record.state == 'done' and 'bg-success' or ''}
    #{record.is_priority and 'border-warning' or ''}
"/>
```

---

## Template Inheritance and Calls

### Calling Other Templates
```xml
<!-- Define a template -->
<template id="address_block">
    <div class="address">
        <t t-esc="partner.street"/>
        <t t-esc="partner.city"/>
        <t t-esc="partner.country_id.name"/>
    </div>
</template>

<!-- Call the template -->
<t t-call="my_module.address_block">
    <t t-set="partner" t-value="record.partner_id"/>
</t>
```

### Template with Parameters
```xml
<!-- Template expecting parameters -->
<template id="price_display">
    <span t-attf-class="price #{highlight and 'text-success' or ''}">
        <t t-esc="amount"/>
        <t t-esc="currency"/>
    </span>
</template>

<!-- Call with parameters -->
<t t-call="my_module.price_display">
    <t t-set="amount" t-value="record.amount_total"/>
    <t t-set="currency" t-value="record.currency_id.symbol"/>
    <t t-set="highlight" t-value="True"/>
</t>
```

### Inheriting Templates
```xml
<!-- Extend existing template -->
<template id="custom_layout" inherit_id="web.layout">
    <xpath expr="//head" position="inside">
        <link rel="stylesheet" href="/my_module/static/src/css/custom.css"/>
    </xpath>
</template>
```

---

## Report-Specific Patterns

### Report Document Structure
```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h1 t-field="doc.name"/>
                    <!-- Report content -->
                </div>
            </t>
        </t>
    </t>
</template>
```

### Field Formatting in Reports
```xml
<!-- Date formatting -->
<span t-field="doc.date_order" t-options="{'format': 'dd MMMM yyyy'}"/>

<!-- Monetary formatting -->
<span t-field="doc.amount_total"
      t-options="{'widget': 'monetary', 'display_currency': doc.currency_id}"/>

<!-- Duration formatting -->
<span t-field="doc.duration" t-options="{'widget': 'duration'}"/>

<!-- Address formatting -->
<div t-field="doc.partner_id"
     t-options="{'widget': 'contact', 'fields': ['address', 'phone', 'email']}"/>
```

### Table with Totals
```xml
<table class="table table-sm">
    <thead>
        <tr>
            <th>Product</th>
            <th class="text-end">Quantity</th>
            <th class="text-end">Price</th>
            <th class="text-end">Subtotal</th>
        </tr>
    </thead>
    <tbody>
        <t t-foreach="doc.line_ids" t-as="line">
            <tr>
                <td t-esc="line.product_id.name"/>
                <td class="text-end" t-esc="line.quantity"/>
                <td class="text-end" t-field="line.price_unit"/>
                <td class="text-end" t-field="line.price_subtotal"/>
            </tr>
        </t>
    </tbody>
    <tfoot>
        <tr>
            <td colspan="3" class="text-end"><strong>Total:</strong></td>
            <td class="text-end" t-field="doc.amount_total"/>
        </tr>
    </tfoot>
</table>
```

---

## Kanban View QWeb

### Kanban Card Template
```xml
<kanban>
    <field name="name"/>
    <field name="state"/>
    <field name="partner_id"/>
    <field name="color"/>
    <templates>
        <t t-name="kanban-box">
            <div t-attf-class="oe_kanban_card oe_kanban_global_click
                               o_kanban_record_has_image_fill
                               #{record.color.raw_value ? 'oe_kanban_color_' + record.color.raw_value : ''}">
                <div class="oe_kanban_content">
                    <div class="o_kanban_record_top">
                        <div class="o_kanban_record_headings">
                            <strong class="o_kanban_record_title">
                                <field name="name"/>
                            </strong>
                        </div>
                    </div>
                    <div class="o_kanban_record_body">
                        <field name="partner_id"/>
                    </div>
                    <div class="o_kanban_record_bottom">
                        <div class="oe_kanban_bottom_left">
                            <field name="priority" widget="priority"/>
                        </div>
                        <div class="oe_kanban_bottom_right">
                            <field name="user_id" widget="many2one_avatar_user"/>
                        </div>
                    </div>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

### Kanban with Dropdown Menu
```xml
<div class="o_dropdown_kanban dropdown">
    <a role="button" class="dropdown-toggle o-no-caret btn"
       data-bs-toggle="dropdown" href="#">
        <span class="fa fa-ellipsis-v"/>
    </a>
    <div class="dropdown-menu" role="menu">
        <a role="menuitem" type="edit" class="dropdown-item">Edit</a>
        <a role="menuitem" type="delete" class="dropdown-item">Delete</a>
        <div role="separator" class="dropdown-divider"/>
        <a role="menuitem" type="object" name="action_archive"
           class="dropdown-item">Archive</a>
    </div>
</div>
```

---

## Website QWeb Patterns

### Page Template
```xml
<template id="my_page" name="My Page">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <section class="container py-5">
                <h1>My Page Title</h1>
                <t t-foreach="records" t-as="record">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 t-esc="record.name"/>
                            <p t-raw="record.description"/>
                        </div>
                    </div>
                </t>
            </section>
        </div>
    </t>
</template>
```

### Portal Template
```xml
<template id="portal_my_records" name="My Records">
    <t t-call="portal.portal_layout">
        <t t-set="breadcrumbs_searchbar" t-value="True"/>
        <t t-call="portal.portal_searchbar">
            <t t-set="title">My Records</t>
        </t>
        <t t-if="records">
            <t t-foreach="records" t-as="record">
                <div class="card mb-2">
                    <div class="card-body">
                        <a t-attf-href="/my/records/#{record.id}">
                            <t t-esc="record.name"/>
                        </a>
                    </div>
                </div>
            </t>
        </t>
        <t t-else="">
            <p>No records found.</p>
        </t>
    </t>
</template>
```

---

## Useful Expressions

### String Operations
```xml
<t t-esc="record.name.upper()"/>
<t t-esc="record.name[:20]"/>
<t t-esc="', '.join(record.tag_ids.mapped('name'))"/>
<t t-esc="record.name or 'No name'"/>
```

### Number Formatting
```xml
<t t-esc="'%.2f' % record.amount"/>
<t t-esc="'{:,.2f}'.format(record.amount)"/>
<t t-esc="int(record.progress)"/>
```

### Date Formatting
```xml
<!-- Using format_date helper (reports) -->
<t t-esc="format_date(env, record.date)"/>

<!-- Using strftime -->
<t t-esc="record.date.strftime('%d/%m/%Y') if record.date else ''"/>
```

### List Operations
```xml
<t t-esc="len(record.line_ids)"/>
<t t-esc="sum(record.line_ids.mapped('amount'))"/>
<t t-esc="record.line_ids.filtered(lambda l: l.state == 'done')"/>
```

---

## Best Practices

1. **Use t-esc for safety** - Always escape user content
2. **Use t-field in reports** - Proper formatting and translation
3. **Keep logic minimal** - Complex logic belongs in Python
4. **Use t-call for reuse** - DRY principle for templates
5. **Name templates clearly** - Descriptive IDs for maintenance
6. **Use semantic HTML** - Proper structure for accessibility
7. **Handle empty states** - Always check for missing data
8. **Use Bootstrap classes** - Consistent styling with Odoo
9. **Test with real data** - Verify edge cases
10. **Version awareness** - QWeb syntax stable across versions
