# Test Report: {FEATURE_NAME}

**Date**: {DATE}
**Module**: `{module_name}`
**Test Status**: ⏳ Running / ✅ Passed / ❌ Failed

---

## 1. Test Execution Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | {X} |
| **Passed** | {Y} ✅ |
| **Failed** | {Z} ❌ |
| **Errors** | {E} ⚠️ |
| **Skipped** | {S} ⏭️ |
| **Success Rate** | {XX}% |
| **Execution Time** | {X.XX}s |
| **Database Queries** | {XXXX} |

**Overall Status**: {PASSED / FAILED}

---

## 2. Test Suite Details

### 2.1 Test File Information

**File**: `tests/test_{model_name}.py`
**Test Class**: `Test{ModelName}`
**Setup Method**: `setUpClass()` / `setUp()`

**Test Data Setup**:
```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    cls.partner = cls.env.ref('base.res_partner_1')
    cls.{model} = cls.env['{model.name}'].create({
        'name': 'Test Record',
        'partner_id': cls.partner.id,
    })
```

---

## 3. Test Results by Category

### 3.1 Model Creation Tests

#### ✅ test_01_create_{model}_basic
**Purpose**: Test basic record creation

**Steps**:
1. Create record with required fields
2. Verify record is created
3. Check default values

**Status**: PASSED ✅
**Duration**: 0.05s
**Assertions**: 3/3 passed

**Output**:
```
test_01_create_{model}_basic (tests.test_{model}.Test{Model}) ... ok
```

---

#### ✅ test_02_create_{model}_with_relations
**Purpose**: Test record creation with relational fields

**Steps**:
1. Create related records (lines, tags)
2. Create main record with relations
3. Verify relations are correct

**Status**: PASSED ✅
**Duration**: 0.08s
**Assertions**: 5/5 passed

---

### 3.2 Business Logic Tests

#### ✅ test_03_compute_fields
**Purpose**: Test computed field calculations

**Steps**:
1. Create record with line items
2. Verify total is computed correctly
3. Update lines and verify recomputation

**Status**: PASSED ✅
**Duration**: 0.06s
**Assertions**: 4/4 passed

**Computed Fields Tested**:
- `total_amount`: ✓ Correct calculation
- `field_count`: ✓ Correct count

---

#### ✅ test_04_state_transitions
**Purpose**: Test workflow state transitions

**Steps**:
1. Create record in 'draft' state
2. Call `action_confirm()` → verify 'confirmed'
3. Call `action_done()` → verify 'done'
4. Test `action_cancel()` from various states

**Status**: PASSED ✅
**Duration**: 0.07s
**Assertions**: 6/6 passed

**State Transitions Tested**:
| From | To | Method | Result |
|------|-----|--------|--------|
| draft | confirmed | `action_confirm()` | ✅ |
| confirmed | done | `action_done()` | ✅ |
| draft | cancelled | `action_cancel()` | ✅ |
| confirmed | cancelled | `action_cancel()` | ✅ |

---

### 3.3 Validation & Constraint Tests

#### ✅ test_05_required_fields
**Purpose**: Test required field validation

**Steps**:
1. Attempt to create record without required fields
2. Verify ValidationError is raised
3. Test each required field individually

**Status**: PASSED ✅
**Duration**: 0.04s
**Assertions**: 3/3 passed

**Required Fields Tested**:
- `name`: ✓ Validates correctly
- `partner_id`: ✓ Validates correctly
- `date_start`: ✓ Validates correctly

---

#### ✅ test_06_sql_constraints
**Purpose**: Test SQL constraint enforcement

**Steps**:
1. Create record with unique field
2. Attempt to create duplicate
3. Verify IntegrityError is raised

**Status**: PASSED ✅
**Duration**: 0.05s
**Assertions**: 2/2 passed

**SQL Constraints Tested**:
- `name_unique`: ✓ Enforced correctly

---

#### ✅ test_07_python_constraints
**Purpose**: Test Python constraint decorators

**Steps**:
1. Create record with valid data
2. Attempt invalid combinations
3. Verify ValidationError with correct message

**Status**: PASSED ✅
**Duration**: 0.06s
**Assertions**: 4/4 passed

**Python Constraints Tested**:
- `_check_dates()`: ✓ Date validation works
- `_check_amounts()`: ✓ Amount validation works

---

### 3.4 CRUD Operation Tests

#### ✅ test_08_write_operations
**Purpose**: Test record updates

**Steps**:
1. Create record
2. Update various fields
3. Verify changes are saved
4. Test write with invalid data

**Status**: PASSED ✅
**Duration**: 0.05s
**Assertions**: 5/5 passed

---

#### ✅ test_09_unlink_operations
**Purpose**: Test record deletion

**Steps**:
1. Create record in 'draft' state
2. Delete → verify success
3. Create record in 'confirmed' state
4. Attempt delete → verify error

**Status**: PASSED ✅
**Duration**: 0.04s
**Assertions**: 3/3 passed

**Deletion Rules Tested**:
- Draft records: ✓ Can delete
- Confirmed records: ✓ Cannot delete (correct error)

---

### 3.5 Model Extension Tests

#### ✅ test_10_extended_model_fields
**Purpose**: Test new fields added to existing model

**Steps**:
1. Get existing model record
2. Set new custom fields
3. Verify values are saved

**Status**: PASSED ✅
**Duration**: 0.04s
**Assertions**: 2/2 passed

**Extended Model**: `{existing.model}`
**New Fields Tested**:
- `custom_field`: ✓ Works correctly
- `related_id`: ✓ Relation works

---

#### ✅ test_11_extended_model_methods
**Purpose**: Test method overrides on existing model

**Steps**:
1. Get existing model record
2. Call overridden method
3. Verify custom logic executes
4. Verify super() is called

**Status**: PASSED ✅
**Duration**: 0.06s
**Assertions**: 3/3 passed

**Method Overrides Tested**:
- `action_confirm()`: ✓ Custom logic + super()
- `write()`: ✓ Tracking works

---

### 3.6 Security Tests

#### ✅ test_12_access_rights_user
**Purpose**: Test access rights for regular users

**Steps**:
1. Switch to user context
2. Test read access
3. Test write access
4. Test create access
5. Test delete access (should fail)

**Status**: PASSED ✅
**Duration**: 0.07s
**Assertions**: 4/4 passed

**Access Rights for `group_user`**:
- Read: ✓ Allowed
- Write: ✓ Allowed
- Create: ✓ Allowed
- Delete: ✓ Denied (correct)

---

#### ✅ test_13_record_rules
**Purpose**: Test record-level security rules

**Steps**:
1. Create records with different owners
2. Switch to user context
3. Verify user sees only own records

**Status**: PASSED ✅
**Duration**: 0.08s
**Assertions**: 3/3 passed

**Record Rules Tested**:
- User own records: ✓ Can see own records
- Other user records: ✓ Cannot see others' records

---

### 3.7 Integration Tests

#### ✅ test_14_with_related_modules
**Purpose**: Test integration with dependent modules

**Steps**:
1. Verify dependent module is installed
2. Test interactions with related models
3. Verify data flows correctly

**Status**: PASSED ✅
**Duration**: 0.09s
**Assertions**: 4/4 passed

**Module Integrations Tested**:
- `project`: ✓ Task integration works
- `quality_control`: ✓ Quality point integration works

---

#### ✅ test_15_chatter_functionality
**Purpose**: Test mail.thread integration

**Steps**:
1. Create record
2. Post message to chatter
3. Add follower
4. Schedule activity
5. Verify all features work

**Status**: PASSED ✅
**Duration**: 0.10s
**Assertions**: 5/5 passed

**Chatter Features Tested**:
- Message posting: ✓ Works
- Followers: ✓ Can add/remove
- Activities: ✓ Can schedule
- Tracking: ✓ Field changes tracked

---

## 4. Failed Tests (if any)

### ❌ test_XX_test_name (EXAMPLE - Remove if none)
**Purpose**: Test description

**Status**: FAILED ❌
**Duration**: 0.05s
**Error Type**: AssertionError

**Failure Details**:
```python
AssertionError: Expected 100.0, got 95.5
```

**Stack Trace**:
```
File "tests/test_{model}.py", line 123, in test_XX_test_name
    self.assertEqual(record.total_amount, 100.0)
AssertionError: 95.5 != 100.0
```

**Cause**: {explanation}

**Fix Required**: {fix_description}

---

## 5. Test Coverage Analysis

### 5.1 Code Coverage

**Overall Coverage**: {XX}%

| File | Coverage | Lines | Covered | Missing |
|------|----------|-------|---------|---------|
| `models/{model}.py` | 95% | 150 | 142 | 8 |
| `models/{model}_extend.py` | 100% | 45 | 45 | 0 |

**Uncovered Lines**:
- `models/{model}.py:78-82`: Exception handling path (edge case)
- `models/{model}.py:145-148`: Deprecated method

---

### 5.2 Feature Coverage

| Feature | Tests | Coverage |
|---------|-------|----------|
| Model creation | 2 | ✅ |
| Computed fields | 1 | ✅ |
| State transitions | 1 | ✅ |
| Constraints | 3 | ✅ |
| CRUD operations | 3 | ✅ |
| Security | 2 | ✅ |
| Integrations | 2 | ✅ |

**Uncovered Features**:
- Multi-company scenarios
- Advanced reporting
- Email notifications

---

## 6. Performance Analysis

### 6.1 Query Analysis

**Total Queries**: {XXXX}
**Average per Test**: {XX}
**Slowest Test**: `test_XX_name` ({X.XX}s)

### 6.2 Query Breakdown

| Test | Queries | Time | Avg Query Time |
|------|---------|------|----------------|
| test_01_create_basic | 45 | 0.05s | 1.1ms |
| test_04_state_transitions | 89 | 0.07s | 0.8ms |
| test_12_access_rights | 120 | 0.07s | 0.6ms |

**N+1 Query Patterns**: None detected ✅

---

## 7. Test Execution Log

### 7.1 Command
```bash
invoke test --modules={module_name}
```

### 7.2 Full Output
```
Running tests for module: {module_name}
odoo.tests.loader: discovered 15 tests in tests.test_{model}

test_01_create_{model}_basic (tests.test_{model}.Test{Model}) ... ok
test_02_create_{model}_with_relations (tests.test_{model}.Test{Model}) ... ok
test_03_compute_fields (tests.test_{model}.Test{Model}) ... ok
test_04_state_transitions (tests.test_{model}.Test{Model}) ... ok
test_05_required_fields (tests.test_{model}.Test{Model}) ... ok
test_06_sql_constraints (tests.test_{model}.Test{Model}) ... ok
test_07_python_constraints (tests.test_{model}.Test{Model}) ... ok
test_08_write_operations (tests.test_{model}.Test{Model}) ... ok
test_09_unlink_operations (tests.test_{model}.Test{Model}) ... ok
test_10_extended_model_fields (tests.test_{model}.Test{Model}) ... ok
test_11_extended_model_methods (tests.test_{model}.Test{Model}) ... ok
test_12_access_rights_user (tests.test_{model}.Test{Model}) ... ok
test_13_record_rules (tests.test_{model}.Test{Model}) ... ok
test_14_with_related_modules (tests.test_{model}.Test{Model}) ... ok
test_15_chatter_functionality (tests.test_{model}.Test{Model}) ... ok

----------------------------------------------------------------------
Ran 15 tests in 1.02s

OK
```

---

## 8. Recommendations

### 8.1 Test Improvements
1. Add tests for multi-company scenarios
2. Add performance tests with large datasets
3. Add tests for concurrent access
4. Improve coverage of exception handling

### 8.2 Code Improvements (based on testing)
1. Consider caching for `computed_field_name` to reduce queries
2. Add transaction handling for bulk operations
3. Add logging for state transitions

---

## 9. Comparison with Specification

### 9.1 Requirements Coverage

**From**: `specs/SPEC-{feature-name}.md`

| Requirement | Implemented | Tested | Status |
|-------------|-------------|--------|--------|
| Create records with validation | ✅ | ✅ | ✓ |
| State transitions | ✅ | ✅ | ✓ |
| Computed fields | ✅ | ✅ | ✓ |
| Security rules | ✅ | ✅ | ✓ |
| Model extensions | ✅ | ✅ | ✓ |
| Chatter integration | ✅ | ✅ | ✓ |

**Coverage**: 100% of specified requirements are tested

---

## 10. Known Issues & Limitations

### 10.1 Test Environment
- Testing on single database only
- No multi-company testing yet
- No load testing performed

### 10.2 Test Data
- Using demo data only
- Real-world data patterns not tested
- Edge cases may not be covered

---

## 11. Next Steps

### 11.1 If Tests Pass ✅
1. ✅ Generate documentation with `odoo-documenter`
2. ✅ Update README with test results
3. ✅ Create user guide
4. ✅ Prepare for deployment

### 11.2 If Tests Fail ❌
1. ❌ Review failure details above
2. ❌ Fix code issues
3. ❌ Re-run validation with `odoo-validator`
4. ❌ Re-run tests
5. ❌ Iterate until all pass

---

## 12. Approval

**Test Status**: ✅ ALL TESTS PASSED / ❌ TESTS FAILED

**Critical Failures**: 0
**Non-Critical Issues**: 0

**Recommendation**:
- ✅ Proceed to documentation
- ❌ Fix failures and re-test

**Tester**: odoo-tester agent
**Date**: {DATE}

---

**Next Step**: Generate documentation with `odoo-documenter` agent
