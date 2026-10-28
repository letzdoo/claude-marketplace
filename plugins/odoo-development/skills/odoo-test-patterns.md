# Odoo Test Patterns Guide

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  TEST PATTERNS GUIDE                                                         ║
║  Comprehensive testing patterns for Odoo modules across all versions         ║
║  Generate when include_tests: true is specified                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Test File Structure

```
{module_name}/
├── tests/
│   ├── __init__.py
│   ├── common.py              # Shared test data and base classes
│   ├── test_{model_name}.py   # Model unit tests
│   ├── test_security.py       # Security/access tests
│   └── test_integration.py    # Integration tests
```

## Test Class Hierarchy

```python
# tests/__init__.py
from . import test_my_model
from . import test_security
from . import test_integration
```

Test collection fails silently (nothing warns):

- The file must be named `test_*.py` **and** be imported in `tests/__init__.py`; otherwise it is never collected.
- **Imported test classes**: a `TestCase` class imported into another test file is collected again (runs twice) in 14.0-17.0; from 18.0 classes whose `__module__` is another file are skipped. Define each test class in exactly one `test_*.py` file and import shared bases from `common.py` (not from another `test_*.py`).
- **Inherited `test_*` methods**: collected from base classes in 14.0-17.0 (a shared base with `test_*` methods runs once per subclass); from 18.0 they are **not** collected unless the subclass sets `allow_inherited_tests_method = True`. Put shared tests in a mixin without `test_` methods, or set the flag deliberately (18.0+).

## Base Test Classes

### Base classes per version

| Class | 14.0 | 15.0 | 16.0-17.0 | 18.0-19.0 |
|---|---|---|---|---|
| `TransactionCase` (`odoo.tests`) | per-test transaction, **no** class-level `cls.env` | savepoint-based, `setUpClass` + `cls.env` | same | same |
| `SavepointCase` | class-level fixtures (use this in 14.0) | deprecated alias | 16.0: deprecated alias; 17.0: removed | removed |
| `HttpCase` | yes | yes | yes | yes |
| `BaseCommon` (`odoo.addons.base.tests.common`) | - | - | yes | yes (19.0 extended, see below) |
| `BaseUsersCommon` (adds `user_internal`, `user_portal`) | - | - | yes | 18.0 yes; 19.0 - (use `BaseCommon._create_new_internal_user()` / `_create_new_portal_user()`) |
| `TransactionCaseWithUserDemo` / `HttpCaseWithUserDemo` | yes (per-test `setUp`) | yes | yes | yes |
| `new_test_user` (`odoo.tests.common`) | yes | yes | yes | yes |

What `BaseCommon` really sets up:
- **16.0-18.0**: `cls.env` with a context that disables mail side effects (`DISABLED_MAIL_CONTEXT`: `tracking_disable`, `mail_create_nolog`, `mail_create_nosubscribe`, `mail_notrack`, `no_reset_password`), USD forced as company currency, and a test partner `cls.partner`. The test still runs as **superuser**; there is no non-admin user or extra company. `BaseUsersCommon` adds `cls.user_internal` and `cls.user_portal`.
- **19.0**: same context (overridable `default_env_context()`), plus `cls.company`, `cls.currency`, `cls.partner`. `setup_independent_user()` / `setup_independent_company()` are hooks returning `None` by default - unless overridden, the test still runs as superuser (with `base.group_user` added).

For tests that must check access rights, create a user explicitly (`new_test_user`, `BaseUsersCommon` in 16.0-18.0, or as in the common setup below) and use `with_user()`. Demo data is not guaranteed to be installed - only use `TransactionCaseWithUserDemo`/`HttpCaseWithUserDemo` when the test needs the demo user.

```python
# 16.0+ business test base
from odoo.addons.base.tests.common import BaseCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestMyFlow(BaseCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env['my.model'].create({'name': 'X', 'partner_id': cls.partner.id})
```

### Common Test Setup

> **Version notes for this example**
> - **14.0**: no class-level `cls.env` in `TransactionCase` (see table above); a `setUpClass` fixture needs
>   `from odoo.tests.common import SavepointCase` and `class TestMyModuleCommon(SavepointCase)`.
> - **14.0**: no `Command`; use tuples `[(6, 0, ids)]` as below. 15.0+: `[Command.set(ids)]`.
> - **19.0**: the `res.users` groups field is `group_ids`, not `groups_id`.

```python
# tests/common.py (15.0-18.0 as written; see notes above for 14.0 and 19.0)
from odoo.tests import TransactionCase, tagged

class TestMyModuleCommon(TransactionCase):
    """Common setup for all tests in this module"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create shared test data
        cls.company = cls.env.ref('base.main_company')
        cls.user_admin = cls.env.ref('base.user_admin')

        # Create test partner
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })

        # Create test user with specific groups
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'test_manager',
            'email': 'manager@example.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('my_module.group_manager').id,
            ])],
        })

        cls.user_basic = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'user@example.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
            ])],
        })
```

## Unit Tests

### Basic Model Tests

```python
# tests/test_my_model.py
from odoo.tests import tagged
from odoo.exceptions import ValidationError, UserError
from .common import TestMyModuleCommon


@tagged('post_install', '-at_install')
class TestMyModel(TestMyModuleCommon):
    """Unit tests for my.model"""

    def test_create_record(self):
        """Test basic record creation"""
        record = self.env['my.model'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
        })
        self.assertTrue(record.id)
        self.assertEqual(record.name, 'Test Record')
        self.assertEqual(record.state, 'draft')

    def test_create_with_defaults(self):
        """Test creation with default values"""
        record = self.env['my.model'].create({
            'name': 'Test',
        })
        # Check default company
        self.assertEqual(record.company_id, self.env.company)
        # Check default state
        self.assertEqual(record.state, 'draft')

    def test_name_required(self):
        """Test that name is required"""
        with self.assertRaises(Exception):
            self.env['my.model'].create({})

    def test_state_workflow(self):
        """Test state transitions"""
        record = self.env['my.model'].create({
            'name': 'Workflow Test',
        })

        # Add required line for confirmation
        self.env['my.model.line'].create({
            'model_id': record.id,
            'name': 'Line 1',
            'quantity': 1,
        })

        # Test confirm
        self.assertEqual(record.state, 'draft')
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')

        # Test done
        record.action_done()
        self.assertEqual(record.state, 'done')

    def test_confirm_without_lines_fails(self):
        """Test that confirmation requires lines"""
        record = self.env['my.model'].create({
            'name': 'No Lines Test',
        })

        with self.assertRaises(UserError):
            record.action_confirm()
```

### Computed Field Tests

```python
@tagged('post_install', '-at_install')
class TestMyModelComputed(TestMyModuleCommon):
    """Test computed fields"""

    def test_compute_total(self):
        """Test total computation"""
        record = self.env['my.model'].create({
            'name': 'Computed Test',
        })

        # Create lines
        self.env['my.model.line'].create({
            'model_id': record.id,
            'name': 'Line 1',
            'quantity': 2,
            'price_unit': 10.0,
        })
        self.env['my.model.line'].create({
            'model_id': record.id,
            'name': 'Line 2',
            'quantity': 3,
            'price_unit': 20.0,
        })

        # Total should be (2*10) + (3*20) = 80
        self.assertEqual(record.total_amount, 80.0)

    def test_compute_line_count(self):
        """Test line count computation"""
        record = self.env['my.model'].create({'name': 'Count Test'})
        self.assertEqual(record.line_count, 0)

        self.env['my.model.line'].create({
            'model_id': record.id,
            'name': 'Line 1',
        })
        self.assertEqual(record.line_count, 1)
```

### Constraint Tests

```python
@tagged('post_install', '-at_install')
class TestMyModelConstraints(TestMyModuleCommon):
    """Test model constraints"""

    def test_date_constraint(self):
        """Test date_start must be before date_end"""
        with self.assertRaises(ValidationError):
            self.env['my.model'].create({
                'name': 'Date Test',
                'date_start': '2024-12-31',
                'date_end': '2024-01-01',  # Before start
            })

    def test_unique_code_per_company(self):
        """Test unique code constraint"""
        self.env['my.model'].create({
            'name': 'First',
            'code': 'TEST001',
        })

        with self.assertRaises(Exception):  # IntegrityError wrapped
            self.env['my.model'].create({
                'name': 'Duplicate',
                'code': 'TEST001',  # Same code
            })

    def test_positive_quantity(self):
        """Test quantity must be positive"""
        record = self.env['my.model'].create({'name': 'Qty Test'})

        with self.assertRaises(ValidationError):
            self.env['my.model.line'].create({
                'model_id': record.id,
                'name': 'Negative',
                'quantity': -1,
            })
```

## Security Tests

```python
# tests/test_security.py
from odoo.tests import tagged
from odoo.exceptions import AccessError
from .common import TestMyModuleCommon


@tagged('post_install', '-at_install')
class TestMyModelSecurity(TestMyModuleCommon):
    """Security and access rights tests"""

    def test_user_can_read_own_records(self):
        """Test basic user can read their own records"""
        record = self.env['my.model'].with_user(self.user_basic).create({
            'name': 'User Record',
        })

        # Should be able to read
        record.with_user(self.user_basic).read(['name'])

    def test_user_cannot_delete(self):
        """Test basic user cannot delete records"""
        record = self.env['my.model'].create({'name': 'Test'})

        with self.assertRaises(AccessError):
            record.with_user(self.user_basic).unlink()

    def test_manager_can_delete(self):
        """Test manager can delete records"""
        record = self.env['my.model'].create({'name': 'Test'})
        record.with_user(self.user_manager).unlink()
        self.assertFalse(record.exists())

    def test_multi_company_isolation(self):
        """Test records are isolated by company"""
        # Create second company
        company2 = self.env['res.company'].create({
            'name': 'Company 2',
        })

        # Create user in company2
        user_company2 = self.env['res.users'].create({
            'name': 'User Company 2',
            'login': 'user_c2',
            'company_id': company2.id,
            'company_ids': [(6, 0, [company2.id])],
        })

        # Create record in main company
        record = self.env['my.model'].create({
            'name': 'Main Company Record',
            'company_id': self.company.id,
        })

        # User in company2 should not see it
        records = self.env['my.model'].with_user(user_company2).search([])
        self.assertNotIn(record, records)

    def test_sudo_bypasses_rules(self):
        """Test sudo() bypasses record rules"""
        record = self.env['my.model'].create({'name': 'Test'})

        # Admin can access via sudo
        record_sudo = record.sudo()
        self.assertTrue(record_sudo.exists())
```

## Integration Tests

```python
# tests/test_integration.py
from odoo.tests import tagged, HttpCase
from .common import TestMyModuleCommon


@tagged('post_install', '-at_install')
class TestMyModelIntegration(TestMyModuleCommon):
    """Integration tests"""

    def test_full_workflow(self):
        """Test complete record lifecycle"""
        # Create
        record = self.env['my.model'].create({
            'name': 'Full Workflow Test',
            'partner_id': self.partner.id,
        })
        self.assertEqual(record.state, 'draft')

        # Add lines
        self.env['my.model.line'].create({
            'model_id': record.id,
            'name': 'Line 1',
            'quantity': 1,
            'price_unit': 100,
        })

        # Confirm
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')

        # Check partner was notified (if mail integration)
        if hasattr(record, 'message_ids'):
            self.assertTrue(len(record.message_ids) > 0)

        # Complete
        record.action_done()
        self.assertEqual(record.state, 'done')

        # Cannot delete done records
        from odoo.exceptions import UserError
        with self.assertRaises(UserError):
            record.unlink()

    def test_copy_record(self):
        """Test record duplication"""
        record = self.env['my.model'].create({
            'name': 'Original',
            'state': 'confirmed',
        })

        # Add line
        self.env['my.model.line'].create({
            'model_id': record.id,
            'name': 'Line',
        })

        # Copy
        copy = record.copy()

        self.assertNotEqual(copy.id, record.id)
        self.assertIn('(copy)', copy.name)
        self.assertEqual(copy.state, 'draft')  # Reset to draft
        self.assertEqual(len(copy.line_ids), len(record.line_ids))  # Lines copied

    def test_batch_operations(self):
        """Test batch create and write"""
        # Batch create
        records = self.env['my.model'].create([
            {'name': 'Batch 1'},
            {'name': 'Batch 2'},
            {'name': 'Batch 3'},
        ])
        self.assertEqual(len(records), 3)

        # Batch write
        records.write({'active': False})
        for record in records:
            self.assertFalse(record.active)
```

## HTTP/Tour Tests

```python
# tests/test_ui.py
from odoo.tests import tagged, HttpCase


@tagged('post_install', '-at_install')
class TestMyModelUI(HttpCase):
    """UI/Tour tests"""

    def test_ui_create_record(self):
        """Test creating record via UI"""
        self.start_tour(
            '/web',
            'my_module_create_tour',
            login='admin',
        )
```

## Test Tags Reference

| Tag | Meaning |
|-----|---------|
| `standard` | Default tag of every test class (all versions) |
| `at_install` | **Default** in 14.0-19.0: runs right after the module is installed, before later modules load |
| `post_install` | Runs after all modules are installed (fully loaded registry); must be added explicitly |
| `-at_install` | Removes the default `at_install` tag |
| `external` | Requires external services (excluded unless selected) |

Master/20.0 switched the default to `post_install`; **14.0-19.0 did not**.

- The default tags `{'standard', 'at_install'}` apply to `HttpCase` too.
- Post-install test: `@tagged('post_install', '-at_install')`. Required for `HttpCase` and tours (they need the fully loaded registry and assets).
- Set exactly one of `at_install` / `post_install`:
  - `@tagged('post_install')` alone keeps the default `at_install` -> the class carries **both** tags and **runs twice**.
  - `@tagged('-at_install')` without `post_install` -> **neither** tag -> the class **never runs**.
  - `tagged()` only logs a warning in both cases; nothing fails.
- Tests run only for installed modules (`--test-enable` with `-i`/`-u`, or `--test-tags`).

```python
from odoo.tests import HttpCase, TransactionCase, tagged


class TestMyModelInstall(TransactionCase):
    """No decorator: tags {'standard', 'at_install'} - runs right after install."""


@tagged('post_install', '-at_install')
class TestMyModelPost(TransactionCase):
    """Runs once, after all modules are installed."""


@tagged('post_install', '-at_install')
class TestMyModelUi(HttpCase):
    """HttpCase/tours: always post_install."""
```

`--test-tags` grammar (all versions): `[-][tag][/module][:class][.method]`, comma-separated.

```bash
--test-tags /my_module                       # all tests of my_module
--test-tags /my_module:TestMyModel           # one class
--test-tags /my_module:TestMyModel.test_create_record   # one method
--test-tags post_install/my_module           # only post_install tests of my_module
--test-tags /my_module,-/my_module:TestSlow  # exclude a class
```

Tag inheritance differs: in 14.0 every test class gets the default tags again (a `@tagged` on a common base class is **not** inherited); in 19.0 tags are inherited from the base class. Decorate every concrete test class explicitly so the behaviour is the same in all versions.

## Additional Rules from Odoo's Official Guidelines (verified for 14.0-19.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/`, branch 20.0) and were checked against the 14.0-19.0 sources.

### assertQueryCount, @warmup, @users

- Use `assertQueryCount` only in dedicated performance tests, never inside a business test (breaks on any unrelated ORM change).
- Only **exceeding** the budget fails; a lower count is merely logged - keep budgets exact.
- The count is asserted only on a **warm** run (`self.warm`): decorate the test with `@warmup`, otherwise the context manager only flushes and checks nothing. `@users('admin', 'demo')` runs the test once per login. Both decorators live in `odoo.tests.common`.

```python
from odoo.tests.common import TransactionCase, users, warmup


class TestMyPerf(TransactionCase):

    @users('admin')
    @warmup
    def test_read_partner_names(self):
        partners = self.env['res.partner'].search([], limit=20)
        partners.invalidate_recordset()  # 16.0+; 14.0-15.0: partners.invalidate_cache()
        with self.assertQueryCount(admin=1):  # exact budget measured on the warm run
            partners.mapped('name')
```

### mute_logger

Wrap expected errors and warnings so they do not pollute the test log (all versions):

```python
from psycopg2 import IntegrityError
from odoo.tools import mute_logger

with mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
    self.env['my.model'].create({'code': 'DUPLICATE'})  # violates a unique SQL constraint
```

## Version-Specific Test Patterns

### v15+ with Command Class

```python
def test_create_with_command(self):
    """Test creation with Command class (15.0+; in 14.0 use (0, 0, vals) tuples)"""
    from odoo.fields import Command

    record = self.env['my.model'].create({
        'name': 'Command Test',
        'line_ids': [
            Command.create({'name': 'Line 1', 'quantity': 1}),
            Command.create({'name': 'Line 2', 'quantity': 2}),
        ],
    })
    self.assertEqual(len(record.line_ids), 2)
```

### v17+ Visibility Testing

```python
def test_view_visibility(self):
    """Test view visibility conditions (v17+)"""
    record = self.env['my.model'].create({
        'name': 'Visibility Test',
        'state': 'draft',
    })

    # Get form view
    view = self.env['ir.ui.view'].search([
        ('model', '=', 'my.model'),
        ('type', '=', 'form'),
    ], limit=1)

    # In v17+, visibility uses Python expressions
    # Test that the view renders correctly
    fields_view = self.env['my.model'].get_views(
        [(view.id, 'form')]
    )['views']['form']
    self.assertIn('invisible', str(fields_view))
```

### Multi-Company Testing (all versions: `_check_company_auto` + `check_company=True`)

```python
def test_check_company_auto(self):
    """Test automatic company checking (14.0+; requires _check_company_auto = True
    on the model and check_company=True on partner_id)"""
    # Create partner in different company
    company2 = self.env['res.company'].create({'name': 'Company 2'})
    partner_c2 = self.env['res.partner'].create({
        'name': 'Partner C2',
        'company_id': company2.id,
    })

    # Should raise if check_company=True
    with self.assertRaises(Exception):
        self.env['my.model'].create({
            'name': 'Cross Company',
            'company_id': self.company.id,
            'partner_id': partner_c2.id,  # Different company
        })
```

## Running Tests

```bash
# Run all tests for a module
./odoo-bin -d testdb -i my_module --test-enable --stop-after-init

# Run specific test class (grammar: see Test Tags Reference)
./odoo-bin -d testdb -u my_module --test-tags /my_module:TestMyModel --stop-after-init

# Run with coverage
coverage run ./odoo-bin -d testdb -i my_module --test-enable --stop-after-init
coverage report
```

## Test Generation Checklist

For each model, generate tests for:

- [ ] Basic CRUD operations (create, read, update, delete)
- [ ] All computed fields
- [ ] All constraints (Python and SQL)
- [ ] State workflow transitions
- [ ] Access rights by user group
- [ ] Record rules (multi-company, ownership)
- [ ] Onchange methods
- [ ] Action methods (buttons)
- [ ] Copy behavior
- [ ] Batch operations
