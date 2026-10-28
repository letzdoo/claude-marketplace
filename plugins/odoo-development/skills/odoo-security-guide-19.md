# Odoo Security Guide - Version 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 19.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 19.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  Released (final) - verified against the 19.0 source.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 19.0 Requirements

- **Python**: 3.10 - 3.14
- **Key Features**: `ir.model.access` + `ir.rule` (no `ir.access`), groups organised through
  `res.groups.privilege`, `group_ids` / `user_ids` field names, `@api.private`, `odoo.fields.Domain`,
  `SQL()` builder recommended, Owl 2.8.x

## Security Groups (v19 Syntax)

In 19.0 `res.groups` is linked to a `res.groups.privilege` (`privilege_id`), and the privilege
carries the `ir.module.category`. Users are in `user_ids` (was `users`).

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_custom" model="ir.module.category">
        <field name="name">Custom Module</field>
        <field name="sequence">100</field>
    </record>

    <record id="res_groups_privilege_custom" model="res.groups.privilege">
        <field name="name">Custom Module</field>
        <field name="category_id" ref="module_category_custom"/>
    </record>

    <record id="group_custom_user" model="res.groups">
        <field name="name">User</field>
        <field name="privilege_id" ref="res_groups_privilege_custom"/>
    </record>

    <record id="group_custom_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="privilege_id" ref="res_groups_privilege_custom"/>
        <field name="implied_ids" eval="[Command.link(ref('group_custom_user'))]"/>
    </record>
</odoo>
```

## Access Rights (v19)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

- Rights are the union over the user's groups; a model with no row is inaccessible except in
  sudo (a warning "have no access rules" is logged at install).
- Flag create/write/unlink granted to `base.group_portal`, `base.group_public` or to rows without
  a group. There is no `base.group_everyone` in 19.0, and master's `ir.access` does not exist.

## Record Rules (v19 Syntax)

- Global rules (no groups) are AND-ed; group rules of the user's groups are OR-ed, then AND-ed
  with the global ones. Two disjoint global rules lock everyone out.
- Rules are per operation (`perm_read`, `perm_write`, `perm_create`, `perm_unlink`): a rule
  covering only read leaves write governed by ACLs alone - cover all CRUD operations.

### Multi-Company Rule (v19)

```xml
<!-- v19: the ir.rule eval context provides user, company_ids, company_id.
     allowed_company_ids is NOT defined there. A rule without groups is global.
     Use [('company_id', 'in', company_ids)], or company_ids + [False] when the company is optional. -->
<record id="custom_model_rule_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="domain_force">[('company_id', 'in', company_ids + [False])]</field>
</record>
```

## Model Security (v19 Patterns; type annotations optional)

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

    # Annotations on fields are optional (not used by the framework)
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
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        return super().write(vals)

    def action_sensitive_operation(self) -> None:
        """Public method = RPC-callable; check rights explicitly."""
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(self.env._("Only managers can perform this action."))
        # v19: check_access_rights()/check_access_rule() are deprecated since 18.0
        self.check_access('write')  # ACL + record rules in one call
        self._execute_sensitive_operation()

    def _execute_sensitive_operation(self) -> None:
        """Internal method with type hints."""
        pass
```

### SQL Builder (v19, recommended)

`cr.execute()` still accepts a string plus a params tuple, but `SQL()` is the safe way to compose
queries: values as `SQL("... %s", value)`, identifiers via `SQL.identifier(name)`, `IN %s` with a
tuple. Never format values into the SQL string (`%`, `+`, `.format`, f-strings). For ORM-filtered
SQL use `query = Model._search(domain)`, then `cr.execute(query.select(SQL(...)))`.

```python
from typing import Any

from odoo import models
from odoo.tools import SQL

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    def _get_secure_data(self) -> list[dict[str, Any]]:
        """Raw SQL bypasses ir.rule: restrict rows explicitly."""
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

            <!-- Group restriction: groups attribute (not a Python expression) -->
            <field name="internal_notes"
                   groups="custom_module.group_manager"/>

            <!-- Group restriction combined with a state condition -->
            <field name="secret_field"
                   groups="custom_module.group_manager"
                   invisible="state == 'draft'"/>

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
        groups="base.group_system"/>
```

View-level `groups` only hides elements. The method behind a button is still RPC-callable by
anyone with model access, so re-check rights in the method (or use `groups=` on the field /
`@api.private` / `_` prefix).

## Enhanced Audit Trail (v19)

```python
from __future__ import annotations
import json
from typing import Any
from odoo import api, fields, models
from odoo.exceptions import UserError

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
        raise UserError(self.env._("Audit logs cannot be modified."))

    def unlink(self) -> bool:
        raise UserError(self.env._("Audit logs cannot be deleted."))
```

## v19 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Use `_check_company_auto = True` for multi-company models
- [ ] Use `check_company=True` on relational fields
- [ ] Record rules use `company_ids` / `company_id` / `user` (no `allowed_company_ids`)
- [ ] `check_access()` / `has_access()` instead of `check_access_rights()` / `check_access_rule()`
- [ ] `SQL()` builder for raw SQL, no values formatted into SQL strings
- [ ] Views use direct `invisible` attribute; group restrictions via `groups="..."`
- [ ] No `attrs` attribute in views

## Key Differences from v18

| Feature | v18 | v19 |
|---------|-----|-----|
| Group fields | `groups_id` / `users` | `group_ids` / `user_ids` |
| Group category | `category_id` on res.groups | `privilege_id` -> `res.groups.privilege` (has `category_id`) |
| SQL constraints | `_sql_constraints` | `models.Constraint` (`_sql_constraints` ignored) |
| Domains | `osv.expression` | `odoo.fields.Domain` (`osv.expression` deprecated) |
| RPC guard | `check_method_name` | `get_public_method` (blocks `_*`, `@api.private`) |
| JSON routes | `type='json'` | `type='jsonrpc'` (`json` deprecated alias) |
| Owl | 2.x | 2.8.x (no Owl 3) |

## Additional Rules from Odoo's Official Guidelines (verified for 19.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were
checked against the 19.0 source; master-only APIs are translated to the 19.0 equivalent or marked
as not available.

### Audit sweep (pattern -> what makes it a finding)

| Pattern | Finding when ... | 19.0 form |
|---------|------------------|-----------|
| `.sudo()` | attacker-controlled model/record/field/domain/vals reach a read, search, create or write under sudo; `record.sudo().write(post)` in a controller | `sudo(flag=True)`; whitelist keys; `sudo(user)` does not exist |
| `with_user()` / `with_company()` | the switch is not intentional or uses request data | `with_user(user)` (drops su), `with_company(company)`; `force_company` context is deprecated |
| x2many commands under sudo | vals with `Command.*` on a security-sensitive comodel are written in sudo | set `_allow_sudo_commands = False` on the comodel (as `res.groups` does) |
| `related=` | sensitive chain (e.g. to `ir.attachment`, tokens) without `related_sudo=False` | related fields are computed as superuser by default |
| `cr.execute` | values formatted into the string; dynamic identifiers not wrapped | `SQL()` / `SQL.identifier()`; see SQL Builder |
| domains | a user-supplied list is concatenated onto a security domain | `Domain(user_dom) & Domain('company_id', 'in', ids)`; `Domain.AND/OR` |
| public methods | a non-`_` method does something an RPC caller must not trigger with arbitrary args | prefix `_` or `@api.private`; guard is `odoo.service.model.get_public_method` (blocks `_*`, classmethods/staticmethods, `@api.private`) |
| `@http.route` | `auth` wider than needed; writes on GET; `csrf=False` on a `type='http'` route that is not a webhook | `auth` in `user`/`bearer`/`public`/`none` (no `bearer_scope`); writes with `methods=['POST']`; CSRF on for `http`, none for `jsonrpc` |
| POST forms in QWeb | missing token | `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>` |
| QWeb output | `t-raw` (still renders unescaped in 19.0, warns); `Markup()` wrapped around user data; f-strings building HTML | `t-out` (escapes non-Markup); `Markup("<p>{}</p>").format(user_value)`; `_()` escapes when an arg is Markup; `t-esc` still escapes but is deprecated |
| JS HTML sinks | `innerHTML`, `insertAdjacentHTML`, `markup(nonLiteral)` | `htmlEscape` / tagged ``markup`...` `` from `@odoo/owl`; `setElementContent`, `htmlJoin`, `htmlSprintf` from `@web/core/utils/html` (no `setInnerHtml`) |
| `fields.Html` | user HTML stored with `sanitize=False` or relaxed options | keep `sanitize=True`; options `sanitize_tags`, `sanitize_attributes`, `sanitize_style`, `sanitize_form`, `strip_style`, `strip_classes`, `sanitize_overridable` |
| secrets / tokens | field readable by normal users (`search_read`) | `groups="base.group_system"` or `groups=fields.NO_ACCESS`; groups also hide the field from `fields_get` and raise on explicit read/write |
| `open()` | path influenced by input | `odoo.tools.file_open(name, mode, filter_ext=..., env=...)` (confined to addons paths, root path and registered temp dirs; never creates files) |
| `eval` / `exec` | any use on data | `json.loads`, `ast.literal_eval`; at worst `safe_eval` with a constrained context for trusted users (dunder names are rejected) |
| `getattr` / `setattr` | dynamic field name from input | `record[fname]` after checking `fname in record._fields` |
| `pickle` | any use | no restricted pickle wrapper in 19.0; use JSON |
| token comparison | `==` on secrets | `odoo.tools.consteq(a, b)`; better: look the token up in the DB |
| mutable defaults | `def f(self, vals={})` | `None` default |

## AI Agent Instructions (v19)

When generating Odoo 19.0 security code:

1. **ALWAYS** use `ir.model.access.csv` + `ir.rule` (never `ir.access`)
2. **ALWAYS** use `company_ids` in record rules (no `allowed_company_ids`)
3. **ALWAYS** use `group_ids` / `user_ids` / `privilege_id` (19.0 field names)
4. **ALWAYS** use `_check_company_auto = True` + `check_company=True` for multi-company
5. **Use** `check_access()` / `has_access()` for programmatic checks
6. **Use** `SQL()` for raw SQL; never interpolate values
7. **Use** `groups=` (fields, view elements) and `@api.private` / `_` prefix for methods
8. **Use** direct `invisible` attribute (no `attrs`)
9. **Verify** patterns against the `19.0` branch of odoo/odoo (not `master`)
