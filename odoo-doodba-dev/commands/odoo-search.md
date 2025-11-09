---
description: Fast unified search for Odoo codebase using the indexer (models, fields, views, actions, menus)
---

# Odoo Code Search

Search your Odoo codebase with lightning-fast queries using the indexer. Get information about models, fields, views, actions, menus, and more in <100ms.

## Your Role

You help users search and explore the Odoo codebase using the indexer. Interpret natural language queries and translate them into indexer commands.

---

## Search Capabilities

The indexer can search for:
- **Models**: All Odoo models with their fields and methods
- **Fields**: Field definitions with types and relationships
- **Views**: Form, list, search views with inheritance
- **Actions**: Window actions, server actions, client actions
- **Menus**: Menu structure and hierarchy
- **XML IDs**: All XML ID references
- **Modules**: List and analyze modules

**Speed**: <50ms for most queries
**Efficiency**: 95% fewer tokens than reading files

---

## Common Query Patterns

### Pattern 1: "What is {model}?"

**User**: "What is sale.order?"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/get_details.py model "sale.order"
```

**Response Format**:
```markdown
**Model**: `sale.order`
**Module**: sale
**Description**: Sales Order

**Inherits**:
- mail.thread
- mail.activity.mixin
- portal.mixin

**Key Fields** ({X} total):
- `name` (Char, required) - Order Reference
- `partner_id` (Many2one → res.partner, required) - Customer
- `order_line` (One2many → sale.order.line) - Order Lines
- `amount_total` (Monetary, computed, stored) - Total Amount
- `state` (Selection) - Status: draft|sent|sale|done|cancel
- `date_order` (Datetime) - Order Date
- `user_id` (Many2one → res.users) - Salesperson

**Views** ({Y} total):
- sale.view_order_form (form)
- sale.view_quotation_tree (list)
- sale.view_sales_order_filter (search)
- [... more]

**Actions**:
- sale.action_quotations
- sale.action_orders

**Location**: `odoo/custom/src/sale/models/sale_order.py`
**Lines**: 450

Query time: 28ms
```

---

### Pattern 2: "What fields does {model} have?"

**User**: "What fields does res.partner have?"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/get_details.py model "res.partner"
```

**Response Format** (focus on fields):
```markdown
**res.partner** has **{X}** fields:

**Contact Information**:
- `name` (Char, required) - Name
- `email` (Char) - Email
- `phone` (Char) - Phone
- `mobile` (Char) - Mobile

**Address**:
- `street` (Char) - Street
- `city` (Char) - City
- `zip` (Char) - Zip
- `country_id` (Many2one → res.country) - Country

**Relationships**:
- `parent_id` (Many2one → res.partner) - Related Company
- `child_ids` (One2many → res.partner) - Contacts
- `user_ids` (One2many → res.users) - Users

**Categorization**:
- `category_id` (Many2many → res.partner.category) - Tags

[Full list: {X} fields total]

Use specific field search for details on a particular field.
```

---

### Pattern 3: "Find {search_term}"

**User**: "Find all Many2one fields in sale module"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/search_by_attr.py field \
  --filters '{"field_type": "Many2one"}' \
  --module sale
```

**Response Format**:
```markdown
Found **{X}** Many2one fields in sale module:

**sale.order**:
- partner_id → res.partner
- user_id → res.users
- team_id → crm.team
- company_id → res.company
- pricelist_id → product.pricelist

**sale.order.line**:
- order_id → sale.order
- product_id → product.product
- product_uom → uom.uom

[... more]

Total: {X} Many2one fields
Query time: 45ms
```

---

### Pattern 4: "Search for {element}"

**User**: "Search for project task views"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/search.py "%task%" --type view --module project --limit 20
```

**Response Format**:
```markdown
Found **{X}** views for project tasks:

**Form Views**:
- project.view_task_form2 (project.task)
- project.view_task_form_simplified (project.task)

**List Views**:
- project.view_task_tree2 (project.task)

**Search Views**:
- project.view_task_search_form (project.task)

**Kanban Views**:
- project.view_task_kanban (project.task)

**Calendar Views**:
- project.view_task_calendar (project.task)

[... more]

Use get_details to see view contents.
Query time: 32ms
```

---

### Pattern 5: "Where is {element} defined?"

**User**: "Where is project.task defined?"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/search.py "project.task" --type model
```

**Response Format**:
```markdown
**project.task** is defined in:

**Module**: project
**File**: `odoo/custom/src/project/models/project_task.py`
**Lines**: 850-1245

**Defined Fields**: 67
**Inherited From**:
- mail.thread
- mail.activity.mixin
- portal.mixin
- rating.mixin

**Extended By** (other modules):
- project_enterprise (5 fields added)
- hr_timesheet (8 fields added)
- sale_project (3 fields added)

Use get_details for full field list.
```

---

### Pattern 6: "Show me {specific_field} in {model}"

**User**: "Show me partner_id in sale.order"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/get_details.py field "partner_id" --parent "sale.order"
```

**Response Format**:
```markdown
**Field**: `partner_id` in `sale.order`

**Type**: Many2one
**Comodel**: res.partner
**Attributes**:
- Required: Yes
- Tracking: Yes
- String: "Customer"
- Domain: [('customer_rank', '>', 0)]
- Context: {'show_address': 1}

**Defined In**:
- Module: sale
- File: `models/sale_order.py`
- Line: 125

**Used In Views** ({X} views):
- sale.view_order_form (visible)
- sale.view_quotation_tree (visible)
- sale.view_sales_order_filter (searchable)

**Related Fields**:
- partner_shipping_id (Many2one → res.partner) - Delivery Address
- partner_invoice_id (Many2one → res.partner) - Invoice Address
```

---

### Pattern 7: "List modules"

**User**: "List all modules" or "What modules do I have?"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/list_modules.py
```

**Response Format**:
```markdown
Found **{X}** indexed modules:

**Core Modules**:
- base ({Y} models, {Z} views)
- mail ({Y} models, {Z} views)
- web ({Y} models, {Z} views)

**Business Modules**:
- sale ({Y} models, {Z} views)
- purchase ({Y} models, {Z} views)
- account ({Y} models, {Z} views)
- stock ({Y} models, {Z} views)
- project ({Y} models, {Z} views)

**Custom Modules** (odoo/custom/src/private):
- my_custom_module ({Y} models, {Z} views)

[... full list]

Use module stats for detailed info:
uv run scripts/module_stats.py module_name
```

---

### Pattern 8: "Module info {module}"

**User**: "Tell me about the sale module"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/module_stats.py sale
```

**Response Format**:
```markdown
**Module**: sale

**Statistics**:
- Models: {X}
- Fields: {Y}
- Views: {Z}
- Actions: {N}
- Menus: {M}

**Main Models**:
- sale.order (Sales Order) - {F} fields
- sale.order.line (Sales Order Line) - {F} fields
- sale.order.template (Quotation Template) - {F} fields

**Dependencies**:
- base, product, account, portal, mail, web

**Dependents** (modules that depend on this):
- sale_management, sale_stock, sale_project, sale_crm

**Location**: `odoo/custom/src/sale/`
**Indexed**: Yes
**Last Updated**: [from index]
```

---

### Pattern 9: "Find XML ID {xml_id}"

**User**: "Find action_view_task"

**Action**:
```bash
uv run skills/odoo-indexer/scripts/search_xml_id.py "action_view_task"
```

**Response Format**:
```markdown
Found **{X}** XML IDs matching "action_view_task":

1. **project.action_view_task**
   - Type: ir.actions.act_window
   - Model: project.task
   - View Mode: list,form,calendar,pivot,graph,activity
   - Module: project
   - File: `views/project_views.xml`

2. **project_enterprise.action_view_task_from_milestone**
   - Type: ir.actions.act_window
   - Model: project.task
   - Module: project_enterprise

Use with ref(): `ref('project.action_view_task')`
```

---

### Pattern 10: "How does {feature} work?"

**User**: "How does sale order confirmation work?"

**Action** (multi-step):
```bash
# 1. Find the model
uv run skills/odoo-indexer/scripts/get_details.py model "sale.order"

# 2. Look for confirm methods
grep -n "def.*confirm" from results
```

**Response Format**:
```markdown
**Sale Order Confirmation** (`sale.order.action_confirm`):

**Method**: `action_confirm()`
**Location**: `odoo/custom/src/sale/models/sale_order.py:450`

**What it does**:
1. Validates order (check required fields)
2. Changes state: draft → sale
3. Creates procurement orders (if sale_stock installed)
4. Sends confirmation email (if configured)
5. Posts message in chatter
6. Triggers webhook (if configured)

**Related Methods**:
- `_action_confirm()` - Internal confirmation logic
- `_prepare_confirmation_values()` - Prepare values
- `_create_procurement()` - Create procurements

**State Transitions**:
- draft → sent (action_quotation_send)
- draft → sale (action_confirm)
- sale → done (action_done)
- any → cancel (action_cancel)

**To confirm an order**:
```python
order = env['sale.order'].browse(order_id)
order.action_confirm()
```
```

---

## Query Interpretation

Translate natural language to indexer commands:

### Type Mapping

| User Says | Indexer Type |
|-----------|--------------|
| "model", "object", "table" | `model` |
| "field", "column" | `field` |
| "view", "form", "list", "tree" | `view` |
| "action", "button action" | `action` |
| "menu", "navigation" | `menu` |
| "XML ID", "reference" | (use search_xml_id.py) |

### Search Strategy

**Exact match**: Use get_details.py
```bash
uv run scripts/get_details.py model "sale.order"
```

**Partial match**: Use search.py with wildcards
```bash
uv run scripts/search.py "%order%" --type model
```

**Attribute filter**: Use search_by_attr.py
```bash
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one"}'
```

---

## Response Guidelines

### Be Concise But Complete

**Good**:
```
sale.order has 127 fields.

Key fields:
- partner_id (Many2one → res.partner) - Customer
- order_line (One2many → sale.order.line) - Lines
- amount_total (Monetary, computed) - Total

[Show top 10, mention "X more fields"]
```

**Not Good** (too verbose):
```
The sale.order model, which is defined in the sale module and represents...
[500 words of explanation]
```

### Highlight Important Info

Use **bold** for:
- Field names
- Model names
- Key attributes

Use `code` for:
- Technical values
- File paths
- Commands

### Provide Next Steps

Always suggest related searches:
```
Found sale.order model.

Related searches:
- Get field details: "Show me partner_id in sale.order"
- Find views: "Search for sale order views"
- See methods: "How does sale order confirmation work?"
```

### Handle "Not Found"

If indexer returns no results:

```
❌ Not found: "custom.model"

Possible reasons:
1. Model doesn't exist
2. Typo in name (did you mean "sale.order"?)
3. Module not installed/indexed

Suggestions:
- List all models: "Find all models"
- Search similar: "Find %custom%"
- Update index: `uv run scripts/update_index.py`
```

---

## Advanced Searches

### Cross-Reference Search

**User**: "Find all models that reference res.partner"

```bash
uv run skills/odoo-indexer/scripts/search_by_attr.py field \
  --filters '{"field_type": "Many2one", "comodel_name": "res.partner"}'
```

### Inheritance Search

**User**: "Find all models that inherit mail.thread"

```bash
# Search for models, then filter by inheritance
uv run skills/odoo-indexer/scripts/search.py "%" --type model | \
  # Check each for mail.thread inheritance
```

### Module Dependency Tree

**User**: "What modules depend on sale?"

```bash
uv run skills/odoo-indexer/scripts/module_stats.py sale
# Look for "Dependents" section
```

---

## Performance Tips

### Use Specific Queries

**Fast** (exact match):
```bash
uv run scripts/get_details.py model "sale.order"  # <20ms
```

**Slower** (wildcard search):
```bash
uv run scripts/search.py "%" --type model  # <100ms but returns many results
```

### Limit Results

Always use `--limit` for broad searches:
```bash
uv run scripts/search.py "%order%" --type model --limit 10
```

### Cache Results

For repeated searches, mention caching:
```
I've already searched for sale.order models.
From previous results: [cached data]
```

---

## Troubleshooting

### Index Out of Date

If results seem wrong:
```
The index may be out of date.

Update with:
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py
```

### Module Not Found

If module not in index:
```
Module "custom_module" not indexed.

Check:
1. Is it in odoo/custom/src/?
2. Has index been built?
3. Run: uv run scripts/update_index.py
```

### Slow Queries

If query takes >1 second:
```
Query taking longer than expected.

Possible causes:
1. Very broad search (use --limit)
2. Index corruption (rebuild: update_index.py --full)
3. Database file too large (check index_status.py)
```

---

## Examples

### Example 1: Quick Field Lookup

**User**: "What type is partner_id in sale.order?"

```
🔍 Searching...

`partner_id` in `sale.order`:
- Type: Many2one
- Comodel: res.partner
- Required: Yes
- String: "Customer"

Query: 15ms
```

### Example 2: Model Overview

**User**: "Tell me about project.task"

```
🔍 Searching...

**project.task** (Project Task)

Module: project
Fields: 67
Views: 12 (form, list, kanban, calendar, pivot, graph, activity, search, map, cohort, gantt, timeline)

Key Fields:
- name (Char, required) - Task Title
- project_id (Many2one → project.project, required)
- user_ids (Many2many → res.users) - Assignees
- stage_id (Many2one → project.task.type)
- priority (Selection) - Priority

Location: `project/models/project_task.py`
Query: 28ms
```

### Example 3: Find Related

**User**: "Find all One2many fields in sale.order"

```
🔍 Searching...

One2many fields in `sale.order`:

- order_line → sale.order.line (Order Lines)
- invoice_ids → account.move (Invoices)
- picking_ids → stock.picking (Deliveries)
- activity_ids → mail.activity (Activities)
- message_ids → mail.message (Messages)

Total: 12 One2many fields
Query: 34ms
```

---

## Critical Rules

### Always Use Indexer
- **NEVER** read files directly for searches
- **ALWAYS** use indexer scripts
- 95% faster, 95% fewer tokens

### Format Results Clearly
- Show most relevant info first
- Limit long lists (top 10 + "X more")
- Provide follow-up suggestions

### Be Accurate
- Show exact field types
- Include module prefix for XML IDs
- Report query time

### Handle Errors Gracefully
- "Not found" → Suggest alternatives
- Slow query → Suggest optimization
- Ambiguous → Ask for clarification

---

**Remember**: The indexer is your superpower - use it for every search to give instant, accurate results!
