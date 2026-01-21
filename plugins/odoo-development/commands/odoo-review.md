---
name: odoo-review
description: Review an Odoo module for best practices, security issues, and performance. Use when user asks to "review odoo module", "audit module", "check security", "analyze code quality".
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

## Execution Flow

### Step 1: Identify Module and Version

If not provided:
1. Look for `__manifest__.py` in current directory or ask for path
2. Extract version from manifest's `version` field (e.g., `18.0.1.0.0`)
3. If unclear, ask the user

### Step 2: Load Version-Specific Knowledge

```
Read: odoo-development/skills/odoo-security-guide-{version}.md
Read: odoo-development/skills/odoo-model-patterns-{version}.md
```

### Step 3: Perform Review

Review the module against these categories:

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
1. [SECURITY] Description...
2. [SECURITY] Description...

### Warnings (Should Fix)
1. [PERFORMANCE] Description...
2. [DEPRECATED] Description...

### Suggestions (Nice to Have)
1. [QUALITY] Description...

### Files Reviewed
- models/model.py: X issues
- views/views.xml: X issues
- security/ir.model.access.csv: X issues

### Version-Specific Notes
- For v{version}, consider...
- Deprecated pattern found: ...
```

## Version-Specific Checks

### Odoo 14
- Check for `@api.multi` (deprecated)
- Check for `track_visibility` usage

### Odoo 15
- Ensure `@api.multi` is removed
- Check `tracking` is used instead of `track_visibility`

### Odoo 16
- Check for `Command` class usage
- Warn about `attrs` deprecation

### Odoo 17
- Error if `attrs` is used (removed)
- Check `@api.model_create_multi` is used

### Odoo 18
- Check for `_check_company_auto`
- Recommend type hints
- Recommend `SQL()` builder
- Check `allowed_company_ids` in rules

### Odoo 19
- Error if no type hints
- Error if raw SQL without `SQL()` builder

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
2. **LOAD**: Version-specific review criteria
3. **SCAN**: All module files systematically
4. **CATEGORIZE**: Issues by severity and type
5. **REPORT**: Structured review with actionable recommendations
6. **PRIORITIZE**: Critical security issues first
