# Validation Report: {FEATURE_NAME}

**Date**: {DATE}
**Module**: `{module_name}`
**Status**: ⏳ Validating / ✅ Passed / ❌ Failed

---

## 1. Validation Summary

| Check | Status | Issues |
|-------|--------|--------|
| Module Structure | ✓ / ✗ | 0 |
| Model Definitions | ✓ / ✗ | 0 |
| View Syntax | ✓ / ✗ | 0 |
| Security Rules | ✓ / ✗ | 0 |
| Indexer Validation | ✓ / ✗ | 0 |
| Static Analysis | ✓ / ✗ | 0 |
| Installation Test | ✓ / ✗ | 0 |

**Overall**: {X} checks passed, {Y} checks failed

---

## 2. Module Structure Validation

### 2.1 Required Files
- [x] `__init__.py` exists
- [x] `__manifest__.py` exists and valid
- [x] `models/__init__.py` exists
- [x] `views/` directory exists
- [x] `security/ir.model.access.csv` exists
- [x] `README.md` exists

### 2.2 Manifest Validation
```python
{
    'name': '✓ Present',
    'version': '✓ Valid format (18.0.1.0.0)',
    'depends': '✓ All modules available',
    'data': '✓ All files exist',
    'demo': '✓ All files exist',
    'license': '✓ Valid license',
}
```

**Issues**: None

---

## 3. Model Validation

### 3.1 Model: `{model.name}`

**File**: `models/{model_name}.py`

#### Import Validation
- [x] Imports are correct
- [x] No circular imports
- [x] All Odoo modules imported

#### Model Definition
- [x] `_name` is defined
- [x] `_description` is present
- [x] Inheritance is correct (`_inherit` or `_inherits`)
- [x] No naming conflicts (indexer checked)

#### Field Validation

| Field | Type | Issues | Indexer Check |
|-------|------|--------|---------------|
| `name` | Char | ✓ | N/A (new) |
| `partner_id` | Many2one | ✓ | ✓ res.partner exists |
| `state` | Selection | ✓ | N/A (new) |
| `line_ids` | One2many | ✓ | ✓ Comodel exists |

**Field Naming Conventions**:
- [x] Many2one fields end with `_id`
- [x] Many2many/One2many fields end with `_ids`
- [x] No reserved keyword usage

#### Method Validation
- [x] API decorators are correct (`@api.depends`, `@api.model`, etc.)
- [x] Super calls are present in overrides
- [x] Return values are correct

**Issues**: None

---

### 3.2 Extended Models

#### Model: `{existing.model}`

**File**: `models/{model_name}_extend.py`

- [x] Model exists (indexer validated)
- [x] `_inherit` is correct
- [x] No field name conflicts (indexer validated)
- [x] Method overrides call super()

**Issues**: None

---

## 4. View Validation

### 4.1 List View: `{module}.{model}_view_list`

**File**: `views/{model}_views.xml`

- [x] XML syntax is valid
- [x] Model reference is correct
- [x] All fields exist in model (indexer validated)

**Field Validation**:
| Field | Exists in Model | Widget Compatible |
|-------|-----------------|-------------------|
| `name` | ✓ | ✓ |
| `partner_id` | ✓ | ✓ |
| `state` | ✓ | ✓ |

**Issues**: None

---

### 4.2 Form View: `{module}.{model}_view_form`

**File**: `views/{model}_views.xml`

- [x] XML syntax is valid
- [x] Model reference is correct
- [x] All fields exist (indexer validated)
- [x] Widget usage is correct
- [x] Chatter elements are correct

**Widget Validation**:
| Field | Widget | Compatible | Notes |
|-------|--------|------------|-------|
| `partner_id` | default | ✓ | Many2one standard |
| `state` | statusbar | ✓ | Selection field |
| `description` | html | ✓ | Html field type |
| `line_ids` | inline tree | ✓ | One2many allows inline |

**Issues**: None

---

### 4.3 View Inheritance

#### Inherited View: `{parent_view_xmlid}`

**File**: `views/{model}_views.xml`

- [x] Parent view exists (indexer validated)
- [x] Parent view XML ID is correct with module prefix
- [x] XPath expressions are valid
- [x] XPath targets exist in parent view (likely)
- [x] Odoo version compatibility (using `<list>` for Odoo 18)

**XPath Validation**:
| XPath | Valid | Target Exists | Version OK |
|-------|-------|---------------|------------|
| `//field[@name='partner_id']` | ✓ | ✓ (indexer) | ✓ |
| `//notebook` | ✓ | ✓ (standard) | ✓ Odoo 18 |

**Issues**: None

---

## 5. Action and Menu Validation

### 5.1 Actions

#### Action: `{module}.action_{model}`

**File**: `views/{model}_views.xml`

- [x] XML syntax valid
- [x] Model reference correct
- [x] View mode valid
- [x] Context is valid Python dict

**Issues**: None

---

### 5.2 Menus

#### Menu: `{module}.menu_{model}`

**File**: `views/{model}_views.xml`

- [x] XML syntax valid
- [x] Action reference exists
- [x] Parent menu exists or is being created
- [x] Sequence is defined

**Issues**: None

---

## 6. Security Validation

### 6.1 Access Rights

**File**: `security/ir.model.access.csv`

- [x] File format is correct (CSV)
- [x] All models have at least one access rule
- [x] Group references are valid (indexer validated)

**Access Rules**:
| Model | Groups | Read | Write | Create | Delete |
|-------|--------|------|-------|--------|--------|
| `{model.name}` | User | ✓ | ✓ | ✓ | ✗ |
| `{model.name}` | Manager | ✓ | ✓ | ✓ | ✓ |

**Group Validation**:
- [x] `base.group_user` exists (indexer)
- [x] Custom groups are defined in security.xml

**Issues**: None

---

### 6.2 Record Rules

**File**: `security/security.xml`

- [x] XML syntax valid
- [x] Domain expressions are valid
- [x] Group references exist (indexer validated)
- [x] Model references are correct

**Issues**: None

---

## 7. Data Files Validation

### 7.1 Default Data

**File**: `data/data.xml`

- [x] XML syntax valid
- [x] No `<data>` wrapper (deprecated in Odoo 18)
- [x] All XML ID references exist (indexer validated)
- [x] Model references are correct

**XML ID Validation**:
| Reference | Module Prefix | Exists | Indexer |
|-----------|---------------|--------|---------|
| `base.main_company` | ✓ | ✓ | ✓ |
| `base.group_user` | ✓ | ✓ | ✓ |

**Issues**: None

---

### 7.2 Demo Data

**File**: `data/demo_data.xml`

- [x] XML syntax valid
- [x] All references valid
- [x] Demo flag in manifest

**Issues**: None

---

## 8. Indexer Validation Results

### 8.1 Model Validation

**Validation Command**:
```bash
mcp__plugin_odoo-doodba-dev_odoo-indexer__search_odoo_index(
    query="{model}",
    item_type="model"
)
```

**Results**:
- [x] `res.partner` exists in `base`
- [x] `mail.thread` exists in `mail`
- [x] `{existing.model}` exists in `{module}`
- [x] No naming conflicts detected

---

### 8.2 Field Validation

**Checked Fields**:
| Model | Field | Type | Exists | Naming OK |
|-------|-------|------|--------|-----------|
| `res.partner` | `name` | Char | ✓ | ✓ |
| `{existing.model}` | `partner_id` | Many2one | ✓ | ✓ _id suffix |
| `{existing.model}` | `line_ids` | One2many | ✓ | ✓ _ids suffix |

**Issues**: None

---

### 8.3 XML ID Validation

**Checked XML IDs**:
| XML ID | Module | Type | Exists |
|--------|--------|------|--------|
| `base.group_user` | base | Group | ✓ |
| `base.main_company` | base | Company | ✓ |
| `{module}.{parent_view}` | {module} | View | ✓ |

**Issues**: None

---

### 8.4 View Inheritance Validation

**Parent Views**:
| View XML ID | Model | Type | Exists | XPath Compatible |
|-------------|-------|------|--------|------------------|
| `{module}.{view}` | {model} | form | ✓ | ✓ |

**Issues**: None

---

## 9. Static Analysis

### 9.1 Python Code Quality

**Tool**: `pylint` / `flake8`

**Results**:
```
{module}/models/{model}.py: 9.5/10
  - No critical issues
  - 2 warnings (docstring style)

{module}/models/{model}_extend.py: 10.0/10
  - No issues
```

**Issues**:
- Warning: Missing docstrings (non-critical)

---

### 9.2 Code Style

**PEP8 Compliance**: ✓ Passed

**Odoo Conventions**:
- [x] Model naming (snake_case)
- [x] Method naming (snake_case)
- [x] Private methods start with `_`
- [x] API decorators used correctly
- [x] No hardcoded strings in raise statements

**Issues**: None

---

## 10. Version Compatibility

### 10.1 Odoo Version Detection

**Command**:
```bash
cat odoo/custom/src/odoo/odoo/release.py | grep "version_info"
```

**Result**: Odoo 18.0

### 10.2 Compatibility Checks

- [x] Using `<list>` instead of `<tree>` for list views
- [x] XPath uses `//list` not `//tree`
- [x] No deprecated widgets
- [x] No deprecated API usage
- [x] No `<data>` wrapper in XML files

**Issues**: None

---

## 11. Installation Test

### 11.1 Pre-Installation Checks

**Command**: `/odoo-validate {module_name}`

**Results**:
- [x] All dependencies available
- [x] No conflicting modules
- [x] Database connection OK

---

### 11.2 Installation Attempt

**Command**: `invoke install --modules={module_name}`

**Output**:
```
Installing module {module_name}...
Loading data files...
  - security/ir.model.access.csv: ✓
  - views/{model}_views.xml: ✓
  - data/data.xml: ✓
Module {module_name} installed successfully in 2.5s
```

**Status**: ✅ SUCCESS

---

### 11.3 Post-Installation Checks

**Checks**:
- [x] Module shows in Apps list
- [x] Menus are visible
- [x] Views load without errors
- [x] No JavaScript console errors
- [x] Access rights work correctly

**Database Queries**: 1,245 queries (normal range)

**Load Time**: 2.5s (acceptable)

---

## 12. Error Summary

### Critical Errors (Must Fix)
None

### Warnings (Should Fix)
1. Missing docstrings in `{file}:{line}`
   - **Impact**: Low (documentation only)
   - **Fix**: Add docstrings to public methods

### Informational (Nice to Have)
1. Consider adding database indexes on `{field}`
   - **Impact**: Performance optimization
   - **Fix**: Add `index=True` to field definition

---

## 13. Test Readiness

### Prerequisites for Testing
- [x] Module installed successfully
- [x] No validation errors
- [x] Views are accessible
- [x] Security rules allow test operations

**Ready for Testing**: ✅ YES

**Next Step**: Proceed to `odoo-tester` agent for test generation and execution

---

## 14. Recommendations

### Code Quality
1. ✅ Add docstrings to public methods
2. ✅ Add database indexes on frequently searched fields
3. ✅ Consider adding more computed fields for UI performance

### Security
1. ✅ Security rules are well-defined
2. ✅ Consider multi-company rules if needed

### Performance
1. ✅ Use stored computed fields
2. ✅ Batch operations are used correctly
3. ✅ No N+1 query patterns detected

---

## 15. Approval

**Validation Status**: ✅ PASSED

**Blocker Issues**: 0
**Critical Issues**: 0
**Warnings**: 2 (non-critical)

**Recommendation**: ✅ Proceed to testing phase

**Validator**: odoo-validator agent
**Date**: {DATE}

---

**Next Steps**:
1. Address non-critical warnings (optional)
2. Proceed with `odoo-tester` agent for test generation
3. Run full test suite
4. Generate documentation with `odoo-documenter` agent
