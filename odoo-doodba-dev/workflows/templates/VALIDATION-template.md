# Validation Report: {FEATURE_NAME}

**Date**: {DATE}
**Module**: `{module_name}`
**Status**: ⏳ Validating / ✅ Passed / ❌ Failed

---

## Summary

| Check | Status | Issues |
|-------|--------|--------|
| Module Structure | ✓ / ✗ | 0 |
| Models | ✓ / ✗ | 0 |
| Views | ✓ / ✗ | 0 |
| Security | ✓ / ✗ | 0 |
| Indexer | ✓ / ✗ | 0 |
| Installation | ✓ / ✗ | 0 |

**Result**: {X} passed, {Y} failed

---

## 1. Module Structure

**Required Files**:
- [x] `__init__.py`, `__manifest__.py`
- [x] `models/__init__.py`
- [x] `views/`, `security/`
- [x] `README.md`

**Manifest**:
- [x] Valid format
- [x] All dependencies available
- [x] All data files exist

**Issues**: {None / List issues}

---

## 2. Models

### `{model.name}`

**Validation**:
- [x] `_name`, `_description` defined
- [x] Correct imports
- [x] Field naming (_id, _ids suffixes)
- [x] API decorators correct
- [x] Super calls in overrides

**Indexer**:
- [x] No naming conflicts
- [x] All comodels exist
- [x] Inheritance targets exist

**Issues**: {None / List issues}

---

## 3. Views

### List View: `{module}.{model}_view_list`
- [x] XML syntax valid
- [x] All fields exist (indexer)
- [x] Odoo 18: Using `<list>` not `<tree>`

### Form View: `{module}.{model}_view_form`
- [x] XML syntax valid
- [x] All fields exist (indexer)
- [x] Widget compatibility

### View Inheritance
- [x] Parent view exists (indexer)
- [x] XPath targets valid

**Issues**: {None / List issues}

---

## 4. Security

**Access Rights** (`ir.model.access.csv`):
- [x] CSV format correct
- [x] All models have rules
- [x] Groups exist (indexer)

**Record Rules** (`security.xml`):
- [x] XML syntax valid
- [x] Domains valid
- [x] Groups exist (indexer)

**Issues**: {None / List issues}

---

## 5. Data Files

**Default Data** (`data/data.xml`):
- [x] XML syntax valid
- [x] No `<data>` wrapper
- [x] All XML ID refs exist (indexer)

**Demo Data** (`data/demo_data.xml`):
- [x] XML syntax valid
- [x] All refs exist (indexer)

**Issues**: {None / List issues}

---

## 6. Indexer Validation

**Models Validated**: {X}
- [x] All comodel references exist
- [x] No naming conflicts

**Fields Validated**: {Y}
- [x] All fields exist in views
- [x] Naming conventions correct

**XML IDs Validated**: {Z}
- [x] All references have correct module prefix
- [x] All targets exist

**Version**: Odoo {VERSION}
- [x] Syntax appropriate for version

**Issues**: {None / List issues}

---

## 7. Installation Test

**Command**:
```bash
invoke restart && invoke install --modules={module_name}
```

**Result**: ✅ Success / ❌ Failed

**Output**:
```
{Installation output or error log}
```

**Post-Install**:
- [x] Module in Apps list
- [x] Menus visible
- [x] Views load without errors

**Issues**: {None / List issues}

---

## 8. Issues Summary

### Critical (Must Fix)
{None / List with fix instructions}

### Warnings (Should Fix)
{None / List with recommendations}

---

## 9. Recommendations

**Code Quality**:
- {Recommendation 1}

**Performance**:
- {Recommendation 1}

**Security**:
- {Recommendation 1}

---

## 10. Approval

**Status**: ✅ PASSED / ❌ FAILED

**Blockers**: {X}
**Critical**: {Y}
**Warnings**: {Z}

**Recommendation**:
- ✅ Proceed to testing
- ❌ Fix issues first

**Validator**: odoo-validator agent
**Date**: {DATE}

---

**Next**: {
  If PASSED: Run `odoo-tester` agent
  If FAILED: Fix {X} issues and re-validate
}
