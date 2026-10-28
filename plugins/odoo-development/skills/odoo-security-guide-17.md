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
- **Key Changes**: `attrs` removed from views, `@api.model_create_multi` expected (a single-dict `@api.model` create still works but logs a warning)

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

- Access model in 17.0: `ir.model.access` (CSV) + `ir.rule`. There is no `ir.access` model in 17.0.
- Default deny: a model without a matching access row is inaccessible (a warning is logged at module load).
- An access row with an **empty `group_id`** applies to every user, including portal and public. There is no `base.group_everyone` in 17.0. Flag create/write/unlink granted to an empty group, `base.group_portal` or `base.group_public`.

## Record Rules (v17 Syntax)

- Rule combination: global rules (no groups) are AND-ed; the rules of **all** the user's groups are OR-ed together and that result is AND-ed with the globals. Non-overlapping global rules lock everyone out.
- `perm_read/perm_write/perm_create/perm_unlink` default to True; a rule restricted to some operations leaves the others unfiltered.
- Rule eval context: `user`, `time`, `company_ids`, `company_id`. `allowed_company_ids` is NOT available in rule domains (the rule fails validation).

### Multi-Company Rule (v17)

```xml
<!-- v17: Use company_ids for multi-company -->
<record id="rule_custom_model_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <!-- No groups => global rule ('global' is computed from groups, do not set it) -->
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
        # v17: batch create; a single-dict @api.model create only logs a warning
        return super().create(vals_list)

    def action_sensitive_operation(self):
        """Check permissions before sensitive operations."""
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(_("Only managers can perform this action."))
        self._do_sensitive_work()
```

### Secure SQL Queries (v17 - Parameterized)

Prefer the ORM. Never build SQL with `+`, `%`, `.format()` or f-strings. 17.0 form: `from odoo.tools import SQL`; `SQL("... %s ...", value)`, `SQL.identifier(name)` for identifiers (validated by assert).

```python
from odoo.tools import SQL

def _get_secure_data(self):
    """Use parameterized queries (v17 pattern)."""
    # SAFE: values as parameters, table name via SQL.identifier
    self.env.cr.execute(SQL(
        """
        SELECT id, name, amount
        FROM %s
        WHERE company_id = %s
          AND active = %s
          AND create_uid = %s
        """,
        SQL.identifier(self._table),
        self.env.company.id, True, self.env.user.id,
    ))
    return self.env.cr.dictfetchall()
```

For SQL over ORM-filtered rows: `query = self._search(domain)` (returns a `Query`) then `self.env.cr.execute(query.select(SQL(...)))`.

## View Security (v17 Syntax - NO attrs)

### Field Visibility

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- v17: Direct invisible attribute (NOT attrs) -->
            <field name="internal_notes" groups="custom_module.group_custom_manager"/>

            <!-- v17: group restriction uses the groups attribute; user_has_groups() is not
                 available in view expressions (evaluated client-side) -->
            <field name="secret_field" groups="custom_module.group_custom_manager"/>

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

<!-- v17: Group check via the groups attribute -->
<button name="action_admin"
        string="Admin Action"
        type="object"
        groups="base.group_system"/>
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

Field `groups` hides the field from `fields_get` and raises `AccessError` on explicit read/write/search. Secret fields (passwords/tokens) need `groups="base.group_system"` or `groups=fields.NO_ACCESS` (`'.'`).

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
        <!-- No groups => global rule ('global' is computed, do not set it) -->
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

## Additional Rules from Odoo's Official Guidelines (verified for 17.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 17.0 source; master-only APIs are translated to the 17.0 equivalent or marked as not available.

### Audit sweep (pattern -> what makes it a finding)

| Pattern | Finding when... (17.0 form) |
|---------|-----------------------------|
| `.sudo()` | Any attacker-controlled model, record id, field name, domain or vals reaches a read/search/create/write under sudo. Controllers: `record.sudo().write(post)` is always a finding; whitelist keys. `sudo(flag=True)` only takes a bool (`sudo(user)` does not exist; use `with_user(user)`). |
| `with_user()` / `with_company()` | The switch is not intentional or widens access (`with_user` drops superuser mode). |
| x2many vals under sudo | `Command`/tuple payloads on a sensitive comodel run with sudo unless the comodel sets `_allow_sudo_commands = False` (core does this on `ir.rule`, `ir.model.access`, ...). |
| `related=` | Related fields are computed as superuser by default (`related_sudo=True`). A related chain onto `ir.attachment` or other sensitive data needs `related_sudo=False`. |
| `cr.execute(...)` | String building with `+`, `%`, `.format()` or f-strings; see Secure SQL Queries. |
| Domains | A user-supplied list concatenated onto a security domain. 17.0 has no `fields.Domain`; combine with `from odoo.osv import expression` -> `expression.AND([...])` / `expression.OR([...])`. |
| Public model method | Any method without `_` is callable via RPC with attacker arguments. The 17.0 guard (`odoo.service.model.get_public_method`) blocks `_`-prefixed names and methods decorated with `@api.private`; it does NOT block classmethods/staticmethods. |
| `@http.route` auth | `auth` must match exposure: `'user'`, `'public'` or `'none'` (no `bearer` in 17.0). |
| `@http.route` type/CSRF | Route types are `'http'` and `'json'` only. `type='http'` checks the CSRF token for every method except GET/HEAD/OPTIONS/TRACE; `csrf=False` only for external webhooks. `type='json'` has no token check. A state change on GET is a finding. POST forms need `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>`. |
| QWeb output | Use `t-out` (escapes; a `Markup` value passes through raw). In 17.0 `t-esc` still works as a deprecated alias of `t-out`; `t-raw` still works (deprecation warning) and outputs unescaped, so any `t-raw` on user data is a finding. |
| Python HTML building | f-strings or `%` on plain `str` that is then wrapped in `Markup`. Use `Markup("<p>%s</p>") % value` or `Markup(...).format(...)`; `_("...%s", value)` escapes the translation when an argument is `Markup`. |
| JS HTML sinks | `innerHTML`, `insertAdjacentHTML`, Owl `markup()` on non-literal values. 17.0 helpers: `htmlEscape` and `markup` from `@odoo/owl`, `escape` from `@web/core/utils/strings`. (`@web/core/utils/html` does not exist in 17.0.) |
| `fields.Html` | Escaping is not sanitizing. Options: `sanitize`, `sanitize_overridable`, `sanitize_tags`, `sanitize_attributes`, `sanitize_style`, `sanitize_form`, `strip_style`, `strip_classes`. |
| Secret fields | Passwords/tokens without `groups="base.group_system"` or `groups=fields.NO_ACCESS`; see Field-Level Security. |
| `open()` | Builtin `open()` on an influenceable path. Use `odoo.tools.file_open(name, mode='r', filter_ext=None, env=None)`: confined to addons paths, the Odoo root and temp dirs from `file_open_temporary_directory(env)`; it never creates files but opens existing ones in any mode. |
| `eval`/`exec` | Any use. Use `json.loads`/`ast.literal_eval`; at worst `odoo.tools.safe_eval.safe_eval` with a minimal namespace. safe_eval rejects every name containing `__`; public model methods returning rich objects are reachable from server actions. |
| `getattr`/`setattr` on records | Dynamic field names; use `record[name]`. |
| `pickle` | Stdlib pickle on untrusted data. 17.0 still ships a restricted `odoo.tools.misc.pickle` (whitelisted unpickler), but prefer JSON. |
| Secret comparison | `==` on tokens. Use `odoo.tools.consteq` (= `hmac.compare_digest`), better: look the token up in the DB. |
| Mutable defaults | `def m(self, vals={})` / `[]` defaults. |

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
| Create method | `@api.model` single-dict create works, logs a warning | same (still a warning); use `@api.model_create_multi` |
| Domain syntax | Still supports `attrs` | `attrs` removed |

## AI Agent Instructions (v17)

When generating Odoo 17.0 security code:

1. **Never use** `attrs` attribute in views (removed in v17)
2. **Always use** direct `invisible`, `readonly`, `required` attributes
3. **Use** Python expressions for visibility: `invisible="state != 'draft'"`
4. **Use** the `groups` attribute for group checks (`groups="base.group_system"`); `user_has_groups()` is not available in v17 view expressions
5. **Use** `@api.model_create_multi` for create methods (single-dict `@api.model` create only warns, but do not generate it)
6. **Use** parameterized SQL queries
7. **Use** `company_ids` in multi-company record rules
