# Usage Guide - Odoo Doodba Dev Plugin v2.0

Practical examples and workflows for the Odoo Doodba Development Plugin.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Quick Mode Examples](#quick-mode-examples)
3. [Full Mode Examples](#full-mode-examples)
4. [Search Mode Examples](#search-mode-examples)
5. [Common Workflows](#common-workflows)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First Time Setup

```bash
# 1. Install plugin
/plugin install odoo-doodba-dev@letzdoo

# 2. Run setup (automatic)
/odoo-setup

# 3. Start developing!
/odoo-dev "your first task"
```

**Time**: 5-10 minutes total

---

### Your First Task

Let's add a simple field to an existing model:

```bash
/odoo-dev "add notes field (Text) to res.partner"
```

**What happens**:
```
🎯 Quick Mode detected (simple task)

💻 Analyzing...
   ✓ Model res.partner found
   ✓ Field name available

📐 Architecture:
   Extend: res.partner (base module)
   Add field: notes (Text)
   Update: partner form view

   Proceed? y

💻 Implementing...
   ✓ Field added to model
   ✓ View updated
   ✓ Validated with indexer

🧪 Verifying...
   ✓ Structure valid
   ✓ 2/2 tests passed

✅ Complete! (6 minutes)

Files modified:
- odoo/custom/src/odoo-sh/partner_notes/models/res_partner.py
- odoo/custom/src/odoo-sh/partner_notes/views/res_partner_views.xml

Install: invoke install -m partner_notes
```

**That's it!** You just completed your first development task.

---

## Quick Mode Examples

Quick Mode is for simple tasks: adding fields, minor view changes, small extensions.

### Example 1: Add Single Field

**Task**: Add priority field to project.task

```bash
/odoo-dev "add priority (Selection) to project.task with values: low, normal, high, urgent"
```

**Result**:
- Field added to model
- Form view updated
- List view updated
- Tests generated
- **Time**: 5-7 minutes

---

### Example 2: Add Many2one Field

**Task**: Add responsible person to project.task

```bash
/odoo-dev "add responsible_id (Many2one to res.users) to project.task"
```

**Claude will**:
1. Validate res.users exists ✓
2. Add field with proper naming (_id)
3. Update views
4. Add to search filters
5. Create tests

**Time**: 6-8 minutes

---

### Example 3: Add Computed Field

**Task**: Add total hours field to project.task

```bash
/odoo-dev "add total_hours (Float, computed from timesheet_ids) to project.task, store=True"
```

**Claude will**:
1. Research timesheet_ids field
2. Create computed field with @api.depends
3. Add to views
4. Test computation
5. Test edge cases

**Time**: 7-10 minutes

---

### Example 4: Modify View

**Task**: Add field to existing view

```bash
/odoo-dev "add my_custom_field to sale.order form view after partner_id"
```

**Claude will**:
1. Find correct view to inherit
2. Validate XML ID
3. Add xpath for insertion
4. Validate field exists
5. Test view loads

**Time**: 5-6 minutes

---

### Example 5: Add Menu Item

**Task**: Add menu for custom model

```bash
/odoo-dev "add menu item for quality.check model under Quality main menu"
```

**Claude will**:
1. Create action
2. Create menu with proper parent
3. Set sequence
4. Validate menu structure

**Time**: 4-5 minutes

---

## Full Mode Examples

Full Mode is for complex features: new modules, multiple models, workflows.

### Example 1: New Module with Single Model

**Task**: Create equipment tracking module

```bash
/odoo-dev "create equipment_tracking module to track company equipment with fields: name, serial_number, purchase_date, assigned_to (res.users), status (draft/in_use/maintenance/retired)"
```

**Workflow**:

**Step 1: Architecture Discussion**
```
🎯 Full Mode detected (new module)

🔍 Researching codebase...
   ✓ Checked existing equipment modules
   ✓ Validated dependencies

📐 Architecture Proposal:

**Module**: equipment_tracking
**Location**: odoo/custom/src/odoo-sh/equipment_tracking

**Models**:
1. equipment.tracking
   - name (Char, required)
   - serial_number (Char, required, unique)
   - purchase_date (Date)
   - assigned_to_id (Many2one → res.users)
   - status (Selection: draft/in_use/maintenance/retired)
   - notes (Text)

**Views**:
- List view (name, serial_number, assigned_to, status)
- Form view (all fields, with statusbar)
- Search view (filters by status, assigned_to)
- Kanban view (grouped by status)

**Security**:
- User: read, create
- Manager: all permissions

**Dependencies**: base, mail

**Validation**: ✓ All dependencies available

Proceed with this architecture? y
```

**Step 2: Implementation**
```
💻 Implementing...

Phase 1: Models
   ✓ Created equipment.tracking model
   ✓ Added 6 fields
   ✓ Added state workflow methods
   ✓ Validated all references

Phase 2: Views
   ✓ Created list view
   ✓ Created form view with statusbar
   ✓ Created search view with filters
   ✓ Created kanban view

Phase 3: Security
   ✓ Created access rights (user, manager)
   ✓ Added record rules

Phase 4: Data
   ✓ Created demo data
   ✓ Created default statuses

Phase 5: Tests
   ✓ Created 8 comprehensive tests
```

**Step 3: Verification**
```
🧪 Verifying...
   ✓ Structure valid
   ✓ All references validated
   ✓ 8/8 tests passed

✅ Complete! (22 minutes)
```

**Step 4: Optional Documentation**
```
📚 Generate documentation? y

📝 Creating documentation...
   ✓ README.md
   ✓ USER-GUIDE.md

✅ Fully complete! (24 minutes)
```

**Result**: Production-ready module in 24 minutes!

---

### Example 2: Module with Multiple Models

**Task**: Create quality control system

```bash
/odoo-dev "create quality_control module with models:
- quality.checkpoint (name, project_id, sequence)
- quality.check (checkpoint_id, task_id, result (pass/fail), notes)
- quality.result (check_id, inspector_id, date, status)"
```

**Architecture Discussion**:
```
📐 Architecture Proposal:

**Module**: quality_control
**Models**: 3

1. quality.checkpoint (master data)
   - name, project_id, sequence
   - One2many: check_ids

2. quality.check (main entity)
   - checkpoint_id, task_id
   - result, notes
   - One2many: result_ids

3. quality.result (detailed results)
   - check_id, inspector_id
   - date, status

**Relationships**:
- checkpoint → checks (One2many)
- check → results (One2many)
- check → task (Many2one: project.task)
- result → inspector (Many2one: res.users)

**Views**: 11 total (list, form, search for each model + kanban)
**Dependencies**: project, mail

Proceed? y
```

**Result**: Complete quality control system in 25-30 minutes

---

### Example 3: Integration Module

**Task**: Integrate timesheet with quality checks

```bash
/odoo-dev "create timesheet_quality module that:
- Links hr.timesheet.line with quality.check
- Shows quality checks on timesheet lines
- Validates timesheet approval based on quality results
- Adds reports for quality vs time"
```

**This is complex** because it:
- Extends multiple modules
- Adds business logic
- Includes computed fields
- Has workflow dependencies

**Time**: 30-35 minutes

**Claude will**:
1. Research both modules (timesheet, quality)
2. Plan integration points
3. Discuss architecture thoroughly
4. Implement in phases
5. Comprehensive testing
6. Full documentation

---

## Search Mode Examples

Search Mode is for questions about the codebase - instant answers!

### Example 1: Model Information

**Query**:
```bash
/odoo-search "what is sale.order?"
```

**Response** (<2 seconds):
```
**Model**: sale.order
**Module**: sale
**Description**: Sales Order

**Inherits**:
- mail.thread
- mail.activity.mixin
- portal.mixin

**Key Fields** (127 total):
- name (Char) - Order Reference
- partner_id (Many2one → res.partner) - Customer
- order_line (One2many → sale.order.line) - Order Lines
- amount_total (Monetary, computed) - Total
- state (Selection) - Status

**Views**: 8 (form, list, search, kanban, calendar, pivot, graph, activity)

**Location**: odoo/custom/src/sale/models/sale_order.py

Query: 28ms
```

---

### Example 2: Field Details

**Query**:
```bash
/odoo-search "what fields does res.partner have?"
```

**Response** (<2 seconds):
```
res.partner has 156 fields:

**Contact**:
- name, email, phone, mobile

**Address**:
- street, city, zip, country_id

**Relationships**:
- parent_id, child_ids, user_ids

**Business**:
- customer_rank, supplier_rank, category_id

[Full list available]
```

---

### Example 3: Find Elements

**Query**:
```bash
/odoo-search "find all Many2one fields pointing to res.partner in sale module"
```

**Response** (<2 seconds):
```
Found 12 Many2one fields → res.partner in sale:

sale.order:
- partner_id (Customer)
- partner_invoice_id (Invoice Address)
- partner_shipping_id (Delivery Address)

sale.order.line:
- partner_id (Related Customer)

[... more]
```

---

### Example 4: View Information

**Query**:
```bash
/odoo-search "show me sale.order form views"
```

**Response** (<2 seconds):
```
Found 3 form views for sale.order:

1. sale.view_order_form (main form)
   - Module: sale
   - Priority: 1
   - Inherited by: 15 modules

2. sale.view_order_form_with_phone (variant)
   - Inherits: view_order_form
   - Adds: phone field

[Use get_details for full XML]
```

---

### Example 5: Method Information

**Query**:
```bash
/odoo-search "how does sale.order confirmation work?"
```

**Response** (<3 seconds):
```
**Sale Order Confirmation** (action_confirm):

**Method**: action_confirm()
**Location**: sale/models/sale_order.py:450

**Process**:
1. Validate order fields
2. Change state: draft → sale
3. Create procurements (if sale_stock)
4. Send confirmation email
5. Post message in chatter

**Related**:
- _action_confirm() - Internal logic
- _create_procurement() - Create stock moves

[See implementation in file]
```

---

## Common Workflows

### Workflow 1: Adding Field to Existing Module

**Scenario**: You need to track customer reference on sale orders

**Steps**:

1. **Use Quick Mode**:
   ```bash
   /odoo-dev "add client_ref (Char) to sale.order, show in form view after name field"
   ```

2. **Review Architecture** (inline):
   ```
   📐 Architecture:
      Extend: sale.order
      Add field: client_ref (Char)
      Update: form view (after name)

      Proceed? y
   ```

3. **Auto-implementation**: 5-7 minutes

4. **Install**:
   ```bash
   invoke restart
   invoke install -m sale_custom_fields
   ```

**Total time**: 10-12 minutes

---

### Workflow 2: Creating New Feature Module

**Scenario**: Build customer satisfaction tracking

**Steps**:

1. **Use Full Mode**:
   ```bash
   /odoo-dev "create customer_satisfaction module to track satisfaction surveys after sales with ratings, comments, follow-up actions"
   ```

2. **Participate in Architecture**:
   - Review model structure
   - Suggest changes if needed
   - Approve when satisfied

3. **Auto-implementation**: 20-25 minutes

4. **Review Results**:
   - Check files created
   - Review tests passed
   - Read generated README

5. **Optional Documentation**:
   ```
   Generate docs? y
   ```

6. **Install and Test**:
   ```bash
   invoke restart
   invoke install -m customer_satisfaction
   ```

**Total time**: 30-35 minutes

---

### Workflow 3: Exploring Codebase

**Scenario**: Understand how project tasks work

**Steps**:

1. **Get model overview**:
   ```bash
   /odoo-search "what is project.task?"
   ```

2. **See fields**:
   ```bash
   /odoo-search "what fields does project.task have?"
   ```

3. **Find specific field**:
   ```bash
   /odoo-search "show me stage_id in project.task"
   ```

4. **Understand workflow**:
   ```bash
   /odoo-search "how do project.task stages work?"
   ```

5. **Find related code**:
   ```bash
   /odoo-search "find all views for project.task"
   ```

**Total time**: 5 minutes, complete understanding!

---

### Workflow 4: Debugging Issue

**Scenario**: Field not showing in view

**Steps**:

1. **Verify field exists**:
   ```bash
   /odoo-search "does sale.order have my_custom_field?"
   ```

2. **Check view inheritance**:
   ```bash
   /odoo-search "find sale.order form views"
   ```

3. **Validate XML ID**:
   ```bash
   /odoo-search "find XML ID action_view_sale_order"
   ```

4. **Fix if needed**:
   ```bash
   /odoo-dev "add my_custom_field to sale.order form view"
   ```

**Total time**: 5-10 minutes

---

### Workflow 5: Module Testing

**Scenario**: Test a module you just created

**Steps**:

1. **Run module tests**:
   ```bash
   /odoo-test my_module
   ```

2. **If tests fail**, see error details and fix:
   ```bash
   /odoo-test my_module --debug
   ```

3. **Rerun after fixes**:
   ```bash
   /odoo-test my_module
   ```

4. **All passed? Install**:
   ```bash
   invoke restart
   invoke install -m my_module
   ```

**Total time**: 10-15 minutes

---

## Best Practices

### 1. Let Claude Detect Mode

**DON'T**:
```bash
"Use quick mode to add this field..."
```

**DO**:
```bash
"Add notes field to res.partner"
```

Claude automatically detects the best mode!

---

### 2. Be Specific About Requirements

**VAGUE**:
```bash
"Add some fields to partners"
```

**SPECIFIC**:
```bash
"Add company_size (Selection: small/medium/large) and industry_id (Many2one to res.partner.industry) to res.partner"
```

Better requirements = better results!

---

### 3. Trust the Validation

Claude validates everything with the indexer:
- ✓ Models exist
- ✓ Fields are correctly typed
- ✓ XML IDs are valid
- ✓ Security groups exist

**You can trust** that references are correct!

---

### 4. Review Architecture Carefully

The architecture approval is your main checkpoint:
- Model structure
- Field names and types
- View organization
- Security setup

**Take time** to review before approving!

---

### 5. Use Search for Learning

Before implementing, understand existing code:

```bash
# Learn about models
/odoo-search "what is sale.order?"

# See patterns
/odoo-search "find all computed fields in sale.order"

# Understand structure
/odoo-search "how does sale.order relate to account.move?"
```

**Knowledge first**, implementation second!

---

### 6. Keep Index Fresh

Update after major changes:

```bash
# After installing new modules
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py

# Weekly (recommended)
uv run scripts/update_index.py --full
```

---

### 7. Start Simple

**First task**? Start with Quick Mode:
```bash
/odoo-dev "add test_field to res.partner"
```

**Once comfortable**, move to Full Mode:
```bash
/odoo-dev "create complete module..."
```

---

## Troubleshooting

### Issue: "Validation failed"

**Cause**: Invalid reference (model/field/XML ID)

**Solution**:
1. Check exact names with search:
   ```bash
   /odoo-search "what is the exact field name?"
   ```

2. Use exact name from indexer
3. Retry development

---

### Issue: "Tests failed"

**Cause**: Test logic or implementation issue

**Solution**:
1. Review test output
2. Identify failing test
3. Fix implementation or test
4. Rerun:
   ```bash
   /odoo-test module_name
   ```

---

### Issue: "Module not in index"

**Cause**: New module not yet indexed

**Solution**:
```bash
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py
```

---

### Issue: "Slow responses"

**Cause**: Index may be stale or corrupted

**Solution**:
```bash
# Rebuild index
cd odoo-doodba-dev/skills/odoo-indexer
uv run scripts/update_index.py --full
```

---

### Issue: "Architecture keeps changing"

**Cause**: Ambiguous requirements

**Solution**: Be more specific:
- Exact field types
- Relationships clearly stated
- Dependencies mentioned
- Target locations specified

---

## Tips & Tricks

### Tip 1: Use Natural Language

You don't need technical terms:

**Works**: "Add a dropdown to partners for company size"
**Also works**: "Add company_size (Selection) to res.partner"

Claude understands both!

---

### Tip 2: Ask for Examples

```bash
/odoo-search "show me an example of computed field in sale.order"
```

Learn from existing code!

---

### Tip 3: Iterate on Architecture

If architecture isn't quite right:
```
📐 Architecture proposal...

Proceed? n

[Explain what you want changed]

📐 Revised architecture...

Proceed? y
```

---

### Tip 4: Request Documentation

For complex modules:
```
Documentation needed? y
```

Get README and guides automatically!

---

### Tip 5: Use Wrappers for Speed

For quick checks:
```bash
# Fast model lookup
./skills/odoo-indexer/tools/get_model_details.sh "sale.order"

# Quick validation
./skills/odoo-indexer/tools/validate_field.sh "sale.order" "partner_id"
```

---

## Next Steps

1. **Try Quick Mode**: Add a simple field
2. **Try Search Mode**: Explore existing models
3. **Try Full Mode**: Create a small module
4. **Read best practices**: Review this guide
5. **Build real features**: Start your project!

---

## Additional Resources

- **README.md**: Plugin overview and features
- **INSTALLATION.md**: Setup and configuration
- **Skill README**: Indexer usage details

---

**Happy coding with v2.0!** 🚀
