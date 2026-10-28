# Odoo Security Guide - Version 14.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 14.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 14.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  NOTE: Odoo 14.0 is LEGACY - consider upgrading to a supported version.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 14.0 Requirements

- **Python**: 3.6+ required
- **Key Features**: `@api.multi` already removed (since 13.0), `attrs` in views, legacy widget system (Owl 1.4.11 bundled)

## Security Groups (v14 Syntax)

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

## Access Rights (v14)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

- A model without any row is inaccessible, TransientModels included.
- Never grant create/write/unlink to `base.group_portal` or `base.group_public`, or with an empty `group_id` (= every user; `base.group_everyone` does not exist in 14.0).

## Record Rules (v14 Syntax)

- Rules only cover the modes they set (`perm_read/write/create/unlink`): the other operations are governed by ACLs only.
- Global rules (no `groups`) are AND-ed: non-overlapping globals lock everyone out. All rules of the user's groups are OR-ed together, then AND-ed with the globals.
- Multi-company models need a company rule (first example below).
- The `domain_force` eval context holds `user`, `time`, `company_ids`, `company_id` (no `allowed_company_ids`).

```xml
<record id="rule_custom_model_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <!-- global = no groups; the 'global' field is computed from 'groups' -->
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

## Model Security (v14 Patterns)

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
        tracking=True,  # v14: 'tracking' is the valid parameter (track_visibility logs a warning)
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

    # v14: BaseModel.create is already model_create_multi
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def write(self, vals):
        return super().write(vals)

    # v14: @api.multi does not exist (removed in 13.0) - never add it
    def action_sensitive_operation(self):
        """Check permissions before sensitive operations."""
        if not self.env.user.has_group('custom_module.group_manager'):
            raise AccessError(_("Only managers can perform this action."))
        for record in self:
            record._do_sensitive_work()
```

## View Security (v14 Syntax - attrs)

### Using attrs for Visibility

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- v14: Use attrs for conditional visibility -->
            <field name="internal_notes"
                   attrs="{'invisible': [('state', '=', 'draft')]}"/>

            <!-- v14: Combine attrs with groups -->
            <field name="secret_field"
                   attrs="{'invisible': [('state', '=', 'draft')]}"
                   groups="custom_module.group_manager"/>

            <!-- v14: Multiple conditions in attrs -->
            <field name="amount"
                   attrs="{'readonly': [('state', '!=', 'draft')], 'required': [('type', '=', 'invoice')]}"/>
        </group>
    </sheet>
</form>
```

### Button Security (v14)

```xml
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_manager"
        attrs="{'invisible': [('state', '!=', 'pending')]}"/>

<button name="action_confirm"
        string="Confirm"
        type="object"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

### Complete Form Example (v14)

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
                    <field name="message_follower_ids" widget="mail_followers"/>
                    <field name="activity_ids" widget="mail_activity"/>
                    <field name="message_ids" widget="mail_thread"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
```

## Field-Level Security (v14)

```python
class SecureModel(models.Model):
    _name = 'custom.secure'
    _description = 'Secure Model'

    name = fields.Char(required=True)  # 'tracking' needs _inherit = ['mail.thread']

    internal_notes = fields.Text(
        string='Internal Notes',
        groups='custom_module.group_manager',
    )

    cost_price = fields.Float(
        string='Cost Price',
        groups='account.group_account_user',
    )
```

Field `groups` hides the field from `fields_get` and raises AccessError on explicit read/write. Password or token fields on a model readable through `search_read` must have `groups=`: use `groups='base.group_system'` or `groups=fields.NO_ACCESS` (`'.'`, exists in 14.0).

## Additional Rules from Odoo's Official Guidelines (verified for 14.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 14.0 source; master-only APIs are translated to the 14.0 equivalent or marked as not available.

### Audit sweep (pattern -> what makes it a finding)

| Pattern | Finding when ... (14.0 form) |
|---------|------------------------------|
| `sudo()` / `with_user()` / `with_company()` | an attacker controls the model, record ids, field names, values or domain reached under sudo. Controllers: `record.sudo().write(post)` or `create(kw)` without a key whitelist. `sudo(user)` is deprecated in 14.0 (it logs a warning and calls `with_user`). |
| x2many values under `sudo()` | tuple commands `(0, 0, vals)` / `(1, id, vals)` from user input reach a comodel that keeps the default `_allow_sudo_commands = True`: they run as superuser on the comodel. Set `_allow_sudo_commands = False` on sensitive comodels (`ir.rule` and `ir.model.access` already do). There is no `Command` class in 14.0. |
| `related=` fields | a sudo-computed related (`related_sudo=True` is the default) exposes data the user cannot read, e.g. a related onto `ir.attachment` (arbitrary `attachment_id` -> arbitrary file). Use `related_sudo=False` on sensitive chains. |
| `cr.execute` | the query uses `%`, `+`, `.format` or f-strings with values. Pass parameters: `cr.execute("... WHERE id IN %s", (tuple(ids),))`. There is no `odoo.tools.SQL` in 14.0: identifiers come from `psycopg2.sql.Identifier` or a whitelist. Over ORM-filtered rows: `query = Model._search(domain)` then `sql, params = query.select('"my_table"."amount"')` (handle the `[]` return for an always-false domain). |
| domains | a user-supplied list is concatenated onto a security domain. Combine with `odoo.osv.expression.AND([...])` / `OR([...])`. |
| public model methods | a method without `_` prefix does something unsafe with its arguments: every public method is callable over RPC. The 14.0 guard (`check_method_name`) only blocks names starting with `_` and `init`. There is no `@api.private`, and public classmethods/staticmethods are not blocked. |
| `@http.route` | `auth` does not match the exposure (14.0 values: `user`, `public`, `none`; no `bearer`). A state change is reachable by GET (`methods` defaults to all). `csrf=False` on a `type='http'` route that is not a webhook. `type` must be `'http'` or `'json'`. An override of a route without `@http.route()` silently removes the URL. |
| CSRF | a POST form template lacks `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>`. JSON routes have no token check by design. |
| server QWeb | `t-raw` on anything that is not sanitized HTML. 14.0 has no `t-out`: `t-esc` is the escaping directive, `t-raw` prints raw. HTML built in Python with `%`/f-strings from user data and then rendered with `t-raw`: escape the parts with `odoo.tools.html_escape()`. `_()` does not escape arguments in 14.0. |
| JS | `$el.html(userValue)`, `innerHTML`, `insertAdjacentHTML` with non-literal content. Owl is 1.4.11 (no `markup`, no `htmlEscape`, no `@web/core/utils/html`): render through QWeb `t-esc` or set `.text()`/`textContent`. |
| `fields.Html` | `sanitize=False` on user-editable content. Available options: `sanitize`, `sanitize_tags`, `sanitize_attributes`, `sanitize_style`, `sanitize_form`, `strip_style`, `strip_classes`. |
| secrets and tokens | a password or token field without `groups=` on a model readable through `search_read`; see Field-Level Security (v14). |
| `open()` | a path influenced by input. Use `odoo.tools.file_open(name, mode='r', subdir='addons', pathinfo=False, filter_ext=None, env=None)`: it only resolves inside addons paths, `root_path` and temp dirs registered on `env`, and never creates files. |
| `eval` / `exec` | any use. Use `json.loads` / `ast.literal_eval`; `odoo.tools.safe_eval.safe_eval` only with a constrained namespace for trusted users. safe_eval rejects names containing `__`. Public methods returning rich objects are reachable from server actions. |
| `getattr` / `setattr` | a dynamic field name from input. Use `record[name]` after checking `name in record._fields`. |
| `pickle` | stdlib `pickle.loads` on untrusted data. 14.0 still ships the restricted `odoo.tools.misc.pickle` (no globals), but prefer JSON. |
| secret comparison | `==` on tokens. Use `odoo.tools.consteq(a, b)`, or better look the token up in the database. |
| mutable defaults | `def m(self, vals={})` / `=[]`. |
| `ir.model.access.csv` | a row grants create/write/unlink to portal/public or with an empty `group_id`, or a model has no row; see Access Rights (v14). |
| `ir.rule` | rules miss modes, globals do not overlap, or a multi-company model has no company rule; see Record Rules (v14 Syntax). |

## v14 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Use `attrs` for view visibility conditions
- [ ] Use `tracking=True` for field tracking (on `mail.thread` models)
- [ ] `@api.model_create_multi` create overrides
- [ ] No `@api.multi` (it does not exist in 14.0)
- [ ] Use legacy chatter widgets

## Key v14 Patterns

| Feature | v14 Pattern |
|---------|-------------|
| Field tracking | `tracking=True` |
| View visibility | `attrs="{'invisible': [...]}"` |
| Create method | `@api.model_create_multi` + `def create(self, vals_list):` |
| Chatter | `widget="mail_followers"`, `widget="mail_thread"` |

## AI Agent Instructions (v14)

When generating Odoo 14.0 security code:

1. **Use** `attrs` for view visibility: `attrs="{'invisible': [...]}"`
2. **Use** `tracking=True` for field tracking
3. **Use** `@api.model_create_multi` for create overrides
4. **Do NOT** use `@api.multi` (removed - fails in 14.0)
5. **Use** legacy chatter widgets: `widget="mail_followers"`
6. **Note**: v14 is legacy - recommend upgrading
