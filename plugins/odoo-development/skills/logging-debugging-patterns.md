# Logging and Debugging Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  LOGGING & DEBUGGING PATTERNS                                                ║
║  Proper logging, error tracking, and debugging techniques                    ║
║  Use for troubleshooting, monitoring, and audit trails                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Logging Setup

### Module Logger
```python
import logging

_logger = logging.getLogger(__name__)


class MyModel(models.Model):
    _name = 'my.model'

    def process_record(self):
        """Process with proper logging."""
        _logger.info("Processing record %s", self.id)

        try:
            result = self._do_work()
            _logger.debug("Work completed with result: %s", result)
            return result

        except ValueError as e:
            _logger.warning("Invalid value for record %s: %s", self.id, e)
            raise

        except Exception as e:
            _logger.error("Failed to process record %s: %s", self.id, e)
            _logger.exception("Full traceback:")
            raise
```

### Log Levels
| Level | Use Case |
|-------|----------|
| `DEBUG` | Detailed diagnostic info (disabled in production) |
| `INFO` | Normal operation events |
| `WARNING` | Something unexpected but not breaking |
| `ERROR` | Error that affects the operation |
| `CRITICAL` | System-level failure |

### Logging Best Practices
```python
# Good - Use lazy formatting
_logger.info("Processing order %s for customer %s", order.id, customer.name)

# Bad - Eager string formatting (computed even if not logged)
_logger.info(f"Processing order {order.id} for customer {customer.name}")

# Good - Log exceptions with traceback
try:
    risky_operation()
except Exception as e:
    _logger.exception("Operation failed: %s", e)

# Bad - Lose traceback information
try:
    risky_operation()
except Exception as e:
    _logger.error("Operation failed: %s", e)

# Good - Structured context
_logger.info(
    "Order %s: state changed from %s to %s",
    self.name, old_state, new_state
)

# Good - Performance-sensitive debug
if _logger.isEnabledFor(logging.DEBUG):
    _logger.debug("Full data: %s", expensive_data_format())
```

---

## Audit Logging

### Audit Trail Model
```python
class AuditLog(models.Model):
    _name = 'audit.log'
    _description = 'Audit Log'
    _order = 'create_date desc'

    model_name = fields.Char(string='Model', required=True, index=True)
    record_id = fields.Integer(string='Record ID', index=True)
    action = fields.Selection([
        ('create', 'Create'),
        ('write', 'Update'),
        ('unlink', 'Delete'),
        ('action', 'Action'),
    ], string='Action', required=True)
    user_id = fields.Many2one(
        'res.users', string='User',
        default=lambda self: self.env.user,
    )
    timestamp = fields.Datetime(
        string='Timestamp',
        default=fields.Datetime.now,
    )
    old_values = fields.Text(string='Old Values')
    new_values = fields.Text(string='New Values')
    ip_address = fields.Char(string='IP Address')
    description = fields.Text(string='Description')


class AuditMixin(models.AbstractModel):
    _name = 'audit.mixin'
    _description = 'Audit Mixin'

    def write(self, vals):
        """Log changes with audit trail."""
        for record in self:
            old_values = record._get_audit_values(vals.keys())
            result = super(AuditMixin, record).write(vals)
            new_values = record._get_audit_values(vals.keys())
            record._create_audit_log('write', old_values, new_values)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Log creation with audit trail."""
        records = super().create(vals_list)
        for record in records:
            record._create_audit_log('create', {}, record._get_audit_values())
        return records

    def unlink(self):
        """Log deletion with audit trail."""
        for record in self:
            record._create_audit_log('unlink', record._get_audit_values(), {})
        return super().unlink()

    def _get_audit_values(self, field_names=None):
        """Get values for audit logging."""
        self.ensure_one()
        if field_names is None:
            field_names = self._get_audit_fields()
        return {
            field: getattr(self, field)
            for field in field_names
            if hasattr(self, field)
        }

    def _get_audit_fields(self):
        """Override to specify fields to audit."""
        return ['name', 'state']

    def _create_audit_log(self, action, old_values, new_values):
        """Create audit log entry."""
        self.env['audit.log'].sudo().create({
            'model_name': self._name,
            'record_id': self.id,
            'action': action,
            'old_values': json.dumps(old_values, default=str),
            'new_values': json.dumps(new_values, default=str),
            'ip_address': self._get_client_ip(),
        })

    def _get_client_ip(self):
        """Get client IP from request."""
        try:
            from odoo.http import request
            if request:
                return request.httprequest.remote_addr
        except Exception:
            pass
        return None
```

---

## Performance Logging

### Query Profiling
```python
import time


class PerformanceLogger:
    """Context manager for performance logging."""

    def __init__(self, operation_name, logger=None):
        self.operation_name = operation_name
        self.logger = logger or _logger
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if duration > 1.0:  # Log slow operations
            self.logger.warning(
                "Slow operation: %s took %.2fs",
                self.operation_name, duration
            )
        else:
            self.logger.debug(
                "Operation %s completed in %.3fs",
                self.operation_name, duration
            )


# Usage
def compute_report(self):
    with PerformanceLogger("compute_report"):
        # Heavy computation
        pass
```

### SQL Query Logging
```python
def _log_query_count(self, operation_name):
    """Log number of SQL queries in operation."""
    cr = self.env.cr

    initial_count = cr.sql_log_count if hasattr(cr, 'sql_log_count') else 0

    yield

    final_count = cr.sql_log_count if hasattr(cr, 'sql_log_count') else 0
    query_count = final_count - initial_count

    if query_count > 100:
        _logger.warning(
            "High query count in %s: %d queries",
            operation_name, query_count
        )
```

### Memory Profiling (Development)
```python
import tracemalloc


def profile_memory(func):
    """Decorator for memory profiling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        try:
            result = func(*args, **kwargs)
            current, peak = tracemalloc.get_traced_memory()
            _logger.info(
                "%s memory: current=%.1fMB, peak=%.1fMB",
                func.__name__,
                current / 1024 / 1024,
                peak / 1024 / 1024
            )
            return result
        finally:
            tracemalloc.stop()
    return wrapper
```

---

## Error Tracking

### Error Log Model
```python
class ErrorLog(models.Model):
    _name = 'error.log'
    _description = 'Error Log'
    _order = 'create_date desc'

    name = fields.Char(string='Error', required=True)
    model_name = fields.Char(string='Model')
    record_id = fields.Integer(string='Record ID')
    method_name = fields.Char(string='Method')
    error_type = fields.Char(string='Error Type')
    error_message = fields.Text(string='Error Message')
    traceback = fields.Text(string='Traceback')
    user_id = fields.Many2one('res.users', string='User')
    resolved = fields.Boolean(string='Resolved', default=False)
    occurrence_count = fields.Integer(string='Occurrences', default=1)

    @api.model
    def log_error(self, error, model_name=None, record_id=None, method_name=None):
        """Log error with deduplication."""
        import traceback as tb

        error_type = type(error).__name__
        error_message = str(error)
        traceback_str = tb.format_exc()

        # Check for existing similar error
        existing = self.search([
            ('error_type', '=', error_type),
            ('error_message', '=', error_message),
            ('resolved', '=', False),
        ], limit=1)

        if existing:
            existing.occurrence_count += 1
            return existing

        return self.create({
            'name': f"{error_type}: {error_message[:100]}",
            'model_name': model_name,
            'record_id': record_id,
            'method_name': method_name,
            'error_type': error_type,
            'error_message': error_message,
            'traceback': traceback_str,
            'user_id': self.env.uid,
        })
```

### Error Handling Decorator
```python
def log_exceptions(model_name=None, method_name=None):
    """Decorator to log exceptions to error.log."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                _logger.exception("Error in %s: %s", func.__name__, e)
                self.env['error.log'].sudo().log_error(
                    error=e,
                    model_name=model_name or self._name,
                    record_id=self.id if hasattr(self, 'id') else None,
                    method_name=method_name or func.__name__,
                )
                raise
        return wrapper
    return decorator


# Usage
class MyModel(models.Model):
    _name = 'my.model'

    @log_exceptions()
    def risky_operation(self):
        # Code that might fail
        pass
```

---

## Debug Helpers

### Debug Mode Check
```python
from odoo.tools import config


def is_debug_mode():
    """Check if server is in debug mode."""
    return config.get('dev_mode') or config.get('debug')


class MyModel(models.Model):
    _name = 'my.model'

    def process(self):
        if is_debug_mode():
            _logger.setLevel(logging.DEBUG)
            _logger.debug("Debug mode enabled - verbose logging")

        # Processing logic
```

### Temporary Debug Output
```python
def debug_record(self):
    """Debug helper to print record details."""
    self.ensure_one()

    info = {
        'id': self.id,
        'name': self.name,
        'state': self.state,
        'create_date': str(self.create_date),
        'write_date': str(self.write_date),
    }

    _logger.info("=== DEBUG RECORD ===")
    for key, value in info.items():
        _logger.info("  %s: %s", key, value)
    _logger.info("====================")
```

### SQL Debug
```python
def debug_sql(self, query):
    """Execute and log SQL query for debugging."""
    _logger.info("Executing SQL: %s", query)
    self.env.cr.execute(query)
    result = self.env.cr.fetchall()
    _logger.info("Result: %s rows", len(result))
    return result
```

---

## Request Logging

### HTTP Request Logger
```python
from odoo import http
from odoo.http import request
import time


class RequestLogger(http.Controller):

    @http.route('/api/endpoint', type='json', auth='user')
    def my_endpoint(self, **kwargs):
        start_time = time.time()
        request_id = self._generate_request_id()

        _logger.info(
            "[%s] Request: user=%s, params=%s",
            request_id, request.env.user.login, kwargs
        )

        try:
            result = self._process_request(**kwargs)

            duration = time.time() - start_time
            _logger.info(
                "[%s] Response: success, duration=%.3fs",
                request_id, duration
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(
                "[%s] Response: error=%s, duration=%.3fs",
                request_id, str(e), duration
            )
            raise

    def _generate_request_id(self):
        import uuid
        return str(uuid.uuid4())[:8]
```

---

## Configuration

### Odoo Logging Configuration
```ini
# odoo.conf
[options]
log_level = info
log_handler = :INFO,odoo.addons.my_module:DEBUG
log_db = True
log_db_level = warning
logfile = /var/log/odoo/odoo.log
```

### Per-Module Log Level
```python
# At module init, set specific log level
import logging

# Set module-specific log level
logging.getLogger('odoo.addons.my_module').setLevel(logging.DEBUG)

# Or conditionally
if config.get('my_module_debug'):
    logging.getLogger('odoo.addons.my_module').setLevel(logging.DEBUG)
```

---

## Best Practices

1. **Use module logger** - `_logger = logging.getLogger(__name__)`
2. **Lazy formatting** - `_logger.info("x=%s", x)` not `f"x={x}"`
3. **Include context** - Log record IDs, user, operation name
4. **Use appropriate levels** - DEBUG for dev, INFO for operations
5. **Log exceptions** - Use `_logger.exception()` to include traceback
6. **Don't log sensitive data** - Mask passwords, tokens, PII
7. **Performance aware** - Check log level before expensive formatting
8. **Structured logging** - Consistent format for parsing
9. **Audit critical operations** - Financial, security, compliance
10. **Clean up debug logs** - Remove temporary logging before commit
