# Context and Environment Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  CONTEXT & ENVIRONMENT PATTERNS                                              ║
║  Using context, environment, and recordset manipulation                      ║
║  Use for passing data, changing behavior, and managing state                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Understanding the Environment

### Environment Components
```python
# self.env contains:
# - env.cr: Database cursor
# - env.uid: Current user ID
# - env.context: Context dictionary
# - env.user: Current user record
# - env.company: Current company
# - env.companies: Accessible companies
# - env.lang: Current language
# - env.ref(): Get record by XML ID
# - env['model.name']: Access model
```

### Accessing Environment
```python
class MyModel(models.Model):
    _name = 'my.model'

    def example_method(self):
        # Database cursor
        cr = self.env.cr

        # Current user
        user = self.env.user
        user_id = self.env.uid

        # Current company
        company = self.env.company
        companies = self.env.companies

        # Language
        lang = self.env.lang

        # Access other models
        partners = self.env['res.partner'].search([])

        # Get record by XML ID
        admin = self.env.ref('base.user_admin')

        # Context
        ctx = self.env.context
```

---

## Context Usage

### Reading Context Values
```python
def my_method(self):
    # Get context value with default
    active_id = self.env.context.get('active_id')
    active_ids = self.env.context.get('active_ids', [])
    active_model = self.env.context.get('active_model')

    # Boolean context flags
    skip_validation = self.env.context.get('skip_validation', False)

    # With default
    limit = self.env.context.get('limit', 100)
```

### Passing Context
```python
# Using with_context()
def action_with_context(self):
    # Add to existing context
    record = self.with_context(my_flag=True)
    record.do_something()

    # Replace entire context
    record = self.with_context({'lang': 'en_US'})

    # Multiple values
    record = self.with_context(
        active_test=False,
        lang='fr_FR',
        custom_value=42,
    )
```

### Context in Fields
```python
# Default from context
partner_id = fields.Many2one(
    'res.partner',
    default=lambda self: self.env.context.get('default_partner_id'),
)

# In XML views
"""
<field name="partner_id"
       context="{'default_company_id': company_id,
                 'show_archived': True}"/>
"""
```

### Context in Actions
```python
def action_open_wizard(self):
    return {
        'type': 'ir.actions.act_window',
        'name': 'My Wizard',
        'res_model': 'my.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_partner_id': self.partner_id.id,
            'default_amount': self.amount_total,
            'active_id': self.id,
            'active_ids': self.ids,
            'active_model': self._name,
        },
    }
```

---

## Common Context Keys

### Standard Keys
```python
# active_id/active_ids - Current record(s) from action
active_id = self.env.context.get('active_id')
active_ids = self.env.context.get('active_ids', [])

# active_model - Model name
active_model = self.env.context.get('active_model')

# default_* - Default values for fields
default_name = self.env.context.get('default_name')

# search_default_* - Default search filters
# In action: context="{'search_default_my_filter': 1}"

# active_test - Include archived records
# False = show archived, True/missing = hide archived
records = self.with_context(active_test=False).search([])

# lang - Language code
translated = self.with_context(lang='fr_FR').name

# tz - Timezone
# Automatically used for datetime display

# mail_create_nosubscribe - Don't auto-subscribe creator
# mail_create_nolog - Don't create "created" message
# mail_notrack - Don't track field changes
# tracking_disable - Disable all tracking
```

### Custom Context Patterns
```python
class MyModel(models.Model):
    _name = 'my.model'

    def create(self, vals):
        # Check for context flags
        if self.env.context.get('import_mode'):
            # Skip validations during import
            pass

        if self.env.context.get('from_cron'):
            # Different behavior for scheduled actions
            pass

        return super().create(vals)

    def _compute_field(self):
        # Use context to modify computation
        if self.env.context.get('simplified_calculation'):
            # Simplified logic
            pass
        else:
            # Full calculation
            pass
```

---

## Recordset Operations

### Creating Records
```python
# Single record
record = self.env['my.model'].create({
    'name': 'Test',
    'partner_id': partner.id,
})

# Multiple records (v17+)
records = self.env['my.model'].create([
    {'name': 'Record 1'},
    {'name': 'Record 2'},
])

# With context
record = self.env['my.model'].with_context(
    mail_create_nosubscribe=True
).create(vals)
```

### Searching Records
```python
# Basic search
records = self.env['my.model'].search([
    ('state', '=', 'draft'),
])

# With limit and order
records = self.env['my.model'].search(
    [('state', '=', 'draft')],
    limit=10,
    order='create_date desc',
)

# Search and read in one call
data = self.env['my.model'].search_read(
    [('state', '=', 'draft')],
    ['name', 'state', 'amount'],
    limit=10,
)

# Count
count = self.env['my.model'].search_count([('state', '=', 'draft')])

# Include archived
all_records = self.env['my.model'].with_context(
    active_test=False
).search([])
```

### Browsing Records
```python
# By ID
record = self.env['my.model'].browse(record_id)

# Multiple IDs
records = self.env['my.model'].browse([1, 2, 3])

# From context
records = self.env['my.model'].browse(
    self.env.context.get('active_ids', [])
)

# Check existence
if record.exists():
    # Record exists in database
    pass
```

### Recordset Manipulation
```python
# Combine recordsets (OR/union)
combined = records1 | records2

# Intersection
common = records1 & records2

# Difference
diff = records1 - records2

# Filter
draft_records = records.filtered(lambda r: r.state == 'draft')
draft_records = records.filtered('is_draft')  # Boolean field

# Map
names = records.mapped('name')
partner_ids = records.mapped('partner_id.id')
partners = records.mapped('partner_id')  # Returns recordset

# Sort
sorted_records = records.sorted(key=lambda r: r.date)
sorted_records = records.sorted('date', reverse=True)

# Iterate
for record in records:
    record.do_something()

# Check if recordset
if records:
    # Has at least one record
    pass

# Ensure single record
record.ensure_one()
```

---

## Changing User/Company Context

### Change User
```python
# Execute as specific user
admin = self.env.ref('base.user_admin')
record_as_admin = self.with_user(admin)
record_as_admin.action_confirm()

# Execute with sudo (superuser)
self.sudo().write({'internal_field': value})

# IMPORTANT: sudo() bypasses access rights
# Use sparingly and carefully
```

### Change Company
```python
# Execute in different company context
other_company = self.env['res.company'].browse(2)
record_in_company = self.with_company(other_company)
record_in_company.create_in_company()

# Get company from context
company = self.env.company  # Current company
companies = self.env.companies  # All accessible
```

### Combining Context Changes
```python
# Change multiple aspects
result = self.sudo().with_company(company).with_context(
    skip_validation=True,
    lang='en_US',
).create(vals)
```

---

## Environment in Cron Jobs

### Proper Cron Setup
```python
@api.model
def _cron_process(self):
    """Cron method with proper environment handling."""
    # Cron runs as OdooBot or specific user

    # Process records
    records = self.search([('state', '=', 'pending')])

    for record in records:
        try:
            # Use with_context for isolation
            record.with_context(from_cron=True)._process()

            # Commit after each to preserve progress
            self.env.cr.commit()

        except Exception as e:
            _logger.error("Failed to process %s: %s", record.id, e)
            self.env.cr.rollback()
```

### Multi-Company Cron
```python
@api.model
def _cron_multi_company(self):
    """Process for all companies."""
    companies = self.env['res.company'].search([])

    for company in companies:
        self.with_company(company)._process_company()
        self.env.cr.commit()

def _process_company(self):
    """Process for current company context."""
    records = self.search([
        ('company_id', '=', self.env.company.id),
    ])
    # Process records
```

---

## Cache and Invalidation

### Cache Behavior
```python
# Records are cached in environment
record = self.env['my.model'].browse(1)
name1 = record.name  # DB query
name2 = record.name  # From cache

# Invalidate specific field
self.env['my.model'].invalidate_model(['name'])

# Invalidate all cache
self.env.invalidate_all()

# Clear all caches
self.env.cache.clear()
```

### Refresh from Database
```python
# Invalidate and re-read
record.invalidate_recordset()
fresh_value = record.name

# Or browse again
record = self.env['my.model'].browse(record.id)
```

---

## Best Practices

### 1. Don't Modify Context Directly
```python
# Bad
self.env.context['key'] = value

# Good
self = self.with_context(key=value)
```

### 2. Use sudo() Sparingly
```python
# Only when necessary, with minimal scope
partner = self.sudo().partner_id  # Just read related
partner.sudo().write({'internal': True})  # Just this write
```

### 3. Preserve Context in Overrides
```python
def create(self, vals):
    # Context is automatically preserved
    return super().create(vals)

# If you need to modify:
def create(self, vals):
    self = self.with_context(creating=True)
    return super(MyModel, self).create(vals)
```

### 4. Use ensure_one() for Single Records
```python
def action_confirm(self):
    self.ensure_one()  # Raises if not exactly one record
    # Process single record
```

### 5. Handle Empty Recordsets
```python
def get_partner_name(self):
    partner = self.partner_id
    # Bad - error if no partner
    return partner.name

    # Good
    return partner.name if partner else ''
```

### 6. Check Record Existence
```python
record = self.env['my.model'].browse(potentially_deleted_id)
if record.exists():
    # Safe to use
    pass
```
