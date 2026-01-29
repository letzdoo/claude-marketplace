---
name: odoo-development
description: |
  MUST be loaded when ANY Odoo development task is detected.
  CRITICAL: Claude MUST use this skill for ALL tasks involving:
  - "odoo", "module", "model", "view", "field", "OWL", "manifest"
  - ANY mention of Odoo versions (14, 15, 16, 17, 18, 19)
  - "create odoo module", "generate odoo code", "review odoo module"
  - "upgrade odoo", "odoo best practices", "odoo security"

  ALWAYS trigger the odoo-context-gatherer agent BEFORE writing ANY Odoo code.
---

# Odoo Development Skill Index

> **CRITICAL**: Before writing ANY Odoo code, Claude MUST invoke the
> `odoo-context-gatherer` agent to compile relevant patterns for the task.
>
> **MANDATORY WORKFLOW**:
> 1. Detect/confirm Odoo version (NEVER skip)
> 2. Invoke `odoo-development:odoo-context-gatherer` agent with task description
> 3. Use returned context patterns for code generation
> 4. NEVER skip step 2 - context gathering is REQUIRED

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  BEFORE generating Odoo code, you MUST:                                      ║
║  1. Determine the target Odoo version                                        ║
║  2. Invoke odoo-context-gatherer agent with task description                 ║
║  3. Use the patterns returned by the agent                                   ║
║                                                                              ║
║  DO NOT generate Odoo code without context from the agent.                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

> **Usage**: This is a lightweight discovery index. DO NOT read full skill files unless needed.
> Use `Read` tool on specific file paths only when you need the detailed pattern.

## Quick Reference (Copy-Paste Ready)

### Field Declarations
```python
# Basic fields
name = fields.Char(required=True)
active = fields.Boolean(default=True)
sequence = fields.Integer(default=10)
amount = fields.Float(digits=(16, 2))
date = fields.Date(default=fields.Date.today)
note = fields.Text()
html_content = fields.Html()

# Relational
partner_id = fields.Many2one('res.partner', ondelete='cascade')
tag_ids = fields.Many2many('my.tag', string='Tags')
line_ids = fields.One2many('my.line', 'parent_id')

# Computed
total = fields.Float(compute='_compute_total', store=True)
@api.depends('line_ids.amount')
def _compute_total(self):
    for rec in self:
        rec.total = sum(rec.line_ids.mapped('amount'))
```

### Model Declaration
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'
```

### View Visibility (v17+ vs v14-16)
```xml
<!-- v17+: direct attribute -->
<field name="x" invisible="state != 'draft'"/>
<field name="y" readonly="is_locked"/>

<!-- v14-16: attrs dict -->
<field name="x" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

---

## Skill Discovery Index

| Intent / Keywords | Skill File | Description |
|-------------------|------------|-------------|
| fields, char, many2one, one2many, selection | `skills/field-type-reference.md` | All field types with attributes |
| computed, depends, inverse, search | `skills/computed-field-patterns.md` | Computed field patterns |
| constraint, validation, check | `skills/constraint-patterns.md` | SQL and Python constraints |
| onchange, dynamic, domain | `skills/onchange-dynamic-patterns.md` | Form field dynamics |
| view, form, tree, kanban, search | `skills/xml-view-patterns.md` | XML view patterns |
| widget, statusbar, badge, image | `skills/widget-field-patterns.md` | Field widgets |
| qweb, template, t-if, t-foreach | `skills/qweb-template-patterns.md` | QWeb templating |
| action, window, server, client | `skills/action-patterns.md` | Action patterns |
| menu, navigation, menuitem | `skills/menu-navigation-patterns.md` | Menu structure |
| security, access, rule, group | `skills/odoo-security-guide.md` | Security configuration |
| workflow, state, statusbar, approval | `skills/workflow-state-patterns.md` | State machines |
| wizard, transient, dialog | `skills/wizard-patterns.md` | Wizard patterns |
| report, pdf, qweb, print | `skills/report-patterns.md` | PDF reports |
| cron, scheduled, automation | `skills/cron-automation-patterns.md` | Scheduled actions |
| controller, http, api, rest, json | `skills/controller-api-patterns.md` | HTTP controllers |
| mail, email, chatter, activity | `skills/mail-notification-patterns.md` | Mail integration |
| multi-company, company, currency | `skills/multi-company-patterns.md` | Multi-company |
| inherit, extend, override | `skills/inheritance-patterns.md` | Model/view inheritance |
| migration, upgrade, version | `skills/data-migration-patterns.md` | Data migration |
| website, portal, public | `skills/website-integration-patterns.md` | Website integration |
| external, api, webhook, sync | `skills/external-api-patterns.md` | External APIs |
| logging, debug, error | `skills/logging-debugging-patterns.md` | Logging/debugging |
| stock, inventory, warehouse, move | `skills/stock-inventory-patterns.md` | Stock operations |
| account, invoice, journal, payment | `skills/accounting-patterns.md` | Accounting |
| sale, order, quotation, crm, lead | `skills/sale-crm-patterns.md` | Sales/CRM |
| hr, employee, contract, leave | `skills/hr-employee-patterns.md` | HR patterns |
| domain, filter, search, operator | `skills/domain-filter-patterns.md` | Search domains |
| sequence, number, reference | `skills/sequence-numbering-patterns.md` | Auto-numbering |
| purchase, vendor, procurement | `skills/purchase-procurement-patterns.md` | Purchasing |
| project, task, timesheet | `skills/project-task-patterns.md` | Project management |
| context, env, sudo, with_context | `skills/context-environment-patterns.md` | Environment/context |
| exception, error, validation | `skills/error-handling-patterns.md` | Error handling |
| portal, token, access, share | `skills/portal-access-patterns.md` | Portal access |
| dashboard, kpi, analytics, graph | `skills/dashboard-kpi-patterns.md` | Dashboards |
| settings, config, parameter | `skills/config-settings-patterns.md` | Module settings |
| translation, i18n, language | `skills/translation-i18n-patterns.md` | Translations |
| assets, js, css, scss, bundle | `skills/assets-bundling-patterns.md` | Asset bundling |
| variant, attribute, product | `skills/product-variant-patterns.md` | Product variants |
| pricelist, price, discount | `skills/pricelist-pricing-patterns.md` | Pricing |
| uom, unit, measure, conversion | `skills/uom-patterns.md` | Units of measure |
| lot, serial, batch, expiry | `skills/lot-serial-patterns.md` | Lot/serial tracking |
| import, export, csv, excel | `skills/import-export-patterns.md` | Data import/export |
| tax, fiscal, vat | `skills/tax-fiscal-patterns.md` | Tax configuration |
| owl, component, frontend, javascript | `skills/odoo-owl-components.md` | OWL components |
| test, unittest, integration | `skills/odoo-test-patterns.md` | Testing |
| performance, optimize, index | `skills/odoo-performance-guide.md` | Performance |
| manifest, module, depends | `skills/odoo-module-generator.md` | Module structure |
| version, 14, 15, 16, 17, 18, 19 | `skills/odoo-version-knowledge.md` | Version differences |
| binary, attachment, file, image | `skills/attachment-binary-patterns.md` | File handling |

---

## Version-Specific Patterns

For version-specific code, check these skill files:
- `skills/odoo-version-knowledge.md` - Breaking changes by version
- `skills/odoo-owl-components.md` - OWL 1.x (v15) / 2.x (v16-18) / 3.x (v19)
- Version-specific files: `skills/{pattern}-{version}.md`

## How to Use This Index

1. **Identify keywords** from user's request
2. **Find matching row** in the index table
3. **Read only the specific skill file** using `Read` tool
4. **Use patterns** from that file
5. **Don't preload** - only load what you need

Example:
```
User: "Create a computed field that sums order lines"
→ Keywords: computed, depends
→ Read: skills/computed-field-patterns.md
→ Use the pattern, don't keep file in context
```
