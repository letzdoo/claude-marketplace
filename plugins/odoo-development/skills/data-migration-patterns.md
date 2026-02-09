# Data Migration and Upgrade Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  DATA MIGRATION PATTERNS                                                     ║
║  Version upgrades, data transformation, and migration scripts                ║
║  Use for module upgrades, data fixes, and version transitions                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Migration Script Structure

### Directory Layout
```
my_module/
├── migrations/
│   ├── 14.0.1.1/
│   │   ├── pre-migrate.py
│   │   └── post-migrate.py
│   ├── 15.0.1.0/
│   │   ├── pre-migrate.py
│   │   └── post-migrate.py
│   └── 16.0.2.0/
│       └── post-migrate.py
└── __manifest__.py
```

### Version Numbering
```python
# __manifest__.py
{
    'name': 'My Module',
    'version': '16.0.2.0.1',  # odoo_version.module_version
    #           ^^ ^^ ^ ^
    #           |  |  | └── patch
    #           |  |  └──── minor
    #           |  └─────── major
    #           └────────── Odoo version
}
```

---

## Pre-Migration Scripts

Pre-migrations run BEFORE the module is updated. Use for:
- Renaming tables/columns
- Preserving data before schema changes
- Removing constraints that would block updates

### Basic Pre-Migration
```python
# migrations/16.0.2.0/pre-migrate.py
import logging
from odoo import SUPERUSER_ID
from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Pre-migration: prepare database for update."""
    if not version:
        # Fresh install, no migration needed
        return

    _logger.info("Starting pre-migration from %s", version)

    # Rename column before ORM sees it
    cr.execute("""
        ALTER TABLE my_model
        RENAME COLUMN old_field TO x_old_field_backup
    """)

    _logger.info("Pre-migration completed")
```

### Rename Table
```python
def migrate(cr, version):
    """Rename table before model rename."""
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'old_model_name'
        )
    """)
    if cr.fetchone()[0]:
        cr.execute("ALTER TABLE old_model_name RENAME TO new_model_name")
        _logger.info("Renamed table old_model_name to new_model_name")
```

### Preserve Data Before Removal
```python
def migrate(cr, version):
    """Backup data before field removal."""
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = 'my_model'
            AND column_name = 'deprecated_field'
        )
    """)
    if cr.fetchone()[0]:
        # Create backup table
        cr.execute("""
            CREATE TABLE IF NOT EXISTS my_model_field_backup AS
            SELECT id, deprecated_field
            FROM my_model
            WHERE deprecated_field IS NOT NULL
        """)
        _logger.info("Backed up deprecated_field data")
```

### Remove Constraints
```python
def migrate(cr, version):
    """Remove constraint before schema change."""
    cr.execute("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'my_model'
        AND constraint_name LIKE '%_check'
    """)
    for (constraint_name,) in cr.fetchall():
        cr.execute(f"ALTER TABLE my_model DROP CONSTRAINT {constraint_name}")
        _logger.info("Dropped constraint %s", constraint_name)
```

---

## Post-Migration Scripts

Post-migrations run AFTER the module is updated. Use for:
- Data transformation
- Setting default values
- Migrating data between fields
- Cleanup operations

### Basic Post-Migration
```python
# migrations/16.0.2.0/post-migrate.py
import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-migration: transform data after update."""
    if not version:
        return

    _logger.info("Starting post-migration from %s", version)

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Use ORM for data operations
    records = env['my.model'].search([('new_field', '=', False)])
    for record in records:
        record.new_field = record.old_field

    _logger.info("Migrated %d records", len(records))
```

### Migrate Field Data
```python
def migrate(cr, version):
    """Migrate data from old field to new field."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Direct SQL for large datasets
    cr.execute("""
        UPDATE my_model
        SET new_state = CASE state
            WHEN 'draft' THEN 'new'
            WHEN 'open' THEN 'in_progress'
            WHEN 'done' THEN 'completed'
            ELSE 'unknown'
        END
        WHERE new_state IS NULL
    """)
    _logger.info("Migrated %d state values", cr.rowcount)
```

### Migrate Many2one to Many2many
```python
def migrate(cr, version):
    """Convert single relation to multiple."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Get records with old single value
    cr.execute("""
        SELECT id, old_partner_id
        FROM my_model
        WHERE old_partner_id IS NOT NULL
    """)

    for record_id, partner_id in cr.fetchall():
        # Insert into relation table
        cr.execute("""
            INSERT INTO my_model_partner_rel (my_model_id, partner_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (record_id, partner_id))

    _logger.info("Migrated partner relations")
```

### Set Computed Field Store
```python
def migrate(cr, version):
    """Initialize stored computed field."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Trigger recomputation
    records = env['my.model'].search([])
    records._compute_total_amount()

    # Or use SQL for performance
    cr.execute("""
        UPDATE my_model m
        SET total_amount = (
            SELECT COALESCE(SUM(l.amount), 0)
            FROM my_model_line l
            WHERE l.model_id = m.id
        )
    """)
```

### Migrate XML IDs
```python
def migrate(cr, version):
    """Rename XML IDs after module rename."""
    cr.execute("""
        UPDATE ir_model_data
        SET module = 'new_module_name'
        WHERE module = 'old_module_name'
    """)

    # Update specific record references
    cr.execute("""
        UPDATE ir_model_data
        SET name = REPLACE(name, 'old_prefix_', 'new_prefix_')
        WHERE module = 'my_module'
        AND name LIKE 'old_prefix_%'
    """)
```

---

## openupgrade Patterns

Using OpenUpgrade library for complex migrations:

### Rename Field
```python
from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.rename_fields(
        cr,
        [
            ('my.model', 'my_model', 'old_field', 'new_field'),
        ]
    )
```

### Rename Model
```python
def migrate(cr, version):
    openupgrade.rename_models(
        cr,
        [
            ('old.model', 'new.model'),
        ]
    )
    openupgrade.rename_tables(
        cr,
        [
            ('old_model', 'new_model'),
        ]
    )
```

### Merge Records
```python
def migrate(cr, version):
    """Merge duplicate records."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    duplicates = env['my.model'].search([])
    groups = {}
    for record in duplicates:
        key = record.name.lower().strip()
        if key not in groups:
            groups[key] = []
        groups[key].append(record)

    for key, records in groups.items():
        if len(records) > 1:
            main = records[0]
            for duplicate in records[1:]:
                openupgrade.merge_records(
                    env,
                    'my.model',
                    [duplicate.id],
                    main.id,
                )
```

---

## Batch Processing

### Large Dataset Migration
```python
def migrate(cr, version):
    """Process large dataset in batches."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    batch_size = 1000
    offset = 0
    total = 0

    while True:
        cr.execute("""
            SELECT id FROM my_model
            WHERE needs_migration = true
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (batch_size, offset))

        ids = [row[0] for row in cr.fetchall()]
        if not ids:
            break

        records = env['my.model'].browse(ids)
        for record in records:
            record._migrate_data()
            total += 1

        # Commit batch
        cr.commit()
        env.invalidate_all()

        offset += batch_size
        _logger.info("Processed %d records...", total)

    _logger.info("Migration complete: %d records", total)
```

### Parallel Migration (Advanced)
```python
def migrate(cr, version):
    """Use SQL for parallel-safe operations."""
    # Atomic update with RETURNING
    while True:
        cr.execute("""
            WITH to_update AS (
                SELECT id FROM my_model
                WHERE migrated = false
                LIMIT 100
                FOR UPDATE SKIP LOCKED
            )
            UPDATE my_model m
            SET
                new_field = old_field * 1.1,
                migrated = true
            FROM to_update
            WHERE m.id = to_update.id
            RETURNING m.id
        """)

        updated = cr.fetchall()
        if not updated:
            break

        cr.commit()
```

---

## Testing Migrations

### Migration Test Pattern
```python
# tests/test_migration.py
from odoo.tests import TransactionCase


class TestMigration(TransactionCase):

    def setUp(self):
        super().setUp()
        # Create test data with old structure
        self.test_record = self.env['my.model'].create({
            'name': 'Test',
            'old_field': 'value',
        })

    def test_field_migration(self):
        """Test that old field migrates to new field."""
        # Simulate migration
        self.test_record._migrate_field()

        self.assertEqual(
            self.test_record.new_field,
            'value',
            "Field value should be migrated"
        )

    def test_state_migration(self):
        """Test state value mapping."""
        self.test_record.old_state = 'draft'
        self.test_record._migrate_state()

        self.assertEqual(
            self.test_record.state,
            'new',
            "State 'draft' should map to 'new'"
        )
```

---

## Common Migration Tasks

### Add Default Value
```python
def migrate(cr, version):
    """Set default for new required field."""
    cr.execute("""
        UPDATE my_model
        SET new_required_field = 'default_value'
        WHERE new_required_field IS NULL
    """)
```

### Convert Data Type
```python
def migrate(cr, version):
    """Convert char to integer."""
    # Add temporary column
    cr.execute("""
        ALTER TABLE my_model
        ADD COLUMN IF NOT EXISTS numeric_code INTEGER
    """)

    # Convert with error handling
    cr.execute("""
        UPDATE my_model
        SET numeric_code = CASE
            WHEN char_code ~ '^[0-9]+$' THEN char_code::INTEGER
            ELSE 0
        END
    """)
```

### Migrate Attachments
```python
def migrate(cr, version):
    """Move attachments to new model."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    attachments = env['ir.attachment'].search([
        ('res_model', '=', 'old.model'),
    ])

    for attachment in attachments:
        # Find corresponding new record
        cr.execute("""
            SELECT new_id FROM model_mapping
            WHERE old_id = %s
        """, (attachment.res_id,))
        result = cr.fetchone()

        if result:
            attachment.write({
                'res_model': 'new.model',
                'res_id': result[0],
            })
```

### Update Mail Followers
```python
def migrate(cr, version):
    """Update followers after model rename."""
    cr.execute("""
        UPDATE mail_followers
        SET res_model = 'new.model'
        WHERE res_model = 'old.model'
    """)

    cr.execute("""
        UPDATE mail_message
        SET model = 'new.model'
        WHERE model = 'old.model'
    """)
```

---

## Best Practices

### 1. Always Check Version
```python
def migrate(cr, version):
    if not version:
        return  # Fresh install
    # Migration code
```

### 2. Use Logging
```python
_logger.info("Starting migration from %s", version)
_logger.info("Migrated %d records", count)
_logger.warning("Skipped %d invalid records", skipped)
```

### 3. Handle Errors Gracefully
```python
def migrate(cr, version):
    try:
        # Migration code
    except Exception as e:
        _logger.error("Migration failed: %s", e)
        raise
```

### 4. Make Idempotent
```python
# Good - can run multiple times
cr.execute("""
    UPDATE my_model
    SET new_field = old_field
    WHERE new_field IS NULL  -- Only unmigrated
""")

# Bad - breaks on re-run
cr.execute("""
    UPDATE my_model
    SET new_field = old_field
""")
```

### 5. Commit Large Operations
```python
for i, record in enumerate(records):
    record.migrate()
    if i % 1000 == 0:
        cr.commit()
        env.invalidate_all()
```

### 6. Test Before Production
```python
# Run on copy of production database
# Verify data integrity after migration
# Check performance with realistic data volumes
```

### 7. Installing Modules During Migration
```python
# Good - use button_install() during migration
def migrate(cr, version):
    """Install dependency module during migration."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    module = env['ir.module.module'].search([
        ('name', '=', 'required_module'),
        ('state', '!=', 'installed'),
    ])

    if module:
        module.button_install()
        _logger.info("Queued installation of %s", module.name)

# Bad - causes UserError during migration
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env['ir.module.module'].search([
        ('name', '=', 'required_module'),
    ])
    module._button_immediate_install()  # ERROR: Cannot be called on non-loaded registries
```

**Why**: During migration, the registry is not fully loaded. The `_button_immediate_install()` method requires a complete registry and will raise:
```
odoo.exceptions.UserError: The method _button_immediate_install cannot be called on init or non loaded registries. Please use button_install instead.
```

Use `button_install()` which queues the installation to happen after the registry is properly initialized.

---

## Version-Specific Notes

| Version | Migration Notes |
|---------|-----------------|
| 14→15 | `@api.multi` removed, update method signatures |
| 15→16 | OWL 2.x, `Command` class for x2many |
| 16→17 | `attrs` removed, use inline expressions |
| 17→18 | `_check_company_auto`, `SQL()` builder |
| 18→19 | Type hints required, `SQL()` mandatory |
