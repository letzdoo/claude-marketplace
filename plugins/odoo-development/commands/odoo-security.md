---
name: odoo-security
description: Generate or audit security configuration for an Odoo module. Use when user asks to "generate security", "add access rights", "create record rules", "audit permissions".
arguments:
  - name: action
    description: Action to perform (generate, audit)
    required: false
  - name: path
    description: Path to the module
    required: false
  - name: version
    description: Target Odoo version
    required: false
input_examples:
  - description: "Generate security for new module"
    arguments:
      action: "generate"
      path: "./inventory_tracker"
      version: "18.0"
  - description: "Audit existing module security"
    arguments:
      action: "audit"
      path: "./hr_custom"
  - description: "Interactive security generation"
    arguments: {}
---

# /odoo-security Command

Generate security configuration or audit existing security for an Odoo module.

## CRITICAL: VERSION REQUIREMENT

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  Security patterns differ between Odoo versions.                             ║
║  Using wrong patterns can create security vulnerabilities.                   ║
║  ALWAYS identify the target version before generating security code.         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Actions

### Generate Security (`/odoo-security generate`)

Generate complete security configuration for a module:

1. Security groups (res.groups)
2. Access rights (ir.model.access.csv)
3. Record rules (ir.rule)
4. Field-level security

### Audit Security (`/odoo-security audit`)

Review existing security configuration for:

1. Missing access rights
2. Overly permissive rules
3. SQL injection vulnerabilities
4. sudo() abuse
5. Hardcoded IDs
6. Missing multi-company rules

## Execution Flow

### Step 1: Determine Action and Version

```
What would you like to do?
1. Generate new security configuration
2. Audit existing security

What Odoo version? (14.0-19.0)
```

### Step 2: Load Version-Specific Skill

```
Read: odoo-development/skills/odoo-security-guide-{version}.md
```

### Step 3: Gather Information (for generate)

- Module name
- Model names
- Security level (basic, advanced, audit-grade)
- Multi-company requirement
- User roles needed

### Step 4: Execute Action

## Security Level Definitions

### Basic
- User group (CRUD on own records)
- Manager group (CRUD on all records)
- Simple multi-company rule

### Advanced
- Viewer group (read-only)
- Editor group (read, write, create)
- Manager group (full access)
- Field-level restrictions
- Record rules by team/department

### Audit-Grade
- Separate permissions (read, create, edit, delete)
- Audit logging
- Change tracking
- Immutable logs
- IP tracking
- Full separation of duties

## Output Format (Generate)

```
security/
├── {module_name}_security.xml    # Groups and record rules
└── ir.model.access.csv           # Access rights
```

### Groups XML Template
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Groups, rules, categories -->
</odoo>
```

### Access Rights CSV
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

## Output Format (Audit)

```markdown
# Security Audit: {module_name}
## Version: {version}

### Security Score: X/10

### Critical Issues
1. [CRITICAL] Missing access rights for model X
2. [CRITICAL] SQL injection vulnerability in file:line

### Warnings
1. [WARNING] Overly permissive rule...
2. [WARNING] sudo() usage without justification

### Recommendations
1. Add field groups to sensitive fields
2. Implement audit logging

### Files Reviewed
- security/ir.model.access.csv: X issues
- security/security.xml: X issues
- models/*.py: X issues
```

## Version-Specific Patterns

### v14-16
```xml
<field name="domain_force">[('company_id', 'in', company_ids)]</field>
```

### v17
```xml
<field name="domain_force">[('company_id', 'in', company_ids)]</field>
<!-- Same but no attrs in views -->
```

### v18+
```xml
<field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>
```

```python
_check_company_auto = True
partner_id = fields.Many2one('res.partner', check_company=True)
```

## Example Usage

```
# Generate security for current module
/odoo-security generate

# Audit existing security
/odoo-security audit ./my_module

# Generate for specific version
/odoo-security generate ./my_module 18.0
```

## AI Agent Instructions

1. **DETERMINE**: Action (generate or audit) and version
2. **LOAD**: Version-specific security guide
3. **FOR GENERATE**:
   - Gather model information
   - Apply security level patterns
   - Generate version-appropriate code
4. **FOR AUDIT**:
   - Scan all security-related files
   - Check for vulnerabilities
   - Verify patterns match version
5. **OUTPUT**: Structured results with actionable items
