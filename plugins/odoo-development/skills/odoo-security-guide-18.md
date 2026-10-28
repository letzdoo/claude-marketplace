# Odoo Security Guide - Version 18.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 18.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 18.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 18.0 Requirements

- **Python**: 3.10+ required (`odoo/__init__.py`: `MIN_PY_VERSION = (3, 10)`)
- **Key Features**: `_check_company_auto`, `check_company`, `SQL()` builder, `check_access()`, `@api.private`, `auth='bearer'` routes

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

- Two access models: `ir.model.access` (`security/ir.model.access.csv`) and `ir.rule`. There is no `ir.access` and no `base.group_everyone` in 18.
- Default deny: a model without an ACL row is inaccessible except under sudo; module loading logs "The models [...] have no access rules".
- An ACL row with an empty `group_id` grants that permission to everyone. Flag create/write/unlink granted to an empty group, `base.group_portal` or `base.group_public`.

### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

## Record Rules (v18 Syntax)

- Global rules (no groups; `global` is computed) are AND-ed; the rules of all groups the user belongs to are OR-ed together into one block; result = global rules AND (group rules OR-ed). Two non-overlapping global rules lock everybody out.
- A rule only applies to the operations whose `perm_*` flag is set; a rule with only `perm_write` leaves read/create/unlink governed by the other rules.
- Rule domains are evaluated with `user`, `time`, `company_ids` and `company_id` only. `allowed_company_ids` is not available (install fails with "Invalid domain").

### Multi-Company Rule (v18 Pattern)

```xml
<record id="rule_custom_model_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
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

## Model Security (v18 Patterns)

### _check_company_auto (v18 Feature)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'
    _check_company_auto = True  # v18: Automatic company validation

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    # check_company validates company matches
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        check_company=True,
    )
    warehouse_id = fields.Many2one(
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

        # Check ACL + record rules in one call (v18: check_access_rights()/
        # check_access_rule() are deprecated and emit DeprecationWarning).
        # Non-raising variants: has_access('write'), _filtered_access('write')
        self.check_access('write')

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

    def _get_ids_in(self, ids):
        # Values as parameters, never string formatting (%, +, .format, f-string)
        self.env.cr.execute(SQL("SELECT name FROM custom_secure WHERE id IN %s", tuple(ids)))
        return self.env.cr.fetchall()

    def _get_filtered_ids(self, domain):
        # Raw SQL over ORM-filtered rows (record rules applied by _search)
        query = self._search(domain)
        return self.env.execute_query(query.select(SQL.identifier(self._table, 'id')))
```

Identifiers: `SQL.identifier(name)` or `SQL.identifier(table, column)`.

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

            <!-- Group-restricted field: use the groups attribute, not a Python
                 expression (user_has_groups() is not available in v18 view expressions) -->
            <field name="secret_field" groups="custom_module.group_custom_manager"/>
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

<!-- Conditional on group: groups attribute (UI only, re-check in the method) -->
<button name="action_admin"
        string="Admin Action"
        type="object"
        groups="base.group_system"/>
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
    name = fields.Char(required=True)

    # Manager-only field: hidden from fields_get/views, explicit read/write
    # by other users raises AccessError
    internal_notes = fields.Text(
        string='Internal Notes',
        groups='custom_module.group_custom_manager',
    )

    # Finance-only field
    cost_price = fields.Float(
        string='Cost Price',
        groups='account.group_account_user',
        digits='Product Price',
    )

    # Multiple groups (any of them can access)
    sensitive_data = fields.Char(
        string='Sensitive Data',
        groups='custom_module.group_custom_manager,base.group_system',
    )

    # Secrets/tokens: nobody except superuser (sudo) may read them
    api_token = fields.Char(groups=fields.NO_ACCESS)
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

    model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    action = fields.Selection([
        ('create', 'Created'),
        ('write', 'Updated'),
        ('unlink', 'Deleted'),
    ], required=True)
    user_id = fields.Many2one('res.users', required=True, index=True)
    timestamp = fields.Datetime(default=fields.Datetime.now)
    old_values = fields.Text()
    new_values = fields.Text()
    display_name = fields.Char(compute='_compute_display_name')

    @api.depends('model', 'res_id', 'action')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.model}/{record.res_id} - {record.action}"


class AuditedModel(models.Model):
    _name = 'custom.audited'
    _description = 'Audited Model'
    _audit_fields = ['name', 'state', 'amount']

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')])
    amount = fields.Float()

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
                old_values[record.id] = {f: record[f] for f in audit_fields}

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
                f: record[f] for f in self._audit_fields
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

    <!-- Multi-Company Rule (no groups = global rule) -->
    <record id="rule_custom_model_company" model="ir.rule">
        <field name="name">Custom Model: Multi-Company</field>
        <field name="model_id" ref="model_custom_model"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
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

## Additional Rules from Odoo's Official Guidelines (verified for 18.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 18.0 source; master-only APIs are translated to their 18.0 equivalent or marked as not available.

### Audit sweep (pattern -> what makes it a finding)

| Pattern | Finding when ... | 18.0 form |
|---------|------------------|-----------|
| `sudo()` | attacker-controlled model/record/field/domain reaches a sudo read/search/create/write; `record.sudo().write(post)` with raw request params | `sudo(flag=True)` only toggles superuser mode (user unchanged); whitelist keys from `post` |
| `with_user()` / `with_company()` | switch not intentional (e.g. `with_user(SUPERUSER_ID)` as a sudo workaround) | `with_user(user)` sets su=False; `with_company(company)` rewrites `allowed_company_ids` in the context |
| x2many commands under sudo | sensitive comodel receives `Command` payloads from user input in a sudo env | set `_allow_sudo_commands = False` on the comodel: commands then run as `sudo(False).with_user(env.uid_origin)` |
| `related=` fields | sudo-computed chain exposes data the user may not read (e.g. related onto `ir.attachment` content) | related fields are computed as superuser by default (`related_sudo=True` -> `compute_sudo`); use `related_sudo=False` on sensitive chains |
| raw SQL | string formatting (`%`, `+`, `.format`, f-string) builds the query | `SQL()` with parameters, see Secure SQL Queries |
| domains | user-supplied list concatenated onto a security domain | `from odoo.osv import expression`; `expression.AND([security_domain, user_domain])` (there is no `odoo.fields.Domain` in 18) |
| public model methods | a method without `_` prefix does something unsafe with attacker args | RPC guard `odoo.service.model.get_public_method` blocks `_` names, `@api.private` methods and `_UNSAFE_ATTRIBUTES`. It does **not** block classmethods/staticmethods -> prefix them with `_` |
| routes `auth` | exposure does not match (`public`/`none` on data-changing code) | `user`, `bearer` (API key in `Authorization: Bearer`, no `bearer_scope` parameter in 18), `public`, `none` |
| routes `type` / CSRF | state change on GET; `csrf=False` on a browser-facing `type='http'` route | only `type='http'` and `type='json'` exist; http routes check CSRF for every non-GET/HEAD/OPTIONS/TRACE request; json routes have no token check (JSON content type); writes use `methods=['POST']`; forms include `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>` |
| server QWeb | `t-raw` anywhere; `Markup(user_value)`; f-string HTML then wrapped in `Markup` | use `t-out` (escapes). In 18 `t-raw` still renders **unescaped** (deprecation warning) and `t-esc` is a working, escaping alias of `t-out`. Build HTML with `Markup("<p>%s</p>") % value` or `Markup("<p>{}</p>").format(value)`; `_()` escapes the translation when an argument is `Markup` |
| JS XSS | `innerHTML`/`insertAdjacentHTML`/`markup()` on non-literal content | `htmlEscape()` and `setElementContent(el, content)` from `@web/core/utils/html` (also `htmlEscape` from `@odoo/owl`); Owl `markup` as tagged template (``markup`<b>${value}</b>` ``) escapes placeholders. `setInnerHtml` and `htmlJoin` do not exist in 18 |
| field `groups` | password/token/secret field readable on a permissive model | `groups="base.group_system"` or `groups=fields.NO_ACCESS`, see Field-Level Security |
| files | builtin `open()` on a path the user can influence | `odoo.tools.file_open(path, mode='r', filter_ext=(), env=None)`: confined to addons paths, the Odoo root and `file_open_temporary_directory()` dirs; the file must already exist |
| `eval`/`exec` | any use on user data | `json.loads` / `ast.literal_eval`; `odoo.tools.safe_eval.safe_eval` only for trusted (admin-defined) expressions; it rejects names containing `__` |
| `getattr`/`setattr` on records | field name comes from input | `record[field_name]` |
| `pickle` | any use | 18 ships no restricted pickle wrapper (`odoo/tools/pickle.py` removed); use json |
| secret comparison | `token == expected` | `odoo.tools.consteq(a, b)`, or look the token up in the database |
| mutable defaults | `def m(self, vals={})` | `vals=None` then `vals = vals or {}` |

## v18 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Multi-company models use `_check_company_auto = True`
- [ ] Relational fields use `check_company=True` where appropriate
- [ ] Record rules use `company_ids` for multi-company (never `allowed_company_ids`)
- [ ] Views use direct `invisible` attribute (not `attrs`)
- [ ] SQL queries use `SQL()` builder
- [ ] `check_access()` instead of `check_access_rights()`/`check_access_rule()`
- [ ] Audit logging for sensitive operations
- [ ] sudo() usage is minimal and justified
- [ ] No hardcoded IDs

## AI Agent Instructions (v18)

When generating Odoo 18.0 security code:

1. **Always use** `_check_company_auto = True` for multi-company models
2. **Always use** `check_company=True` on relational fields referencing company-scoped models
3. **Use** `company_ids` in record rule domains (`allowed_company_ids` is not in the rule eval context)
4. **Use** direct `invisible` attribute in views, not `attrs`
5. **Use** `SQL()` builder for any raw SQL queries
6. **Use** `check_access()` for explicit access checks
7. **Never** use `attrs` attribute (removed in v17)
