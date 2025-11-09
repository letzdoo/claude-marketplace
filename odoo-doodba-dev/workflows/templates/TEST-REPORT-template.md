# Test Report: {FEATURE_NAME}

> **⚠️ DEPRECATED (v2.0)**: This template is for v1.x workflow reference only.
>
> **v2.0 testing is automatic and inline** - results are reported directly in chat.
> The `odoo-verifier` agent runs tests automatically and reports results inline.
> Detailed test reports are only created if there are failures requiring investigation.
>
> This template is kept for reference but is not actively used in v2.0 workflow.

---

**Date**: {DATE}
**Module**: `{module_name}`
**Status**: ⏳ Running / ✅ Passed / ❌ Failed

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | {X} |
| **Passed** | {Y} ✅ |
| **Failed** | {Z} ❌ |
| **Success Rate** | {XX}% |
| **Execution Time** | {X.XX}s |
| **Database Queries** | {XXXX} |

**Overall**: {PASSED / FAILED}

---

## Test Results

### 1. Creation Tests

#### ✅ test_01_create_basic
- **Purpose**: Test basic record creation
- **Status**: PASSED
- **Duration**: 0.05s

{Repeat for each test}

---

### 2. Business Logic Tests

#### ✅ test_02_computed_fields
- **Purpose**: Test computed field calculations
- **Status**: PASSED
- **Duration**: 0.06s

#### ✅ test_03_state_transitions
- **Purpose**: Test workflow state changes
- **Status**: PASSED
- **Duration**: 0.07s

**State Transitions Tested**:
| From | To | Method | Result |
|------|-----|--------|--------|
| draft | confirmed | `action_confirm()` | ✅ |
| confirmed | done | `action_done()` | ✅ |

---

### 3. Validation Tests

#### ✅ test_04_required_fields
- **Purpose**: Test required field validation
- **Status**: PASSED
- **Duration**: 0.04s

#### ✅ test_05_constraints
- **Purpose**: Test SQL and Python constraints
- **Status**: PASSED
- **Duration**: 0.05s

---

### 4. CRUD Tests

#### ✅ test_06_write_operations
- **Purpose**: Test record updates
- **Status**: PASSED
- **Duration**: 0.05s

#### ✅ test_07_unlink_operations
- **Purpose**: Test record deletion with rules
- **Status**: PASSED
- **Duration**: 0.04s

---

### 5. Security Tests

#### ✅ test_08_access_rights
- **Purpose**: Test user access permissions
- **Status**: PASSED
- **Duration**: 0.07s

**Access Results**:
| Operation | User | Manager |
|-----------|------|---------|
| Read | ✓ | ✓ |
| Write | ✓ | ✓ |
| Create | ✓ | ✓ |
| Delete | ✗ | ✓ |

#### ✅ test_09_record_rules
- **Purpose**: Test record-level security
- **Status**: PASSED
- **Duration**: 0.08s

---

### 6. Integration Tests

#### ✅ test_10_module_integration
- **Purpose**: Test integration with dependent modules
- **Status**: PASSED
- **Duration**: 0.09s

---

## Failed Tests

{If any tests failed, list them here with error details}

### ❌ test_XX_name
- **Purpose**: {description}
- **Status**: FAILED
- **Error**: {error message}
- **Fix Required**: {fix description}

---

## Coverage Analysis

### Code Coverage
**Overall**: {XX}%

| File | Coverage | Lines | Covered |
|------|----------|-------|---------|
| `models/{model}.py` | 95% | 150 | 142 |
| `models/{model}_extend.py` | 100% | 45 | 45 |

### Feature Coverage
| Feature | Tests | Status |
|---------|-------|--------|
| Model creation | 2 | ✅ |
| Computed fields | 1 | ✅ |
| State transitions | 1 | ✅ |
| Constraints | 2 | ✅ |
| CRUD operations | 3 | ✅ |
| Security | 2 | ✅ |
| Integrations | 1 | ✅ |

**Uncovered Features**: {List if any}

---

## Performance

**Total Queries**: {XXXX}
**Average per Test**: {XX}
**Slowest Test**: {test_name} ({X.XX}s)

**N+1 Patterns**: {None detected / List issues}

---

## Test Execution

**Command**:
```bash
invoke test --modules={module_name}
```

**Output**:
```
Ran {X} tests in {X.XX}s
OK / FAILED
```

---

## Spec Compliance

**From**: `specs/SPEC-{feature-name}.md`

| Requirement | Implemented | Tested | Status |
|-------------|-------------|--------|--------|
| Create records | ✅ | ✅ | ✓ |
| State transitions | ✅ | ✅ | ✓ |
| Computed fields | ✅ | ✅ | ✓ |
| Security rules | ✅ | ✅ | ✓ |

**Coverage**: {XX}% of spec requirements tested

---

## Recommendations

**Test Improvements**:
1. {Recommendation}

**Code Improvements**:
1. {Recommendation}

---

## Approval

**Status**: ✅ ALL PASSED / ❌ TESTS FAILED

**Critical Failures**: {X}
**Non-Critical Issues**: {Y}

**Recommendation**:
- ✅ Proceed to documentation
- ❌ Fix failures and re-test

**Tester**: odoo-tester agent
**Date**: {DATE}

---

**Next**: {
  If PASSED: Run `odoo-documenter` agent
  If FAILED: Fix issues and re-run tests
}
