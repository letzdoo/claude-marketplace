---
name: odoo-module
description: |
  MUST be invoked when user asks to "create odoo module", "generate module", "scaffold odoo", "new odoo app".
  CRITICAL: This command MUST invoke the odoo-context-gatherer agent before generating any code.
arguments:
  - name: version
    description: Target Odoo version (14.0, 15.0, 16.0, 17.0, 18.0, 19.0)
    required: false
  - name: name
    description: Technical module name (snake_case)
    required: false
input_examples:
  - description: "Generate inventory tracking module for Odoo 18"
    arguments:
      version: "18.0"
      name: "inventory_tracker"
  - description: "Create HR extension module"
    arguments:
      version: "17.0"
      name: "hr_custom_fields"
  - description: "Interactive mode - will prompt for details"
    arguments: {}
---

# /odoo-module Command

Generate a production-ready Odoo module following version-specific best practices.

## CRITICAL: VERSION REQUIREMENT

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  Before generating any code, you MUST determine the target Odoo version.     ║
║  Then load the version-specific skill file.                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## CRITICAL: MANDATORY AGENT INVOCATION

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  You MUST invoke the odoo-context-gatherer agent BEFORE generating code.     ║
║  DO NOT proceed to code generation without context from this agent.          ║
║                                                                              ║
║  Invoke: Task tool with subagent_type="odoo-development:odoo-context-gatherer"║
║  Prompt: "[User's task description]" + "version: [detected version]"         ║
║                                                                              ║
║  NEVER skip this step. Context gathering is MANDATORY.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### NO PARALLEL EXPLORATION WHILE THE AGENT RUNS

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  When dispatching odoo-context-gatherer, you MUST NOT in the same message    ║
║  (or while waiting for its result) run Bash/Read/Grep/Glob calls that        ║
║  inspect the same modules, models, or files the agent will examine.          ║
║  Duplicating its work wastes tokens and produces overlapping output the      ║
║  user has to mentally merge.                                                 ║
║                                                                              ║
║  Allowed in parallel with the agent:                                         ║
║    - Reading the project CLAUDE.md or memory files.                          ║
║    - Reading the manifest of the NEW module being created (does not exist    ║
║      yet, so the agent cannot examine it).                                   ║
║    - Dispatching a SECOND agent on a DISJOINT subject.                       ║
║                                                                              ║
║  Forbidden in parallel with the agent:                                       ║
║    - Grepping or listing files in the modules named in the agent prompt.    ║
║    - Reading model/view/security files of the same Odoo apps the agent is   ║
║      gathering patterns for.                                                 ║
║    - Cat-ing manifests of modules the agent has been asked to study.        ║
║                                                                              ║
║  Default behavior: dispatch the agent ALONE, wait for its report, THEN       ║
║  explore anything the report did not cover.                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Execution Flow

### Step 1: Determine Odoo Version

If version argument is not provided, ASK the user:

```
What Odoo version should I target?
- 14.0 (Legacy)
- 15.0 (Legacy)
- 16.0 (Supported)
- 17.0 (Supported)
- 18.0 (Current) - Recommended
- 19.0 (Development)
```

### Step 2: Load Version-Specific Skill

Based on the version, load the appropriate skill file:

```
Read: odoo-development/skills/odoo-module-generator-{version}.md
```

For example, for Odoo 18.0:
```
Read: odoo-development/skills/odoo-module-generator-18.md
```

### Step 3: Gather Module Information

If not provided as arguments, ask the user:

**Required:**
- Module name (technical name, lowercase with underscores)
- Module description (human-readable)

**Optional (ask based on use case):**
- Target apps to extend (CRM, Sale, Purchase, HR, etc.)
- UI stack preference (OWL, classic, hybrid)
- Multi-company support needed?
- Security level (basic, advanced, audit)
- Custom models to create
- Custom fields to add to existing models

### Step 4: Generate Module Structure

Using the version-specific patterns, generate:

1. **__manifest__.py** - Module metadata
2. **__init__.py** - Package initialization
3. **models/** - Python model files
4. **views/** - XML view definitions
5. **security/** - Access rights and record rules
6. **static/** - Web assets (if OWL components needed)
7. **tests/** - Unit test files

### Step 5: Provide Next Steps

After generation, provide:
- Installation instructions
- Testing recommendations
- Documentation links
- Upgrade considerations

## Example Usage

```
/odoo-module 18.0 custom_inventory

# Or interactive:
/odoo-module
```

## Output Format

Generate files in the current working directory:

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── {model_name}.py
├── views/
│   ├── {model_name}_views.xml
│   └── menuitems.xml
├── security/
│   ├── ir.model.access.csv
│   └── {module_name}_security.xml
└── tests/
    ├── __init__.py
    └── test_{model_name}.py
```

## Version-Specific Considerations

### For Odoo 14-15
- Use `attrs` in views
- Use `track_visibility` (v14) or `tracking` (v15)

### For Odoo 16
- Use `Command` class
- Transition from `attrs` to direct attributes

### For Odoo 17
- No `attrs` in views
- `@api.model_create_multi` mandatory

### For Odoo 18
- `_check_company_auto` + `check_company=True` are opt-in (available since 14.0)
- Add type hints to fields
- Use `company_ids` in record rules (`allowed_company_ids` is not available there)

### For Odoo 19
- Full type annotations required
- `SQL()` builder required

## AI Agent Instructions

1. **FIRST**: Determine Odoo version (ask if not provided)
2. **MANDATORY**: Invoke `odoo-development:odoo-context-gatherer` agent with task description
   - Dispatch the agent **alone** in its own tool-use message.
   - Do NOT in the same message (or while waiting for the result) run Bash/Read/Grep/Glob
     against modules, models, or files the agent will examine. See "NO PARALLEL EXPLORATION".
   - Wait for the agent's report before any further file inspection.
3. **THEN**: Load the version-specific module generator skill
4. **GATHER**: Required information from user
5. **GENERATE**: Version-appropriate code using patterns from context gatherer
6. **VERIFY**: Code follows version-specific patterns
7. **OUTPUT**: Complete module structure

**CRITICAL**: Step 2 is MANDATORY. NEVER skip the context gatherer agent invocation,
and NEVER duplicate its work with parallel file exploration.
