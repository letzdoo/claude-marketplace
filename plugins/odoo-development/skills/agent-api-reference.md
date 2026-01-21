# Agent API Reference

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  AGENT API REFERENCE                                                         ║
║  Complete reference for all workflows, endpoints, and operations             ║
║  Use this to understand available operations and their inputs/outputs        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Available Workflows

| Workflow | Purpose | Input Required |
|----------|---------|----------------|
| `generate_module` | Create new Odoo module | Module spec |
| `review_module` | Review existing module | Module path |
| `upgrade_module` | Upgrade between versions | Module path + versions |
| `generate_security` | Create security config | Model names + level |
| `generate_tests` | Create test files | Model names |
| `generate_owl` | Create OWL components | Component spec |

---

## Workflow: generate_module

### Purpose
Generate a complete, production-ready Odoo module with all required files.

### Input Schema
```json
{
  "workflow": "generate_module",
  "input": {
    "module_name": "string (required)",
    "module_description": "string (required)",
    "odoo_version": "14.0|15.0|16.0|17.0|18.0|19.0 (required)",
    "target_apps": ["sale", "purchase", ...],
    "ui_stack": "classic|owl|hybrid",
    "multi_company": true|false,
    "multi_currency": true|false,
    "security_level": "basic|advanced|audit",
    "performance_critical": true|false,
    "include_tests": true|false,
    "include_demo": true|false,
    "models": [...],
    "inherit_models": [...]
  }
}
```

### Output Schema
```json
{
  "status": "success|error",
  "module_name": "my_module",
  "odoo_version": "18.0",
  "files": {
    "__manifest__.py": "content...",
    "__init__.py": "content...",
    "models/__init__.py": "content...",
    "models/my_model.py": "content...",
    "views/my_model_views.xml": "content...",
    "views/menuitems.xml": "content...",
    "security/my_module_security.xml": "content...",
    "security/ir.model.access.csv": "content...",
    "tests/__init__.py": "content...",
    "tests/test_my_model.py": "content..."
  },
  "file_tree": [
    "my_module/",
    "├── __manifest__.py",
    "├── __init__.py",
    "├── models/",
    "│   ├── __init__.py",
    "│   └── my_model.py",
    "..."
  ],
  "version_notes": [
    "Using @api.model_create_multi for batch create",
    "Using inline visibility expressions (v17+ required)"
  ],
  "warnings": [],
  "github_verified": true
}
```

### Example Call
```json
{
  "workflow": "generate_module",
  "input": {
    "module_name": "equipment_tracking",
    "module_description": "Track company equipment with maintenance schedules",
    "odoo_version": "18.0",
    "target_apps": ["maintenance", "hr"],
    "multi_company": true,
    "security_level": "advanced",
    "include_tests": true,
    "models": [
      {
        "name": "equipment.tracking.item",
        "description": "Equipment Item",
        "inherit_mail": true,
        "has_workflow": true,
        "fields": [
          {"name": "name", "type": "Char", "required": true},
          {"name": "serial_number", "type": "Char", "index": true},
          {"name": "employee_id", "type": "Many2one", "comodel_name": "hr.employee"},
          {"name": "purchase_date", "type": "Date"},
          {"name": "purchase_value", "type": "Monetary"}
        ]
      }
    ]
  }
}
```

### Skills Loaded
- `odoo-module-generator-{version}.md`
- `odoo-model-patterns-{version}.md`
- `odoo-security-guide-{version}.md`
- `odoo-owl-components-{version}.md` (if OWL)
- `odoo-test-patterns.md` (if tests)
- `odoo-performance-guide.md` (if performance_critical)

---

## Workflow: review_module

### Purpose
Review an existing Odoo module for best practices, security, and version compliance.

### Input Schema
```json
{
  "workflow": "review_module",
  "input": {
    "module_path": "string (required)",
    "odoo_version": "14.0|15.0|16.0|17.0|18.0|19.0 (required)",
    "review_areas": ["security", "performance", "patterns", "tests"],
    "strict_mode": true|false
  }
}
```

### Output Schema
```json
{
  "status": "success",
  "module_name": "my_module",
  "odoo_version": "18.0",
  "summary": {
    "total_issues": 15,
    "critical": 2,
    "warnings": 8,
    "suggestions": 5
  },
  "issues": [
    {
      "severity": "critical|warning|suggestion",
      "category": "security|performance|pattern|test",
      "file": "models/my_model.py",
      "line": 45,
      "message": "Using @api.model instead of @api.model_create_multi",
      "fix": "Replace @api.model with @api.model_create_multi"
    }
  ],
  "security_audit": {
    "access_rights": "ok|missing|incomplete",
    "record_rules": "ok|missing|incomplete",
    "sql_injection_risk": true|false,
    "xss_risk": true|false
  },
  "performance_audit": {
    "n_plus_one_queries": [],
    "missing_indexes": [],
    "inefficient_loops": []
  },
  "version_compliance": {
    "deprecated_patterns": [],
    "missing_required_patterns": []
  }
}
```

### Example Call
```json
{
  "workflow": "review_module",
  "input": {
    "module_path": "/path/to/my_module",
    "odoo_version": "18.0",
    "review_areas": ["security", "performance", "patterns"],
    "strict_mode": true
  }
}
```

### Skills Loaded
- `odoo-model-patterns-{version}.md`
- `odoo-security-guide-{version}.md`
- `odoo-performance-guide.md`
- `odoo-troubleshooting-guide.md`

---

## Workflow: upgrade_module

### Purpose
Analyze module compatibility and generate migration plan between Odoo versions.

### Input Schema
```json
{
  "workflow": "upgrade_module",
  "input": {
    "module_path": "string (required)",
    "source_version": "14.0|15.0|16.0|17.0|18.0 (required)",
    "target_version": "15.0|16.0|17.0|18.0|19.0 (required)",
    "generate_migration_scripts": true|false,
    "preserve_data": true|false
  }
}
```

### Output Schema
```json
{
  "status": "success",
  "module_name": "my_module",
  "migration_path": ["16.0", "17.0", "18.0"],
  "breaking_changes": [
    {
      "version": "17.0",
      "change": "attrs attribute removed",
      "affected_files": ["views/my_views.xml"],
      "migration_required": true
    }
  ],
  "deprecations": [
    {
      "version": "16.0",
      "pattern": "tuple x2many operations",
      "replacement": "Command class",
      "affected_files": ["models/my_model.py"]
    }
  ],
  "migration_scripts": {
    "migrations/17.0.1.0.0/pre-migration.py": "content...",
    "migrations/17.0.1.0.0/post-migration.py": "content..."
  },
  "updated_files": {
    "models/my_model.py": "updated content...",
    "views/my_views.xml": "updated content..."
  },
  "manual_review_required": [
    "Custom JavaScript may need OWL migration",
    "SQL queries should use SQL() builder"
  ]
}
```

### Example Call
```json
{
  "workflow": "upgrade_module",
  "input": {
    "module_path": "/path/to/my_module",
    "source_version": "16.0",
    "target_version": "18.0",
    "generate_migration_scripts": true,
    "preserve_data": true
  }
}
```

### Skills Loaded (for each version hop)
- `odoo-module-generator-{source}-{target}.md`
- `odoo-model-patterns-{source}-{target}.md`
- `odoo-security-guide-{source}-{target}.md`
- `odoo-owl-components-{source}-{target}.md` (if OWL)
- `odoo-version-knowledge-{source}-{target}.md`

---

## Workflow: generate_security

### Purpose
Generate or audit security configuration for an Odoo module.

### Input Schema
```json
{
  "workflow": "generate_security",
  "input": {
    "module_name": "string (required)",
    "odoo_version": "string (required)",
    "models": ["model.name", ...],
    "security_level": "basic|advanced|audit",
    "multi_company": true|false,
    "groups": [
      {
        "name": "group_user",
        "display_name": "User",
        "permissions": {"read": true, "write": true, "create": true, "unlink": false}
      }
    ]
  }
}
```

### Output Schema
```json
{
  "status": "success",
  "files": {
    "security/my_module_security.xml": "content...",
    "security/ir.model.access.csv": "content...",
    "security/my_module_rules.xml": "content..."
  },
  "groups_created": ["group_user", "group_manager"],
  "access_rights": [
    {"model": "my.model", "group": "group_user", "permissions": "rwc-"}
  ],
  "record_rules": [
    {"model": "my.model", "rule": "company isolation", "domain": "..."}
  ]
}
```

---

## Workflow: generate_tests

### Purpose
Generate test files for Odoo models.

### Input Schema
```json
{
  "workflow": "generate_tests",
  "input": {
    "module_name": "string (required)",
    "odoo_version": "string (required)",
    "models": ["model.name", ...],
    "test_types": ["unit", "security", "integration"],
    "coverage_target": 80
  }
}
```

### Output Schema
```json
{
  "status": "success",
  "files": {
    "tests/__init__.py": "content...",
    "tests/common.py": "content...",
    "tests/test_my_model.py": "content...",
    "tests/test_security.py": "content...",
    "tests/test_integration.py": "content..."
  },
  "test_count": {
    "unit": 15,
    "security": 8,
    "integration": 5
  },
  "estimated_coverage": 85
}
```

---

## Workflow: generate_owl

### Purpose
Generate OWL components for Odoo frontend.

### Input Schema
```json
{
  "workflow": "generate_owl",
  "input": {
    "module_name": "string (required)",
    "odoo_version": "string (required)",
    "components": [
      {
        "name": "MyComponent",
        "type": "action|field|widget|systray",
        "props": [{"name": "recordId", "type": "Number", "required": true}],
        "services": ["orm", "notification", "action"],
        "features": ["state", "rpc", "effects"]
      }
    ]
  }
}
```

### Output Schema
```json
{
  "status": "success",
  "owl_version": "2.x",
  "files": {
    "static/src/js/my_component.js": "content...",
    "static/src/xml/my_component.xml": "content...",
    "static/src/scss/my_component.scss": "content..."
  },
  "manifest_assets": {
    "web.assets_backend": [
      "my_module/static/src/js/**/*",
      "my_module/static/src/xml/**/*",
      "my_module/static/src/scss/**/*"
    ]
  }
}
```

---

## File Loading Protocol

### Step 1: Identify Version
```python
version = input['odoo_version'].replace('.0', '')  # "18.0" -> "18"
```

### Step 2: Load Base Skills
```python
skills = [
    f"odoo-module-generator-{version}.md",
    f"odoo-model-patterns-{version}.md",
    f"odoo-security-guide-{version}.md",
]
```

### Step 3: Load Conditional Skills
```python
if input.get('ui_stack') in ['owl', 'hybrid']:
    skills.append(f"odoo-owl-components-{version}.md")

if input.get('performance_critical'):
    skills.append("odoo-performance-guide.md")

if input.get('include_tests'):
    skills.append("odoo-test-patterns.md")
```

### Step 4: Load Migration Skills (for upgrades)
```python
def get_migration_skills(source: str, target: str) -> list[str]:
    path = get_migration_path(source, target)
    skills = []
    for i in range(len(path) - 1):
        src = path[i].replace('.0', '')
        tgt = path[i + 1].replace('.0', '')
        skills.extend([
            f"odoo-module-generator-{src}-{tgt}.md",
            f"odoo-model-patterns-{src}-{tgt}.md",
            f"odoo-security-guide-{src}-{tgt}.md",
            f"odoo-version-knowledge-{src}-{tgt}.md",
        ])
    return skills
```

---

## Error Handling

### Error Response Schema
```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR|VERSION_ERROR|FILE_ERROR",
  "message": "Human-readable error message",
  "details": {
    "field": "module_name",
    "value": "Invalid-Name",
    "expected": "lowercase with underscores"
  },
  "suggestions": [
    "Change module_name to 'invalid_name'",
    "See input-validation-schema.md for requirements"
  ]
}
```

### Common Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `VALIDATION_ERROR` | Invalid input | Check input-validation-schema.md |
| `VERSION_ERROR` | Unsupported version | Use 14.0-19.0 |
| `FILE_ERROR` | Cannot read/write file | Check permissions |
| `PATTERN_ERROR` | Invalid code pattern | See troubleshooting guide |
| `SECURITY_ERROR` | Security config issue | See security guide |

---

## GitHub Verification

### Verify Pattern Against Source
```python
def verify_pattern(version: str, pattern_type: str) -> str:
    """Get GitHub URL for verification"""
    base = f"https://raw.githubusercontent.com/odoo/odoo/{version}"

    urls = {
        "orm": f"{base}/odoo/models.py",
        "fields": f"{base}/odoo/fields.py",
        "api": f"{base}/odoo/api.py",
        "sale": f"{base}/addons/sale/models/sale_order.py",
        "views": f"{base}/addons/sale/views/sale_order_views.xml",
    }

    return urls.get(pattern_type, base)
```

### Version Branch Mapping
```python
VERSION_BRANCHES = {
    "14.0": "14.0",
    "15.0": "15.0",
    "16.0": "16.0",
    "17.0": "17.0",
    "18.0": "18.0",
    "19.0": "master",  # Development branch
}
```

---

## Quick Reference

### Minimum Required Input
```json
{
  "module_name": "my_module",
  "module_description": "My module description",
  "odoo_version": "18.0"
}
```

### Full Featured Input
```json
{
  "module_name": "advanced_module",
  "module_description": "Full-featured module with all options",
  "odoo_version": "18.0",
  "target_apps": ["sale", "account", "mail"],
  "ui_stack": "hybrid",
  "multi_company": true,
  "multi_currency": true,
  "security_level": "audit",
  "performance_critical": true,
  "include_tests": true,
  "include_demo": true,
  "models": [...],
  "inherit_models": [...]
}
```

### Workflow Selection Guide

| Need | Workflow |
|------|----------|
| New module from scratch | `generate_module` |
| Check existing code | `review_module` |
| Move to new Odoo version | `upgrade_module` |
| Add/fix security | `generate_security` |
| Add test coverage | `generate_tests` |
| Add frontend component | `generate_owl` |
