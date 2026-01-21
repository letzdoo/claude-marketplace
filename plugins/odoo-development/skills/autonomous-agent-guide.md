# Autonomous Agent Guide for Odoo Development

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  AUTONOMOUS AGENT GUIDE                                                      ║
║  Complete instructions for AI agents to use this plugin autonomously         ║
║  Follow these workflows for reliable, version-correct Odoo code generation   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Purpose

This guide enables AI agents to **autonomously** generate, review, and upgrade Odoo modules without human intervention, ensuring version-correct code and best practices compliance.

## Core Principles

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  1. ALWAYS identify Odoo version FIRST - before any code generation          ║
║  2. ALWAYS load version-specific skill files                                 ║
║  3. NEVER mix patterns from different Odoo versions                          ║
║  4. VERIFY patterns against GitHub when uncertain                            ║
║  5. XML file ordering in manifest is CRITICAL                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Input Parameter Schema

AI agents should accept and parse these input parameters:

```json
{
  "module_name": "string (required) - Technical name, snake_case",
  "module_description": "string (required) - Human-readable description",
  "odoo_version": "string (required) - 14.0|15.0|16.0|17.0|18.0|19.0",
  "target_apps": ["string"] - Apps to extend (sale, stock, hr, etc.)",
  "ui_stack": "string - classic|owl|hybrid",
  "multi_company": "boolean - Enable multi-company support",
  "multi_currency": "boolean - Enable multi-currency support",
  "security_level": "string - basic|advanced|audit",
  "performance_critical": "boolean - Optimize for performance",
  "custom_models": [
    {
      "name": "string - Model technical name (e.g., my.model)",
      "description": "string - Model description",
      "inherit_mail": "boolean - Inherit mail.thread",
      "fields": [
        {
          "name": "string",
          "type": "string - Char|Integer|Float|Boolean|Date|Datetime|Selection|Many2one|One2many|Many2many",
          "required": "boolean",
          "tracking": "boolean"
        }
      ]
    }
  ],
  "custom_fields": [
    {
      "model": "string - Existing model to extend",
      "name": "string - Field name",
      "type": "string",
      "params": {}
    }
  ],
  "include_tests": "boolean - Generate test files",
  "include_demo": "boolean - Generate demo data"
}
```

## Workflow 1: Generate New Module

### Step-by-Step Process

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: PARSE INPUT AND VALIDATE                                    │
├─────────────────────────────────────────────────────────────────────┤
│ - Extract module_name, odoo_version, and other parameters           │
│ - Validate module_name is snake_case                                │
│ - Validate odoo_version is supported (14.0-19.0)                    │
│ - If version not specified, ASK USER before proceeding              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: LOAD VERSION-SPECIFIC SKILLS                                │
├─────────────────────────────────────────────────────────────────────┤
│ Read these files based on detected version:                         │
│                                                                     │
│ skills/odoo-module-generator-{version}.md                           │
│ skills/odoo-model-patterns-{version}.md                             │
│ skills/odoo-security-guide-{version}.md                             │
│                                                                     │
│ If UI includes OWL:                                                 │
│ skills/odoo-owl-components-{version}.md                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: GENERATE MODULE STRUCTURE                                   │
├─────────────────────────────────────────────────────────────────────┤
│ Create directory structure:                                         │
│                                                                     │
│ {module_name}/                                                      │
│ ├── __init__.py                                                     │
│ ├── __manifest__.py                                                 │
│ ├── models/                                                         │
│ │   ├── __init__.py                                                 │
│ │   └── {model_files}.py                                            │
│ ├── views/                                                          │
│ │   ├── {model}_views.xml                                           │
│ │   └── menuitems.xml                                               │
│ ├── security/                                                       │
│ │   ├── {module}_security.xml  (groups first!)                      │
│ │   └── ir.model.access.csv                                         │
│ ├── data/                                                           │
│ │   └── {data_files}.xml                                            │
│ ├── static/                                                         │
│ │   └── src/                                                        │
│ │       ├── js/                                                     │
│ │       ├── xml/                                                    │
│ │       └── scss/                                                   │
│ └── tests/                                                          │
│     └── test_{model}.py                                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: APPLY VERSION-SPECIFIC PATTERNS                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ VERSION 14.0:                                                       │
│ - Use tracking=True (not track_visibility)                          │
│ - Single create(vals) is OK                                         │
│ - attrs in views OK                                                 │
│                                                                     │
│ VERSION 15.0:                                                       │
│ - NO @api.multi                                                     │
│ - tracking=True required                                            │
│ - attrs in views OK                                                 │
│ - OWL 1.x if needed                                                 │
│                                                                     │
│ VERSION 16.0:                                                       │
│ - Use Command class for x2many                                      │
│ - @api.model_create_multi recommended                               │
│ - Start using invisible= instead of attrs                           │
│ - OWL 2.x                                                           │
│                                                                     │
│ VERSION 17.0:                                                       │
│ - @api.model_create_multi MANDATORY                                 │
│ - NO attrs in views (use invisible/readonly/required)               │
│ - Python expressions for visibility                                 │
│ - OWL 2.x enhanced                                                  │
│                                                                     │
│ VERSION 18.0:                                                       │
│ - _check_company_auto = True                                        │
│ - check_company=True on relational fields                           │
│ - allowed_company_ids in record rules                               │
│ - SQL() builder recommended                                         │
│ - Type hints recommended                                            │
│ - OWL 2.x                                                           │
│                                                                     │
│ VERSION 19.0:                                                       │
│ - Type hints MANDATORY                                              │
│ - SQL() builder MANDATORY                                           │
│ - OWL 3.x                                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: VALIDATE AND OUTPUT                                         │
├─────────────────────────────────────────────────────────────────────┤
│ - Verify manifest data file order is correct                        │
│ - Check all XML IDs are namespaced                                  │
│ - Verify no hardcoded record IDs                                    │
│ - Output structured JSON or file tree                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Workflow 2: Review Existing Module

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: DETECT VERSION FROM __manifest__.py                         │
├─────────────────────────────────────────────────────────────────────┤
│ Pattern: 'version': '{major}.{minor}.{patch}.{sub}.{rev}'           │
│ First digit = Odoo version                                          │
│ Example: '18.0.1.0.0' → Odoo 18.0                                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: LOAD REVIEW CRITERIA                                        │
├─────────────────────────────────────────────────────────────────────┤
│ Load version-specific skill files for review criteria               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: SCAN ALL FILES                                              │
├─────────────────────────────────────────────────────────────────────┤
│ Use Glob and Grep to find:                                          │
│ - Python files: *.py                                                │
│ - XML files: *.xml                                                  │
│ - JavaScript: *.js                                                  │
│ - Security: ir.model.access.csv                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: CHECK PATTERNS                                              │
├─────────────────────────────────────────────────────────────────────┤
│ Search for version-incorrect patterns:                              │
│                                                                     │
│ v15+: "@api.multi" → ERROR                                          │
│ v15+: "track_visibility" → WARN (deprecated)                        │
│ v17+: "attrs=" → ERROR (removed)                                    │
│ v17+: "def create(self, vals):" without _create_multi → ERROR       │
│ v18+: Missing _check_company_auto → WARN                            │
│ v19+: Missing type hints → ERROR                                    │
│ v19+: Raw SQL without SQL() → ERROR                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: OUTPUT REVIEW REPORT                                        │
├─────────────────────────────────────────────────────────────────────┤
│ Format: Markdown with severity levels                               │
│ - CRITICAL: Must fix (breaking errors)                              │
│ - WARNING: Should fix (deprecations)                                │
│ - INFO: Nice to have (improvements)                                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Workflow 3: Upgrade Module Between Versions

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: IDENTIFY SOURCE AND TARGET VERSIONS                         │
├─────────────────────────────────────────────────────────────────────┤
│ Source: Current version in __manifest__.py                          │
│ Target: User-specified target version                               │
│ Calculate jump: single (16→17) or multi (15→18)                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: LOAD ALL MIGRATION GUIDES IN PATH                           │
├─────────────────────────────────────────────────────────────────────┤
│ For 16→18 upgrade, load:                                            │
│ - odoo-*-16-17.md (all categories)                                  │
│ - odoo-*-17-18.md (all categories)                                  │
│                                                                     │
│ Categories:                                                         │
│ - module-generator                                                  │
│ - model-patterns                                                    │
│ - security-guide                                                    │
│ - owl-components                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: SCAN FOR BREAKING CHANGES                                   │
├─────────────────────────────────────────────────────────────────────┤
│ Search patterns that need migration:                                │
│                                                                     │
│ 15→16: Check for tuple x2many → Command class                       │
│ 16→17: Check for attrs= → direct attributes                         │
│ 17→18: Check for company_ids → allowed_company_ids                  │
│ 18→19: Check for missing type hints                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: GENERATE MIGRATION PLAN                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Output detailed plan with:                                          │
│ - Breaking changes (file:line, before/after code)                   │
│ - Deprecation warnings                                              │
│ - New features available                                            │
│ - Migration scripts if needed                                       │
│ - Estimated effort                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## GitHub Verification Process

When uncertain about patterns, verify against official Odoo repository:

```
┌─────────────────────────────────────────────────────────────────────┐
│ GITHUB VERIFICATION WORKFLOW                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 1. Identify pattern to verify                                       │
│    Example: "Is @api.model_create_multi required in v18?"           │
│                                                                     │
│ 2. Construct raw GitHub URL                                         │
│    Base: https://raw.githubusercontent.com/odoo/odoo/{branch}/      │
│                                                                     │
│    Branches:                                                        │
│    - 14.0, 15.0, 16.0, 17.0, 18.0 for stable versions              │
│    - master for 19.0 development                                    │
│                                                                     │
│ 3. Use WebFetch to retrieve file                                    │
│    URL: https://raw.githubusercontent.com/odoo/odoo/18.0/           │
│          addons/sale/models/sale_order.py                           │
│    Prompt: "Show create method signature and decorators"            │
│                                                                     │
│ 4. Analyze response and confirm pattern                             │
│                                                                     │
│ 5. Document verification in output                                  │
│    "Verified against Odoo 18.0 official repository"                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Reference Files by Component

| Component | File Path |
|-----------|-----------|
| ORM/Models | `odoo/models.py` |
| Fields | `odoo/fields.py` |
| API decorators | `odoo/api.py` |
| Sale example | `addons/sale/models/sale_order.py` |
| View example | `addons/sale/views/sale_order_views.xml` |
| Security example | `addons/sale/security/sale_security.xml` |
| OWL hooks | `addons/web/static/src/core/utils/hooks.js` |

## Example Agent Calls

### Example 1: Generate Basic Module for v18

```json
{
  "action": "generate",
  "params": {
    "module_name": "equipment_tracking",
    "module_description": "Track company equipment and assignments",
    "odoo_version": "18.0",
    "target_apps": ["hr"],
    "multi_company": true,
    "security_level": "basic",
    "custom_models": [
      {
        "name": "equipment.item",
        "description": "Equipment Item",
        "inherit_mail": true,
        "fields": [
          {"name": "name", "type": "Char", "required": true, "tracking": true},
          {"name": "serial_number", "type": "Char", "required": true},
          {"name": "employee_id", "type": "Many2one", "comodel": "hr.employee"},
          {"name": "state", "type": "Selection", "selection": [["available", "Available"], ["assigned", "Assigned"], ["maintenance", "Maintenance"]], "tracking": true}
        ]
      }
    ]
  }
}
```

**Agent Response Should Include:**
1. Complete file tree with all code
2. Version-specific patterns applied (v18: `_check_company_auto`, `check_company=True`)
3. Proper manifest with correct data file ordering
4. Security groups defined before access rights

### Example 2: Review Module for v17

```json
{
  "action": "review",
  "params": {
    "module_path": "/path/to/module",
    "expected_version": "17.0"
  }
}
```

**Agent Response Should Include:**
1. Version compliance check (attrs removed, create_multi used)
2. Security audit
3. Performance recommendations
4. File-by-file issues with line numbers

### Example 3: Upgrade Module 16→18

```json
{
  "action": "upgrade",
  "params": {
    "module_path": "/path/to/module",
    "source_version": "16.0",
    "target_version": "18.0"
  }
}
```

**Agent Response Should Include:**
1. Multi-hop migration plan (16→17→18)
2. All breaking changes identified
3. Before/after code examples
4. Migration scripts if needed

## Structured Output Format

AI agents should return structured output:

```json
{
  "status": "success|error",
  "odoo_version": "18.0",
  "module_name": "equipment_tracking",
  "files": {
    "__manifest__.py": "# File content...",
    "__init__.py": "# File content...",
    "models/__init__.py": "# File content...",
    "models/equipment_item.py": "# File content...",
    "views/equipment_item_views.xml": "# File content...",
    "views/menuitems.xml": "# File content...",
    "security/equipment_tracking_security.xml": "# File content...",
    "security/ir.model.access.csv": "# File content..."
  },
  "version_notes": [
    "Using @api.model_create_multi for batch creates (v17+ mandatory)",
    "Using _check_company_auto for multi-company (v18 pattern)",
    "Using check_company=True on employee_id field (v18 pattern)",
    "Using direct invisible/readonly attributes (v17+ required)"
  ],
  "warnings": [],
  "github_verified": true,
  "verification_details": "Patterns verified against odoo/odoo 18.0 branch"
}
```

## Critical Reminders

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                           NEVER DO THIS                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ✗ Generate code without knowing the Odoo version                             ║
║ ✗ Mix patterns from different versions                                       ║
║ ✗ Use attrs in v17+ views                                                    ║
║ ✗ Use @api.multi in v15+                                                     ║
║ ✗ Use single create(vals) in v17+ (must use create_multi)                    ║
║ ✗ Put views before security groups in manifest                               ║
║ ✗ Use hardcoded IDs (e.g., res_id="1")                                       ║
║ ✗ Skip security files (ir.model.access.csv is mandatory)                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                           ALWAYS DO THIS                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ✓ Identify Odoo version before any code generation                           ║
║ ✓ Load version-specific skill files                                          ║
║ ✓ Order manifest data files: security → data → views → menus                 ║
║ ✓ Use XML IDs with module prefix (my_module.record_id)                       ║
║ ✓ Create ir.model.access.csv for ALL new models                              ║
║ ✓ Use version-appropriate decorators and patterns                            ║
║ ✓ Verify patterns against GitHub when uncertain                              ║
║ ✓ Include tracking=True for auditable fields                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Quick Reference Card

### Version Detection Patterns

| If you see... | Version is... |
|---------------|---------------|
| `@api.multi` | 14.0 (deprecated) |
| `track_visibility` | 14.0 |
| `tracking=True` only | 15.0+ |
| `Command.create()` | 16.0+ |
| `attrs="{'invisible':...}"` | ≤16.0 |
| `invisible="state == 'draft'"` | 17.0+ |
| `_check_company_auto` | 18.0+ |
| Type hints on fields | 18.0+ |
| `SQL()` builder | 18.0+ |
| Mandatory type hints | 19.0 |

### File Loading Decision Tree

```
Is this a NEW module generation?
├─ YES → Load odoo-module-generator-{version}.md
│        Load odoo-model-patterns-{version}.md
│        Load odoo-security-guide-{version}.md
│        (If OWL) Load odoo-owl-components-{version}.md
│
├─ Is this a CODE REVIEW?
│  └─ YES → Load odoo-model-patterns-{version}.md
│           Load odoo-security-guide-{version}.md
│
└─ Is this an UPGRADE?
   └─ YES → Load ALL odoo-*-{source}-{target}.md files
            for each hop in the migration path
```
