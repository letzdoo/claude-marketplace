# Odoo Security Guide - Version 16.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 16.0 SECURITY PATTERNS                                                 ║
║  This file contains ONLY Odoo 16.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 16.0 Requirements

- **Python**: 3.7+ (`MIN_PY_VERSION = (3, 7)`, `MAX_PY_VERSION = (3, 12)` in `odoo/__init__.py`)
- **Key Features**: `Command` class, `attrs`/`states` are THE view-modifier syntax (direct `invisible="expr"` is 17.0+ only), OWL 2.x

## Security Groups (v16 Syntax)

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

## Access Rights (v16)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

- Model access is `ir.model.access` (`security/ir.model.access.csv`); row-level is `ir.rule`. There is no `ir.access` / `ir.access.csv` in 16.0.
- A model without any access row is inaccessible to non-superusers; module loading logs "The models [...] have no access rules".
- An access row with empty `group_id` applies to everyone (there is no `base.group_everyone` group). Flag create/write/unlink granted to `base.group_portal`, `base.group_public` or to an empty group.
- Access rights and rules are per operation (`perm_read/write/create/unlink`); a rule with only `perm_write` does not restrict reading.

## Record Rules (v16 Syntax)

- Rule combination: all global rules (no groups) are AND-ed; all group rules matching any of the user's groups are OR-ed together, then AND-ed with the globals. Non-overlapping global rules lock everyone out.
- Names available in `domain_force`: `user`, `time`, `company_ids` (enabled companies), `company_id`. `allowed_company_ids` is NOT in the eval context.
- Reading a field through `browse(id)` in a non-sudo env checks ACLs and record rules (AccessError); the IDOR risk is `sudo()`.

### Multi-Company Rule

```xml
<record id="rule_custom_model_company" model="ir.rule">
    <field name="name">Custom Model: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <!-- no <field name="groups"> => global rule (AND-ed with all other global rules) -->
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

## Model Security (v16 Patterns)

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
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
    )
    line_ids = fields.One2many('custom.secure.line', 'parent_id')

    # v16: always batch; a single-dict @api.model create still works but
    # logs "not overriding the create method in batch" (WARNING)
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def action_update_lines(self):
        """v16: Use Command class for x2many operations."""
        self.write({
            'line_ids': [
                Command.create({'name': 'New Line'}),
                Command.update(1, {'name': 'Updated'}),
                Command.delete(2),
                Command.link(3),
                Command.unlink(4),
                Command.clear(),
                Command.set([5, 6]),
            ]
        })
```

## View Security (v16 Syntax - `attrs` is correct)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  In 16.0 record-dependent visibility MUST use attrs="{...}" (domains) or     ║
║  states="...". Direct invisible="state == 'draft'" is NOT a record condition ║
║  in 16.0: non-boolean values are stored as context-dependent modifiers and   ║
║  evaluated with only `context` available (ir_ui_view.py,                     ║
║  transfer_node_to_modifiers / _postprocess_context_dependent), so a field    ║
║  name in the expression fails. Expressions are 17.0+.                        ║
║  Allowed direct values in 16.0: "1"/"0"/"True"/"False" or context.get(...).  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- Record-dependent visibility: attrs with a domain -->
            <field name="internal_notes"
                   attrs="{'invisible': [('state', '=', 'draft')]}"/>

            <!-- Security is groups=, visibility is attrs= -->
            <field name="manager_notes"
                   groups="custom_module.group_manager"
                   attrs="{'invisible': [('state', '=', 'draft')]}"/>

            <!-- readonly / required also via attrs -->
            <field name="amount"
                   attrs="{'readonly': [('state', '!=', 'draft')]}"/>

            <!-- Context-dependent: allowed as direct attribute in 16.0 -->
            <field name="cost_price" invisible="context.get('hide_cost', False)"/>
        </group>
    </sheet>
</form>
```

### Button Security (v16)

```xml
<button name="action_approve"
        string="Approve"
        type="object"
        groups="custom_module.group_manager"
        attrs="{'invisible': [('state', '!=', 'pending')]}"/>

<!-- states= is a 16.0 shorthand for "visible only in these states" -->
<button name="action_confirm"
        string="Confirm"
        type="object"
        states="draft"/>
```

`groups=` on a view node removes the node for non-members (`_postprocess_access_rights`), but that is UI only: protect data with field `groups=`, ACLs and record rules.

## Field-Level Security (v16)

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

Sensitive fields (password/token/cost) without `groups` are readable via `search_read`: use `groups="base.group_system"` or `groups=fields.NO_ACCESS` (`'.'`, exists in 16.0). Restricted fields are dropped from `fields_get`; an explicit read raises `AccessError`.

## Complete Security Template (v16)

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

    <!-- Global rule = no groups (the `global` field is computed from groups) -->
    <record id="rule_custom_model_company" model="ir.rule">
        <field name="name">Custom Model: Multi-Company</field>
        <field name="model_id" ref="model_custom_model"/>
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

## Additional Rules from Odoo's Official Guidelines (verified for 16.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 16.0 source; master-only APIs are translated to the 16.0 equivalent or marked as not available.

### Audit sweep (pattern -> what makes it a finding)

| Pattern | Finding when ... | 16.0 form / note |
|---|---|---|
| `.sudo()` | attacker-controlled model/record/field/domain/vals reach a sudo read/search/create/write; `record.sudo().write(post)` in a controller | `sudo(flag=True)` takes a bool only (`sudo(user)` does not exist); whitelist keys: `vals = {k: post[k] for k in ALLOWED if k in post}` |
| `with_user()` / `with_company()` | the switch is not intentional or uses request input unchecked | both exist (`@api.private`) |
| x2many `Command`s under sudo | sudo-written vals contain `Command.create/update/...` for a sensitive comodel | commands run as sudo on the comodel unless the comodel sets `_allow_sudo_commands = False` (then they run as the original user, `env.uid_origin`) |
| `related=` | sudo-computed related exposes data (e.g. related onto `ir.attachment`) | `related_sudo=True` is the default; set `related_sudo=False` on sensitive chains |
| `cr.execute(...)` | string building with `%`, `+`, `.format()`, f-string; ORM could do it | pass params: `cr.execute("... WHERE id IN %s", [tuple(ids)])`. No master `SQL()` builder in 16.0; `from odoo.tools import SQL` is **psycopg2's** `sql.SQL` (different API). Identifiers: `psycopg2.sql.SQL("... {}").format(psycopg2.sql.Identifier(name))`. Custom SQL over ORM-filtered rows: `query = Model._search(domain)` returns a `Query` (or `[]` if the domain is trivially false); `sql, params = query.select('"my_table"."id"')`; never `if query:` (that executes it) |
| domain concatenation | user-supplied list appended to a security domain | `from odoo.osv import expression`; `expression.AND([security_domain, user_domain])` (no `fields.Domain` in 16.0) |
| public model method | method without `_` prefix that is not meant for RPC | RPC guard `odoo.service.model.get_public_method` blocks names starting with `_`, methods marked `@api.private` (exists in 16.0) and `safe_eval._UNSAFE_ATTRIBUTES`; classmethods/staticmethods are NOT blocked in 16.0, so prefix them with `_` |
| `@http.route` | `auth` too open for the data exposed; state change on GET; `csrf=False` outside webhooks | `auth`: `user` (default), `public`, `none` (no `bearer` in 16.0); `type`: `http` or `json` only; `type='http'` checks CSRF for non-GET/HEAD/OPTIONS/TRACE unless `csrf=False`; `type='json'` has no token check but requires a JSON content type; write routes use `methods=['POST']`; an override must be re-decorated with `@http.route()` (16.0 auto-decorates with a warning) |
| POST forms in QWeb | missing token | `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>` |
| server QWeb output | `t-raw` anywhere; `Markup(...)` wrapping user content; f-string HTML | `t-out` escapes; `t-esc` is a deprecated alias of `t-out` (still escapes); `t-raw` still works in 16.0 but renders `Markup(content)` UNESCAPED (XSS sink, replace by `t-out`). Build HTML with `Markup("<p>%s</p>") % value`. `_()` does NOT escape Markup args in 16.0: use `Markup(_("Hello %s")) % value` |
| JS output | `innerHTML`, `insertAdjacentHTML`, `markup()` on non-literal data | Owl 2: `import { markup, htmlEscape } from "@odoo/owl"`; `import { escape } from "@web/core/utils/strings"`. `@web/core/utils/html` (`setInnerHtml`, `htmlJoin`) does not exist in 16.0 |
| `fields.Html` | user HTML stored with `sanitize=False` or `sanitize_overridable=True` without reason | options: `sanitize`, `sanitize_overridable`, `sanitize_tags`, `sanitize_attributes`, `sanitize_style`, `sanitize_form`, `strip_style`, `strip_classes` |
| sensitive field without `groups` | password/token/cost readable via `search_read` | see Field-Level Security |
| builtin `open()` | path influenced by input | `odoo.tools.file_open(path, mode='r', filter_ext=None, env=None)`: only addons paths, Odoo root and temp dirs from `file_open_temporary_directory(env)`; existing files only |
| `eval` / `exec` | any use on data | `json.loads` / `ast.literal_eval`; at most `odoo.tools.safe_eval.safe_eval` (rejects names containing `__` and `_UNSAFE_ATTRIBUTES`) with a minimal context |
| `getattr`/`setattr` on records | dynamic field name | `record[fname]` |
| `pickle` | any unpickling of untrusted data | 16.0 still ships a restricted `odoo.tools.misc.pickle` (only set/datetime/pytz globals); prefer `json` |
| secret comparison with `==` | token/hash compared directly | `odoo.tools.misc.consteq(a, b)` (= `hmac.compare_digest`), better: look the token up in the DB |
| mutable default args | `def f(self, vals={})` | `vals=None` |

## v16 Security Checklist

- [ ] All models have `ir.model.access.csv` entries
- [ ] Record rules use `company_ids` for multi-company
- [ ] Record-dependent visibility uses `attrs`/`states` (not `invisible="expr"`)
- [ ] Use `Command` class for x2many security operations
- [ ] Use `tracking=True` instead of `track_visibility`
- [ ] No `t-raw`, no `sudo()` on user-controlled input, no string-built SQL

## Key Differences

| Feature | v15 | v16 |
|---------|-----|-----|
| x2many commands | `Command` class (already in 15) or tuples | `Command` class or tuples |
| View visibility | `attrs` / `states` | `attrs` / `states` (expressions only from 17.0) |
| RPC guard | `check_method_name` (`_` prefix) | `get_public_method` + `@api.private` |
| Tracking | `tracking=True` | `tracking=True` |

## AI Agent Instructions (v16)

When generating Odoo 16.0 security code:

1. **Use** `attrs="{'invisible': [...]}"` / `states=` for record-dependent visibility; never `invisible="state == 'draft'"` in 16.0
2. **Use** `Command` class for x2many operations
3. **Use** `tracking=True` for field tracking
4. **Use** `company_ids` in multi-company record rules; global rules have no `groups` (never set `global`)
5. **Use** `t-out`, never `t-raw`; parameterized SQL; `expression.AND` for domains
6. **Use** `@api.model_create_multi` (single-dict create logs a warning)
