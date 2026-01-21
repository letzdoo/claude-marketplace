# Odoo Security Guide - Version 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 19.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 19.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  NOTE: Odoo 19.0 is in DEVELOPMENT - patterns may change.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 19.0 Requirements

- **Python**: 3.12+ required
- **Key Features**: Full type annotations, mandatory SQL builder, OWL 3.x, enhanced security

## Security Groups (v19 Syntax)

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

## Access Rights (v19)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

## Record Rules (v19 Syntax)

### Multi-Company Rule (v19)

```xml
<!-- v19: Enhanced multi-company with allowed_company_ids -->
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

## Model Security (v19 Patterns - Full Type Annotations)

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any
from odoo import api, fields, models, Command, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import SQL

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    # v19: Full type annotations on ALL fields
    name: str = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        index='btree',
    )
    active: bool = fields.Boolean(default=True)
    sequence: int = fields.Integer(default=10)
    company_id: int = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id: int = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        check_company=True,
        index=True,
    )
    user_id: int = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True,
    )
    amount: float = fields.Float(
        string='Amount',
        digits='Product Price',
    )
    currency_id: int = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    state: str = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        copy=False,
    )
    line_ids: list[int] = fields.One2many(
        comodel_name='custom.secure.line',
        inverse_name='parent_id',
        string='Lines',
    )
    tag_ids: list[int] = fields.Many2many(
        comodel_name='custom.tag',
        string='Tags',
    )

    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> SecureModel:
        """v19: Full type annotations on method signatures."""
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        """v19: Typed write method."""
        return super().write(vals)

    def action_sensitive_operation(self) -> None:
        """Method with security checks and type hints."""
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(_("Only managers can perform this action."))
        self.check_access_rights('write')
        self.check_access_rule('write')
        self._execute_sensitive_operation()

    def _execute_sensitive_operation(self) -> None:
        """Internal method with type hints."""
        pass
```

### Mandatory SQL Builder (v19)

```python
from odoo import models
from odoo.tools import SQL

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    def _get_secure_data(self) -> list[dict[str, Any]]:
        """v19: SQL builder is MANDATORY for raw SQL."""
        query = SQL(
            """
            SELECT id, name, amount
            FROM %(table)s
            WHERE company_id = %(company_id)s
              AND active = %(active)s
              AND create_uid = %(user_id)s
            ORDER BY %(order)s
            """,
            table=SQL.identifier(self._table),
            company_id=self.env.company.id,
            active=True,
            user_id=self.env.user.id,
            order=SQL.identifier('create_date') + SQL(' DESC'),
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    def _execute_complex_query(self) -> list[dict[str, Any]]:
        """v19: Complex query with SQL builder."""
        query = SQL(
            """
            SELECT
                m.id,
                m.name,
                p.name AS partner_name,
                COALESCE(SUM(l.amount), 0) AS total_amount
            FROM %(main_table)s m
            LEFT JOIN %(partner_table)s p ON m.partner_id = p.id
            LEFT JOIN %(line_table)s l ON l.parent_id = m.id
            WHERE m.company_id IN %(company_ids)s
              AND m.state = %(state)s
            GROUP BY m.id, m.name, p.name
            HAVING COALESCE(SUM(l.amount), 0) > %(min_amount)s
            """,
            main_table=SQL.identifier(self._table),
            partner_table=SQL.identifier('res_partner'),
            line_table=SQL.identifier('custom_secure_line'),
            company_ids=tuple(self.env.companies.ids),
            state='confirmed',
            min_amount=0,
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
```

## View Security (v19 Syntax)

### Field Visibility

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- v19: Direct invisible with Python expression -->
            <field name="internal_notes"
                   invisible="not user_has_groups('custom_module.group_manager')"/>

            <!-- v19: Conditional visibility -->
            <field name="secret_field"
                   invisible="state == 'draft' or not user_has_groups('custom_module.group_manager')"/>

            <!-- v19: Combined conditions -->
            <field name="amount"
                   readonly="state != 'draft'"
                   required="state == 'confirmed'"/>
        </group>
    </sheet>
</form>
```

### Button Security (v19)

```xml
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_manager"
        invisible="state != 'pending'"
        class="btn-primary"/>

<button name="action_admin"
        string="Admin Action"
        type="object"
        invisible="not user_has_groups('base.group_system')"/>
```

## Enhanced Audit Trail (v19)

```python
from __future__ import annotations
import json
from typing import Any
from odoo import api, fields, models

class AuditLog(models.Model):
    _name = 'custom.audit.log'
    _description = 'Audit Log'
    _order = 'create_date desc'

    model: str = fields.Char(required=True, index=True)
    res_id: int = fields.Integer(required=True, index=True)
    action: str = fields.Selection([
        ('create', 'Created'),
        ('write', 'Updated'),
        ('unlink', 'Deleted'),
        ('access', 'Accessed'),
        ('export', 'Exported'),
    ], required=True, index=True)
    user_id: int = fields.Many2one('res.users', required=True, index=True)
    timestamp: fields.Datetime = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    old_values: str = fields.Text()
    new_values: str = fields.Text()
    ip_address: str = fields.Char(index=True)
    user_agent: str = fields.Char()

    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> AuditLog:
        # Audit logs should be immutable
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        raise UserError(_("Audit logs cannot be modified."))

    def unlink(self) -> bool:
        raise UserError(_("Audit logs cannot be deleted."))
```

## v19 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Use `_check_company_auto = True` for multi-company models
- [ ] Use `check_company=True` on relational fields
- [ ] Use `allowed_company_ids` in record rules
- [ ] Full type annotations on ALL fields
- [ ] Full type annotations on ALL method signatures
- [ ] Use `SQL()` builder for ALL raw SQL (mandatory)
- [ ] Views use direct `invisible` attribute
- [ ] No `attrs` attribute in views

## Key Differences from v18

| Feature | v18 | v19 |
|---------|-----|-----|
| Type hints | Recommended | Mandatory |
| SQL builder | Recommended | Mandatory |
| Python | 3.11+ | 3.12+ |
| OWL | 2.x | 3.x |

## AI Agent Instructions (v19)

When generating Odoo 19.0 security code:

1. **ALWAYS** add type hints to ALL fields
2. **ALWAYS** add type hints to ALL method signatures
3. **ALWAYS** use `SQL()` builder for raw SQL (mandatory)
4. **ALWAYS** use `_check_company_auto = True` for multi-company
5. **ALWAYS** use `check_company=True` on relational fields
6. **Use** `allowed_company_ids` in record rules
7. **Use** direct `invisible` attribute (no `attrs`)
8. **Use** Python 3.12+ features where appropriate
9. **Verify** patterns against `master` branch of odoo/odoo GitHub
