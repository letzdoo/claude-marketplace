# Odoo Security Guide - Version 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 18.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 18.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 18.0 Requirements

- **Python**: 3.11+ required
- **Key Features**: `_check_company_auto`, `check_company`, type hints, `SQL()` builder

## Security Groups (v18 Syntax)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Category -->
    <record id="module_category_custom" model="ir.module.category">
        <field name="name">Custom Module</field>
        <field name="sequence">100</field>
    </record>

    <!-- User Group -->
    <record id="group_custom_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_custom"/>
    </record>

    <!-- Manager Group (inherits User) -->
    <record id="group_custom_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_custom"/>
        <field name="implied_ids" eval="[(4, ref('group_custom_user'))]"/>
    </record>
</odoo>
```

## Access Rights (v18)

### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

## Record Rules (v18 Syntax)

### Multi-Company Rule (v18 Pattern)

```xml
<!-- v18: Use allowed_company_ids for multi-company -->
<record id="rule_custom_model_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', allowed_company_ids)
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

## Model Security (v18 Patterns)

### _check_company_auto (v18 Feature)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'
    _check_company_auto = True  # v18: Automatic company validation

    # Type hints (v18 recommended)
    name: str = fields.Char(string='Name', required=True)
    company_id: int = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    # check_company validates company matches (v18)
    partner_id: int = fields.Many2one(
        'res.partner',
        string='Partner',
        check_company=True,
    )
    warehouse_id: int = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        check_company=True,
    )
```

### Secure Method Implementation (v18)

```python
from odoo import api, models, _
from odoo.exceptions import AccessError, UserError

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    def action_sensitive_operation(self):
        """Method with security checks."""
        # Check group membership
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(_("Only managers can perform this action."))

        # Check record-level access
        self.check_access_rights('write')
        self.check_access_rule('write')

        # Perform operation
        self._execute_sensitive_operation()

    def _execute_sensitive_operation(self):
        """Internal method - never call directly from external code."""
        # Sensitive logic here
        pass
```

### Secure SQL Queries (v18 - SQL Builder)

```python
from odoo import models
from odoo.tools import SQL

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    def _get_secure_data(self):
        """Use SQL builder for secure raw SQL (v18 pattern)."""
        query = SQL(
            """
            SELECT id, name, amount
            FROM %(table)s
            WHERE company_id = %(company_id)s
              AND active = %(active)s
              AND create_uid = %(user_id)s
            """,
            table=SQL.identifier(self._table),
            company_id=self.env.company.id,
            active=True,
            user_id=self.env.user.id,
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
```

## View Security (v18 Syntax)

### Field Visibility with Groups

```xml
<form>
    <sheet>
        <group>
            <!-- Field visible to all -->
            <field name="name"/>

            <!-- Field visible only to managers -->
            <field name="internal_notes" groups="custom_module.group_custom_manager"/>

            <!-- Field with conditional visibility (v18 syntax) -->
            <field name="secret_field" invisible="not user_has_groups('custom_module.group_custom_manager')"/>
        </group>
    </sheet>
</form>
```

### Button Security (v18 Syntax)

```xml
<!-- v18: Direct invisible attribute with Python expression -->
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_custom_manager"
        invisible="state != 'pending'"
        class="btn-primary"/>

<!-- Conditional on group -->
<button name="action_admin"
        string="Admin Action"
        type="object"
        invisible="not user_has_groups('base.group_system')"/>
```

### Menu Security

```xml
<menuitem id="menu_custom_root"
          name="Custom Module"
          groups="custom_module.group_custom_user"/>

<menuitem id="menu_custom_config"
          name="Configuration"
          parent="menu_custom_root"
          groups="custom_module.group_custom_manager"/>
```

## Field-Level Security (v18)

```python
class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    # Public field
    name: str = fields.Char(required=True)

    # Manager-only field
    internal_notes: str = fields.Text(
        string='Internal Notes',
        groups='custom_module.group_custom_manager',
    )

    # Finance-only field
    cost_price: float = fields.Float(
        string='Cost Price',
        groups='account.group_account_user',
        digits='Product Price',
    )

    # Multiple groups (any of them can access)
    sensitive_data: str = fields.Char(
        string='Sensitive Data',
        groups='custom_module.group_custom_manager,base.group_system',
    )
```

## Audit Trail (v18 Pattern)

```python
import json
from odoo import api, fields, models

class AuditLog(models.Model):
    _name = 'custom.audit.log'
    _description = 'Audit Log'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    model: str = fields.Char(required=True, index=True)
    res_id: int = fields.Integer(required=True, index=True)
    action: str = fields.Selection([
        ('create', 'Created'),
        ('write', 'Updated'),
        ('unlink', 'Deleted'),
    ], required=True)
    user_id: int = fields.Many2one('res.users', required=True, index=True)
    timestamp: fields.Datetime = fields.Datetime(default=fields.Datetime.now)
    old_values: str = fields.Text()
    new_values: str = fields.Text()
    display_name: str = fields.Char(compute='_compute_display_name')

    @api.depends('model', 'res_id', 'action')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.model}/{record.res_id} - {record.action}"


class AuditedModel(models.Model):
    _name = 'custom.audited'
    _description = 'Audited Model'
    _audit_fields = ['name', 'state', 'amount']

    name: str = fields.Char(required=True)
    state: str = fields.Selection([('draft', 'Draft'), ('done', 'Done')])
    amount: float = fields.Float()

    def _create_audit_log(self, action, old_values=None, new_values=None):
        self.env['custom.audit.log'].sudo().create({
            'model': self._name,
            'res_id': self.id,
            'action': action,
            'user_id': self.env.user.id,
            'old_values': json.dumps(old_values) if old_values else False,
            'new_values': json.dumps(new_values) if new_values else False,
        })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record, vals in zip(records, vals_list):
            audit_vals = {k: v for k, v in vals.items() if k in self._audit_fields}
            record._create_audit_log('create', new_values=audit_vals)
        return records

    def write(self, vals):
        audit_fields = [f for f in vals.keys() if f in self._audit_fields]
        old_values = {}
        if audit_fields:
            for record in self:
                old_values[record.id] = {f: getattr(record, f) for f in audit_fields}

        result = super().write(vals)

        if audit_fields:
            for record in self:
                record._create_audit_log(
                    'write',
                    old_values=old_values.get(record.id),
                    new_values={k: vals[k] for k in audit_fields}
                )
        return result

    def unlink(self):
        for record in self:
            record._create_audit_log('unlink', old_values={
                f: getattr(record, f) for f in self._audit_fields
            })
        return super().unlink()
```

## Security Levels Implementation (v18)

### Basic Security

```csv
# ir.model.access.csv - Basic
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model.user,model_custom_model,custom_module.group_user,1,1,1,0
access_model_manager,model.manager,model_custom_model,custom_module.group_manager,1,1,1,1
```

### Advanced Security

```csv
# ir.model.access.csv - Advanced (viewer/editor/manager)
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_viewer,model.viewer,model_custom_model,custom_module.group_viewer,1,0,0,0
access_model_editor,model.editor,model_custom_model,custom_module.group_editor,1,1,1,0
access_model_manager,model.manager,model_custom_model,custom_module.group_manager,1,1,1,1
```

### Audit-Grade Security

```csv
# ir.model.access.csv - Audit-grade (full separation)
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_reader,model.reader,model_custom_model,custom_module.group_reader,1,0,0,0
access_model_creator,model.creator,model_custom_model,custom_module.group_creator,1,0,1,0
access_model_editor,model.editor,model_custom_model,custom_module.group_editor,1,1,0,0
access_model_deleter,model.deleter,model_custom_model,custom_module.group_deleter,1,0,0,1
access_audit_auditor,audit.auditor,model_custom_audit_log,custom_module.group_auditor,1,0,0,0
```

## Complete Security File Template (v18)

### security/custom_module_security.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Category -->
    <record id="module_category_custom" model="ir.module.category">
        <field name="name">Custom Module</field>
        <field name="sequence">100</field>
    </record>

    <!-- Groups -->
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
            ('company_id', 'in', allowed_company_ids)
        ]</field>
    </record>

    <!-- User sees own records -->
    <record id="rule_custom_model_user" model="ir.rule">
        <field name="name">Custom Model: User Own Records</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('group_custom_user'))]"/>
    </record>

    <!-- Manager sees all -->
    <record id="rule_custom_model_manager" model="ir.rule">
        <field name="name">Custom Model: Manager All Records</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('group_custom_manager'))]"/>
    </record>
</odoo>
```

## v18 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Multi-company models use `_check_company_auto = True`
- [ ] Relational fields use `check_company=True` where appropriate
- [ ] Record rules use `allowed_company_ids` for multi-company
- [ ] Views use direct `invisible` attribute (not `attrs`)
- [ ] SQL queries use `SQL()` builder
- [ ] Type hints on all relational fields
- [ ] Audit logging for sensitive operations
- [ ] sudo() usage is minimal and justified
- [ ] No hardcoded IDs

## AI Agent Instructions (v18)

When generating Odoo 18.0 security code:

1. **Always use** `_check_company_auto = True` for multi-company models
2. **Always use** `check_company=True` on relational fields referencing company-scoped models
3. **Use** `allowed_company_ids` in record rule domains
4. **Use** direct `invisible` attribute in views, not `attrs`
5. **Use** `SQL()` builder for any raw SQL queries
6. **Add** type hints to all relational fields
7. **Never** use `attrs` attribute (removed in v17)
