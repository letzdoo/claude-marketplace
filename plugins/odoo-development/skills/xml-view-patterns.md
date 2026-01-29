# XML View Patterns Reference

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  XML VIEW PATTERNS                                                           ║
║  Complete reference for Odoo view definitions with version-specific syntax   ║
║  Critical: visibility syntax differs between versions                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## View Types Overview

| View Type | Purpose | Element |
|-----------|---------|---------|
| Form | Single record editing | `<form>` |
| Tree/List | Multiple records display | `<tree>` |
| Kanban | Card-based view | `<kanban>` |
| Search | Filtering/grouping | `<search>` |
| Graph | Charts/analytics | `<graph>` |
| Pivot | Pivot tables | `<pivot>` |
| Calendar | Date-based display | `<calendar>` |
| Gantt | Timeline view | `<gantt>` |

---

## Form View

### Basic Structure
```xml
<record id="my_model_view_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form string="My Model">
            <header>
                <!-- Status bar and buttons -->
            </header>
            <sheet>
                <!-- Main content -->
            </sheet>
            <div class="oe_chatter">
                <!-- Mail integration -->
            </div>
        </form>
    </field>
</record>
```

### Complete Form Example (v18)
```xml
<record id="my_model_view_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form string="My Model">
            <header>
                <button name="action_confirm"
                        type="object"
                        string="Confirm"
                        class="btn-primary"
                        invisible="state != 'draft'"/>
                <button name="action_cancel"
                        type="object"
                        string="Cancel"
                        invisible="state not in ('draft', 'confirmed')"/>
                <field name="state" widget="statusbar"
                       statusbar_visible="draft,confirmed,done"/>
            </header>
            <sheet>
                <div class="oe_button_box" name="button_box">
                    <button name="action_view_invoices"
                            type="object"
                            class="oe_stat_button"
                            icon="fa-pencil-square-o">
                        <field name="invoice_count" widget="statinfo"
                               string="Invoices"/>
                    </button>
                </div>
                <widget name="web_ribbon" title="Archived"
                        bg_color="bg-danger"
                        invisible="active"/>
                <div class="oe_title">
                    <h1>
                        <field name="name" placeholder="Name"/>
                    </h1>
                </div>
                <group>
                    <group string="General">
                        <field name="partner_id"/>
                        <field name="date"/>
                        <field name="user_id"/>
                    </group>
                    <group string="Details">
                        <field name="company_id" groups="base.group_multi_company"/>
                        <field name="currency_id" invisible="1"/>
                        <field name="amount"/>
                    </group>
                </group>
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <tree editable="bottom">
                                <field name="sequence" widget="handle"/>
                                <field name="name"/>
                                <field name="quantity"/>
                                <field name="price_unit"/>
                                <field name="subtotal"/>
                            </tree>
                        </field>
                    </page>
                    <page string="Notes" name="notes">
                        <field name="notes" placeholder="Internal notes..."/>
                    </page>
                </notebook>
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

---

## Visibility Syntax by Version

### v14-v16: attrs Syntax
```xml
<!-- DEPRECATED in v16, REMOVED in v17 -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'readonly': [('state', '!=', 'draft')],
               'required': [('type', '=', 'customer')]}"/>

<button name="action"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>

<group attrs="{'invisible': [('show_details', '=', False)]}">
    <field name="detail"/>
</group>
```

### v17+: Inline Expression Syntax
```xml
<!-- REQUIRED in v17+ -->
<field name="partner_id"
       invisible="state == 'draft'"
       readonly="state != 'draft'"
       required="type == 'customer'"/>

<button name="action"
        invisible="state != 'draft'"/>

<group invisible="not show_details">
    <field name="detail"/>
</group>
```

### Expression Conversion Table

| attrs Domain | v17+ Expression |
|--------------|-----------------|
| `[('field', '=', 'value')]` | `field == 'value'` |
| `[('field', '!=', 'value')]` | `field != 'value'` |
| `[('field', '=', True)]` | `field` |
| `[('field', '=', False)]` | `not field` |
| `[('field', 'in', ['a','b'])]` | `field in ('a', 'b')` |
| `[('field', '>', 0)]` | `field > 0` |
| `['&', A, B]` | `A and B` |
| `['|', A, B]` | `A or B` |

### Complex Expressions (v17+)
```xml
<!-- AND condition -->
<field name="x" invisible="state == 'draft' and not is_manager"/>

<!-- OR condition -->
<field name="x" invisible="state == 'done' or state == 'cancel'"/>

<!-- Nested -->
<field name="x" invisible="state == 'draft' or (type == 'service' and qty == 0)"/>

<!-- Parent access in One2many -->
<field name="x" invisible="parent.state != 'draft'"/>

<!-- Context access -->
<field name="x" invisible="context.get('hide_field')"/>
```

---

## Tree/List View

### Basic Tree
```xml
<record id="my_model_view_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree string="My Models">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date"/>
            <field name="state"/>
            <field name="amount" sum="Total"/>
        </tree>
    </field>
</record>
```

### Advanced Tree (v17+)
```xml
<tree string="My Models"
      decoration-danger="state == 'cancel'"
      decoration-warning="state == 'draft'"
      decoration-success="state == 'done'"
      default_order="date desc">
    <field name="sequence" widget="handle"/>
    <field name="name"/>
    <field name="partner_id"/>
    <field name="date"/>
    <field name="state" widget="badge"
           decoration-success="state == 'done'"
           decoration-info="state == 'confirmed'"
           decoration-warning="state == 'draft'"/>
    <field name="amount" sum="Total"/>
    <field name="company_id" column_invisible="True"/>
    <field name="internal_notes" optional="hide"/>
</tree>
```

### Editable Tree
```xml
<tree editable="bottom">  <!-- or "top" -->
    <field name="product_id"/>
    <field name="quantity"/>
    <field name="price_unit"/>
    <field name="subtotal" readonly="1"/>
</tree>
```

### Column Visibility (v17+)
```xml
<!-- Hide column completely -->
<field name="internal_id" column_invisible="True"/>

<!-- Optional column (user can show/hide) -->
<field name="notes" optional="hide"/>
<field name="important" optional="show"/>

<!-- Conditional column visibility -->
<field name="cost" column_invisible="not context.get('show_cost')"/>
```

---

## Search View

```xml
<record id="my_model_view_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search string="Search My Model">
            <!-- Search fields -->
            <field name="name"/>
            <field name="partner_id"/>
            <field name="user_id"/>

            <!-- Filters -->
            <separator/>
            <filter name="draft" string="Draft"
                    domain="[('state', '=', 'draft')]"/>
            <filter name="confirmed" string="Confirmed"
                    domain="[('state', '=', 'confirmed')]"/>
            <separator/>
            <filter name="my_records" string="My Records"
                    domain="[('user_id', '=', uid)]"/>
            <separator/>
            <filter name="today" string="Today"
                    domain="[('date', '=', context_today().strftime('%Y-%m-%d'))]"/>
            <filter name="this_month" string="This Month"
                    domain="[('date', '>=', (context_today() - relativedelta(day=1)).strftime('%Y-%m-%d')),
                             ('date', '&lt;', (context_today() + relativedelta(months=1, day=1)).strftime('%Y-%m-%d'))]"/>

            <!-- Group By -->
            <group expand="0" string="Group By">
                <filter name="group_state" string="Status"
                        context="{'group_by': 'state'}"/>
                <filter name="group_partner" string="Partner"
                        context="{'group_by': 'partner_id'}"/>
                <filter name="group_date" string="Date"
                        context="{'group_by': 'date:month'}"/>
            </group>

            <!-- Search Panel (left sidebar) -->
            <searchpanel>
                <field name="state" icon="fa-filter" enable_counters="1"/>
                <field name="category_id" icon="fa-folder" enable_counters="1"/>
            </searchpanel>
        </search>
    </field>
</record>
```

---

## Kanban View

```xml
<record id="my_model_view_kanban" model="ir.ui.view">
    <field name="name">my.model.kanban</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state"
                class="o_kanban_small_column"
                on_create="quick_create"
                quick_create_view="my_module.my_model_view_form_quick_create">
            <field name="id"/>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="state"/>
            <field name="color"/>
            <templates>
                <t t-name="kanban-box">
                    <div t-attf-class="oe_kanban_card oe_kanban_global_click #{kanban_color(record.color.raw_value)}">
                        <div class="oe_kanban_content">
                            <div class="o_kanban_record_top">
                                <div class="o_kanban_record_headings">
                                    <strong class="o_kanban_record_title">
                                        <field name="name"/>
                                    </strong>
                                </div>
                                <div class="o_dropdown_kanban dropdown">
                                    <a role="button" class="dropdown-toggle o-no-caret btn"
                                       data-bs-toggle="dropdown" href="#">
                                        <span class="fa fa-ellipsis-v"/>
                                    </a>
                                    <div class="dropdown-menu" role="menu">
                                        <a t-if="widget.editable" role="menuitem"
                                           type="edit" class="dropdown-item">Edit</a>
                                        <a t-if="widget.deletable" role="menuitem"
                                           type="delete" class="dropdown-item">Delete</a>
                                    </div>
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
    </field>
</record>
```

---

## View Inheritance

### Basic Inheritance
```xml
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.my_module</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <!-- Add field after existing field -->
        <xpath expr="//field[@name='email']" position="after">
            <field name="x_custom_field"/>
        </xpath>

        <!-- Add field before existing field -->
        <xpath expr="//field[@name='phone']" position="before">
            <field name="x_another_field"/>
        </xpath>

        <!-- Replace field -->
        <xpath expr="//field[@name='website']" position="replace">
            <field name="website" widget="url"/>
        </xpath>

        <!-- Add attributes -->
        <xpath expr="//field[@name='name']" position="attributes">
            <attribute name="required">1</attribute>
        </xpath>

        <!-- Add inside element -->
        <xpath expr="//group[@name='sale']" position="inside">
            <field name="x_sales_field"/>
        </xpath>

        <!-- Add new page to notebook -->
        <xpath expr="//notebook" position="inside">
            <page string="Custom" name="custom">
                <group>
                    <field name="x_custom_field"/>
                </group>
            </page>
        </xpath>
    </field>
</record>
```

### XPath Expressions

| Expression | Matches |
|------------|---------|
| `//field[@name='x']` | Field with name='x' |
| `//group[@name='x']` | Group with name='x' |
| `//page[@name='x']` | Page with name='x' |
| `//button[@name='x']` | Button with name='x' |
| `//notebook` | First notebook |
| `//sheet` | The sheet element |
| `//div[@class='x']` | Div with specific class |

### Position Values

| Position | Action |
|----------|--------|
| `before` | Insert before matched element |
| `after` | Insert after matched element |
| `inside` | Insert as last child |
| `replace` | Replace entire element |
| `attributes` | Modify attributes only |

### CRITICAL: Always Verify XPath Expressions

**ALWAYS read the parent view structure before writing inheritance code.** XPath expressions must match the ACTUAL view structure, not assumptions.

#### Common Mistakes
```xml
<!-- ❌ WRONG: Assuming structure without verification -->
<xpath expr="//div[hasclass('flex-row')]" position="inside">
    <field name="x_custom_field"/>
</xpath>

<!-- The actual view might use QWeb templates: -->
<!-- <t t-name="card"><div><div class="flex-row">... -->
```

#### Correct Workflow
```python
# 1. FIRST: Read the parent view to understand structure
# Read base.res_users_apikeys_view_kanban

# 2. THEN: Write correct xpath based on actual structure
```

```xml
<!-- ✅ CORRECT: Verified against actual view structure -->
<record id="res_users_apikeys_view_kanban_inherit" model="ir.ui.view">
    <field name="name">res.users.apikeys.kanban.inherit</field>
    <field name="model">res.users.apikeys</field>
    <field name="inherit_id" ref="base.res_users_apikeys_view_kanban"/>
    <field name="arch" type="xml">
        <!-- Correct xpath after reading actual view structure -->
        <xpath expr="//t[@t-name='card']/div/div" position="inside">
            <span t-if="record.is_readonly.raw_value"
                  class="badge text-bg-warning ms-2"
                  title="This API key can only perform read operations"/>
        </xpath>
    </field>
</record>
```

#### Best Practice Checklist
- ✅ Read parent view XML file first
- ✅ Identify exact element structure (div, t, group, etc.)
- ✅ Note QWeb templates (t-name, t-if, etc.)
- ✅ Verify class names and attributes
- ✅ Test xpath matches target element
- ❌ Never assume structure based on common patterns

---

## Actions and Menus

### Window Action
```xml
<record id="my_model_action" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form,kanban</field>
    <field name="domain">[('active', '=', True)]</field>
    <field name="context">{'search_default_my_records': 1}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first record
        </p>
        <p>
            Click the button to get started.
        </p>
    </field>
</record>
```

### Menu Items
```xml
<!-- Root menu -->
<menuitem id="my_module_menu_root"
          name="My Module"
          sequence="10"
          web_icon="my_module,static/description/icon.png"/>

<!-- Submenu -->
<menuitem id="my_module_menu_main"
          name="Main Menu"
          parent="my_module_menu_root"
          sequence="10"/>

<!-- Action menu item -->
<menuitem id="my_model_menu"
          name="My Models"
          parent="my_module_menu_main"
          action="my_model_action"
          sequence="10"/>
```

---

## Common Widgets

| Widget | Field Types | Purpose |
|--------|-------------|---------|
| `statusbar` | Selection | Status bar display |
| `badge` | Selection | Colored badge |
| `priority` | Selection | Star rating |
| `many2one_avatar_user` | Many2one | User avatar |
| `many2many_tags` | Many2many | Tag chips |
| `monetary` | Float/Monetary | Currency display |
| `handle` | Integer | Drag handle |
| `boolean_toggle` | Boolean | Toggle switch |
| `date` | Date | Date picker |
| `datetime` | Datetime | Datetime picker |
| `image` | Binary | Image display |
| `url` | Char | Clickable URL |
| `email` | Char | Mailto link |
| `phone` | Char | Tel link |
| `html` | Html | Rich text editor |
| `progressbar` | Float/Integer | Progress bar |

---

## Version-Specific Summary

| Feature | v14-v16 | v17+ |
|---------|---------|------|
| Visibility | `attrs="{'invisible': [...]}"` | `invisible="expr"` |
| Readonly | `attrs="{'readonly': [...]}"` | `readonly="expr"` |
| Required | `attrs="{'required': [...]}"` | `required="expr"` |
| Column hide | N/A | `column_invisible="True"` |
| Optional cols | Limited | `optional="show/hide"` |
