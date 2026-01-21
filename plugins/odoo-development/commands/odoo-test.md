---
name: odoo-test
description: Generate test cases for Odoo models and business logic. Use when user asks to "write tests", "generate unit tests", "test module", "create test cases".
arguments:
  - name: path
    description: Path to the module or model to test
    required: false
  - name: type
    description: Test type (unit, integration, security)
    required: false
  - name: version
    description: Target Odoo version
    required: false
input_examples:
  - description: "Generate unit tests for module"
    arguments:
      path: "./inventory_tracker"
      type: "unit"
      version: "18.0"
  - description: "Create security tests"
    arguments:
      path: "./hr_custom"
      type: "security"
  - description: "Full test suite generation"
    arguments:
      path: "./my_module"
      type: "integration"
---

# /odoo-test Command

Generate comprehensive test cases for Odoo models and business logic.

## CRITICAL: VERSION REQUIREMENT

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  Test patterns and decorators vary between Odoo versions.                    ║
║  Identify the target version before generating tests.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Test Types

### Unit Tests
- Model CRUD operations
- Computed field calculations
- Constraint validations
- Business logic methods

### Integration Tests
- Workflow transitions
- Cross-model operations
- API endpoints

### Security Tests
- Access rights verification
- Record rule enforcement
- Field visibility

## Execution Flow

### Step 1: Identify Module and Version

If not provided:
1. Check `__manifest__.py` for version
2. Ask user for target version

### Step 2: Analyze Module

Scan the module to identify:
- Models and their methods
- Computed fields
- Constraints
- Workflows

### Step 3: Generate Tests

Based on analysis, generate:
- Test class structure
- Test methods for each feature
- Fixtures and setup

## Output Format

```
tests/
├── __init__.py
├── test_{model_name}.py
├── test_{model_name}_security.py
└── common.py (shared fixtures)
```

## Test Templates by Version

### Odoo 14-15

```python
# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import AccessError, ValidationError

@tagged('post_install', '-at_install')
class Test{ModelName}(TransactionCase):

    def setUp(self):
        super(Test{ModelName}, self).setUp()
        self.Model = self.env['{model_name}']
        # Setup test data

    def test_create_record(self):
        """Test basic record creation."""
        record = self.Model.create({
            'name': 'Test',
        })
        self.assertTrue(record.id)

    def test_compute_field(self):
        """Test computed field calculation."""
        # Test implementation
```

### Odoo 16+

```python
# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import AccessError, ValidationError

@tagged('post_install', '-at_install')
class Test{ModelName}(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Disable tracking for faster tests
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create test data
        cls.company = cls.env.company
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })

    def test_create_record(self):
        """Test basic record creation."""
        record = self.env['{model_name}'].create({
            'name': 'Test',
        })
        self.assertTrue(record.id)
        self.assertEqual(record.state, 'draft')

    def test_workflow_confirm(self):
        """Test confirmation workflow."""
        record = self.env['{model_name}'].create({
            'name': 'Test',
        })
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')

    def test_constraint_validation(self):
        """Test constraint raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.env['{model_name}'].create({
                'name': '',  # Empty name should fail
            })

    def test_compute_total(self):
        """Test total amount computation."""
        record = self.env['{model_name}'].create({
            'name': 'Test',
            'line_ids': [
                (0, 0, {'name': 'Line 1', 'amount': 100}),
                (0, 0, {'name': 'Line 2', 'amount': 200}),
            ],
        })
        self.assertEqual(record.total_amount, 300)
```

### Security Test Template

```python
# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import AccessError

@tagged('post_install', '-at_install', 'security')
class Test{ModelName}Security(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test users
        cls.user_basic = cls.env['res.users'].create({
            'name': 'Basic User',
            'login': 'basic_user',
            'groups_id': [(6, 0, [cls.env.ref('{module_name}.group_user').id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Manager User',
            'login': 'manager_user',
            'groups_id': [(6, 0, [cls.env.ref('{module_name}.group_manager').id])],
        })

    def test_user_cannot_delete(self):
        """Test that basic users cannot delete records."""
        record = self.env['{model_name}'].create({'name': 'Test'})
        with self.assertRaises(AccessError):
            record.with_user(self.user_basic).unlink()

    def test_manager_can_delete(self):
        """Test that managers can delete records."""
        record = self.env['{model_name}'].create({'name': 'Test'})
        # Should not raise
        record.with_user(self.user_manager).unlink()

    def test_multi_company_isolation(self):
        """Test multi-company record rules."""
        company_2 = self.env['res.company'].create({'name': 'Company 2'})
        record = self.env['{model_name}'].create({
            'name': 'Test',
            'company_id': company_2.id,
        })
        # User from different company should not see record
        records = self.env['{model_name}'].with_user(self.user_basic).search([])
        self.assertNotIn(record.id, records.ids)
```

## Common Test Patterns

### Testing Computed Fields
```python
def test_computed_field(self):
    record = self.Model.create({'field1': 10, 'field2': 20})
    self.assertEqual(record.computed_total, 30)

    # Test recomputation on dependency change
    record.field1 = 15
    self.assertEqual(record.computed_total, 35)
```

### Testing Constraints
```python
def test_constraint(self):
    with self.assertRaises(ValidationError):
        self.Model.create({'amount': -100})  # Negative not allowed
```

### Testing Workflows
```python
def test_workflow(self):
    record = self.Model.create({'name': 'Test'})
    self.assertEqual(record.state, 'draft')

    record.action_confirm()
    self.assertEqual(record.state, 'confirmed')

    record.action_done()
    self.assertEqual(record.state, 'done')

    # Cannot go back from done
    with self.assertRaises(UserError):
        record.action_draft()
```

### Testing with Different Users
```python
def test_as_different_user(self):
    record = self.Model.create({'name': 'Test'})

    # Switch user context
    record_as_user = record.with_user(self.test_user)

    # Test access
    self.assertEqual(record_as_user.name, 'Test')
```

## Running Tests

```bash
# Run all module tests
./odoo-bin -c odoo.conf -d testdb --test-enable -i {module_name} --stop-after-init

# Run specific test class
./odoo-bin -c odoo.conf -d testdb --test-enable --test-tags={ModelName}

# Run with specific tags
./odoo-bin -c odoo.conf -d testdb --test-enable --test-tags=security
```

## Example Usage

```
# Generate tests for current module
/odoo-test

# Generate specific test type
/odoo-test ./my_module unit

# Generate security tests
/odoo-test ./my_module security 18.0
```

## AI Agent Instructions

1. **IDENTIFY**: Module and target version
2. **ANALYZE**: Models, methods, constraints
3. **GENERATE**: Appropriate test structure
4. **INCLUDE**: Setup, teardown, fixtures
5. **COVER**: CRUD, workflows, constraints, security
6. **TAG**: Tests appropriately for selective running
