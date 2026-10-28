---
name: odoo-review
description: |
  MUST be invoked when user asks to "review odoo module", "audit module", "check security", "analyze code quality".
  CRITICAL: This command MUST invoke the odoo-code-reviewer agent for systematic review.
  DO NOT perform manual reviews - ALWAYS use the specialized agent.
arguments:
  - name: path
    description: Path to the module to review
    required: false
  - name: version
    description: Target Odoo version for review criteria
    required: false
input_examples:
  - description: "Review module in current directory"
    arguments: {}
  - description: "Review specific module for Odoo 18"
    arguments:
      path: "./custom_addons/inventory_tracker"
      version: "18.0"
  - description: "Security-focused review of HR module"
    arguments:
      path: "./hr_custom"
---

# /odoo-review Command

Review an Odoo module for best practices, security vulnerabilities, performance issues, and version compatibility.

## CRITICAL: VERSION REQUIREMENT

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  Review criteria depend on the target Odoo version.                          ║
║  You MUST determine the version before reviewing.                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## CRITICAL: MANDATORY AGENT INVOCATION

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  You MUST invoke the odoo-code-reviewer agent to perform the review.         ║
║  DO NOT perform manual code reviews - the agent has systematic checklists.   ║
║                                                                              ║
║  Invoke: Task tool with subagent_type="odoo-development:odoo-code-reviewer"  ║
║  Prompt: "Review module at [path] for version [version]"                     ║
║                                                                              ║
║  NEVER skip this step. Agent-based review is MANDATORY.                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### NO PARALLEL EXPLORATION WHILE THE AGENT RUNS

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  When dispatching odoo-code-reviewer, you MUST NOT in the same message       ║
║  (or while waiting for its result) run Bash/Read/Grep/Glob calls that        ║
║  inspect the module being reviewed. The reviewer agent reads those files     ║
║  systematically; duplicating its work wastes tokens and produces overlapping ║
║  output.                                                                     ║
║                                                                              ║
║  Allowed in parallel with the agent:                                         ║
║    - Reading project CLAUDE.md or memory files.                              ║
║    - Dispatching a SECOND agent on a DISJOINT subject (e.g. a different      ║
║      module).                                                                ║
║                                                                              ║
║  Forbidden in parallel with the agent:                                       ║
║    - Reading any file inside the module path passed to the agent.            ║
║    - Grepping for patterns the reviewer would already check.                 ║
║    - Cat-ing the manifest of the module under review.                        ║
║                                                                              ║
║  Default behavior: dispatch the reviewer ALONE, wait for its report, THEN    ║
║  inspect anything the report did not cover.                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Execution Flow

### Step 1: Identify Module and Version

If not provided:
1. Look for `__manifest__.py` in current directory or ask for path
2. Extract version from manifest's `version` field (e.g., `18.0.1.0.0`)
3. If unclear, ask the user

### Step 2: Perform Review (official Odoo review process)

The agent follows Odoo's official `odoo-review` process (odoo/odoo `skills/`, branch 20.0), adapted to 14.0-19.0; full text in `agents/odoo-code-reviewer.md`:

1. **Scope**: pin the reviewed commit and its base; read the diff, the manifests (`depends`), commit messages and PR description from that checkout only. Note whether the target is a released version. Review an Enterprise/Community other half together.
2. **Map** every changed file to the plugin guideline files of the target version that apply (Python -> `odoo-model-patterns-{version}.md`, controllers/security/sudo/SQL -> `odoo-security-guide-{version}.md` + audit sweep, XML -> `xml-view-patterns.md`, `static/` -> OWL guide, `tests/` -> `odoo-test-patterns.md`, released target -> stable-branch policy).
3. **Read** every mapped section before the first finding.
4. **Rules pass** against the mapped sections and the Review Categories below, including code the diff never shows: overrides of changed methods, renamed names in Python/XML/JS (xpaths, domains, `patch()`), shared context keys and their JS twin, the Enterprise half.
5. **Merits pass**: edge values, rounding, timezones, empty and multi-record `self`, concurrency, the second run, tests that would fail without the change, cost at scale.
6. **Version traps**: confirm every API flagged or recommended exists in the target version (`odoo-version-knowledge-all.md` cross-version table); never recommend master/20.0-only APIs.
7. **Report** each finding with file/line, defect, failure scenario, fix, and rule or *judgement*; end with a **Guidelines read:** line.

## Review Categories

### 1. Security Review
- [ ] Access rights defined (ir.model.access.csv)
- [ ] Record rules for multi-company
- [ ] Field-level security (groups attribute)
- [ ] No SQL injection vulnerabilities
- [ ] No sudo() abuse
- [ ] No hardcoded IDs
- [ ] XSS prevention in views
- [ ] Proper input validation

### 2. Code Quality Review
- [ ] Follows version-specific patterns
- [ ] Proper use of decorators
- [ ] Correct method signatures
- [ ] Proper inheritance patterns
- [ ] No deprecated APIs
- [ ] Clear code organization

### 3. Performance Review
- [ ] Indexed fields for search
- [ ] Stored computed fields where appropriate
- [ ] No N+1 query patterns
- [ ] Efficient batch operations
- [ ] Proper use of prefetch

### 4. View Review
- [ ] Version-appropriate visibility syntax
- [ ] Proper group restrictions
- [ ] Accessible UI design
- [ ] Consistent naming

### 5. Manifest Review
- [ ] Correct version format
- [ ] All dependencies declared
- [ ] Data files listed correctly
- [ ] Appropriate license
- [ ] Assets declared (v15+)

### 6. Test Coverage
- [ ] Unit tests present
- [ ] Security tests
- [ ] Edge cases covered
- [ ] Proper test isolation

## Output Format

```markdown
# Module Review: {module_name}
## Target Version: {version}

### Summary
- **Security Score**: X/10
- **Code Quality Score**: X/10
- **Performance Score**: X/10
- **Overall Score**: X/10

### Critical Issues (Must Fix)
1. [SECURITY] `file:line` - defect / failure scenario / fix / rule
2. [SECURITY] ...

### Warnings (Should Fix)
1. [PERFORMANCE] `file:line` - defect / failure scenario / fix / rule
2. [DEPRECATED] ...

### Suggestions (Nice to Have)
1. [QUALITY] `file:line` - defect / failure scenario / fix / *judgement*

### Files Reviewed
- models/model.py: X issues
- views/views.xml: X issues
- security/ir.model.access.csv: X issues

### Version-Specific Notes
- For v{version}, consider...
- Deprecated pattern found: ...

**Guidelines read:** <every guideline file/section opened>
```

## Version-Specific Checks

Full list in `agents/odoo-code-reviewer.md`; cross-version API table in `skills/odoo-version-knowledge-all.md`.

### All versions (14-19)
- `@api.multi`/`@api.one` are removed; `track_visibility` only warns (use `tracking`)
- `allowed_company_ids` is not available in record rules (use `company_ids`)
- `_check_company_auto`/`check_company=True` exist in every version

### Odoo 14
- No `Command` (tuples), no `t-out`, no manifest `assets` key

### Odoo 15
- `Command` available; prefer `t-out` (`t-raw` deprecated but still raw)

### Odoo 16
- `attrs`/`states` are still the correct view syntax
- Owl 2 patterns

### Odoo 17
- Error if `attrs`/`states` are used (removed)
- `_read_group` tuple API, `SQL` builder available

### Odoo 18
- `<list>` instead of `<tree>`
- `check_access()` instead of deprecated `check_access_rights`/`check_access_rule`

### Odoo 19
- Error on `_sql_constraints` (silently ignored)
- `group_ids` on users, `fields.Domain`; type hints and the `SQL` builder are not mandatory

## Example Usage

```
# Review module in current directory
/odoo-review

# Review specific path
/odoo-review ./my_module

# Review for specific version
/odoo-review ./my_module 18.0
```

## AI Agent Instructions

1. **IDENTIFY**: Determine module path and target version
2. **MANDATORY**: Invoke `odoo-development:odoo-code-reviewer` agent
   - Dispatch the agent **alone** in its own tool-use message.
   - Do NOT in the same message (or while waiting for the result) run Bash/Read/Grep/Glob
     against the module being reviewed. See "NO PARALLEL EXPLORATION".
   - Wait for the agent's report before any further file inspection.
3. **LOAD**: Version-specific review criteria (done by agent)
4. **SCAN**: All module files systematically (done by agent)
5. **CATEGORIZE**: Issues by severity and type (done by agent)
6. **REPORT**: Structured review with actionable recommendations
7. **PRIORITIZE**: Critical security issues first

**CRITICAL**: Step 2 is MANDATORY. NEVER perform manual reviews without the agent,
and NEVER duplicate its work with parallel file exploration.
