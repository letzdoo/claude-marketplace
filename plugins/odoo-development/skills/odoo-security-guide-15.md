# Odoo Security Guide - Version 15.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 15.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 15.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  NOTE: Odoo 15.0 is LEGACY - consider upgrading to a supported version.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 15.0 Requirements

- **Python**: 3.7+ (`odoo/__init__.py` MIN_PY_VERSION)
- **Key facts**: no `@api.multi` (already absent in 14.0), `tracking=True` for field tracking, Owl 1.4 (also shipped with 14.0), `Command` class available (`from odoo import Command`)

## Security Groups (v15 Syntax)

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

## Access Rights (v15)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

- Access model: `ir.model.access` (CSV, per operation `perm_read/write/create/unlink`) + `ir.rule`. There is no `ir.access` model in 15.0.
- Default deny: a model without a matching ACL row is inaccessible; module loading logs "The models [...] have no access rules" (also for TransientModels).
- `base.group_everyone` does not exist. An ACL row with an empty `group_id` applies to everybody, including portal and public users: flag write/create/unlink on such rows and on `base.group_portal` / `base.group_public`.

## Record Rules (v15 Syntax)

```xml
<record id="rule_custom_model_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <!-- no groups => global rule; `global` is computed from `groups`, never set it -->
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
```

- Rule combination: global rules (no `groups`) are AND-ed; all applicable group rules of the user are OR-ed together and then AND-ed with the globals. Non-overlapping global rules lock everybody out.
- A rule restricted to some `perm_*` operations leaves the other operations unrestricted: cover all CRUD operations.
- Rule eval context: `user`, `time`, `company_ids`, `company_id` (NOT `allowed_company_ids`); multi-company domain as in the first example.

## Model Security (v15 Patterns)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,  # v15: tracking replaces track_visibility
    )
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
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)

    # v15: base create() is @api.model_create_multi; override it the same way
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    # v15: @api.multi is REMOVED - do not use
    def action_sensitive_operation(self):
        """Check permissions before sensitive operations."""
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(_("Only managers can perform this action."))
        for record in self:
            record._do_sensitive_work()
```

## View Security (v15 Syntax - attrs)

### Using attrs for Visibility

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- v15: Use attrs for conditional visibility -->
            <field name="internal_notes"
                   attrs="{'invisible': [('state', '=', 'draft')]}"/>

            <!-- v15: Combine attrs with groups -->
            <field name="secret_field"
                   attrs="{'invisible': [('state', '=', 'draft')]}"
                   groups="custom_module.group_manager"/>
        </group>
    </sheet>
</form>
```

### Button Security (v15)

```xml
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_manager"
        attrs="{'invisible': [('state', '!=', 'pending')]}"/>
```

### Complete Form Example (v15)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="custom_model_view_form" model="ir.ui.view">
        <field name="name">custom.model.form</field>
        <field name="model">custom.model</field>
        <field name="arch" type="xml">
            <form string="Custom Model">
                <header>
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary"
                            attrs="{'invisible': [('state', '!=', 'draft')]}"/>
                    <button name="action_done" string="Done" type="object"
                            attrs="{'invisible': [('state', '!=', 'confirmed')]}"/>
                    <button name="action_approve" string="Approve" type="object"
                            groups="custom_module.group_manager"
                            attrs="{'invisible': [('state', '!=', 'pending')]}"/>
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
                    <group string="Internal" groups="custom_module.group_manager">
                        <field name="internal_notes"/>
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

## Field-Level Security (v15)

```python
class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    name = fields.Char(required=True, tracking=True)

    internal_notes = fields.Text(
        string='Internal Notes',
        groups='custom_module.group_manager',
    )

    cost_price = fields.Float(
        string='Cost Price',
        groups='account.group_account_user',
    )
```

Password/token/API key fields on a model readable by normal users are readable via `search_read` unless they carry `groups`: use `groups='base.group_system'` or `groups=fields.NO_ACCESS` (`'.'`, only sudo can read). `groups` hides the field from `fields_get` and raises on explicit read/write.

## Additional Rules from Odoo's Official Guidelines (verified for 15.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 15.0 source; master-only APIs are translated to the 15.0 equivalent or marked as not available.

### Audit sweep (15.0 forms)

| Pattern to grep | It is a finding when ... | 15.0 form / fix |
|---|---|---|
| `.sudo(` | an attacker controls the model, record ids, field names, domain or vals of a read/search/create/write done under sudo; `record.sudo().write(post)` in a controller | Whitelist keys from `post`; sudo only the minimal call. `sudo()` takes a bool; `sudo(user)` still works but logs a deprecation and delegates to `with_user(user)` |
| `.with_user(` / `.with_company(` | the switch is driven by request input or is not intentional | Both exist in 15.0; `with_company()` rewrites `allowed_company_ids` in the context |
| x2many vals written under sudo | the comodel is security-sensitive and keeps `_allow_sudo_commands = True` (default) | Set `_allow_sudo_commands = False` on the comodel: Command/tuple payloads then run with `sudo(False)` as the original user (core does this on `ir.rule`, `ir.model.data`) |
| `related=` | the chain reaches sensitive data, e.g. a user-settable m2o to `ir.attachment` | Related fields are computed as superuser by default; add `related_sudo=False`. A `readonly=False` related writes through in the user's env |
| `cr.execute(` | SQL built with `+`, `%`, `.format()` or f-strings from non-constant input | Pass values as parameters (`IN %s` takes a tuple). Dynamic identifiers: `psycopg2.sql.Identifier` or a whitelist from `self._fields` / `self._table`. `odoo.tools.SQL` does NOT exist in 15.0 |
| raw SQL over ORM-filtered rows | the query ignores record rules | `query = self._search(domain)` (rules applied, returns `odoo.osv.query.Query`, or `[]` when the domain is trivially false - check `isinstance(query, Query)`, never `if query:` which executes it); `query.order = None`; `query_str, params = query.select('"%s"."amount"' % self._table)`; `self.env.cr.execute(query_str, params)` |
| domain concatenation | a user-supplied list is appended to a security domain | `from odoo.osv import expression`; `domain = expression.AND([base_domain, user_domain])` (no `fields.Domain` in 15.0) |
| public model method (no `_` prefix) | it accepts ids/domains/vals and acts with sudo or skips checks | Every non-`_` method is callable over RPC. The 15.0 guard `check_method_name` only blocks names matching `^(_.*\|init)$`; there is no `@api.private`. Prefix internal methods with `_` |
| `@http.route(` | `auth` broader than needed; state change on GET; `csrf=False` on a non-webhook route | `auth` is `user` (default), `public` or `none` (no `bearer` in 15.0); `type` is `http` or `json`. Writing routes: `methods=['POST']`. `type='http'` checks the CSRF token on every non-GET/HEAD/OPTIONS/TRACE request; `type='json'` has no token check |
| HTML forms posting to `type='http'` | no CSRF token | `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>` |
| server QWeb `t-raw` | any use (legacy raw-HTML sink) | 15.0 has `t-out` (escapes). `t-esc` is a working, escaping alias. `t-raw` still renders, logs a deprecation warning and outputs the value unescaped: replace it by `t-out` |
| `Markup(` | user content is formatted into the Markup string via f-string/`+` | `Markup("<p>%s</p>") % value` or `Markup("<p>{}</p>").format(value)` escape the arguments. `_()` in 15.0 does plain `%` formatting and does NOT escape Markup arguments: escape before translating into HTML |
| JS `innerHTML`, `$el.html(`, `insertAdjacentHTML`, Owl 1 `t-raw` | the value is not a trusted constant | Owl 1.4 has no `markup()`; `@web/core/utils/html` does not exist in 15.0. Use `t-esc` in templates or escape with underscore's `_.escape` |
| `fields.Html(` | `sanitize=False` on user-editable content | Keep `sanitize=True`; tune `sanitize_tags`, `sanitize_attributes`, `sanitize_style`, `sanitize_form`, `strip_style`, `strip_classes` |
| password/token/API key fields | no `groups` on a model readable by normal users | see Field-Level Security (v15) |
| builtin `open(` | the path is influenced by input | `odoo.tools.file_open(path, mode, filter_ext=..., env=...)`: confined to addons paths, the server root and temp dirs from `file_open_temporary_directory(env)`; only existing files |
| `eval(` / `exec(` | any use on data | `json.loads` / `ast.literal_eval`; `odoo.tools.safe_eval.safe_eval` only for trusted (admin) input. Names containing `__` are rejected by safe_eval |
| `getattr(record, name)` / `setattr` | `name` comes from input | `record[name]` after checking `name in record._fields` |
| `pickle.loads` | data is not fully trusted | Use JSON. 15.0 still ships a restricted `odoo.tools.misc.pickle` (no globals), but do not rely on it |
| `==` on secrets/tokens | timing-unsafe comparison | `odoo.tools.consteq(a, b)`; better: look the token up in the database |
| `def f(x=[])` / `={}` | mutable default argument | `None` default |

Access model (ACLs, record rules): see Access Rights (v15) and Record Rules (v15 Syntax).

## v15 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Use `attrs` for view visibility conditions
- [ ] Use `tracking=True` (NOT `track_visibility`)
- [ ] Do NOT use `@api.multi` (removed)
- [ ] Update chatter widgets (simplified)

## Key Differences from v14

| Feature | v14 | v15 |
|---------|-----|-----|
| Field tracking | `track_visibility='onchange'` | `tracking=True` |
| @api.multi | Absent | Absent |
| OWL | Owl 1.4 shipped (legacy widgets dominate) | Owl 1.4, new `@web/core` web client, `@odoo-module` ES modules |
| x2many commands | Tuples only | `Command` class available (tuples still valid) |
| Chatter widgets | Legacy widgets | Simplified |

## AI Agent Instructions (v15)

When generating Odoo 15.0 security code:

1. **Use** `attrs` for view visibility: `attrs="{'invisible': [...]}"`
2. **Use** `tracking=True` for field tracking (NOT `track_visibility`)
3. **Do NOT** use `@api.multi` (does not exist in 15.0)
3a. **Follow** the "Additional Rules from Odoo's Official Guidelines (verified for 15.0)" audit sweep above
4. **Use** updated chatter syntax (no widget attribute needed)
5. **Note**: v15 is legacy - recommend upgrading
