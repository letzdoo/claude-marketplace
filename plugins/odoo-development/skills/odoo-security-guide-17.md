# Odoo Security Guide - Version 17.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 17.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 17.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 17.0 Requirements

- **Python**: 3.10+ required
- **Key Changes**: `attrs` removed from views, `@api.model_create_multi` mandatory

## Security Groups (v17 Syntax)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_custom" model="ir.module.category">
        <field name="name">Custom Module</field>
        <field name="sequence">100</field>
    </record>

    <record id="group_custom_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_custom"/>
    </record>

    <record id="group_custom_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_custom"/>
        <field name="implied_ids" eval="[(4, ref('group_custom_user'))]"/>
    </record>
</odoo>
```

## Access Rights (v17)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

## Record Rules (v17 Syntax)

### Multi-Company Rule (v17)

```xml
<!-- v17: Use company_ids for multi-company -->
<record id="rule_custom_model_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

### User Own Records Rule

```xml
<record id="rule_custom_model_user_own" model="ir.rule">
    <field name="name">Custom Model: User Own Records</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_custom_user'))]"/>
</record>
```

## Model Security (v17 Patterns)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain="[('company_id', 'in', [company_id, False])]",
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        # v17: @api.model_create_multi is mandatory
        return super().create(vals_list)

    def action_sensitive_operation(self):
        """Check permissions before sensitive operations."""
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(_("Only managers can perform this action."))
        self._do_sensitive_work()
```

### Secure SQL Queries (v17 - Parameterized)

```python
def _get_secure_data(self):
    """Use parameterized queries (v17 pattern)."""
    # SAFE: Parameterized query
    self.env.cr.execute(
        """
        SELECT id, name, amount
        FROM %s
        WHERE company_id = %%s
          AND active = %%s
          AND create_uid = %%s
        """ % self._table,
        [self.env.company.id, True, self.env.user.id]
    )
    return self.env.cr.dictfetchall()
```

## View Security (v17 Syntax - NO attrs)

### Field Visibility

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- v17: Direct invisible attribute (NOT attrs) -->
            <field name="internal_notes" groups="custom_module.group_custom_manager"/>

            <!-- v17: Python expression in invisible -->
            <field name="secret_field" invisible="not user_has_groups('custom_module.group_custom_manager')"/>

            <!-- v17: Conditional based on field value -->
            <field name="manager_notes" invisible="state == 'draft'"/>
        </group>
    </sheet>
</form>
```

### Button Security (v17 Syntax)

```xml
<!-- v17: Direct invisible attribute with Python expression -->
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_custom_manager"
        invisible="state != 'pending'"
        class="btn-primary"/>

<!-- v17: Group check in invisible -->
<button name="action_admin"
        string="Admin Action"
        type="object"
        invisible="not user_has_groups('base.group_system')"/>
```

### Complete Form Example (v17)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="custom_model_view_form" model="ir.ui.view">
        <field name="name">custom.model.form</field>
        <field name="model">custom.model</field>
        <field name="arch" type="xml">
            <form string="Custom Model">
                <header>
                    <!-- v17: invisible takes Python expression -->
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary" invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object"
                            invisible="state != 'confirmed'"/>
                    <button name="action_approve" string="Approve" type="object"
                            groups="custom_module.group_manager"
                            invisible="state != 'pending'"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="partner_id"/>
                        </group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="user_id"/>
                        </group>
                    </group>
                    <!-- Manager-only section -->
                    <group string="Internal" groups="custom_module.group_manager">
                        <field name="internal_notes"/>
                        <field name="cost_price"/>
                    </group>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
```

## Field-Level Security (v17)

```python
class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    name = fields.Char(required=True)

    # Manager-only field
    internal_notes = fields.Text(
        string='Internal Notes',
        groups='custom_module.group_custom_manager',
    )

    # Finance-only field
    cost_price = fields.Float(
        string='Cost Price',
        groups='account.group_account_user',
    )
```

## Complete Security Template (v17)

### security/custom_module_security.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_custom" model="ir.module.category">
        <field name="name">Custom Module</field>
        <field name="sequence">100</field>
    </record>

    <record id="group_custom_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_custom"/>
    </record>

    <record id="group_custom_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_custom"/>
        <field name="implied_ids" eval="[(4, ref('group_custom_user'))]"/>
        <field name="users" eval="[(4, ref('base.user_admin'))]"/>
    </record>

    <!-- Multi-Company Rule -->
    <record id="rule_custom_model_company" model="ir.rule">
        <field name="name">Custom Model: Multi-Company</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
        ]</field>
    </record>

    <record id="rule_custom_model_user" model="ir.rule">
        <field name="name">Custom Model: User Own Records</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('group_custom_user'))]"/>
    </record>

    <record id="rule_custom_model_manager" model="ir.rule">
        <field name="name">Custom Model: Manager All Records</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('group_custom_manager'))]"/>
    </record>
</odoo>
```

## v17 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Record rules use `company_ids` for multi-company
- [ ] Views use direct `invisible` attribute (NOT `attrs`)
- [ ] Use `@api.model_create_multi` for create methods
- [ ] SQL queries use parameterized syntax
- [ ] Button visibility uses `invisible` with Python expression
- [ ] No `attrs` attribute anywhere in views

## Key Differences from v16

| Feature | v16 | v17 |
|---------|-----|-----|
| View visibility | `attrs="{'invisible': [...]}"` | `invisible="expression"` |
| Create method | `@api.model_create_multi` optional | `@api.model_create_multi` mandatory |
| Domain syntax | Still supports `attrs` | `attrs` removed |

## AI Agent Instructions (v17)

When generating Odoo 17.0 security code:

1. **Never use** `attrs` attribute in views (removed in v17)
2. **Always use** direct `invisible`, `readonly`, `required` attributes
3. **Use** Python expressions for visibility: `invisible="state != 'draft'"`
4. **Use** `user_has_groups()` for group checks: `invisible="not user_has_groups('base.group_manager')"`
5. **Use** `@api.model_create_multi` for create methods (mandatory)
6. **Use** parameterized SQL queries
7. **Use** `company_ids` in multi-company record rules
