# Model and View Inheritance Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  INHERITANCE PATTERNS                                                        ║
║  Extending models, views, and controllers without modifying core code        ║
║  Use for customizations, extensions, and module integrations                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Inheritance Types Overview

| Type | `_name` | `_inherit` | Use Case |
|------|---------|-----------|----------|
| Extension | None | `'model'` | Add fields/methods to existing model |
| Delegation | `'new'` | `'model'` | Link new model to existing |
| Prototype | `'new'` | `['model']` | Copy structure from existing |

---

## Model Extension (Most Common)

### Add Fields to Existing Model
```python
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # New fields
    x_loyalty_points = fields.Integer(
        string='Loyalty Points',
        default=0,
    )
    x_customer_tier = fields.Selection(
        selection=[
            ('bronze', 'Bronze'),
            ('silver', 'Silver'),
            ('gold', 'Gold'),
        ],
        string='Customer Tier',
        compute='_compute_customer_tier',
        store=True,
    )
    x_account_manager_id = fields.Many2one(
        comodel_name='res.users',
        string='Account Manager',
    )

    @api.depends('x_loyalty_points')
    def _compute_customer_tier(self):
        for partner in self:
            if partner.x_loyalty_points >= 1000:
                partner.x_customer_tier = 'gold'
            elif partner.x_loyalty_points >= 500:
                partner.x_customer_tier = 'silver'
            else:
                partner.x_customer_tier = 'bronze'
```

### Override Methods
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """Override confirm to add custom logic."""
        # Pre-processing
        for order in self:
            order._check_credit_limit()

        # Call original method
        result = super().action_confirm()

        # Post-processing
        for order in self:
            order._send_confirmation_notification()

        return result

    def _check_credit_limit(self):
        """Custom credit check before confirmation."""
        if self.partner_id.credit_limit and \
           self.amount_total > self.partner_id.credit_limit:
            raise UserError("Order exceeds credit limit.")

    def _send_confirmation_notification(self):
        """Send notification after confirmation."""
        template = self.env.ref('my_module.email_template_order_confirm')
        template.send_mail(self.id)
```

### Extend Computed Fields
```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """Extend to add loyalty discount."""
        super()._compute_amount()

        for line in self:
            if line.order_id.partner_id.x_customer_tier == 'gold':
                # Apply additional 5% discount for gold customers
                line.price_subtotal *= 0.95
```

### Add to Selection Field
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Extend existing selection
    state = fields.Selection(
        selection_add=[
            ('pending_approval', 'Pending Approval'),
            ('approved', 'Approved'),
        ],
        ondelete={
            'pending_approval': 'set default',
            'approved': 'set default',
        },
    )
```

---

## Delegation Inheritance

### Link to Existing Model
```python
class Employee(models.Model):
    _name = 'hr.employee'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Related Partner',
        required=True,
        ondelete='cascade',
    )

    # Employee-specific fields
    department_id = fields.Many2one('hr.department')
    job_id = fields.Many2one('hr.job')

    # Inherited fields from res.partner are accessible directly
    # employee.name -> partner.name
    # employee.email -> partner.email
```

### Custom Delegation
```python
class ProductVariant(models.Model):
    _name = 'product.product'
    _inherits = {'product.template': 'product_tmpl_id'}

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
    )

    # Variant-specific fields
    barcode = fields.Char(string='Barcode')
    default_code = fields.Char(string='Internal Reference')
```

---

## Abstract Models (Mixins)

### Create Reusable Mixin
```python
class TimestampMixin(models.AbstractModel):
    _name = 'timestamp.mixin'
    _description = 'Timestamp Mixin'

    created_at = fields.Datetime(
        string='Created At',
        default=fields.Datetime.now,
        readonly=True,
    )
    updated_at = fields.Datetime(
        string='Updated At',
        readonly=True,
    )

    def write(self, vals):
        vals['updated_at'] = fields.Datetime.now()
        return super().write(vals)


class ApprovalMixin(models.AbstractModel):
    _name = 'approval.mixin'
    _description = 'Approval Mixin'

    approval_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Approval Status',
        default='draft',
        tracking=True,
    )
    approved_by = fields.Many2one(
        comodel_name='res.users',
        string='Approved By',
        readonly=True,
    )
    approved_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
    )

    def action_submit_for_approval(self):
        self.write({'approval_state': 'pending'})

    def action_approve(self):
        self.write({
            'approval_state': 'approved',
            'approved_by': self.env.uid,
            'approved_date': fields.Datetime.now(),
        })

    def action_reject(self):
        self.write({'approval_state': 'rejected'})
```

### Use Mixins
```python
class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'timestamp.mixin', 'approval.mixin']

    name = fields.Char(string='Reference', required=True)
    amount = fields.Monetary(string='Amount')
    # Gets all fields and methods from mixins
```

---

## View Inheritance

### Extend Form View
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_partner_form_inherit" model="ir.ui.view">
        <field name="name">res.partner.form.inherit.my_module</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="arch" type="xml">
            <!-- Add after existing field -->
            <field name="email" position="after">
                <field name="x_loyalty_points"/>
                <field name="x_customer_tier"/>
            </field>

            <!-- Add new page to notebook -->
            <xpath expr="//notebook" position="inside">
                <page string="Loyalty" name="loyalty">
                    <group>
                        <field name="x_loyalty_points"/>
                        <field name="x_customer_tier"/>
                        <field name="x_account_manager_id"/>
                    </group>
                </page>
            </xpath>

            <!-- Replace existing element -->
            <field name="title" position="replace">
                <field name="title" placeholder="Select title..."/>
            </field>

            <!-- Add attributes -->
            <field name="phone" position="attributes">
                <attribute name="required">1</attribute>
            </field>

            <!-- Hide field (v17+) -->
            <field name="fax" position="attributes">
                <attribute name="invisible">1</attribute>
            </field>
        </field>
    </record>
</odoo>
```

### XPath Expressions

```xml
<!-- By field name -->
<field name="partner_id" position="after">

<!-- By xpath -->
<xpath expr="//field[@name='partner_id']" position="after">

<!-- First field in group -->
<xpath expr="//group[1]/field[1]" position="before">

<!-- Field inside specific group -->
<xpath expr="//group[@name='sale_info']/field[@name='date_order']" position="after">

<!-- Page by name -->
<xpath expr="//page[@name='other_info']" position="inside">

<!-- Button by name -->
<xpath expr="//button[@name='action_confirm']" position="before">

<!-- Div by class -->
<xpath expr="//div[hasclass('oe_title')]" position="inside">

<!-- Last element -->
<xpath expr="//sheet/*[last()]" position="after">
```

### Position Types
| Position | Effect |
|----------|--------|
| `inside` | Add as child (at end) |
| `after` | Add as sibling after |
| `before` | Add as sibling before |
| `replace` | Replace entire element |
| `attributes` | Modify attributes |

### Extend Tree View
```xml
<record id="view_order_tree_inherit" model="ir.ui.view">
    <field name="name">sale.order.tree.inherit</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_tree"/>
    <field name="arch" type="xml">
        <field name="amount_total" position="after">
            <field name="x_margin" optional="show"/>
            <field name="x_priority" decoration-danger="x_priority == 'high'"/>
        </field>
    </field>
</record>
```

### Extend Search View
```xml
<record id="view_order_search_inherit" model="ir.ui.view">
    <field name="name">sale.order.search.inherit</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_sales_order_filter"/>
    <field name="arch" type="xml">
        <filter name="my_quotations" position="after">
            <filter string="High Priority" name="high_priority"
                    domain="[('x_priority', '=', 'high')]"/>
        </filter>

        <xpath expr="//group" position="inside">
            <filter string="Priority" name="group_priority"
                    context="{'group_by': 'x_priority'}"/>
        </xpath>
    </field>
</record>
```

---

## Controller Inheritance

### Extend HTTP Controller
```python
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleExtend(WebsiteSale):

    @http.route()
    def cart(self, **post):
        """Extend cart to add custom data."""
        response = super().cart(**post)

        # Add custom values to qcontext
        if hasattr(response, 'qcontext'):
            response.qcontext['x_loyalty_points'] = \
                request.env.user.partner_id.x_loyalty_points

        return response

    @http.route('/shop/cart/update_loyalty', type='json', auth='user')
    def update_loyalty(self, points_to_use):
        """New endpoint for loyalty point redemption."""
        order = request.website.sale_get_order()
        if order:
            order.x_loyalty_points_used = points_to_use
        return {'success': True}
```

---

## Report Inheritance

### Extend Report Template
```xml
<template id="report_invoice_document_inherit"
          inherit_id="account.report_invoice_document">
    <!-- Add custom section -->
    <xpath expr="//div[@id='informations']" position="after">
        <div class="row mt-3">
            <div class="col-6">
                <strong>Customer Tier:</strong>
                <span t-field="o.partner_id.x_customer_tier"/>
            </div>
            <div class="col-6">
                <strong>Loyalty Points Earned:</strong>
                <span t-esc="int(o.amount_total / 10)"/>
            </div>
        </div>
    </xpath>

    <!-- Modify existing content -->
    <xpath expr="//span[@t-field='o.name']" position="attributes">
        <attribute name="class">h2 text-primary</attribute>
    </xpath>
</template>
```

---

## Security Inheritance

### Extend Access Rights
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# Extend existing model access
access_partner_loyalty_user,res.partner.loyalty.user,base.model_res_partner,base.group_user,1,1,0,0
access_partner_loyalty_manager,res.partner.loyalty.manager,base.model_res_partner,my_module.group_loyalty_manager,1,1,1,1
```

### Add Record Rules
```xml
<record id="rule_partner_loyalty_user" model="ir.rule">
    <field name="name">Partner: Loyalty User See Own</field>
    <field name="model_id" ref="base.model_res_partner"/>
    <field name="domain_force">[
        '|',
        ('x_account_manager_id', '=', user.id),
        ('x_account_manager_id', '=', False)
    ]</field>
    <field name="groups" eval="[(4, ref('my_module.group_loyalty_user'))]"/>
</record>
```

---

## Best Practices

### 1. Use Proper Naming
```python
# Fields: x_ prefix for custom fields
x_custom_field = fields.Char()

# Views: include module name
inherit_id="base.view_partner_form"
name="res.partner.form.inherit.my_module"
```

### 2. Call Super Properly
```python
# Good - always call super
def action_confirm(self):
    result = super().action_confirm()
    self._custom_logic()
    return result

# Bad - skipping super breaks inheritance chain
def action_confirm(self):
    self._custom_logic()
    # Missing super() call!
```

### 3. Use Specific XPath
```xml
<!-- Good - specific path -->
<xpath expr="//field[@name='partner_id']" position="after">

<!-- Bad - fragile, may break -->
<xpath expr="//field[3]" position="after">
```

### 4. Handle Dependencies
```python
# Manifest
{
    'depends': ['sale', 'account'],  # Declare all inherited modules
}
```

### 5. Preserve Original Behavior
```python
# Good - extend, don't replace
def _compute_amount(self):
    super()._compute_amount()
    # Add to computed value
    for line in self:
        line.price_subtotal += line.x_extra_fee

# Bad - completely replaces original
def _compute_amount(self):
    for line in self:
        line.price_subtotal = line.quantity * line.price_unit
```

### 6. Never Use 'string' Attribute as Selector
```xml
<!-- Good - use 'name' attribute (stable identifier) -->
<xpath expr="//page[@name='other_info']" position="inside">
<xpath expr="//field[@name='partner_id']" position="after">
<xpath expr="//button[@name='action_confirm']" position="before">

<!-- Bad - 'string' attribute is translated and may change -->
<xpath expr="//page[@string='Other Information']" position="inside">
<xpath expr="//button[@string='Confirm']" position="before">
```

The `string` attribute should not be used as a selector in view inheritance because:
- It contains translatable text that varies by language
- Labels may be changed in future Odoo versions
- Other modules may override the same string differently

Always prefer `name` attributes which are stable technical identifiers.

### 7. Always Verify XML IDs and Views Before Extension

**⚠️ CRITICAL RULE:** Do not trust your memory or make assumptions about XML IDs, views, records, or any other Odoo identifiers. Your memory is flawed by design. Always use the Odoo indexer or search tools to look them up. **Always read the actual Odoo source code** when in doubt.

```python
# Bad - trusting memory or assumptions about XML IDs
view_id = self.env.ref('base.view_partner_form')  # May not exist!

# Good - verify existence before using
try:
    view_id = self.env.ref('base.view_partner_form', raise_if_not_found=False)
    if not view_id:
        raise ValueError("View not found")
except ValueError:
    # Handle missing view
    pass
```

```xml
<!-- Bad - assuming XML ID exists without verification -->
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.my_module</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <!-- This will fail if base.view_partner_form doesn't exist -->
</record>

<!-- Good - verify XML ID exists first using Odoo code/indexer -->
<!-- Before writing this inheritance, verify the XML ID exists:
     1. Use grep/search to find the view definition in Odoo source
     2. Check ir.ui.view records in database
     3. Use Odoo indexer/IDE tools to look up the XML ID
     4. READ THE ACTUAL ODOO SOURCE CODE - never rely on memory
-->
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.my_module</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <!-- Verified that base.view_partner_form exists by reading Odoo source -->
</record>
```

Why this matters:
- XML IDs can change between Odoo versions
- Views may be renamed, removed, or restructured
- Some models may only have certain view types (e.g., only kanban, no form/tree)
- Not all standard models have all view types defined
- Runtime errors occur when referencing non-existent XML IDs
- Memory of Odoo's structure is unreliable and prone to errors

**Real-world example:**
In Odoo 19, the `res.users.api.keys` model only has a kanban view - no form or tree view exists. Attempting to extend a non-existent form view will cause runtime errors. Always verify what views actually exist before attempting to extend them.

```python
# Example: Check what views exist for a model
def check_available_views(self, model_name):
    """Check what view types exist for a model."""
    views = self.env['ir.ui.view'].search([
        ('model', '=', model_name),
        ('type', '!=', False)
    ])
    return {view.type for view in views}

# Before extending: check if the view type exists
# available_views = check_available_views('res.users.api.keys')
# Result might be: {'kanban'}  # Only kanban, no form or tree!
```

**Always verify XML IDs and view existence before use:**
1. **READ THE ACTUAL ODOO SOURCE CODE** - this is the primary method, never rely on memory
2. Use grep/ripgrep to search Odoo source code for the exact XML ID
3. Check the database `ir.model.data` table for the record
4. Use Odoo indexer or IDE integration tools to look up identifiers
5. Verify which view types exist for a model before extending them
6. Check the specific Odoo version's codebase (views differ between versions)
7. Never assume an XML ID exists - always look it up using the tools above

```python
# Example: Verifying a view exists before inheritance
def _check_view_exists(self, xml_id):
    """Check if XML ID exists before using it."""
    try:
        return self.env.ref(xml_id, raise_if_not_found=False)
    except ValueError:
        return False

# Check if specific view type exists for a model
def _check_view_type_exists(self, model_name, view_type):
    """Check if a specific view type exists for a model."""
    return self.env['ir.ui.view'].search([
        ('model', '=', model_name),
        ('type', '=', view_type)
    ], limit=1)

# In data files, you can use noupdate="1" with error handling
# Or use module dependencies to ensure base modules are loaded
```

**Workflow when extending views:**
1. Identify the model you want to extend
2. Search Odoo source code to find available views for that model
3. Verify the view type exists (form, tree, kanban, etc.)
4. Look up the exact XML ID using search/indexer
5. Read the actual view structure to understand the elements
6. Test your XPath expressions against the actual view structure
7. Only then write your view inheritance
8. Never assume or guess - always verify

### 8. Always Test XPath Expressions Before Use

**⚠️ CRITICAL RULE:** After looking up the XML ID and before writing view inheritance, **read the actual view structure** and verify that your XPath expressions will match the correct elements. XPath errors are a common source of view inheritance failures.

```xml
<!-- Bad - assuming structure without verification -->
<record id="view_apikeys_kanban_inherit" model="ir.ui.view">
    <field name="name">res.users.apikeys.kanban.inherit</field>
    <field name="model">res.users.apikeys</field>
    <field name="inherit_id" ref="base.res_users_apikeys_view_kanban"/>
    <field name="arch" type="xml">
        <!-- Wrong XPath - this doesn't match actual structure! -->
        <xpath expr="//div[hasclass('flex-row')]" position="inside">
            <span>My content</span>
        </xpath>
    </field>
</record>
```

**Correct workflow:**
1. **Read the actual view** to understand its structure
2. **Verify the XPath** matches the actual elements
3. Write the correct inheritance

```xml
<!-- Good - verified XPath matches actual structure -->
<record id="view_apikeys_kanban_inherit" model="ir.ui.view">
    <field name="name">res.users.apikeys.kanban.inherit</field>
    <field name="model">res.users.apikeys</field>
    <field name="inherit_id" ref="base.res_users_apikeys_view_kanban"/>
    <field name="arch" type="xml">
        <!-- Correct XPath after reading the view structure:
             The view has <t t-name="card"> not a div with flex-row class -->
        <xpath expr="//t[@t-name='card']/div/div" position="inside">
            <span>My content</span>
        </xpath>
    </field>
</record>
```

**Real-world example from Odoo 19:**
When extending `res.users.apikeys` kanban view, developers might assume there's a `div` with `flex-row` class. However, reading the actual view reveals it uses `<t t-name="card">` structure instead. Using the wrong XPath will cause runtime errors.

**How to test XPath expressions:**
1. Read the source XML view file from Odoo codebase
2. Identify the exact element structure and attributes
3. Write your XPath to match the actual structure
4. Test by upgrading your module and checking for errors
5. If errors occur, re-read the view and adjust XPath

```python
# Example: Read a view to understand its structure
def read_view_structure(self, xml_id):
    """Read view arch to understand structure before inheritance."""
    view = self.env.ref(xml_id, raise_if_not_found=False)
    if view:
        # Print or log the arch to see actual structure
        print(view.arch)
        return view.arch
    return None

# Before writing inheritance:
# read_view_structure('base.res_users_apikeys_view_kanban')
# Examine output to understand structure and write correct XPath
```

**Common XPath mistakes:**
- Assuming class names that don't exist
- Using wrong element names (div vs t vs field)
- Not checking for QWeb template structures (t-name, t-if, etc.)
- Copying XPath from different Odoo versions
- Not accounting for nested structures

**Best practices for XPath:**
1. Always read the actual view first
2. Use specific, precise selectors (element name + attributes)
3. Prefer `name` attributes over classes or string values
4. Test XPath against the actual structure
5. Document why you chose that specific XPath
6. Never copy-paste XPath without verification

### 8. Always Test XPath Expressions Before Use

When inheriting views, incorrect XPath expressions are a common source of errors. Always verify your XPath expressions match the actual view structure by reading the base view first.

```xml
<!-- Bad - guessing the XPath without reading the view -->
<record id="view_apikeys_kanban_inherit" model="ir.ui.view">
    <field name="name">res.users.apikeys.kanban.inherit</field>
    <field name="model">res.users.apikeys</field>
    <field name="inherit_id" ref="base.res_users_apikeys_view_kanban"/>
    <field name="arch" type="xml">
        <!-- This XPath is incorrect - assuming structure without verification -->
        <xpath expr="//div[hasclass('flex-row')]" position="inside">
            <span t-if="record.is_readonly.raw_value"
                  class="badge text-bg-warning ms-2">
                Read-Only
            </span>
        </xpath>
    </field>
</record>

<!-- Good - verified XPath by reading the actual view structure -->
<record id="view_apikeys_kanban_inherit" model="ir.ui.view">
    <field name="name">res.users.apikeys.kanban.inherit</field>
    <field name="model">res.users.apikeys</field>
    <field name="inherit_id" ref="base.res_users_apikeys_view_kanban"/>
    <field name="arch" type="xml">
        <!-- Correct XPath after reading the view and finding <t t-name="card"> -->
        <xpath expr="//t[@t-name='card']/div/div" position="inside">
            <span t-if="record.is_readonly.raw_value"
                  class="badge text-bg-warning ms-2">
                Read-Only
            </span>
        </xpath>
    </field>
</record>
```

**Best Practice Workflow for XPath Expressions:**

1. **Read the base view first** - Never write XPath expressions from memory
2. **Identify the exact element** - Find the precise structure in the view
3. **Write the XPath expression** - Use the actual element names and attributes
4. **Test the inheritance** - Verify the view renders correctly
5. **Debug if needed** - If it fails, re-read the view and correct the XPath

**Common XPath mistakes:**
- Using `hasclass()` with incorrect class names
- Assuming div structure without checking actual elements (could be `<t>`, `<span>`, etc.)
- Not accounting for QWeb-specific elements like `<t t-name="...">`
- Guessing element hierarchy instead of reading the actual view

**Real-world example from Odoo 19:**

The `res.users.apikeys` kanban view uses `<t t-name="card">` for the card template, not a simple `<div>`. An incorrect XPath like `//div[hasclass('flex-row')]` will fail, while the correct XPath `//t[@t-name='card']/div/div` works because it matches the actual structure.

**How to verify XPath expressions:**
```python
# Read the view to check structure
view = self.env.ref('base.res_users_apikeys_view_kanban')
print(view.arch)  # Examine the XML structure

# Or use grep/search in Odoo source code
# grep -r "res_users_apikeys_view_kanban" odoo/addons/base/
```

Always read first, then write. Never trust your memory about view structures - they change between Odoo versions and even within the same version as views are refactored.

---

## Common Inheritance Patterns

### Add Workflow State
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('waiting_approval', 'Waiting Approval'),
        ],
        ondelete={'waiting_approval': 'set default'},
    )

    def action_submit_approval(self):
        self.write({'state': 'waiting_approval'})

    def action_approve(self):
        self.action_confirm()
```

### Add Smart Button
```xml
<xpath expr="//div[@name='button_box']" position="inside">
    <button class="oe_stat_button" type="object"
            name="action_view_loyalty_history"
            icon="fa-star">
        <field string="Points" name="x_loyalty_points"
               widget="statinfo"/>
    </button>
</xpath>
```

### Conditional Field Display
```xml
<!-- v17+ syntax -->
<field name="x_approval_notes"
       invisible="state not in ['waiting_approval', 'approved']"/>

<!-- Pre-v17 syntax -->
<field name="x_approval_notes"
       attrs="{'invisible': [('state', 'not in', ['waiting_approval', 'approved'])]}"/>
```
