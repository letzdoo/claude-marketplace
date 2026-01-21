# Odoo Module Generator - Version Dispatcher

## CRITICAL: VERSION-SPECIFIC REQUIREMENTS

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ⚠️  MANDATORY VERSION MATCHING ⚠️                                          ║
║                                                                              ║
║   You MUST use the version-specific module generator that matches your       ║
║   target Odoo version. Using patterns from the wrong version WILL            ║
║   cause errors, deprecated code, or security vulnerabilities.                ║
║                                                                              ║
║   BEFORE generating ANY module code, identify your target Odoo version       ║
║   and load the corresponding file. This is NOT optional.                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Files

| Target Version | File to Use | Status |
|----------------|-------------|--------|
| Odoo 14.0 | `odoo-module-generator-14.md` | Legacy |
| Odoo 15.0 | `odoo-module-generator-15.md` | Legacy |
| Odoo 16.0 | `odoo-module-generator-16.md` | Supported |
| Odoo 17.0 | `odoo-module-generator-17.md` | Supported |
| Odoo 18.0 | `odoo-module-generator-18.md` | Current |
| Odoo 19.0 | `odoo-module-generator-19.md` | Development |
| All versions | `odoo-module-generator-all.md` | Core concepts |

## Migration Guides

When upgrading modules between versions:

| Migration Path | File |
|----------------|------|
| 14.0 → 15.0 | `odoo-module-generator-14-15.md` |
| 15.0 → 16.0 | `odoo-module-generator-15-16.md` |
| 16.0 → 17.0 | `odoo-module-generator-16-17.md` |
| 17.0 → 18.0 | `odoo-module-generator-17-18.md` |
| 18.0 → 19.0 | `odoo-module-generator-18-19.md` |

## How to Use This Skill

### Step 1: Identify Target Version

```
QUESTION: What Odoo version are you generating a module for?

If the user doesn't specify, ASK before proceeding:
"What Odoo version should I target? (14.0, 15.0, 16.0, 17.0, 18.0, 19.0)"
```

### Step 2: Load the Correct File

**For AI Agents**: You MUST read the version-specific file before generating any module code:

```
# Example for Odoo 18.0 project
Read: skills/odoo-module-generator-18.md

# Example for upgrading from 17.0 to 18.0
Read: skills/odoo-module-generator-17-18.md
```

### Step 3: Gather Input Parameters

Required parameters for module generation:

| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `module_name` | string | Yes | `custom_inventory` |
| `module_description` | string | Yes | `Custom inventory tracking` |
| `odoo_version` | string | Yes | `18.0` |
| `target_apps` | list | No | `['stock', 'sale']` |
| `ui_stack` | string | No | `owl`, `classic`, `hybrid` |
| `multi_company` | boolean | No | `true` |
| `multi_currency` | boolean | No | `false` |
| `security_level` | string | No | `basic`, `advanced`, `audit` |
| `performance_critical` | boolean | No | `false` |
| `custom_models` | list | No | List of model definitions |
| `custom_fields` | list | No | Fields to add to existing models |

### Step 4: Apply Version-Specific Patterns

Only use patterns from the loaded version-specific file. Never mix patterns from different versions.

## Version Detection Hints

If the version is not explicitly stated, look for these clues in existing code:

| Indicator | Version |
|-----------|---------|
| `@api.multi` decorator | 14.0 (removed in 15.0+) |
| `track_visibility` parameter | 14.0 |
| `tracking` parameter | 15.0+ |
| Tuple syntax for x2many | 14.0-15.0 |
| `Command` class usage | 16.0+ |
| `attrs` in views | 14.0-16.0 |
| Direct `invisible`/`readonly` | 17.0+ |
| `_check_company_auto` | 18.0+ |
| Type hints on fields | 18.0+ |
| `SQL()` builder | 18.0+ |
| Full type annotations | 19.0+ |

## Quick Reference: Major Changes by Version

### v14 Key Patterns
- Single record `create(vals)`
- `track_visibility='onchange'`
- `attrs` in views
- Legacy widgets

### v15 Key Patterns
- `@api.multi` removed
- `tracking=True` replaces `track_visibility`
- OWL 1.x introduced

### v16 Key Patterns
- `Command` class for x2many
- `attrs` deprecated (still works)
- OWL 2.x
- `@api.model_create_multi` recommended

### v17 Key Patterns
- `attrs` removed from views
- Direct `invisible`/`readonly` attributes
- `@api.model_create_multi` mandatory
- Python expressions in visibility

### v18 Key Patterns
- `_check_company_auto = True`
- `check_company=True` on fields
- Type hints recommended
- `SQL()` builder recommended
- `allowed_company_ids` in rules

### v19 Key Patterns
- Type hints mandatory
- `SQL()` builder mandatory
- OWL 3.x
- Python 3.12+

## Structured Output Format

AI agents should produce structured output for programmatic consumption:

```json
{
  "module_skeleton": {
    "name": "module_name",
    "version": "18.0.1.0.0",
    "odoo_version": "18.0",
    "files": {
      "__manifest__.py": "...",
      "__init__.py": "...",
      "models/__init__.py": "...",
      "models/model_name.py": "...",
      "views/model_name_views.xml": "...",
      "views/menuitems.xml": "...",
      "security/ir.model.access.csv": "...",
      "security/module_name_security.xml": "..."
    }
  },
  "version_instructions": [
    "Instruction 1 specific to version",
    "Instruction 2 specific to version"
  ],
  "warnings": [
    "Warning about potential issues"
  ],
  "dependencies": ["base", "mail"],
  "github_verified": true,
  "verification_date": "2025-01-16"
}
```

## GitHub Repository Verification

Before generating modules, agents SHOULD verify patterns against:

**Official Odoo Repository**: https://github.com/odoo/odoo

| Version | Branch |
|---------|--------|
| 14.0 | `14.0` |
| 15.0 | `15.0` |
| 16.0 | `16.0` |
| 17.0 | `17.0` |
| 18.0 | `18.0` |
| 19.0 | `master` |

## Example Module Generation Requests

### Example 1: Basic Inventory Module (v18)

**User Request**:
```
Create an Odoo 18.0 module for tracking equipment assets with:
- Equipment model with name, serial number, purchase date, status
- Assignment to employees
- Maintenance scheduling
- Multi-company support
```

**Agent Workflow**:
1. Identify version: `18.0`
2. Load: `skills/odoo-module-generator-18.md`
3. Load: `skills/odoo-model-patterns-18.md`
4. Generate with v18 patterns:
   - `_check_company_auto = True`
   - `@api.model_create_multi`
   - `check_company=True` on employee relation
   - Direct `invisible`/`readonly` in views

### Example 2: Sales Extension (v17)

**User Request**:
```
Add custom discount approval workflow to Odoo 17.0 sales module
```

**Agent Workflow**:
1. Identify version: `17.0`
2. Load: `skills/odoo-module-generator-17.md`
3. Load: `skills/odoo-model-patterns-17.md`
4. Generate with v17 patterns:
   - Extend `sale.order`
   - `@api.model_create_multi`
   - Python expressions for visibility (`invisible="discount > 20"`)
   - NO `attrs` usage

### Example 3: Dashboard Component (v18)

**User Request**:
```
Create a KPI dashboard for Odoo 18.0 with charts and real-time data
```

**Agent Workflow**:
1. Identify version: `18.0`
2. Load: `skills/odoo-owl-components-18.md`
3. Load: `skills/odoo-module-generator-18.md`
4. Generate with v18 OWL 2.x patterns:
   - `/** @odoo-module **/`
   - `import { Component } from "@odoo/owl"`
   - `useService("orm")` for data
   - Register as client action

### Example 4: Migration Project (v16 → v17)

**User Request**:
```
Upgrade our custom CRM module from Odoo 16.0 to 17.0
```

**Agent Workflow**:
1. Load migration guide: `skills/odoo-module-generator-16-17.md`
2. Key changes to apply:
   - Remove ALL `attrs` from views
   - Add `@api.model_create_multi` to all `create()` methods
   - Convert domain syntax to Python expressions
   - Update manifest version to `17.0.x.x.x`

### Example 5: Multi-Company HR Module (v18)

**User Request**:
```json
{
  "module_name": "hr_custom_leave",
  "module_description": "Custom leave management with approval workflow",
  "odoo_version": "18.0",
  "target_apps": ["hr", "hr_holidays"],
  "multi_company": true,
  "security_level": "advanced",
  "custom_models": [
    {
      "name": "hr.leave.type.custom",
      "description": "Custom Leave Type",
      "fields": [
        {"name": "name", "type": "Char", "required": true},
        {"name": "requires_approval", "type": "Boolean"},
        {"name": "max_days", "type": "Integer"}
      ]
    }
  ]
}
```

**Agent Workflow**:
1. Parse structured input
2. Load v18 patterns
3. Generate complete module skeleton with:
   - Multi-company record rules using `allowed_company_ids`
   - `_check_company_auto = True` on models
   - Advanced security groups
   - Type hints on methods

## Structured Input Schema

For programmatic module generation, use this JSON schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["module_name", "module_description", "odoo_version"],
  "properties": {
    "module_name": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_]*$",
      "description": "Technical module name (snake_case)"
    },
    "module_description": {
      "type": "string",
      "description": "Human-readable description"
    },
    "odoo_version": {
      "type": "string",
      "enum": ["14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]
    },
    "target_apps": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Odoo apps to extend"
    },
    "multi_company": {
      "type": "boolean",
      "default": false
    },
    "multi_currency": {
      "type": "boolean",
      "default": false
    },
    "security_level": {
      "type": "string",
      "enum": ["basic", "advanced", "audit"],
      "default": "basic"
    },
    "custom_models": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"},
          "inherit_mail": {"type": "boolean"},
          "fields": {"type": "array"}
        }
      }
    },
    "custom_fields": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "model": {"type": "string"},
          "name": {"type": "string"},
          "type": {"type": "string"}
        }
      }
    },
    "include_tests": {
      "type": "boolean",
      "default": true
    },
    "include_demo": {
      "type": "boolean",
      "default": false
    }
  }
}
```

---

**REMINDER**: Do not use this dispatcher file for actual module generation. Always load and follow the version-specific file for your target Odoo version.
