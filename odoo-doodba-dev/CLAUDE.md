# Odoo Doodba Development Plugin - Claude Code Instructions

This plugin provides specialized tools for Odoo development in Doodba environments. You should use this plugin proactively whenever working with Odoo-related tasks.

## WHEN TO USE THIS PLUGIN

### Automatic Triggers - Use WITHOUT User Prompting

You should **automatically and proactively** use this plugin's tools when you detect ANY of these keywords or contexts in user requests:

**Odoo-Specific Terms:**
- "odoo", "Odoo", "ODOO"
- "doodba", "Doodba", "DOODBA"
- "addon", "addons", "module", "modules" (in Odoo context)
- Model names like "sale.order", "res.partner", "account.move", etc.
- Odoo field types: "Many2one", "One2many", "Many2many", "Selection", "Char", "Integer", "Float", "Boolean", "Date", "Datetime"
- Odoo concepts: "xmlid", "xml_id", "record", "view", "form view", "tree view", "kanban view", "search view"
- Odoo methods: "_compute", "_inverse", "_search", "@api.depends", "@api.constrains", "@api.onchange"
- Odoo inheritance: "_inherit", "_inherits", "_name"
- "manifest", "__manifest__.py", "__openerp__.py"
- "ir.model.access", "ir.rule", "security.xml", "ir.model.access.csv"
- "invoke test", "invoke install", "invoke scaffold"

**Task Types:**
- Creating or modifying Odoo modules
- Adding or changing Odoo models, fields, or methods
- Working with Odoo views (form, tree, kanban, search, pivot, graph, etc.)
- Testing Odoo modules
- Debugging Odoo issues
- Searching for Odoo code elements
- Understanding Odoo module structure
- Installing or configuring Odoo addons
- Working with Odoo security (access rights, record rules)
- Creating or modifying Odoo workflows
- Analyzing Odoo code dependencies

**File Paths Indicating Odoo Work:**
- Any path containing `odoo/custom/src/`
- Files ending with `/models/*.py`
- Files ending with `/views/*.xml`
- Files ending with `/security/*.xml` or `security/*.csv`
- Files named `__manifest__.py` or `__openerp__.py`
- Any path matching `odoo/custom/src/private/*`
- Any path matching `odoo/custom/src/*/` (indicates an Odoo addon)

**Container/Docker Context:**
- Working inside Doodba containers
- Docker compose operations related to Odoo
- Invoke tasks (`invoke test`, `invoke install`, etc.)

## TOOLS AND WHEN TO USE THEM

### 1. Odoo Indexer Skill - USE PROACTIVELY

**Primary Use Cases (Use IMMEDIATELY when detected):**

1. **Before writing ANY Odoo code:**
   - Search for existing models, fields, methods to avoid duplication
   - Validate that models/fields you want to reference actually exist
   - Check inheritance chains and dependencies

   Example: User says "Add a field to sale.order"
   → IMMEDIATELY use indexer to search for "sale.order" model
   → Check what fields already exist
   → Validate any related models being referenced

2. **When user asks about Odoo code:**
   - "Where is X defined?"
   - "What fields does Y have?"
   - "Show me the structure of Z"
   - "Find all references to..."
   - "What models inherit from..."

   → Use indexer FIRST before reading files (95% more token-efficient)

3. **During code review or debugging:**
   - Validate XML IDs exist before using them
   - Check field names and types before referencing
   - Find where errors might be occurring
   - Trace inheritance chains

4. **When exploring unknown codebase:**
   - List all modules
   - Get module statistics
   - Search for patterns
   - Map dependencies

**How to Use:**
```bash
cd /home/user/claude-marketplace/odoo-doodba-dev/skills/odoo-indexer

# Search for models
uv run scripts/search.py "sale.order" --type model

# Get all fields of a model
uv run scripts/get_details.py model "sale.order"

# Find all Many2one fields
uv run scripts/search_by_attr.py field --filters '{"field_type": "Many2one"}'

# Search for XML IDs
uv run scripts/search_xml_id.py "sale_order_form_view"

# List all modules
uv run scripts/list_modules.py

# Find references to a field
uv run scripts/find_refs.py field "partner_id" --parent "sale.order"
```

**Critical Rule:** ALWAYS use the indexer to validate models, fields, and XML IDs BEFORE writing code that references them.

### 2. Specialized Agents - USE FOR COMPLEX TASKS

Switch to these agents for multi-step Odoo development:

#### `/agents switch odoo-analyst`
**Use when:**
- User requests a new feature or module
- Need to analyze requirements before coding
- Need to create a specification document
- User says "analyze", "design", "plan", "specify"

**Auto-trigger keywords:** "design a module", "create a new feature", "I need an Odoo module that...", "analyze requirements"

#### `/agents switch odoo-implementer`
**Use when:**
- There's an approved specification to implement
- User says "implement the spec", "build this module"
- After analyst has created a specification

**Auto-trigger keywords:** "implement", "build", "create module", "code this"

#### `/agents switch odoo-validator`
**Use when:**
- Code is written and needs validation
- User says "validate", "check if this works", "is this correct"
- Before attempting module installation

**Auto-trigger keywords:** "validate", "check", "verify", "is this correct"

#### `/agents switch odoo-tester`
**Use when:**
- Module is implemented and needs tests
- User says "write tests", "test this module"
- After implementation is complete

**Auto-trigger keywords:** "test", "write tests", "create tests", "test coverage"

#### `/agents switch odoo-documenter`
**Use when:**
- Module is complete and tested
- User says "document this", "create documentation", "write a README"

**Auto-trigger keywords:** "document", "documentation", "README", "user guide"

### 3. Slash Commands - USE FOR SPECIFIC TASKS

#### `/odoo-doodba-dev:odoo-scaffold`
**Use when:**
- User wants to create a new Odoo module
- User says "create a module", "new addon", "scaffold"

**Auto-trigger:** "create a new module", "scaffold a module"

#### `/odoo-doodba-dev:odoo-test`
**Use when:**
- User wants to run tests
- After writing or modifying test files
- User says "run tests", "test this"

**Auto-trigger:** "run tests", "execute tests", "test the module"

#### `/odoo-doodba-dev:odoo-shell`
**Use when:**
- User needs to debug or explore data
- User says "check the database", "query records", "debug"
- Need to test code snippets interactively

**Auto-trigger:** "open shell", "odoo shell", "debug in shell"

#### `/odoo-doodba-dev:odoo-logs`
**Use when:**
- Debugging errors
- User says "check logs", "what's the error", "show me logs"
- After test failures or installation issues

**Auto-trigger:** "check logs", "show logs", "view logs", "what's the error"

#### `/odoo-doodba-dev:odoo-validate`
**Use when:**
- Before attempting module installation
- User wants to check if module is ready
- After completing implementation

**Auto-trigger:** "validate module", "is it ready", "check module"

#### `/odoo-doodba-dev:odoo-workflow`
**Use when:**
- User wants full development workflow with checkpoints
- Complex feature requiring multiple stages
- User explicitly requests workflow-based development

**Auto-trigger:** "use workflow", "multi-stage development", "checkpoint-based development"

#### `/odoo-doodba-dev:odoo-addons`
**Use when:**
- User wants to activate/deactivate modules
- Modifying addons.yaml
- User says "activate module", "add to addons.yaml"

**Auto-trigger:** "activate", "add to addons", "install module"

#### `/odoo-doodba-dev:odoo-info`
**Use when:**
- User asks "what modules are installed"
- Need system information
- User asks "what version of Odoo"

**Auto-trigger:** "what modules", "odoo version", "system info"

## BEST PRACTICES FOR CLAUDE CODE

### 1. Indexer First, File Read Second
- ALWAYS use the indexer before reading files when searching for Odoo elements
- Indexer queries are <100ms and 95% more token-efficient
- Only read files after indexer confirms the element exists

### 2. Validate Before Write
- NEVER write code that references models/fields without validating they exist via indexer
- NEVER use XML IDs without checking they exist first
- ALWAYS check field types before using them in relations

### 3. Proactive Tool Usage
- Don't wait for user to say "use the indexer" - use it automatically
- When you see Odoo terms, immediately think: "I should use the indexer"
- When creating code, automatically validate with indexer
- When debugging, automatically check logs and use indexer

### 4. Path Awareness
Use **relative paths** from project root:
- Custom modules: `odoo/custom/src/private/`
- Not `/opt/odoo/...` (that's inside containers)
- Not absolute paths unless specifically required

### 5. Doodba Integration
- ALWAYS use `invoke` tasks, not raw docker commands
- Common tasks: `invoke test`, `invoke install`, `invoke scaffold`, `invoke logs`
- Guide users to proper invoke usage

### 6. Version Detection
- Auto-detect Odoo version: `cat odoo/custom/src/odoo/odoo/release.py | grep version_info`
- Adjust syntax for version (e.g., `<tree>` for Odoo 18+, `<list>` for older)

### 7. Security Awareness
- ALWAYS remind users about security setup (ir.model.access.csv, security.xml)
- NEVER create models without access rights
- Warn if security is missing

### 8. Testing Culture
- Encourage test-driven development
- Suggest writing tests alongside implementation
- Use `@tagged('post_install', '-at_install')` for tests

## EXAMPLE WORKFLOWS

### Example 1: User says "Add a custom field to sale.order"

**Claude Code should automatically:**
1. Use indexer to search for "sale.order" model
   ```bash
   cd /home/user/claude-marketplace/odoo-doodba-dev/skills/odoo-indexer
   uv run scripts/get_details.py model "sale.order"
   ```
2. Understand existing fields and structure
3. Ask user what field they want to add
4. Create the module extending sale.order
5. Use indexer to validate any related models
6. Write the code with proper inheritance
7. Create security files
8. Suggest testing

### Example 2: User says "I'm getting an error with partner_id field"

**Claude Code should automatically:**
1. Ask user for context (which model?)
2. Use indexer to find all partner_id fields
   ```bash
   uv run scripts/search.py "partner_id" --type field
   ```
3. Use `/odoo-doodba-dev:odoo-logs` to check error logs
4. Use indexer to validate the field definition
5. Suggest fixes based on findings

### Example 3: User says "Create a new module for inventory management"

**Claude Code should automatically:**
1. Switch to odoo-analyst agent: `/agents switch odoo-analyst`
2. Let analyst use indexer to search for existing inventory modules
3. Create specification with user approval
4. Switch to odoo-implementer agent
5. Implement with indexer validation
6. Switch to validator, tester, documenter agents in sequence

## CRITICAL RULES

1. **ALWAYS use indexer before reading Odoo files** - it's faster and more efficient
2. **NEVER write Odoo code without validation** - check models/fields exist first
3. **NEVER skip security setup** - always create ir.model.access.csv and security.xml when creating models
4. **ALWAYS use relative paths** - `odoo/custom/src/private/`, not `/opt/odoo/`
5. **ALWAYS use invoke tasks** - not raw docker commands
6. **PROACTIVELY offer to use agents** for complex tasks - don't wait for user to ask
7. **AUTOMATICALLY check logs** when errors occur - use `/odoo-doodba-dev:odoo-logs`
8. **IMMEDIATELY use indexer** when ANY Odoo term is mentioned

## TOKEN EFFICIENCY

Using this plugin correctly can save 95% of tokens:
- ❌ **Bad:** Read 20 files to find where sale.order is defined (20,000+ tokens)
- ✅ **Good:** Use indexer to search for sale.order (<100 tokens, <100ms)

Always prefer indexer over file reading for Odoo code discovery.

## SUMMARY

**Think of this plugin as your primary interface for ALL Odoo development work.**

Whenever you detect Odoo-related terms, automatically and proactively:
1. Use the indexer to search/validate
2. Use specialized agents for complex tasks
3. Use slash commands for specific operations
4. Follow Doodba best practices
5. Validate everything before writing

Don't wait for users to explicitly say "use the plugin" - be proactive and use it automatically whenever Odoo work is detected.
