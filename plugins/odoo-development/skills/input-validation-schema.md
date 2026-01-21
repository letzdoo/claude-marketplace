# Input Validation Schema for Agents

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  INPUT VALIDATION SCHEMA                                                     ║
║  JSON Schema definitions for programmatic agent input validation             ║
║  Use to validate inputs before calling module generation workflows           ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Complete Input Schema (JSON Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "odoo-module-input",
  "title": "Odoo Module Generation Input",
  "description": "Schema for validating Odoo module generation inputs",
  "type": "object",
  "required": ["module_name", "module_description", "odoo_version"],
  "properties": {
    "module_name": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_]*$",
      "minLength": 2,
      "maxLength": 50,
      "description": "Technical module name (lowercase, underscores)",
      "examples": ["my_module", "sale_extension", "hr_custom"]
    },
    "module_description": {
      "type": "string",
      "minLength": 10,
      "maxLength": 500,
      "description": "Human-readable module description"
    },
    "odoo_version": {
      "type": "string",
      "enum": ["14.0", "15.0", "16.0", "17.0", "18.0", "19.0"],
      "description": "Target Odoo version"
    },
    "target_apps": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "sale", "purchase", "stock", "account", "hr", "hr_expense",
          "hr_holidays", "hr_payroll", "crm", "project", "website",
          "mail", "contacts", "fleet", "maintenance", "mrp", "quality",
          "helpdesk", "documents", "sign", "planning", "timesheet"
        ]
      },
      "default": [],
      "description": "Odoo apps to extend/integrate with"
    },
    "ui_stack": {
      "type": "string",
      "enum": ["classic", "owl", "hybrid"],
      "default": "classic",
      "description": "Frontend technology stack"
    },
    "multi_company": {
      "type": "boolean",
      "default": false,
      "description": "Enable multi-company support"
    },
    "multi_currency": {
      "type": "boolean",
      "default": false,
      "description": "Enable multi-currency support"
    },
    "security_level": {
      "type": "string",
      "enum": ["basic", "advanced", "audit"],
      "default": "basic",
      "description": "Security configuration level"
    },
    "performance_critical": {
      "type": "boolean",
      "default": false,
      "description": "Apply performance optimizations"
    },
    "include_tests": {
      "type": "boolean",
      "default": true,
      "description": "Generate test files"
    },
    "include_demo": {
      "type": "boolean",
      "default": false,
      "description": "Generate demo data"
    },
    "models": {
      "type": "array",
      "items": { "$ref": "#/$defs/model" },
      "default": [],
      "description": "Custom model definitions"
    },
    "inherit_models": {
      "type": "array",
      "items": { "$ref": "#/$defs/inherit_model" },
      "default": [],
      "description": "Models to extend"
    }
  },
  "$defs": {
    "model": {
      "type": "object",
      "required": ["name", "description"],
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_.]*$",
          "description": "Model technical name (e.g., my_module.my_model)"
        },
        "description": {
          "type": "string",
          "description": "Model description for _description"
        },
        "fields": {
          "type": "array",
          "items": { "$ref": "#/$defs/field" },
          "default": []
        },
        "inherit_mail": {
          "type": "boolean",
          "default": false,
          "description": "Inherit mail.thread and mail.activity.mixin"
        },
        "has_workflow": {
          "type": "boolean",
          "default": false,
          "description": "Include state field and workflow"
        },
        "workflow_states": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "value": { "type": "string" },
              "label": { "type": "string" }
            }
          },
          "default": [
            {"value": "draft", "label": "Draft"},
            {"value": "confirmed", "label": "Confirmed"},
            {"value": "done", "label": "Done"}
          ]
        }
      }
    },
    "inherit_model": {
      "type": "object",
      "required": ["model"],
      "properties": {
        "model": {
          "type": "string",
          "description": "Model to inherit (e.g., sale.order, res.partner)"
        },
        "fields": {
          "type": "array",
          "items": { "$ref": "#/$defs/field" },
          "default": []
        }
      }
    },
    "field": {
      "type": "object",
      "required": ["name", "type"],
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]*$",
          "description": "Field name (lowercase)"
        },
        "type": {
          "type": "string",
          "enum": [
            "Char", "Text", "Html", "Integer", "Float", "Monetary",
            "Boolean", "Date", "Datetime", "Selection", "Binary",
            "Many2one", "One2many", "Many2many"
          ]
        },
        "string": {
          "type": "string",
          "description": "Field label"
        },
        "required": {
          "type": "boolean",
          "default": false
        },
        "index": {
          "type": "boolean",
          "default": false
        },
        "tracking": {
          "type": "boolean",
          "default": false
        },
        "comodel_name": {
          "type": "string",
          "description": "Related model for relational fields"
        },
        "inverse_name": {
          "type": "string",
          "description": "Inverse field for One2many"
        },
        "selection": {
          "type": "array",
          "items": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 2,
            "maxItems": 2
          },
          "description": "Selection choices as [[value, label], ...]"
        },
        "compute": {
          "type": "string",
          "description": "Compute method name"
        },
        "store": {
          "type": "boolean",
          "default": false,
          "description": "Store computed field"
        },
        "depends": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Dependencies for computed field"
        }
      }
    }
  }
}
```

## Validation Functions (Python)

```python
"""
Input validation utilities for Odoo module generation
"""
import re
from typing import Any, Optional


class ValidationError(Exception):
    """Validation error with field path"""
    def __init__(self, message: str, path: str = ""):
        self.path = path
        super().__init__(f"{path}: {message}" if path else message)


def validate_module_input(data: dict) -> dict:
    """
    Validate module generation input.
    Returns validated data with defaults applied.
    Raises ValidationError on invalid input.
    """
    errors = []

    # Required fields
    if 'module_name' not in data:
        errors.append(ValidationError("module_name is required"))
    elif not re.match(r'^[a-z][a-z0-9_]*$', data['module_name']):
        errors.append(ValidationError(
            "module_name must be lowercase with underscores",
            "module_name"
        ))

    if 'module_description' not in data:
        errors.append(ValidationError("module_description is required"))
    elif len(data['module_description']) < 10:
        errors.append(ValidationError(
            "module_description must be at least 10 characters",
            "module_description"
        ))

    if 'odoo_version' not in data:
        errors.append(ValidationError("odoo_version is required"))
    elif data['odoo_version'] not in ['14.0', '15.0', '16.0', '17.0', '18.0', '19.0']:
        errors.append(ValidationError(
            "odoo_version must be one of: 14.0, 15.0, 16.0, 17.0, 18.0, 19.0",
            "odoo_version"
        ))

    if errors:
        raise ValidationError("\n".join(str(e) for e in errors))

    # Apply defaults
    validated = {
        'module_name': data['module_name'],
        'module_description': data['module_description'],
        'odoo_version': data['odoo_version'],
        'target_apps': data.get('target_apps', []),
        'ui_stack': data.get('ui_stack', 'classic'),
        'multi_company': data.get('multi_company', False),
        'multi_currency': data.get('multi_currency', False),
        'security_level': data.get('security_level', 'basic'),
        'performance_critical': data.get('performance_critical', False),
        'include_tests': data.get('include_tests', True),
        'include_demo': data.get('include_demo', False),
        'models': data.get('models', []),
        'inherit_models': data.get('inherit_models', []),
    }

    # Validate models
    for i, model in enumerate(validated['models']):
        validate_model(model, f"models[{i}]")

    # Validate inherit_models
    for i, inherit in enumerate(validated['inherit_models']):
        validate_inherit_model(inherit, f"inherit_models[{i}]")

    return validated


def validate_model(model: dict, path: str) -> None:
    """Validate a model definition"""
    if 'name' not in model:
        raise ValidationError("name is required", path)
    if not re.match(r'^[a-z][a-z0-9_.]*$', model['name']):
        raise ValidationError("name must be lowercase with dots/underscores", f"{path}.name")

    if 'description' not in model:
        raise ValidationError("description is required", path)

    for i, field in enumerate(model.get('fields', [])):
        validate_field(field, f"{path}.fields[{i}]")


def validate_inherit_model(inherit: dict, path: str) -> None:
    """Validate an inherit model definition"""
    if 'model' not in inherit:
        raise ValidationError("model is required", path)

    for i, field in enumerate(inherit.get('fields', [])):
        validate_field(field, f"{path}.fields[{i}]")


def validate_field(field: dict, path: str) -> None:
    """Validate a field definition"""
    if 'name' not in field:
        raise ValidationError("name is required", path)
    if not re.match(r'^[a-z][a-z0-9_]*$', field['name']):
        raise ValidationError("name must be lowercase with underscores", f"{path}.name")

    if 'type' not in field:
        raise ValidationError("type is required", path)

    valid_types = [
        'Char', 'Text', 'Html', 'Integer', 'Float', 'Monetary',
        'Boolean', 'Date', 'Datetime', 'Selection', 'Binary',
        'Many2one', 'One2many', 'Many2many'
    ]
    if field['type'] not in valid_types:
        raise ValidationError(f"type must be one of: {', '.join(valid_types)}", f"{path}.type")

    # Relational field validation
    if field['type'] in ['Many2one', 'One2many', 'Many2many']:
        if 'comodel_name' not in field:
            raise ValidationError("comodel_name required for relational fields", path)

    if field['type'] == 'One2many' and 'inverse_name' not in field:
        raise ValidationError("inverse_name required for One2many fields", path)

    if field['type'] == 'Selection' and 'selection' not in field:
        raise ValidationError("selection required for Selection fields", path)
```

## Version Compatibility Matrix

```python
VERSION_FEATURES = {
    "14.0": {
        "api_multi": True,  # Still exists but deprecated
        "track_visibility": True,
        "tracking": True,
        "attrs": True,
        "owl": False,
        "command_class": False,
        "create_multi": False,
        "check_company_auto": False,
        "sql_builder": False,
        "type_hints": False,
    },
    "15.0": {
        "api_multi": False,  # REMOVED
        "track_visibility": False,  # Use tracking
        "tracking": True,
        "attrs": True,
        "owl": "1.x",
        "command_class": False,
        "create_multi": True,  # Optional
        "check_company_auto": False,
        "sql_builder": False,
        "type_hints": False,
    },
    "16.0": {
        "api_multi": False,
        "track_visibility": False,
        "tracking": True,
        "attrs": True,  # Deprecated
        "owl": "2.x",
        "command_class": True,  # Recommended
        "create_multi": True,  # Recommended
        "check_company_auto": False,
        "sql_builder": False,
        "type_hints": False,
    },
    "17.0": {
        "api_multi": False,
        "track_visibility": False,
        "tracking": True,
        "attrs": False,  # REMOVED
        "owl": "2.x",
        "command_class": True,
        "create_multi": True,  # Required
        "check_company_auto": False,
        "sql_builder": False,
        "type_hints": False,
    },
    "18.0": {
        "api_multi": False,
        "track_visibility": False,
        "tracking": True,
        "attrs": False,
        "owl": "2.x",
        "command_class": True,
        "create_multi": True,
        "check_company_auto": True,  # Recommended
        "sql_builder": True,  # Recommended
        "type_hints": True,  # Recommended
    },
    "19.0": {
        "api_multi": False,
        "track_visibility": False,
        "tracking": True,
        "attrs": False,
        "owl": "3.x",
        "command_class": True,
        "create_multi": True,
        "check_company_auto": True,  # Required
        "sql_builder": True,  # Required
        "type_hints": True,  # Required
    },
}


def get_version_features(version: str) -> dict:
    """Get feature flags for a version"""
    return VERSION_FEATURES.get(version, VERSION_FEATURES["18.0"])


def check_version_compatibility(data: dict) -> list[str]:
    """
    Check input for version compatibility issues.
    Returns list of warnings.
    """
    warnings = []
    version = data['odoo_version']
    features = get_version_features(version)

    # Check OWL usage
    if data['ui_stack'] in ['owl', 'hybrid']:
        if not features['owl']:
            warnings.append(f"OWL not available in v{version}, use v15+")
        elif features['owl'] == '1.x':
            warnings.append(f"Using OWL 1.x syntax for v{version}")
        elif features['owl'] == '2.x':
            warnings.append(f"Using OWL 2.x syntax for v{version}")
        elif features['owl'] == '3.x':
            warnings.append(f"Using OWL 3.x syntax for v{version}")

    # Check multi-company
    if data['multi_company'] and not features['check_company_auto']:
        warnings.append(f"v{version} requires manual company validation")

    return warnings
```

## Example Validated Inputs

### Minimal Input
```json
{
  "module_name": "my_module",
  "module_description": "A custom module for managing widgets",
  "odoo_version": "18.0"
}
```

### Full Input
```json
{
  "module_name": "sale_approval_workflow",
  "module_description": "Sales order approval workflow with multi-level authorization",
  "odoo_version": "18.0",
  "target_apps": ["sale", "mail"],
  "ui_stack": "hybrid",
  "multi_company": true,
  "multi_currency": false,
  "security_level": "advanced",
  "performance_critical": false,
  "include_tests": true,
  "include_demo": true,
  "models": [
    {
      "name": "sale.approval.rule",
      "description": "Approval Rule Configuration",
      "fields": [
        {
          "name": "name",
          "type": "Char",
          "string": "Rule Name",
          "required": true
        },
        {
          "name": "amount_threshold",
          "type": "Monetary",
          "string": "Amount Threshold"
        },
        {
          "name": "approver_id",
          "type": "Many2one",
          "string": "Approver",
          "comodel_name": "res.users",
          "required": true
        }
      ],
      "inherit_mail": false,
      "has_workflow": false
    }
  ],
  "inherit_models": [
    {
      "model": "sale.order",
      "fields": [
        {
          "name": "x_requires_approval",
          "type": "Boolean",
          "string": "Requires Approval",
          "compute": "_compute_requires_approval",
          "store": true,
          "depends": ["amount_total"]
        },
        {
          "name": "x_approved_by",
          "type": "Many2one",
          "string": "Approved By",
          "comodel_name": "res.users",
          "tracking": true
        }
      ]
    }
  ]
}
```

## Agent Usage Pattern

```python
# Agent workflow for module generation
def generate_module(user_input: dict) -> dict:
    """
    Main entry point for agents.

    1. Validate input
    2. Load version-specific skills
    3. Generate module files
    4. Return structured output
    """
    # Step 1: Validate
    try:
        validated = validate_module_input(user_input)
    except ValidationError as e:
        return {
            "status": "error",
            "error": str(e),
            "input_schema": "See input-validation-schema.md"
        }

    # Step 2: Check compatibility
    warnings = check_version_compatibility(validated)

    # Step 3: Determine files to load
    version = validated['odoo_version'].replace('.0', '')
    skills_to_load = [
        f"odoo-module-generator-{version}.md",
        f"odoo-model-patterns-{version}.md",
        f"odoo-security-guide-{version}.md",
    ]

    if validated['ui_stack'] in ['owl', 'hybrid']:
        skills_to_load.append(f"odoo-owl-components-{version}.md")

    if validated['performance_critical']:
        skills_to_load.append("odoo-performance-guide.md")

    if validated['include_tests']:
        skills_to_load.append("odoo-test-patterns.md")

    # Step 4: Generate (implementation in specific skills)
    return {
        "status": "validated",
        "input": validated,
        "warnings": warnings,
        "skills_to_load": skills_to_load,
        "next_step": "Load skills and generate files"
    }
```
