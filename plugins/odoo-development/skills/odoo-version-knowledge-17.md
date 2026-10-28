# Odoo 17.0 Version Knowledge

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 17.0 KNOWLEDGE BASE                                                    ║
║  attrs REMOVED, use @api.model_create_multi (single-dict create warns)       ║
║  Released: October 2023                                                      ║
║  VERIFY: https://github.com/odoo/odoo/tree/17.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Overview

| Aspect | Details |
|--------|---------|
| Release Date | October 2023 |
| Python | 3.10, 3.11 |
| PostgreSQL | 13, 14, 15 |
| Frontend | OWL 2.x (enhanced) |
| Support | Community: Active, Enterprise: Active |

## BREAKING Changes from v16

### attrs REMOVED
```xml
<!-- BREAKS IN v17 -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- v17 REQUIRED -->
<field name="partner_id"
       invisible="state == 'draft'"/>
```

### @api.model_create_multi expected
```python
# Still works in v17, but logs a WARNING
# ("The model ... is not overriding the create method in batch")
@api.model
def create(self, vals):
    return super().create(vals)

# v17 correct form
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

## Key Features

### New in Odoo 17
- Improved UI/UX
- Enhanced AI features
- Better mobile experience
- New dashboard widgets
- Improved reporting
- WhatsApp enhancements (Enterprise)

### Technical Stack
- Python 3.10+ (3.11 recommended)
- PostgreSQL 13+
- OWL 2.x (enhanced)
- ES modules

## Version-Specific Patterns

### Model Definition
```python
from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'

    name = fields.Char(
        required=True,
        index='trigram',  # v17: Index type specification
        tracking=True,
    )

    code = fields.Char(index=True, copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, index=True)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], default='0')

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    date = fields.Date(default=fields.Date.context_today)
    date_deadline = fields.Date(index=True)

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        tracking=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        tracking=True,
    )

    line_ids = fields.One2many(
        'my.model.line',
        'model_id',
        copy=True,
    )

    total_amount = fields.Monetary(
        compute='_compute_total',
        store=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )
```

### CRUD Methods (v17 Pattern)
```python
@api.model_create_multi
def create(self, vals_list):
    """Use model_create_multi in v17 (single-dict create only warns)"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('my.model')

    records = super().create(vals_list)

    for record in records:
        record.message_post(body=_("Record created."))

    return records

def write(self, vals):
    """Write with validation"""
    if 'state' in vals and vals['state'] == 'confirmed':
        for record in self:
            if not record.line_ids:
                raise UserError(_("Add at least one line."))
    return super().write(vals)

def unlink(self):
    """Delete with state check"""
    for record in self:
        if record.state not in ('draft', 'cancelled'):
            raise UserError(_("Only draft or cancelled records can be deleted."))
    return super().unlink()
```

### XML Views (v17 Required Syntax)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <!-- v17: Must use Python expressions -->
                    <button name="action_confirm" type="object"
                            string="Confirm" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_start" type="object"
                            string="Start"
                            invisible="state != 'confirmed'"/>
                    <button name="action_done" type="object"
                            string="Done"
                            invisible="state != 'in_progress'"/>
                    <button name="action_cancel" type="object"
                            string="Cancel"
                            invisible="state in ('done', 'cancelled')"/>

                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,in_progress,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_lines" type="object"
                                class="oe_stat_button" icon="fa-list"
                                invisible="line_count == 0">
                            <field name="line_count" widget="statinfo"/>
                        </button>
                    </div>

                    <widget name="web_ribbon" title="Archived"
                            invisible="active"/>

                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Name"
                                   readonly="state == 'done'"/>
                        </h1>
                    </div>

                    <group>
                        <group>
                            <field name="code" readonly="state != 'draft'"/>
                            <field name="partner_id"
                                   readonly="state == 'done'"
                                   required="state == 'confirmed'"/>
                            <field name="user_id"/>
                            <field name="priority" widget="priority"/>
                        </group>
                        <group>
                            <field name="date"/>
                            <field name="date_deadline"
                                   invisible="state == 'draft'"/>
                            <field name="company_id"
                                   groups="base.group_multi_company"
                                   readonly="state != 'draft'"/>
                        </group>
                    </group>

                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids"
                                   readonly="state == 'done'">
                                <tree editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price"/>
                                    <field name="amount" sum="Total"/>
                                </tree>
                            </field>
                            <group class="oe_subtotal_footer">
                                <field name="total_amount"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <record id="view_my_model_tree" model="ir.ui.view">
        <field name="name">my.model.tree</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <tree decoration-danger="state == 'cancelled'"
                  decoration-success="state == 'done'">
                <field name="sequence" widget="handle"/>
                <field name="name"/>
                <field name="partner_id"/>
                <field name="date"/>
                <field name="total_amount" sum="Total"/>
                <field name="state" widget="badge"
                       decoration-success="state == 'done'"
                       decoration-info="state == 'confirmed'"/>
            </tree>
        </field>
    </record>
</odoo>
```

## OWL 2.x Enhanced

### Component Pattern
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
        onConfirm: { type: Function, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            data: [],
            loading: true,
            selectedIds: new Set(),
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state"],
                { order: "create_date DESC", limit: 100 }
            );
        } finally {
            this.state.loading = false;
        }
    }

    toggleSelect(id) {
        if (this.state.selectedIds.has(id)) {
            this.state.selectedIds.delete(id);
        } else {
            this.state.selectedIds.add(id);
        }
        // Force reactivity for Set
        this.state.selectedIds = new Set(this.state.selectedIds);
    }
}

registry.category("actions").add("my_module.my_action", MyComponent);
```

## Migration from v16

### CRITICAL: attrs Migration
Every view using attrs MUST be updated:

```xml
<!-- v16 (BREAKS in v17) -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'required': [('state', '=', 'confirmed')],
               'readonly': [('state', '=', 'done')]}"/>

<!-- v17 (REQUIRED) -->
<field name="partner_id"
       invisible="state == 'draft'"
       required="state == 'confirmed'"
       readonly="state == 'done'"/>
```

### create Method
```python
# v16 style (still works in v17, logs a warning)
@api.model
def create(self, vals):
    return super().create(vals)

# v17 (correct form)
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

### Migration Steps
1. Search all XML files for `attrs=`
2. Convert each attrs to Python expressions
3. Update all create methods to model_create_multi
4. Test thoroughly

## Preparing for v18 Upgrade

### Upcoming Changes
- `check_access_rights()`/`check_access_rule()` deprecated in v18 -> `check_access()` / `has_access()`
- `self.env._` and `LazyTranslate` added in v18 (`_` / `_lt` still work)
- Single-dict `@api.model` create: warning in v17, DeprecationWarning in v18
- Type hints recommended

```python
# Already available in v17 (not new in v18; unchanged in master):
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # exists in v17

    partner_id = fields.Many2one(
        'res.partner',
        check_company=True,  # exists in v17
    )
# odoo.tools.SQL (SQL builder) also exists in v17
```

## Additional Rules from Odoo's Official Guidelines (verified for 17.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 17.0 source; master-only APIs are translated to the 17.0 equivalent or marked as not available.

### API availability in 17.0 vs master

| Topic | 17.0 | master/20.0 |
|-------|------|-------------|
| `sudo()` | `sudo(flag=True)` bool only; `with_user()` / `with_company()` | same |
| `_allow_sudo_commands`, `Command`, `related_sudo` (default True) | exist | same |
| SQL builder | `from odoo.tools import SQL`, `SQL.identifier()`, `_search()` returns `Query`, `query.select(SQL(...))` | same |
| Domain combination | `odoo.osv.expression.AND/OR/normalize_domain` | `odoo.fields.Domain` (absent in 17.0) |
| RPC guard | `get_public_method`: blocks `_` names and `@api.private` (exists) | also blocks classmethod/staticmethod |
| Route `type` | `'http'`, `'json'` | `http`, `jsonrpc`, `json2` |
| Route `auth` | `user`, `public`, `none` | + `bearer` |
| Route override without `@route` | auto-decorated with a warning | same |
| QWeb `t-out` / `t-esc` / `t-raw` | `t-out`; `t-esc` deprecated alias (works); `t-raw` deprecated (works, unescaped) | `t-raw` removed; server QWeb ignores `t-esc` |
| `_()` | frame-based `_("..%s", arg)`, escapes with `Markup` args; `_lt`; `tools.misc.format_list` for lists | `self.env._`, `LazyTranslate`, lists formatted automatically |
| `grouped()` | exists | same |
| `_read_group` | `_read_group(domain, groupby, aggregates)` -> list of tuples; `read_group()` still public | `formatted_read_group` |
| Constraints / indexes | `_sql_constraints`; field `index=True/'btree_not_null'/'trigram'`; multi-column index in `init()` | `models.Constraint/Index/UniqueIndex` (`_sql_constraints` ignored) |
| Restricted `odoo.tools.misc.pickle` | exists (still prefer JSON) | removed |
| `fields.NO_ACCESS`, `odoo.tools.consteq`, `file_open` confinement | exist | same |
| Access model | `ir.model.access` + `ir.rule`; no `base.group_everyone` | `ir.access` |
| Rule eval context | `user`, `time`, `company_ids`, `company_id` | similar (`allowed_company_ids` never available) |
| `<asset>` XML tag, `noupdate` on `<odoo>` | exist | same |
| `t-lang` without `t-call` | `SyntaxError` | same |
| Test default tags | `{'standard', 'at_install'}` (also for `HttpCase`) | `post_install` |
| `BaseCommon` | mail-disabled context + partner + currency, still superuser | adds non-admin user/company |
| Imported TestCase classes / inherited `test_*` methods | collected (run again) | skipped / opt-in |
| Owl | Owl 2: `markup`, `htmlEscape`; no `computed`; `patch(obj, ext)` | `computed` (Owl 3) |
| JS `@web/core/utils/html` | absent (use `escape` from `@web/core/utils/strings`) | exists |

### Master-only - do NOT use in 17.0

Every master/20.0 entry above that differs from 17.0 (`odoo.fields.Domain`, `models.Constraint/Index/UniqueIndex`, `self.env._`, `LazyTranslate`, `ir.access`, `auth='bearer'`, route types `jsonrpc`/`json2`, `formatted_read_group`, Owl `computed`, `@web/core/utils/html`), plus: `odoo.orm.domains`, `security/ir.access.csv`, `bearer_scope`, `setElementContent`, `htmlJoin`, `allow_inherited_tests_method`, `--unsafe-policy`, `allowed_company_ids` in record rule domains.

## Best Practices for v17

1. **NO attrs** - Always use Python expressions
2. **@api.model_create_multi** - For all create methods (single-dict create only warns, but do not write it)
3. **Use Command class** - For x2many operations
4. **Index important fields** - Use `index=True` or `index='trigram'`
5. **Use filtering** - `filtered()` with lambdas

## Manifest Structure

```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Module summary',
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/**/*.js',
            'my_module/static/src/**/*.xml',
            'my_module/static/src/**/*.scss',
        ],
    },
    'installable': True,
    'application': False,
}
```

- 17.0 adds no automatic `base` dependency (master injects it): list `base` in `depends` if needed.
- `license` defaults to LGPL-3 (with a warning) when missing.
- `auto_install` may be a list (a subset of `depends`).

## Common Issues

### attrs Error
```
Invalid XML: attrs attribute is no longer supported
```
Solution: Replace all attrs with invisible/readonly/required attributes

### create Method Warning
```
WARNING ... The model odoo.addons.my_module.models.my_model is not overriding the create method in batch
```
Solution: Use @api.model_create_multi with vals_list parameter (the single-dict form still works in v17)

### Expression Syntax
```xml
<!-- WRONG -->
invisible="[('state', '=', 'draft')]"

<!-- CORRECT -->
invisible="state == 'draft'"
```
