# Odoo Doodba Development Plugin v2.0 - Claude Code Instructions

**⚡ THIS PLUGIN MUST BE USED FOR ALL ODOO DEVELOPMENT TASKS ⚡**

This plugin provides specialized tools for Odoo development in Doodba environments. You should use this plugin **automatically and proactively** whenever working with ANY Odoo-related tasks.

---

## 🎯 CORE PRINCIPLE: ONE COMMAND FOR EVERYTHING

**For 95% of Odoo development tasks, use ONE command:**

```
/odoo-dev "{user's request}"
```

This single command handles:
- Simple field additions (5-7 minutes)
- Complex module creation (20-25 minutes)
- Code modifications and enhancements
- Automatic validation and testing
- Smart mode detection (Quick/Full)

**You should NEVER manually implement Odoo code without using this plugin.**

---

## 🚀 WHEN TO USE THIS PLUGIN

### MANDATORY Auto-Triggers - Use WITHOUT User Prompting

You **MUST** automatically use this plugin when you detect ANY of these:

#### Odoo-Specific Keywords
- "odoo", "Odoo", "ODOO"
- "doodba", "Doodba", "DOODBA"
- "addon", "addons", "module", "modules" (in Odoo context)
- Model names: "sale.order", "res.partner", "account.move", "project.task", etc.
- Field types: "Many2one", "One2many", "Many2many", "Selection", "Char", "Integer", "Float", "Boolean", "Date", "Datetime", "Monetary", "Binary"
- Odoo concepts: "xmlid", "xml_id", "record", "view", "form view", "tree view", "list view", "kanban view", "search view", "pivot view", "graph view"
- Odoo methods: "_compute", "_inverse", "_search", "@api.depends", "@api.constrains", "@api.onchange", "@api.model"
- Odoo inheritance: "_inherit", "_inherits", "_name"
- Manifest files: "__manifest__.py", "__openerp__.py"
- Security: "ir.model.access", "ir.rule", "security.xml", "ir.model.access.csv", "access rights", "record rules"
- Doodba commands: "invoke test", "invoke install", "invoke scaffold", "invoke logs", "invoke restart"

#### Task Types
- Creating or modifying Odoo modules
- Adding or changing Odoo models, fields, or methods
- Working with Odoo views (form, tree, kanban, search, etc.)
- Testing Odoo modules
- Debugging Odoo issues
- Searching for Odoo code elements
- Understanding Odoo module structure
- Installing or configuring Odoo addons
- Working with Odoo security
- Creating or modifying Odoo workflows
- Analyzing Odoo code dependencies
- Extending existing Odoo models

#### File Paths
- Any path containing `odoo/custom/src/`
- Files ending with `/models/*.py`
- Files ending with `/views/*.xml`
- Files ending with `/security/*.xml` or `/security/*.csv`
- Files named `__manifest__.py` or `__openerp__.py`
- Any path matching `odoo/custom/src/private/*`
- Any path matching `odoo/custom/src/odoo-sh/*`

---

## 📋 AVAILABLE COMMANDS (v2.0)

### 1. `/odoo-dev` - **USE THIS FOR 95% OF TASKS**

**Primary development command** - Auto-detects complexity and handles everything.

**When to use:**
- ANY development task (simple or complex)
- Creating new modules
- Modifying existing code
- Adding fields, models, views
- Implementing business logic

**Examples:**
```bash
# Simple tasks
/odoo-dev "add notes field to res.partner"
/odoo-dev "add quality_result_id to project.task"

# Complex tasks
/odoo-dev "create inventory management module with requests and schedules"
/odoo-dev "add workflow to sale.order for approval process"

# Modifications
/odoo-dev "extend project.task with quality inspection fields"
/odoo-dev "modify sale order confirmation to send custom email"
```

**What it does automatically:**
1. Detects task complexity (Quick Mode vs Full Mode)
2. Researches codebase with indexer
3. Proposes architecture
4. Waits for user approval
5. Implements code with auto-validation
6. Runs verification and tests
7. Reports completion

**You get 1 approval point (architecture), then everything is automatic!**

---

### 2. `/odoo-search` - For Questions About Code

**Fast code search** using the indexer (sub-100ms queries).

**When to use:**
- User asks "what is...", "show me...", "find...", "where is...", "how does..."
- Looking up models, fields, views, XML IDs
- Understanding code structure
- Exploring the codebase

**Examples:**
```bash
# Model information
/odoo-search "what is sale.order"
/odoo-search "what fields does res.partner have"

# Finding elements
/odoo-search "find all Many2one fields in sale module"
/odoo-search "search for project task views"
/odoo-search "where is project.task defined"

# XML IDs
/odoo-search "find action_view_task"

# Modules
/odoo-search "list all modules"
/odoo-search "tell me about the sale module"
```

**Response time: <100ms** (95% faster than reading files!)

---

### 3. `/odoo-setup` - First-Time Setup

**Automated plugin setup** - Run once after installation.

**When to use:**
- First time using the plugin
- After updating Odoo installation
- If indexer database is corrupted

**What it does:**
1. Checks prerequisites (Docker, Python, uv)
2. Auto-installs missing dependencies
3. Detects or prompts for Odoo path
4. Builds code indexer database (2-5 minutes)
5. Validates installation
6. Returns ready-to-use status

**You only run this ONCE (or after major changes).**

---

### 4. `/odoo-scaffold` - Generate Module Structure

**Quickly scaffold new Odoo modules** with proper structure.

**When to use:**
- Creating a brand new module from scratch
- Need proper module structure fast

**Example:**
```bash
/odoo-scaffold my_custom_module
```

**Creates:**
- `__manifest__.py` with proper metadata
- `models/__init__.py` and model template
- `views/` directory with view template
- `security/ir.model.access.csv`
- `tests/` directory with test template
- Proper `__init__.py` files

**After scaffolding, use `/odoo-dev` to add functionality!**

---

### 5. `/odoo-test` - Run Tests

**Run Odoo tests** with proper Doodba integration.

**When to use:**
- Testing specific modules
- Debugging test failures
- Running full test suite

**Examples:**
```bash
# Test specific module
/odoo-test my_custom_module

# Test multiple modules
/odoo-test sale,purchase,stock

# Test with debug mode
/odoo-test my_module --debug
```

**Note: Tests are automatically run by `/odoo-dev`, so you rarely need this directly.**

---

## 🔧 HOW TO USE THE PLUGIN

### For Simple Tasks (5-7 minutes)

**Example: "Add notes field to res.partner"**

```
1. User: "Add notes field to res.partner"

2. You: Use /odoo-dev command immediately
   /odoo-dev "add notes field to res.partner"

3. Plugin detects: Quick Mode (simple task)
   - Researches res.partner with indexer
   - Proposes inline architecture
   - Shows: "Extend res.partner, add notes (Text) field, update form view"

4. User approves architecture

5. Plugin automatically:
   - Creates extension module
   - Adds field to model
   - Updates view
   - Validates with indexer
   - Runs tests
   - Reports completion

6. Done! Module ready for installation.
```

**Total time: 5-7 minutes**
**User interactions: 1 (approve architecture)**

---

### For Complex Tasks (20-25 minutes)

**Example: "Create equipment maintenance module"**

```
1. User: "Create equipment maintenance module with maintenance requests and schedules"

2. You: Use /odoo-dev command immediately
   /odoo-dev "create equipment maintenance module with maintenance requests and schedules"

3. Plugin detects: Full Mode (complex feature)
   - Researches related modules (maintenance.equipment, etc.)
   - Analyzes dependencies
   - Validates all references with indexer
   - Proposes detailed architecture:
     * Module: equipment_maintenance
     * Models: 3 (request, schedule, log)
     * Views: 8 (forms, lists, kanban, search)
     * Dependencies: base, mail, maintenance
     * Security: access rights + record rules

4. User reviews and approves detailed architecture

5. Plugin automatically:
   - Creates module structure
   - Implements all models with validation
   - Creates all views with validation
   - Sets up security
   - Creates comprehensive tests
   - Runs verification
   - Reports completion

6. Optional: User requests documentation
   - Plugin generates README, USER-GUIDE, DEVELOPER-GUIDE

7. Done! Full module ready for installation.
```

**Total time: 20-25 minutes**
**User interactions: 1-2 (approve architecture, optional docs)**

---

### For Questions About Code (<2 seconds)

**Example: "What is sale.order?"**

```
1. User: "What is sale.order?"

2. You: Use /odoo-search command immediately
   /odoo-search "what is sale.order"

3. Plugin uses indexer (instant):
   - Queries SQLite database
   - Returns comprehensive info:
     * Model name and description
     * Module location
     * Key fields (partner_id, order_line, amount_total, state, etc.)
     * Views (form, list, kanban, search, etc.)
     * Actions and menus
     * File location

4. Done! Answer provided in <100ms.
```

**Total time: <2 seconds**
**User interactions: 0**

---

## 🎯 WORKFLOW SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│  USER REQUEST: Any Odoo Development Task                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
                ┌──────────────────────┐
                │  Is it a question?   │
                │  (what/where/find)   │
                └──────────────────────┘
                   ↓               ↓
                 YES              NO
                   ↓               ↓
        ┌──────────────────┐  ┌──────────────────┐
        │  /odoo-search    │  │   /odoo-dev      │
        │  (instant)       │  │  (automatic)     │
        └──────────────────┘  └──────────────────┘
                                      ↓
                          ┌──────────────────────┐
                          │  Detects Complexity  │
                          │  (Quick vs Full)     │
                          └──────────────────────┘
                                      ↓
                ┌────────────────────────────────────┐
                │  1. Research with Indexer          │
                │  2. Propose Architecture           │
                │  3. Wait for Approval ◄────────────┤ ONE APPROVAL
                │  4. Implement (auto-validated)     │
                │  5. Verify & Test (automatic)      │
                │  6. Report Completion              │
                └────────────────────────────────────┘
                                      ↓
                            ┌──────────────────┐
                            │   DONE!          │
                            │  Ready to use    │
                            └──────────────────┘
```

---

## 🔍 THE INDEXER: YOUR SECRET WEAPON

The plugin includes a **SQLite-based code indexer** that makes everything 95% faster.

**What it indexes:**
- All models with fields and methods
- All views (form, list, kanban, search, etc.)
- All XML IDs
- All actions and menus
- Module dependencies
- Field relationships

**Query speed: <100ms** (vs 2-5 seconds reading files!)

**The indexer is used automatically by:**
- `/odoo-dev` - validates all references before implementing
- `/odoo-search` - provides instant answers
- All agents - research and validation

**You never need to use it manually** - it's built into the workflow!

---

## ⚠️ CRITICAL RULES FOR CLAUDE CODE

### 1. ALWAYS Use the Plugin for Odoo Work

**NEVER manually:**
- Write Odoo models without using `/odoo-dev`
- Create Odoo views without using `/odoo-dev`
- Modify Odoo code without using `/odoo-dev`
- Search Odoo code without using `/odoo-search`

**ALWAYS:**
- Detect Odoo keywords and use plugin automatically
- Use `/odoo-dev` as the primary command
- Use `/odoo-search` for questions
- Trust the plugin's validation and testing

### 2. Mode Detection is Automatic

**DO NOT ask the user** which mode to use (Quick vs Full).

The plugin automatically detects:
- Quick Mode: 1-2 fields, simple modifications
- Full Mode: New modules, multiple models, complex logic
- Search Mode: Questions about code

**You just pass the request to `/odoo-dev` and it figures it out!**

### 3. One Approval, Then Automatic

The workflow requires **ONE user approval** (architecture proposal), then everything else is automatic:
- Implementation: automatic
- Validation: automatic
- Testing: automatic
- Error fixing: automatic (with user notification)

**DO NOT ask for approval at every step** - the plugin handles it!

### 4. Trust the Validation

The plugin validates EVERYTHING with the indexer:
- Model names exist
- Field references are correct
- XML IDs are valid
- View inheritance is proper
- Security groups exist

**If the plugin says it's validated, it's validated!**

### 5. Path Conventions & Ghost Module Prevention

**⚠️ CRITICAL: ALWAYS create modules ONLY in `odoo-sh/` directory!**

**Module Creation Path (MANDATORY):**
- ✅ `odoo/custom/src/odoo-sh/my_module/` - **ONLY USE THIS!**
- ❌ `odoo/custom/src/private/my_module/` - **NEVER CREATE HERE!**

**Why this matters:**
- Creating modules in multiple locations causes "ghost modules"
- Odoo may load the wrong version (e.g., scaffold template instead of implementation)
- Fields never get created in database
- Installation appears successful but uses wrong files
- Wastes 10+ minutes debugging "invisible" modules

**Before creating ANY module, ALWAYS:**
1. Check for existing duplicates:
   ```bash
   find odoo/custom/src -name "module_name" -type d
   ```
2. If duplicates exist, remove them before proceeding
3. Create ONLY in `odoo/custom/src/odoo-sh/`

**Path conventions for other uses:**
- ✅ `odoo/custom/src/odoo-sh/my_module/` - Module creation (ONLY location)
- ✅ Relative paths from project root
- ❌ `/opt/odoo/custom/src/` (inside container)
- ❌ Absolute paths (unless specifically required)

### 6. Doodba Integration

**ALWAYS use `invoke` commands, NOT raw docker:**
- ✅ `invoke test -m my_module`
- ✅ `invoke install -m my_module`
- ✅ `invoke restart`
- ❌ `docker-compose exec odoo odoo test...`

The plugin handles this automatically!

---

## 📚 EXAMPLE CONVERSATIONS

### Example 1: Simple Field Addition

```
User: "Add a notes field to res.partner"

Claude: I'll use the Odoo development plugin to add this field.

[Uses: /odoo-dev "add notes field to res.partner"]

[Plugin detects Quick Mode]
[Plugin researches res.partner]
[Plugin proposes architecture]

Plugin: 📐 Architecture Proposal:
- Extend res.partner (base module)
- Add field: notes (Text)
- Update partner form view

Proceed?

User: yes

[Plugin implements automatically]
[Plugin validates with indexer]
[Plugin runs tests]

Plugin: ✅ Complete! (6 minutes)
- Field added to res.partner
- View updated
- 3/3 tests passed
- Ready for installation

Claude: Done! The notes field has been successfully added to res.partner.
You can install the changes with: invoke restart
```

### Example 2: Complex Module Creation

```
User: "Create a module for quality inspections on project tasks"

Claude: I'll create a quality inspection module for project tasks using the Odoo development plugin.

[Uses: /odoo-dev "create module for quality inspections on project tasks"]

[Plugin detects Full Mode]
[Plugin researches project.task, quality modules]
[Plugin validates dependencies]
[Plugin proposes detailed architecture]

Plugin: 📐 Architecture Proposal (Full Mode):
Module: project_task_quality
Models:
- project.task.quality (main inspection record)
- project.task.quality.line (inspection checklist items)
- project.task.quality.template (reusable templates)

Views: 8 views (form, list, kanban, search for models)
Dependencies: project, quality_control
Security: User and Manager access levels

[Detailed field list and relationships shown...]

Proceed?

User: yes

[Plugin implements in phases]
Phase 1: Models ✓ (5 min)
Phase 2: Views ✓ (6 min)
Phase 3: Security ✓ (2 min)
[Plugin validates everything]
[Plugin runs tests]

Plugin: ✅ Complete! (24 minutes)
- Module: project_task_quality
- Location: odoo/custom/src/odoo-sh/project_task_quality/
- Tests: 15/15 passed
- Validation: All references validated ✓

Claude: Your quality inspection module is ready! The module includes:
- Quality inspection records linked to tasks
- Checklist functionality with templates
- Full security configuration
- Comprehensive tests

Install with: invoke install -m project_task_quality
```

### Example 3: Code Search

```
User: "What fields does sale.order have?"

Claude: I'll search the Odoo codebase for sale.order fields.

[Uses: /odoo-search "what fields does sale.order have"]

[Plugin queries indexer instantly]

Plugin: sale.order has 127 fields:

Key Fields:
- partner_id (Many2one → res.partner) - Customer
- order_line (One2many → sale.order.line) - Order Lines
- amount_total (Monetary, computed) - Total Amount
- state (Selection) - Status: draft|sent|sale|done|cancel
- date_order (Datetime) - Order Date
- user_id (Many2one → res.users) - Salesperson
- team_id (Many2one → crm.team) - Sales Team
- pricelist_id (Many2one → product.pricelist) - Pricelist

[Shows top 15 most important fields...]

Query time: 28ms

Claude: The sale.order model has 127 fields. I've shown the key fields above.
The most important ones are partner_id (customer), order_line (order items),
and amount_total (total price). Would you like details on any specific field?
```

---

## 🚫 WHAT NOT TO DO

### ❌ DON'T: Manually implement Odoo code

```
User: "Add field to sale.order"

Claude: [Reads sale.order model file]
        [Writes code manually]
        [Creates view manually]
        ❌ WRONG!
```

### ✅ DO: Use the plugin

```
User: "Add field to sale.order"

Claude: /odoo-dev "add field to sale.order"
        ✅ CORRECT!
```

---

### ❌ DON'T: Read files to search for models

```
User: "What is project.task?"

Claude: [Uses Read tool on multiple files]
        [Searches through code manually]
        ❌ WRONG! (Slow, inefficient)
```

### ✅ DO: Use the indexer

```
User: "What is project.task?"

Claude: /odoo-search "what is project.task"
        ✅ CORRECT! (Instant, accurate)
```

---

### ❌ DON'T: Ask the user about mode/complexity

```
User: "Add field to sale.order"

Claude: "Is this a simple or complex task?"
        ❌ WRONG! (Plugin detects this)
```

### ✅ DO: Let the plugin detect automatically

```
User: "Add field to sale.order"

Claude: /odoo-dev "add field to sale.order"
        [Plugin auto-detects Quick Mode]
        ✅ CORRECT!
```

---

### ❌ DON'T: Implement without validation

```
Claude: [Creates model]
        [Adds field partner_id]
        [Doesn't validate res.partner exists]
        ❌ WRONG! (May reference non-existent model)
```

### ✅ DO: Plugin validates everything automatically

```
Claude: /odoo-dev "add partner_id field"
        [Plugin validates res.partner exists]
        [Plugin validates field type]
        [Plugin validates in views]
        ✅ CORRECT!
```

---

### ❌ DON'T: Create modules in wrong directory (causes ghost modules)

```
User: "Create inventory module"

Claude: [Creates scaffold in odoo/custom/src/private/]
        [Later creates implementation in odoo/custom/src/odoo-sh/]
        [Both exist - Odoo loads wrong one!]
        ❌ WRONG! (Ghost module problem - fields never created)
```

### ✅ DO: Check for duplicates and use ONLY odoo-sh directory

```
User: "Create inventory module"

Claude: /odoo-dev "create inventory module"
        [Plugin checks: find odoo/custom/src -name "inventory_*"]
        [Plugin verifies no duplicates exist]
        [Plugin creates ONLY in odoo/custom/src/odoo-sh/]
        [Adds duplicate check to completion report]
        ✅ CORRECT! (Single source of truth)
```

---

### ❌ DON'T: Assume XPath expressions in view inheritance

```
User: "Add field to pos.order search view"

Claude: [Generates view inheritance]
        <xpath expr="//group[@name='group_by']" position="inside">
        [Doesn't read parent view]
        [Assumes group has name='group_by']
        ❌ WRONG! (ParseError - group_by doesn't exist in parent view)
```

### ✅ DO: Validate XPath by reading parent view first

```
User: "Add field to pos.order search view"

Claude: /odoo-dev "add field to pos.order search view"
        [Plugin finds parent view XML ID with indexer]
        [Plugin reads parent view file]
        [Plugin verifies actual structure:
         - Sees <group expand="0" string="Group By"> (no name attribute!)
         - Finds <filter name="order_date"> (actual filter name)
         - Verifies <field name="partner_id"> exists]
        [Plugin writes inheritance with correct XPath:
         <xpath expr="//group[@string='Group By']" position="inside">
         OR
         <xpath expr="//field[@name='partner_id']" position="after">]
        ✅ CORRECT! (XPath validated against actual parent structure)
```

---

## 🎓 LEARNING RESOURCES

- **README.md** - Plugin overview and quick start
- **INSTALLATION.md** - Detailed setup instructions
- **USAGE.md** - Comprehensive usage guide and examples
- **CHANGELOG.md** - What's new in v2.0

---

## 📊 PERFORMANCE METRICS (v2.0)

| Task | Time (previous version) | Time (v2.0) | Improvement |
|------|-------------|-------------|-------------|
| Setup | 15-30 min | 2-5 min | **75% faster** |
| Simple field | 30-60 min | 5-7 min | **88% faster** |
| Complex module | 50-80 min | 20-25 min | **65% faster** |
| Code search | 2-5 sec | <100ms | **95% faster** |
| User approvals | 5 approvals | 1 approval | **80% less friction** |

---

## 🎯 SUMMARY: HOW TO USE THIS PLUGIN

**For Claude Code: Follow these simple rules:**

1. **Detect Odoo keywords** → Automatically use plugin
2. **One command for development** → `/odoo-dev`
3. **Use search for questions** → `/odoo-search`
4. **Trust the automation** → Validation, testing, error handling
5. **One approval point** → Architecture only, rest is automatic
6. **Never manually implement** → Always use the plugin

**For Users:**

1. Install: `/plugin install odoo-doodba-dev@letzdoo`
2. Setup: `/odoo-setup` (once)
3. Develop: `/odoo-dev "your request"`
4. Search: `/odoo-search "your question"`
5. That's it!

---

**🎉 Welcome to 60-80% faster Odoo development with 90% automation!**
