# Workflow Orchestrator for AI Agents

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  WORKFLOW ORCHESTRATOR                                                       ║
║  Step-by-step orchestration for autonomous Odoo module operations            ║
║  Follow these workflows for complete end-to-end execution                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Master Workflow Selector

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  USER REQUEST                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ANALYZE REQUEST TYPE                                                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  "Create module" → WORKFLOW: generate_module                                │
│  "Review module" → WORKFLOW: review_module                                  │
│  "Upgrade module" → WORKFLOW: upgrade_module                                │
│  "Add security" → WORKFLOW: generate_security                               │
│  "Add tests" → WORKFLOW: generate_tests                                     │
│  "Add OWL component" → WORKFLOW: generate_owl                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## WORKFLOW 1: Generate Module

### Overview
```
Input → Validate → Load Skills → Generate Files → Verify → Output
```

### Step-by-Step Execution

#### STEP 1: Parse and Validate Input
```python
# REQUIRED: Extract these from user request
input_data = {
    "module_name": "",           # REQUIRED - lowercase, underscores only
    "module_description": "",    # REQUIRED - min 10 chars
    "odoo_version": "",          # REQUIRED - 14.0/15.0/16.0/17.0/18.0/19.0
}

# OPTIONAL: Apply defaults if not specified
defaults = {
    "target_apps": [],
    "ui_stack": "classic",       # classic/owl/hybrid
    "multi_company": False,
    "multi_currency": False,
    "security_level": "basic",   # basic/advanced/audit
    "performance_critical": False,
    "include_tests": True,
    "include_demo": False,
    "models": [],
    "inherit_models": [],
}

# ACTION: If odoo_version not specified, ASK USER
if not input_data.get("odoo_version"):
    # Use AskUserQuestion tool
    # Question: "Which Odoo version are you targeting?"
    # Options: ["18.0 (Recommended)", "17.0", "16.0", "15.0", "14.0", "19.0 (Development)"]
    pass
```

#### STEP 2: Load Version-Specific Skills
```python
version = input_data["odoo_version"].replace(".0", "")  # "18.0" → "18"

# ALWAYS load these skills (Read tool)
required_skills = [
    f"skills/odoo-module-generator-{version}.md",
    f"skills/odoo-model-patterns-{version}.md",
    f"skills/odoo-security-guide-{version}.md",
]

# CONDITIONALLY load
if input_data.get("ui_stack") in ["owl", "hybrid"]:
    required_skills.append(f"skills/odoo-owl-components-{version}.md")

if input_data.get("performance_critical"):
    required_skills.append("skills/odoo-performance-guide.md")

if input_data.get("include_tests"):
    required_skills.append("skills/odoo-test-patterns.md")

# ACTION: Read all required skill files
for skill in required_skills:
    # Use Read tool to load skill content
    pass
```

#### STEP 3: Verify Patterns Against GitHub
```python
# KEY PATTERNS TO VERIFY based on version
if version >= "17":
    # Verify @api.model_create_multi usage
    # WebFetch: https://raw.githubusercontent.com/odoo/odoo/{version}.0/addons/sale/models/sale_order.py
    # Prompt: "Show create method decorator"
    pass

if version >= "18":
    # Verify _check_company_auto pattern
    # WebFetch: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order.py
    # Prompt: "Show _check_company_auto and check_company usage"
    pass

# Verify view syntax (attrs vs invisible)
# WebFetch: https://raw.githubusercontent.com/odoo/odoo/{version}.0/addons/sale/views/sale_order_views.xml
# Prompt: "Show field visibility syntax"
```

#### STEP 4: Generate Module Files
```python
# Generate files in this ORDER (critical for manifest data list)
files_to_generate = {
    # 1. Module root
    "__manifest__.py": generate_manifest(input_data),
    "__init__.py": generate_root_init(input_data),

    # 2. Models
    "models/__init__.py": generate_models_init(input_data),
    # For each model in input_data["models"]:
    # "models/{model_file}.py": generate_model(model, version),

    # 3. Security (MUST come before views in manifest)
    "security/{module}_security.xml": generate_security_groups(input_data),
    "security/ir.model.access.csv": generate_access_rights(input_data),

    # 4. Views (after security)
    # For each model:
    # "views/{model}_views.xml": generate_views(model, version),
    "views/menuitems.xml": generate_menus(input_data),

    # 5. Static assets (if OWL)
    # "static/src/js/{component}.js": generate_owl_component(...),
    # "static/src/xml/{component}.xml": generate_owl_template(...),

    # 6. Tests (if requested)
    # "tests/__init__.py": ...,
    # "tests/common.py": ...,
    # "tests/test_{model}.py": ...,
}
```

#### STEP 5: Validate Generated Code
```python
# Validation checks
validations = {
    "manifest_data_order": check_data_file_order(manifest),
    "security_before_views": check_security_first(manifest),
    "python_syntax": check_python_syntax(python_files),
    "xml_syntax": check_xml_syntax(xml_files),
    "version_patterns": check_version_compliance(files, version),
}

# Fix any issues before output
for check, result in validations.items():
    if not result["valid"]:
        # Apply fix from result["fix"]
        pass
```

#### STEP 6: Output Results
```python
output = {
    "status": "success",
    "module_name": input_data["module_name"],
    "odoo_version": input_data["odoo_version"],
    "files": files_to_generate,
    "file_tree": generate_file_tree(files_to_generate),
    "version_notes": collect_version_notes(version),
    "warnings": collect_warnings(),
    "github_verified": True,
    "manifest_data_order": [
        "security/{module}_security.xml",
        "security/ir.model.access.csv",
        "views/{model}_views.xml",
        "views/menuitems.xml",
    ],
}

# Write files using Write tool
for path, content in files_to_generate.items():
    full_path = f"{output_directory}/{input_data['module_name']}/{path}"
    # Use Write tool
```

---

## WORKFLOW 2: Review Module

### Overview
```
Path → Scan Files → Load Skills → Analyze → Report Issues
```

### Step-by-Step Execution

#### STEP 1: Scan Module Structure
```python
# Use Glob to find all files
module_files = {
    "manifest": glob(f"{module_path}/__manifest__.py"),
    "python": glob(f"{module_path}/**/*.py"),
    "xml": glob(f"{module_path}/**/*.xml"),
    "csv": glob(f"{module_path}/**/*.csv"),
    "js": glob(f"{module_path}/static/**/*.js"),
}

# Read manifest to determine version
manifest_content = read(f"{module_path}/__manifest__.py")
# Extract version from manifest or ask user
```

#### STEP 2: Load Review Skills
```python
skills_to_load = [
    f"skills/odoo-model-patterns-{version}.md",
    f"skills/odoo-security-guide-{version}.md",
    "skills/odoo-performance-guide.md",
    "skills/odoo-troubleshooting-guide.md",
]
```

#### STEP 3: Analyze Each Area
```python
issues = []

# Security Review
for csv_file in module_files["csv"]:
    issues.extend(check_access_rights(csv_file, version))

for xml_file in module_files["xml"]:
    if "security" in xml_file:
        issues.extend(check_record_rules(xml_file, version))

# Pattern Review
for py_file in module_files["python"]:
    if "models" in py_file:
        issues.extend(check_model_patterns(py_file, version))
        issues.extend(check_deprecated_patterns(py_file, version))

# View Review
for xml_file in module_files["xml"]:
    if "views" in xml_file:
        issues.extend(check_view_patterns(xml_file, version))

# Performance Review
issues.extend(check_performance_patterns(module_files["python"]))
```

#### STEP 4: Generate Report
```python
report = {
    "status": "success",
    "module_path": module_path,
    "odoo_version": version,
    "summary": {
        "total_issues": len(issues),
        "critical": len([i for i in issues if i["severity"] == "critical"]),
        "warnings": len([i for i in issues if i["severity"] == "warning"]),
        "suggestions": len([i for i in issues if i["severity"] == "suggestion"]),
    },
    "issues": issues,
    "recommendations": generate_recommendations(issues),
}
```

---

## WORKFLOW 3: Upgrade Module

### Overview
```
Source → Target → Calculate Path → Load Migrations → Transform → Validate
```

### Step-by-Step Execution

#### STEP 1: Determine Migration Path
```python
source_version = "16.0"
target_version = "18.0"

# Migration must be done version by version
migration_path = calculate_path(source_version, target_version)
# Result: ["16.0", "17.0", "18.0"]

# Each hop requires its own migration
hops = [
    ("16", "17"),  # attrs removal, create_multi required
    ("17", "18"),  # _check_company_auto, SQL() builder
]
```

#### STEP 2: Load Migration Skills
```python
for source, target in hops:
    skills_to_load = [
        f"skills/odoo-module-generator-{source}-{target}.md",
        f"skills/odoo-model-patterns-{source}-{target}.md",
        f"skills/odoo-security-guide-{source}-{target}.md",
        f"skills/odoo-version-knowledge-{source}-{target}.md",
    ]

    if has_owl_components(module_path):
        skills_to_load.append(f"skills/odoo-owl-components-{source}-{target}.md")
```

#### STEP 3: Apply Transformations
```python
transformations = []

for source, target in hops:
    # Python transformations
    if (source, target) == ("16", "17"):
        transformations.extend([
            transform_create_to_create_multi,
            transform_attrs_to_inline,
        ])
    elif (source, target) == ("17", "18"):
        transformations.extend([
            add_check_company_auto,
            add_check_company_fields,
            transform_sql_to_builder,
            add_type_hints,
        ])

# Apply each transformation
for transform in transformations:
    files = transform(module_files)
```

#### STEP 4: Generate Migration Scripts
```python
# Create migration folder structure
migration_files = {
    f"migrations/{target_version}.1.0.0/pre-migration.py": generate_pre_migration(),
    f"migrations/{target_version}.1.0.0/post-migration.py": generate_post_migration(),
}
```

#### STEP 5: Output Upgraded Module
```python
output = {
    "status": "success",
    "source_version": source_version,
    "target_version": target_version,
    "migration_path": migration_path,
    "updated_files": updated_files,
    "migration_scripts": migration_files,
    "breaking_changes": list_breaking_changes(hops),
    "manual_review_required": list_manual_items(),
}
```

---

## Decision Trees

### Version Pattern Selection

```
                    ┌─────────────────────┐
                    │ What's the version? │
                    └─────────────────────┘
                              │
        ┌─────────┬───────────┼───────────┬─────────┐
        ▼         ▼           ▼           ▼         ▼
      v14       v15         v16         v17       v18/v19
        │         │           │           │         │
        ▼         ▼           ▼           ▼         ▼
   @api.multi   Remove    Command     attrs      _check_
   allowed    @api.multi   class     REMOVED   company_auto
        │         │        recommended    │         │
        ▼         ▼           ▼           ▼         ▼
   track_     tracking    @api.model  create_   SQL()
   visibility    =True    _create_multi multi   builder
                            optional   required
```

### Multi-Company Decision

```
                    ┌────────────────────────────┐
                    │ Multi-company required?    │
                    └────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
            YES                              NO
              │                               │
              ▼                               ▼
    ┌─────────────────────┐         Standard single-
    │ What version?       │         company model
    └─────────────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
  v14-v17             v18+
    │                   │
    ▼                   ▼
  Manual            _check_company_auto = True
  company           check_company = True
  validation        allowed_company_ids in rules
```

---

## Error Recovery

### Common Errors and Recovery Actions

| Error | Detection | Recovery |
|-------|-----------|----------|
| Version not specified | `odoo_version` missing | Ask user with AskUserQuestion |
| Invalid module name | Pattern mismatch | Suggest valid name |
| Missing security | No ir.model.access.csv | Generate basic access rights |
| attrs in v17+ | Found attrs= in XML | Transform to inline expression |
| Single create in v17+ | @api.model on create | Change to @api.model_create_multi |

### Recovery Workflow

```python
def recover_from_error(error_type, context):
    recovery_actions = {
        "VERSION_MISSING": lambda: ask_user_version(),
        "INVALID_NAME": lambda: suggest_valid_name(context["name"]),
        "SECURITY_MISSING": lambda: generate_default_security(context),
        "DEPRECATED_PATTERN": lambda: apply_transformation(context),
    }

    if error_type in recovery_actions:
        return recovery_actions[error_type]()
    else:
        return {"status": "error", "message": "Unrecoverable error"}
```

---

## Orchestrator Checklist

### Before Starting Any Workflow

- [ ] Odoo version identified (REQUIRED)
- [ ] Input validated against schema
- [ ] Version-specific skills loaded
- [ ] GitHub verification planned

### During Execution

- [ ] Each file generated in correct order
- [ ] Security files before views in manifest
- [ ] Version-specific patterns applied
- [ ] No deprecated patterns for target version

### Before Output

- [ ] All files syntax-validated
- [ ] Manifest data order verified
- [ ] Version notes collected
- [ ] Warnings documented

---

## Example Complete Execution

```
USER: "Create a sales approval module for Odoo 18"

AGENT WORKFLOW:
1. Parse: module_name="sale_approval", odoo_version="18.0"
2. Load: odoo-module-generator-18.md, odoo-model-patterns-18.md, odoo-security-guide-18.md
3. Verify: WebFetch sale_order.py for v18 patterns
4. Generate:
   - __manifest__.py (with data order)
   - __init__.py
   - models/__init__.py
   - models/sale_approval.py (_check_company_auto, @api.model_create_multi)
   - security/sale_approval_security.xml (groups)
   - security/ir.model.access.csv (access rights)
   - views/sale_approval_views.xml (invisible expressions)
   - views/menuitems.xml
   - tests/__init__.py
   - tests/test_sale_approval.py
5. Validate: All checks pass
6. Output: Complete module with file tree and version notes
```
