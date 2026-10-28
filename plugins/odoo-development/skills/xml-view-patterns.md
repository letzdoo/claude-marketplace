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
<!-- CORRECT in v14-v16 (also in 16.0: a bare invisible="state == 'draft'" is NOT
     evaluated per record there). REMOVED in v17: views using attrs/states fail validation. -->
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
        <tree>
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
<tree decoration-danger="state == 'cancel'"
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

### Anchor on Names, Never on Position

Anchor on a stable, identifying attribute (an element's `name`), never on document position: the parent view belongs to another module that changes it freely, and a positional match silently lands on the wrong element or breaks at install.

```xml
<!-- good: shorthand form, matches the field by name -->
<field name="partner_id" position="after">
    <field name="delivery_instructions"/>
</field>

<!-- good: xpath when the shorthand cannot express the match -->
<xpath expr="//page[@name='other_information']//field[@name='user_id']" position="attributes">
    <attribute name="readonly">1</attribute>
</xpath>

<!-- bad: breaks as soon as the parent view inserts or reorders anything -->
<xpath expr="//group[2]/field[3]" position="after">
    <field name="delivery_instructions"/>
</xpath>
```

Shorthand matching semantics (same in 14.0-19.0):
- A `<field name="x">` locator matches the **first** field named `x` in document order at **any depth** - including fields inside an embedded one2many subview. Other attributes on the locator are ignored. Use an xpath when the name recurs (e.g. `//field[@name='line_ids']/list/field[@name='name']`; `tree` in 14.0-17.0).
- Any **other** tag (`<group name="...">`, `<page name="...">`, `<div class="...">`) matches the first node with the same tag carrying **all** the locator's attributes with equal values (`position` excepted); extra attributes on the target are fine.

Record conventions for inherited views:
- An inheriting view's `name` carries an `.inherit.<details>` suffix.
- A new primary variant (not an extension) sets `<field name="mode">primary</field>` (or `<template primary="True">`) and needs no inherit suffix.
- Do not re-add fields the parent view already renders.

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

## Additional Rules from Odoo's Official Guidelines (verified for 14.0-19.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/odoo-guidelines`, branch 20.0) and were checked against the 14.0-19.0 sources (`odoo/tools/template_inheritance.py`, `odoo/tools/convert.py`).

### Shortcut tags and the `active` trap

Prefer `<menuitem>` and `<template>` (all versions; `<asset>` from 17.0) over raw `<record>`. Trap: an `active` attribute on `<template>` / `<asset>` is applied only when the record is **created** (install, or update when the record does not exist yet). A module **update** (`-u`) refreshes the arch but never changes `active`, so it cannot deactivate an already-installed template.

### `noupdate`

Use `<data noupdate="1">` only for data the user may change and that an update must not overwrite. If the whole file is noupdate, put `noupdate="1"` on the root `<odoo>` and drop `<data>` (supported on `<odoo>` and `<data>` in all of 14.0-19.0; nested elements inherit it).

```xml
<odoo noupdate="1">
    <record id="my_model_rule_user" model="ir.rule">
        ...
    </record>
</odoo>
```

### XML id naming

| Record | Pattern | Example |
|---|---|---|
| View | `<model>_view_<type>` | `my_model_view_form`, `my_model_view_search` (`_view_tree` 14.0-17.0, `_view_list` 18.0+) |
| Action | `<model>_action[_<detail>]` | `my_model_action`, `my_model_action_draft` |
| Window-action view | `<model>_action_view_<type>` | `my_model_action_view_form` |
| Menu | `<model>_menu[_<do_stuff>]` | `my_model_menu`, `my_model_menu_config` |
| Group | `<module>_group_<name>` | `my_module_group_manager` |
| Record rule | `<model>_rule_<group>` | `my_model_rule_user` |

Model names use underscores in ids (`my.model` -> `my_model`). The view `name` field mirrors the id with dots (`my.model.view.form`); actions get a real display name. Put `id` before `model` on records.

### CSS classes

Prefix custom CSS classes in views and templates with `o_<module>` (e.g. `o_my_module_badge`); `o_` alone is reserved for the web client. Never style through ids, and keep names flat (`o_my_module_entry`) instead of mirroring the DOM nesting.

### `t-lang` in QWeb reports

`t-lang` is only meaningful on the node that has `t-call` (it is an alias of `t-options-lang`). From 16.0 using it without `t-call` raises a SyntaxError; in 14.0-15.0 it is silently ignored - the document renders in the wrong language without any error.

```xml
<t t-foreach="docs" t-as="doc">
    <t t-call="my_module.report_my_document" t-lang="doc.partner_id.lang"/>
</t>
```

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
| `states="draft,sent"` | supported | removed (use `invisible="state not in (...)"`) |
| Column hide | N/A | `column_invisible="True"` |
| Optional cols | Limited | `optional="show/hide"` |
| Tree `string` attr | `string="..."` supported | Deprecated (omit it) |

| Feature | v14-v17 | v18+ |
|---------|---------|------|
| List view root / type | `<tree>`, `view_mode="tree,form"` | `<list>`, `view_mode="list,form"` (`tree` no longer accepted) |

The `<tree>` examples in this file are 14.0-17.0 syntax; write `<list>` for 18.0+. In 19.0 the form chatter is `<chatter/>` instead of `<div class="oe_chatter">...</div>`. Shortcut tags and `t-lang`: see "Additional Rules from Odoo's Official Guidelines".
