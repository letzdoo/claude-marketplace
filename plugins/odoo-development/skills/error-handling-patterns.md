# Error Handling Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ERROR HANDLING PATTERNS                                                     ║
║  Exceptions, validation, and error recovery                                  ║
║  Use for robust error handling, user feedback, and data integrity            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Odoo Exception Types

### Standard Exceptions
```python
from odoo.exceptions import (
    UserError,        # User-facing errors (shown in dialog)
    ValidationError,  # Constraint violations
    AccessError,      # Permission denied
    MissingError,     # Record doesn't exist
    AccessDenied,     # Login/authentication failure
    RedirectWarning,  # Error with action button
)
```

### When to Use Each
| Exception | Use Case |
|-----------|----------|
| `UserError` | Business logic errors, invalid operations |
| `ValidationError` | Data validation failures in constraints |
| `AccessError` | Permission/security violations |
| `MissingError` | Record not found (browse deleted ID) |
| `RedirectWarning` | Error with corrective action link |

---

## Raising Exceptions

### UserError (Most Common)
```python
from odoo.exceptions import UserError


class MyModel(models.Model):
    _name = 'my.model'

    def action_confirm(self):
        """Confirm record with validation."""
        self.ensure_one()

        if not self.line_ids:
            raise UserError("Cannot confirm without lines.")

        if self.amount_total <= 0:
            raise UserError(
                f"Amount must be positive. Current: {self.amount_total}"
            )

        if self.state != 'draft':
            raise UserError(
                f"Only draft records can be confirmed. "
                f"Current state: {self.state}"
            )

        self.write({'state': 'confirmed'})
```

### ValidationError (Constraints)
```python
from odoo.exceptions import ValidationError


class MyModel(models.Model):
    _name = 'my.model'

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end:
                if record.date_start > record.date_end:
                    raise ValidationError(
                        "Start date must be before end date."
                    )

    @api.constrains('email')
    def _check_email(self):
        import re
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        for record in self:
            if record.email and not re.match(email_pattern, record.email):
                raise ValidationError(
                    f"Invalid email format: {record.email}"
                )

    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError("Quantity cannot be negative.")
```

### RedirectWarning (With Action)
```python
from odoo.exceptions import RedirectWarning


class MyModel(models.Model):
    _name = 'my.model'

    def action_process(self):
        if not self.env.company.x_config_complete:
            action = self.env.ref('my_module.action_config_wizard')
            raise RedirectWarning(
                "Configuration is incomplete. Please complete setup first.",
                action.id,
                "Go to Configuration",
            )
```

### AccessError (Security)
```python
from odoo.exceptions import AccessError


class MyModel(models.Model):
    _name = 'my.model'

    def action_approve(self):
        if not self.env.user.has_group('my_module.group_approver'):
            raise AccessError(
                "You do not have permission to approve records."
            )
        self.write({'state': 'approved'})
```

---

## Try-Except Patterns

### Basic Error Handling
```python
def process_record(self):
    try:
        self._do_processing()
    except UserError:
        # Re-raise user errors (show to user)
        raise
    except Exception as e:
        _logger.error("Processing failed for %s: %s", self.id, e)
        raise UserError(f"Processing failed: {str(e)}")
```

### Handling Specific Exceptions
```python
def sync_external(self):
    import requests

    try:
        response = requests.get(self.api_url, timeout=30)
        response.raise_for_status()
        return response.json()

    except requests.Timeout:
        raise UserError(
            "External service timed out. Please try again later."
        )
    except requests.ConnectionError:
        raise UserError(
            "Cannot connect to external service. Check your connection."
        )
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise UserError("Authentication failed. Check API credentials.")
        elif e.response.status_code == 404:
            raise UserError("Resource not found on external service.")
        else:
            raise UserError(f"External service error: {e.response.status_code}")
    except Exception as e:
        _logger.exception("Unexpected error in sync: %s", e)
        raise UserError(f"Sync failed: {str(e)}")
```

### Transaction Safety
```python
def process_batch(self):
    """Process batch with transaction safety."""
    for record in self:
        try:
            # Use savepoint for each record
            with self.env.cr.savepoint():
                record._process_single()

        except Exception as e:
            # Savepoint rolled back, continue with next
            _logger.error("Failed to process %s: %s", record.id, e)
            record.message_post(body=f"Processing failed: {e}")
            continue
```

### Graceful Degradation
```python
def get_external_data(self):
    """Get data with fallback."""
    try:
        # Try primary source
        return self._fetch_from_api()
    except Exception as e:
        _logger.warning("API fetch failed: %s, using cache", e)
        try:
            # Fallback to cache
            return self._get_from_cache()
        except Exception:
            _logger.error("Cache also failed")
            return None
```

---

## Validation Patterns

### Pre-Action Validation
```python
class MyModel(models.Model):
    _name = 'my.model'

    def action_confirm(self):
        """Confirm with pre-validation."""
        self._validate_confirm()
        self.write({'state': 'confirmed'})

    def _validate_confirm(self):
        """Validate before confirmation."""
        errors = []

        for record in self:
            if not record.partner_id:
                errors.append(f"[{record.name}] Partner is required.")
            if not record.line_ids:
                errors.append(f"[{record.name}] At least one line required.")
            if record.amount_total <= 0:
                errors.append(f"[{record.name}] Amount must be positive.")

        if errors:
            raise UserError("\n".join(errors))
```

### Field Validation Decorator
```python
def validate_required(field_name, message=None):
    """Decorator to validate required field."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for record in self:
                if not getattr(record, field_name):
                    raise UserError(
                        message or f"{field_name} is required."
                    )
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


class MyModel(models.Model):
    _name = 'my.model'

    @validate_required('partner_id', 'Please select a partner first.')
    def action_send(self):
        # Validation passed
        self._send_to_partner()
```

### SQL Constraint Handling
```python
class MyModel(models.Model):
    _name = 'my.model'

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code, company_id)',
         'Code must be unique per company.'),
        ('amount_positive', 'CHECK(amount >= 0)',
         'Amount must be positive.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        try:
            return super().create(vals_list)
        except IntegrityError as e:
            if 'code_unique' in str(e):
                raise UserError("A record with this code already exists.")
            raise
```

---

## Error Recovery

### Retry Pattern
```python
import time


def retry_on_error(max_retries=3, delay=1, exceptions=(Exception,)):
    """Decorator for retry on error."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        _logger.warning(
                            "Attempt %d failed: %s. Retrying...",
                            attempt + 1, e
                        )
                        time.sleep(delay * (attempt + 1))
            raise last_error
        return wrapper
    return decorator


class MyModel(models.Model):
    _name = 'my.model'

    @retry_on_error(max_retries=3, delay=2)
    def call_external_api(self):
        # May fail temporarily
        pass
```

### Rollback and Notify
```python
def process_with_rollback(self):
    """Process with proper rollback handling."""
    try:
        # Start work
        for record in self:
            record._process()

        # Commit if all successful
        self.env.cr.commit()

    except Exception as e:
        # Rollback transaction
        self.env.cr.rollback()

        # Notify about failure
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'simple_notification',
            {
                'title': 'Processing Failed',
                'message': str(e),
                'type': 'danger',
            }
        )
        raise
```

---

## User Feedback

### Progress Messages
```python
def action_process_batch(self):
    """Process with user feedback."""
    total = len(self)
    processed = 0
    errors = []

    for record in self:
        try:
            record._process()
            processed += 1
        except Exception as e:
            errors.append(f"{record.name}: {str(e)}")

    # Return notification
    if errors:
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Processing Complete',
                'message': f'Processed {processed}/{total}. '
                          f'{len(errors)} errors occurred.',
                'type': 'warning',
                'sticky': True,
            }
        }
    else:
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Successfully processed {total} records.',
                'type': 'success',
            }
        }
```

### Error Details in Chatter
```python
def process_with_logging(self):
    """Process with error logging to chatter."""
    try:
        result = self._do_work()
        self.message_post(
            body=f"Processing completed successfully: {result}",
            message_type='notification',
        )
    except Exception as e:
        self.message_post(
            body=f"<b>Processing Failed</b><br/>{str(e)}",
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        raise UserError(f"Processing failed: {str(e)}")
```

---

## Best Practices

1. **Use appropriate exception types** - UserError for business logic, ValidationError for constraints
2. **Provide clear messages** - Include context and what to do
3. **Log before raising** - Log technical details, show user-friendly message
4. **Don't catch too broadly** - Be specific about what you catch
5. **Always re-raise UserError** - Let it show to user
6. **Use savepoints for batches** - Isolate failures
7. **Validate early** - Check before doing work
8. **Return feedback** - Use notifications for batch operations
9. **Document expected errors** - In docstrings
10. **Test error paths** - Write tests for error scenarios

---

## Anti-Patterns

```python
# Bad - Too broad
try:
    do_something()
except:
    pass

# Bad - Silent failure
try:
    do_something()
except Exception:
    return False

# Bad - Losing error context
try:
    do_something()
except Exception:
    raise UserError("Something went wrong")  # Lost original error

# Good - Preserve and log
try:
    do_something()
except Exception as e:
    _logger.exception("Failed in do_something")
    raise UserError(f"Operation failed: {e}")
```
