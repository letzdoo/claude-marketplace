# Scheduled Actions and Automation Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  CRON & AUTOMATION PATTERNS                                                  ║
║  Scheduled actions, server actions, and automated rules                      ║
║  Use for background jobs, triggers, and workflow automation                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Scheduled Actions (Cron Jobs)

### Basic Cron Definition (XML)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="ir_cron_process_pending" model="ir.cron">
        <field name="name">My Module: Process Pending Records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="state">code</field>
        <field name="code">model._cron_process_pending()</field>
        <field name="interval_number">1</field>
        <field name="interval_type">hours</field>
        <field name="numbercall">-1</field>
        <field name="active">True</field>
        <field name="doall">False</field>
    </record>
</odoo>
```

### Interval Types
| Type | Description |
|------|-------------|
| `minutes` | Run every X minutes |
| `hours` | Run every X hours |
| `days` | Run every X days |
| `weeks` | Run every X weeks |
| `months` | Run every X months |

### Cron Attributes
| Attribute | Description |
|-----------|-------------|
| `interval_number` | Number of intervals |
| `interval_type` | Type of interval |
| `numbercall` | -1 for infinite, or count |
| `active` | Enable/disable cron |
| `doall` | Run missed executions |
| `nextcall` | Next execution datetime |
| `priority` | Execution priority (lower = first) |

---

## Python Cron Methods (v18)

### Basic Cron Method
```python
from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class MyModel(models.Model):
    _name = 'my.model'

    @api.model
    def _cron_process_pending(self) -> None:
        """Process pending records - called by scheduled action."""
        _logger.info("Starting cron: process pending records")

        records = self.search([('state', '=', 'pending')], limit=100)
        _logger.info(f"Found {len(records)} pending records")

        for record in records:
            try:
                record._process_single()
            except Exception as e:
                _logger.error(f"Error processing {record.id}: {e}")

        _logger.info("Cron completed: process pending records")
```

### Batch Processing Cron
```python
@api.model
def _cron_batch_process(self) -> None:
    """Process records in batches with commits."""
    batch_size = 100
    offset = 0
    processed = 0

    while True:
        # Fetch batch
        records = self.search(
            [('state', '=', 'pending')],
            limit=batch_size,
            offset=offset,
        )

        if not records:
            break

        for record in records:
            try:
                record.with_context(from_cron=True)._do_process()
                processed += 1
            except Exception as e:
                _logger.error(f"Error on record {record.id}: {e}")

        # Commit batch and clear cache
        self.env.cr.commit()
        self.env.invalidate_all()

        offset += batch_size
        _logger.info(f"Processed {processed} records so far...")

    _logger.info(f"Batch process complete: {processed} records")
```

### Time-Limited Cron
```python
import time

@api.model
def _cron_time_limited_process(self) -> None:
    """Process with time limit to prevent long-running jobs."""
    max_duration = 300  # 5 minutes
    start_time = time.time()
    processed = 0

    records = self.search([('needs_sync', '=', True)])

    for record in records:
        # Check time limit
        if time.time() - start_time > max_duration:
            _logger.warning(
                f"Time limit reached after {processed} records. "
                f"Remaining: {len(records) - processed}"
            )
            break

        try:
            record._sync_external()
            processed += 1
        except Exception as e:
            _logger.error(f"Sync error for {record.id}: {e}")

        # Periodic commit
        if processed % 50 == 0:
            self.env.cr.commit()

    _logger.info(f"Processed {processed}/{len(records)} records")
```

---

## Server Actions

### Python Code Action
```xml
<record id="action_mark_done" model="ir.actions.server">
    <field name="name">Mark as Done</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list,form</field>
    <field name="state">code</field>
    <field name="code">
if records:
    records.write({'state': 'done'})
    </field>
</record>
```

### Multi-Record Action
```xml
<record id="action_batch_confirm" model="ir.actions.server">
    <field name="name">Confirm Selected</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list</field>
    <field name="state">code</field>
    <field name="code">
for record in records:
    if record.state == 'draft':
        record.action_confirm()
    </field>
</record>
```

### Action with Notification
```xml
<record id="action_notify_users" model="ir.actions.server">
    <field name="name">Notify Users</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
count = len(records)
records.action_send_notification()
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Success',
        'message': f'Notified {count} users.',
        'type': 'success',
        'sticky': False,
    }
}
    </field>
</record>
```

---

## Automated Actions (Base Automation)

### On Create Trigger
```xml
<record id="automation_on_create" model="base.automation">
    <field name="name">Auto-assign on Create</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="trigger">on_create</field>
    <field name="state">code</field>
    <field name="code">
for record in records:
    if not record.user_id:
        record.user_id = record.create_uid
    </field>
</record>
```

### On Write Trigger
```xml
<record id="automation_on_state_change" model="base.automation">
    <field name="name">Notify on State Change</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="trigger">on_write</field>
    <field name="trigger_field_ids" eval="[(6, 0, [ref('field_my_model__state')])]"/>
    <field name="filter_domain">[('state', '=', 'confirmed')]</field>
    <field name="state">code</field>
    <field name="code">
records.message_post(
    body="Record has been confirmed.",
    message_type='notification',
)
    </field>
</record>
```

### Time-Based Trigger
```xml
<record id="automation_overdue_check" model="base.automation">
    <field name="name">Mark Overdue Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="trigger">on_time</field>
    <field name="trg_date_id" ref="field_my_model__deadline"/>
    <field name="trg_date_range">1</field>
    <field name="trg_date_range_type">day</field>
    <field name="filter_domain">[('state', 'not in', ['done', 'cancel'])]</field>
    <field name="state">code</field>
    <field name="code">
records.write({'is_overdue': True})
records.message_post(body="This record is now overdue!")
    </field>
</record>
```

### Trigger Types
| Trigger | When Executed |
|---------|---------------|
| `on_create` | After record creation |
| `on_write` | After record update |
| `on_create_or_write` | After create or update |
| `on_unlink` | Before record deletion |
| `on_time` | Based on date field |

---

## Queue Jobs (for Heavy Processing)

### Using ir.cron with Batching
```python
@api.model
def _cron_heavy_process(self) -> None:
    """Heavy process with queue-like behavior."""
    # Get unprocessed records
    to_process = self.search([
        ('processed', '=', False),
        ('attempts', '<', 3),  # Max retry attempts
    ], limit=50)

    for record in to_process:
        try:
            record.with_context(processing=True)._heavy_operation()
            record.processed = True
            record.processed_date = fields.Datetime.now()
        except Exception as e:
            record.attempts += 1
            record.last_error = str(e)
            _logger.error(f"Processing failed for {record.id}: {e}")

        # Commit after each to preserve progress
        self.env.cr.commit()
```

### Deferred Processing Pattern
```python
class MyModel(models.Model):
    _name = 'my.model'

    process_state = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], default='pending')
    process_error = fields.Text()

    def action_queue_for_processing(self) -> None:
        """Queue records for cron processing."""
        self.write({
            'process_state': 'pending',
            'process_error': False,
        })

    @api.model
    def _cron_process_queue(self) -> None:
        """Process queued records."""
        records = self.search([
            ('process_state', '=', 'pending')
        ], limit=20)

        for record in records:
            record.process_state = 'processing'
            self.env.cr.commit()

            try:
                record._do_heavy_work()
                record.process_state = 'done'
            except Exception as e:
                record.process_state = 'error'
                record.process_error = str(e)

            self.env.cr.commit()
```

---

## Best Practices

### 1. Logging
```python
import logging
_logger = logging.getLogger(__name__)

@api.model
def _cron_task(self) -> None:
    _logger.info("Cron started: %s", self._name)
    try:
        # Work here
        _logger.info("Cron completed successfully")
    except Exception as e:
        _logger.exception("Cron failed: %s", e)
        raise
```

### 2. Transaction Safety
```python
@api.model
def _cron_safe_process(self) -> None:
    """Process with proper transaction handling."""
    records = self.search([('pending', '=', True)])

    for record in records:
        # Use new cursor for isolation
        try:
            with self.env.cr.savepoint():
                record._process()
        except Exception as e:
            _logger.error(f"Failed {record.id}: {e}")
            # Savepoint rollback - continue with next
            continue
```

### 3. Idempotency
```python
@api.model
def _cron_idempotent_sync(self) -> None:
    """Idempotent sync - safe to run multiple times."""
    records = self.search([
        ('needs_sync', '=', True),
        ('last_sync_attempt', '<', fields.Datetime.now() - timedelta(minutes=5)),
    ])

    for record in records:
        record.last_sync_attempt = fields.Datetime.now()
        self.env.cr.commit()

        try:
            record._sync()
            record.needs_sync = False
        except Exception:
            pass  # Will retry on next run
```

### 4. Monitoring
```python
@api.model
def _cron_with_monitoring(self) -> None:
    """Cron with execution tracking."""
    start = fields.Datetime.now()

    try:
        count = self._do_work()
        status = 'success'
        error = False
    except Exception as e:
        count = 0
        status = 'error'
        error = str(e)

    # Log execution
    self.env['my.cron.log'].create({
        'cron_name': 'process_pending',
        'start_time': start,
        'end_time': fields.Datetime.now(),
        'records_processed': count,
        'status': status,
        'error_message': error,
    })
```

---

## Cron Security

### Manifest Declaration
```python
# Cron data file must be in 'data' section
'data': [
    'data/cron.xml',
]
```

### Access Rights
Crons run as the user who created them (usually admin). For specific user context:

```python
@api.model
def _cron_as_specific_user(self) -> None:
    """Run as specific user for proper access rights."""
    cron_user = self.env.ref('my_module.cron_service_user')
    self_as_user = self.with_user(cron_user)
    self_as_user._do_work()
```
