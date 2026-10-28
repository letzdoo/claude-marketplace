# Odoo Module Generator - Version 14.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ODOO 14.0 MODULE GENERATION PATTERNS                                        ║
║  This file contains ONLY Odoo 14.0 specific patterns.                        ║
║  DO NOT use these patterns for other versions.                               ║
║  Note: v14 is LEGACY - consider upgrading to v17+ for new projects.          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version 14.0 Requirements

- **Python**: 3.6+ required, 3.8 recommended
- **Key Features**: no `@api.multi` (removed in 13.0); field tracking with `tracking=True`; `create` is `@api.model_create_multi`
- **View syntax**: `attrs` for visibility/readonly
- **Frontend**: legacy widgets (`odoo.define`); Owl 1.4.11 is bundled but not the main framework

## IMPORTANT: Legacy Version Notes

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  v14 is END OF LIFE (October 2023)                                           ║
║  Only use for maintaining existing modules.                                  ║
║  For new projects, use v17+ with modern patterns.                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## __manifest__.py Template (v14)

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '14.0.1.0.0',
    'category': '{Category}',
    'summary': '{Short description}',
    'description': """
{Detailed description}
    """,
    'author': '{Author}',
    'website': '{Website}',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        # ORDER IS CRITICAL
        'security/{module_name}_security.xml',
        'security/ir.model.access.csv',
        'views/{model_name}_views.xml',
        'views/menuitems.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### Manifest facts (14.0)
- `depends`: list direct dependencies only. 14.0 does NOT inject `base` when `depends` is empty; `base` is always loaded first, so list `'base'` only when there is no other dependency.
- `license` defaults to `'LGPL-3'` when omitted (declare it anyway).
- `auto_install` may be `True` (all depends) or a list that must be a subset of `depends`.
- `application`: only for full apps (default `False`). `external_dependencies`: `{'python': [...], 'bin': [...]}`, checked at install.
- NO `assets` key in 14.0. Static files go in via an XML data file that inherits the bundle template:
  ```xml
  <template id="assets_backend" inherit_id="web.assets_backend" name="my_module assets">
      <xpath expr="." position="inside">
          <script type="text/javascript" src="/my_module/static/src/js/my_widget.js"/>
          <link rel="stylesheet" type="text/scss" href="/my_module/static/src/scss/my_module.scss"/>
      </xpath>
  </template>
  ```
  Client-side QWeb templates are listed in the manifest key `'qweb': ['static/src/xml/my_templates.xml']`.
- Data file tags in 14.0: `record`, `template`, `menuitem`, `report`, `act_window`, `function`, `delete`. There is no `<asset>` tag. `noupdate="1"` works on `<odoo>` and on `<data>`. `<template active="False">` is applied only on install, not on update.

## Model Template (v14)

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class {ModelName}(models.Model):
    _name = '{module_name}.{model_name}'
    _description = '{Model Description}'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # === BASIC FIELDS === #
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,  # v14: valid parameter on mail.thread models
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    # === RELATIONAL FIELDS === #
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name='{module_name}.{model_name}.line',
        inverse_name='parent_id',
        string='Lines',
        copy=True,
    )

    # === SELECTION FIELDS === #
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )

    # === COMPUTED FIELDS === #
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    # === CRUD METHODS (v14 style) === #
    @api.model_create_multi
    def create(self, vals_list):
        """Batch create - BaseModel.create is model_create_multi in v14."""
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    '{module_name}.{model_name}'
                ) or _('New')
        return super().create(vals_list)

    # === x2many OPERATIONS - v14: Use tuple syntax === #
    def action_add_line(self):
        """Use tuple syntax for x2many operations in v14."""
        self.write({
            'line_ids': [
                (0, 0, {'name': 'New Line', 'amount': 0}),  # Create new
            ]
        })

    def action_update_lines(self):
        """Tuple command reference for v14."""
        self.write({
            'line_ids': [
                (0, 0, {'name': 'New'}),        # Create new record
                (1, line_id, {'name': 'Upd'}),  # Update existing
                (2, line_id),                   # Delete from DB
                (3, line_id),                   # Remove from relation
                (4, line_id),                   # Link existing
                (5, 0, 0),                      # Clear all
                (6, 0, [id1, id2]),             # Replace with these
            ]
        })

    # === ACTION METHODS === #
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
```

## View Templates (v14 - attrs syntax)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <!-- v14: Use attrs for visibility -->
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary"
                            attrs="{'invisible': [('state', '!=', 'draft')]}"/>
                    <button name="action_done" string="Done" type="object"
                            attrs="{'invisible': [('state', '!=', 'confirmed')]}"/>
                    <button name="action_cancel" string="Cancel" type="object"
                            attrs="{'invisible': [('state', 'in', ('done', 'cancelled'))]}"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
                    <widget name="web_ribbon" title="Archived" bg_color="bg-danger"
                            attrs="{'invisible': [('active', '=', True)]}"/>
                    <div class="oe_title">
                        <h1><field name="name" placeholder="Name..."/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="partner_id"/>
                            <field name="user_id"/>
                        </group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="total_amount"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids">
                                <tree editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="amount"/>
                                </tree>
                            </field>
                        </page>
                    </notebook>
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

## Security Templates (v14)

### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_name}_user,{model_name}.user,model_{module_name}_{model_name},{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_manager,{model_name}.manager,model_{module_name}_{model_name},{module_name}.group_{module_name}_manager,1,1,1,1
```

### Record Rules (v14 - uses company_ids)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Multi-Company Rule - v14 syntax -->
    <record id="rule_{model_name}_company" model="ir.rule">
        <field name="name">{Model Name}: Multi-Company</field>
        <field name="model_id" ref="model_{module_name}_{model_name}"/>
        <!-- no groups = global rule ('global' is computed from 'groups') -->
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
        ]</field>
    </record>
</odoo>
```

## v14 Patterns Reference

### Field Tracking (v14 syntax)
```python
# v14: 'tracking' is the valid parameter (model must inherit mail.thread)
name = fields.Char(tracking=True)
state = fields.Selection([...], tracking=True)
# track_visibility='onchange' is legacy: still tracked, but logs "unknown parameter"
```

### x2many Commands (v14 tuple syntax)
```python
# v14: Tuple syntax
(0, 0, values)      # Create
(1, id, values)     # Update
(2, id)             # Delete
(3, id)             # Unlink
(4, id)             # Link
(5, 0, 0)           # Clear
(6, 0, [ids])       # Set
```

### View Visibility (v14 attrs)
```xml
<!-- v14: attrs with domain syntax -->
<field name="x" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
<field name="y" attrs="{'readonly': [('state', '!=', 'draft')],
                        'required': [('type', '=', 'invoice')]}"/>
```

## Additional Rules from Odoo's Official Guidelines (verified for 14.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 14.0 source; master-only APIs are translated to the 14.0 equivalent or marked as not available.

### File structure and naming
- One model per file, named after the model: `models/my_model.py`. Views go in `views/my_model_views.xml`, `views/my_module_menus.xml`, `views/my_module_templates.xml`; data in `data/my_module_data.xml`; demo in `demo/my_module_demo.xml`; security in `security/ir.model.access.csv` + `security/my_module_security.xml`.
- Controllers: feature-named files (or `<inherited_module>.py`); `main.py` is legacy.
- Reports: SQL-view models in `report/<model>_report.py`; printable reports split into `<model>_reports.xml` (actions) and `<model>_templates.xml` (QWeb).
- XML ids: `<model>_view_form`, `<model>_view_tree`, `<model>_action`, `<model>_menu`, `<module>_group_<name>`, `<model>_rule_<group>`. Inheriting views use the same prefix + `.inherit.<detail>`; `mode="primary"` (or `<template primary="True">`) for a new primary view.
- Model `_name`: dotted, module-prefixed, singular (`my_module.order`, not `orders`). Wizards: `<base_model>.<action>`; SQL reports: `<base_model>.report.<action>`.
- Method prefixes: `_compute_`, `_inverse_`, `_search_`, `_default_`, `_selection_`, `_onchange_`, `_check_` (constraints), `action_*` (start with `self.ensure_one()` when single-record). Keep methods private (`_`) unless they must be RPC-callable.
- Class body order: private attributes (`_name`, `_description`, `_inherit`, `_order`, `_sql_constraints`) -> default methods -> fields -> compute/inverse/search -> selection -> constrains/onchange -> CRUD overrides -> actions -> business methods.
- Imports: stdlib / third-party / `from odoo import _, api, fields, models` / `from odoo.addons...` (no `Command` in 14.0).

### Generated tests (14.0)
```python
from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestMyModel(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})

    def test_create(self):
        record = self.env['my_module.my_model'].create({'name': 'X', 'partner_id': self.partner.id})
        self.assertEqual(record.state, 'draft')
```
- Default tags are `standard` + `at_install`. For post-install tests (always for `HttpCase`/tours) use `@tagged('post_install', '-at_install')`. Set exactly one of the two: both -> the test runs twice, neither -> it never runs.
- Class-level fixtures need `SavepointCase`. `TransactionCase` creates its env in `setUp` (no `cls.env` in 14.0). There is no `BaseCommon`; use `TransactionCaseWithUserDemo` / `SavepointCaseWithUserDemo` (`odoo.addons.base.tests.common`) or `odoo.tests.common.new_test_user`.
- Test files must be named `test_*.py` AND imported in `tests/__init__.py`. Never import a concrete test class into another test file: it is collected again and runs twice. Inherited `test_*` methods also run.
- Use `from odoo.tools import mute_logger` around expected error logs. Use `assertQueryCount` only in dedicated performance tests with `@warmup` (and `@users`).
- Run one class: `--test-tags /my_module:TestMyModel`.

## v14 Checklist

When generating a v14 module:

- [ ] Use `tracking=True` for field tracking (`track_visibility` is legacy and logs a warning)
- [ ] Use tuple syntax for x2many operations (NOT `Command`)
- [ ] Use `attrs` for view visibility
- [ ] Use `@api.model_create_multi` `create(vals_list)` overrides
- [ ] Use `company_ids` in record rules (NOT `allowed_company_ids`)
- [ ] No manifest `assets` key (asset templates in XML, JS QWeb in `'qweb'`)
- [ ] Data files in correct order in manifest

## Migration Note

To upgrade this module to v15+:
1. Move JS/SCSS asset templates and the `'qweb'` key to the 15.0 `assets` manifest key
2. Read `odoo-module-generator-14-15.md` for full migration guide

## AI Agent Instructions (v14)

When generating an Odoo 14.0 module:

1. **USE** `tracking=True` for tracked fields (model inherits `mail.thread`)
2. **USE** tuple syntax `(0, 0, {...})` for x2many
3. **USE** `attrs` in views for visibility/readonly
4. **USE** `company_ids` in record rules
5. **DO NOT** use `Command` class (15.0+)
6. **DO NOT** use `@api.multi` (removed - fails in 14.0)
7. **DO NOT** use direct `invisible`/`readonly` (v17+)
8. **PREFER** legacy widgets (`odoo.define`); Owl 1.4.11 exists but has no `markup`/`htmlEscape`
