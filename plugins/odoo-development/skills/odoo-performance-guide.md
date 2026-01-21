# Odoo Performance Optimization Guide

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PERFORMANCE OPTIMIZATION GUIDE                                              ║
║  Best practices for high-performance Odoo modules across all versions        ║
║  Critical for modules marked as "performance_critical": true                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Performance Principles

1. **Minimize database queries** - Batch operations, prefetch, avoid N+1
2. **Use stored computed fields** - When values don't change frequently
3. **Index search fields** - For frequently filtered/searched fields
4. **Avoid sudo() in loops** - Cache environment when needed
5. **Use SQL for bulk operations** - When ORM overhead is prohibitive

## Database Query Optimization

### N+1 Query Problem

```python
# BAD: N+1 queries (1 for orders, N for partners)
for order in orders:
    print(order.partner_id.name)  # Query per iteration

# GOOD: Prefetch in single query
orders = self.env['sale.order'].search([])
orders.mapped('partner_id')  # Prefetch all partners
for order in orders:
    print(order.partner_id.name)  # No additional queries

# BETTER: Use search_read when you only need specific fields
data = self.env['sale.order'].search_read(
    [('state', '=', 'sale')],
    ['name', 'partner_id', 'amount_total'],
    limit=100,
)
```

### Batch Operations

```python
# BAD: Individual creates
for data in data_list:
    self.env['my.model'].create(data)

# GOOD: Batch create (v15+)
self.env['my.model'].create(data_list)

# BAD: Individual writes
for record in records:
    record.write({'state': 'done'})

# GOOD: Batch write
records.write({'state': 'done'})

# BAD: Individual unlinks
for record in records:
    record.unlink()

# GOOD: Batch unlink
records.unlink()
```

### Efficient Searching

```python
# BAD: Search then count
count = len(self.env['my.model'].search([('state', '=', 'draft')]))

# GOOD: Use search_count
count = self.env['my.model'].search_count([('state', '=', 'draft')])

# BAD: Search all then filter in Python
records = self.env['my.model'].search([])
draft_records = [r for r in records if r.state == 'draft']

# GOOD: Filter in domain
draft_records = self.env['my.model'].search([('state', '=', 'draft')])

# BAD: Multiple searches for related data
partners = self.env['res.partner'].search([('customer_rank', '>', 0)])
orders = self.env['sale.order'].search([('partner_id', 'in', partners.ids)])

# GOOD: Single search with join
orders = self.env['sale.order'].search([
    ('partner_id.customer_rank', '>', 0)
])
```

## Field Indexing

### When to Index

```python
# Index fields that are:
# 1. Frequently used in search domains
# 2. Used in record rules
# 3. Used in ORDER BY clauses

# Standard B-tree index
state = fields.Selection([...], index=True)
company_id = fields.Many2one('res.company', index=True)
date = fields.Date(index=True)

# Trigram index for ILIKE searches (v16+)
name = fields.Char(index='trigram')  # For pattern searches

# Index types (v16+)
code = fields.Char(index='btree_not_null')  # Exclude NULL values
```

### Index Guidelines

| Field Type | When to Index |
|------------|---------------|
| Selection | If used in filters/domains |
| Many2one | If used in search or rules |
| Date/Datetime | If used in date range queries |
| Char | If used with `=` operator |
| Char (pattern) | Use `index='trigram'` for ILIKE |

## Computed Fields

### Stored vs Non-Stored

```python
# STORED: Computed once, updated on dependency change
# Use when: Value rarely changes, frequently read
total = fields.Float(
    compute='_compute_total',
    store=True,  # Stored in database
)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))

# NON-STORED: Computed on every read
# Use when: Value changes frequently, rarely displayed
days_until_deadline = fields.Integer(
    compute='_compute_days_until_deadline',
    store=False,  # Computed on read
)

def _compute_days_until_deadline(self):
    today = fields.Date.today()
    for record in self:
        if record.deadline:
            record.days_until_deadline = (record.deadline - today).days
        else:
            record.days_until_deadline = 0
```

### Optimizing Computed Fields

```python
# BAD: Individual queries in compute
@api.depends('partner_id')
def _compute_partner_orders(self):
    for record in self:
        record.order_count = self.env['sale.order'].search_count([
            ('partner_id', '=', record.partner_id.id)
        ])

# GOOD: Batch query with read_group
@api.depends('partner_id')
def _compute_partner_orders(self):
    if not self:
        return

    partner_ids = self.mapped('partner_id').ids
    order_data = self.env['sale.order'].read_group(
        [('partner_id', 'in', partner_ids)],
        ['partner_id'],
        ['partner_id'],
    )
    counts = {d['partner_id'][0]: d['partner_id_count'] for d in order_data}

    for record in self:
        record.order_count = counts.get(record.partner_id.id, 0)
```

## SQL Optimization

### When to Use Raw SQL

Use raw SQL for:
- Bulk updates/deletes
- Complex aggregations
- Performance-critical read operations
- Operations on millions of records

### Version-Specific SQL Patterns

```python
# v14-v17: String SQL (works but deprecated in v18+)
self.env.cr.execute("""
    UPDATE sale_order
    SET state = %s
    WHERE id IN %s
""", ('done', tuple(order_ids)))

# v18+: SQL() builder (REQUIRED in v19)
from odoo.tools import SQL

self.env.cr.execute(SQL(
    """
    UPDATE sale_order
    SET state = %s
    WHERE id IN %s
    """,
    'done', tuple(order_ids)
))

# Complex query with SQL builder
self.env.cr.execute(SQL(
    """
    SELECT partner_id, COUNT(*) as order_count, SUM(amount_total) as total
    FROM sale_order
    WHERE state = %s AND company_id = %s
    GROUP BY partner_id
    HAVING SUM(amount_total) > %s
    ORDER BY total DESC
    LIMIT %s
    """,
    'sale', self.env.company.id, 10000, 100
))
results = self.env.cr.dictfetchall()
```

### Cache Invalidation After SQL

```python
# After raw SQL updates, invalidate ORM cache
self.env.cr.execute(SQL(...))

# Invalidate specific records
self.browse(updated_ids).invalidate_recordset()

# Or invalidate entire model cache
self.invalidate_model()
```

## Prefetching

### Understanding Prefetch

```python
# Odoo automatically prefetches in batches of 1000
# When you access a field on one record, it fetches for all in recordset

orders = self.env['sale.order'].search([], limit=500)

# First access triggers prefetch for all 500 orders
for order in orders:
    print(order.name)  # First iteration: 1 query for all names
    print(order.partner_id.name)  # First iteration: 1 query for all partners

# Manual prefetch for related records
orders.mapped('order_line_ids.product_id')  # Prefetch all products
```

### Prefetch Groups

```python
# Efficient related record access
def process_orders(self, orders):
    # Prefetch all related data upfront
    orders.mapped('partner_id')
    orders.mapped('order_line_ids')
    orders.mapped('order_line_ids.product_id')

    # Now process without additional queries
    for order in orders:
        for line in order.order_line_ids:
            print(line.product_id.name)  # No additional queries
```

## ORM Performance Tips

### Use filtered() Efficiently

```python
# filtered() is in-memory, not a database query
# Good for small recordsets already loaded
confirmed_orders = orders.filtered(lambda o: o.state == 'sale')

# For large datasets, use search() instead
confirmed_orders = self.env['sale.order'].search([
    ('id', 'in', orders.ids),
    ('state', '=', 'sale'),
])
```

### Use mapped() for Collections

```python
# Get all partner IDs efficiently
partner_ids = orders.mapped('partner_id.id')

# Get unique values
partner_ids = orders.mapped('partner_id').ids

# Sum values
total = sum(orders.mapped('amount_total'))

# Or use Python's sum with generator
total = sum(o.amount_total for o in orders)
```

### Avoid Repeated Environment Access

```python
# BAD: Repeated env access in loop
for partner_id in partner_ids:
    partner = self.env['res.partner'].browse(partner_id)
    print(partner.name)

# GOOD: Single browse for all
partners = self.env['res.partner'].browse(partner_ids)
for partner in partners:
    print(partner.name)
```

## Cron Job Optimization

```python
@api.model
def _cron_process_large_dataset(self):
    """Process records in batches to avoid memory issues"""
    batch_size = 1000
    offset = 0

    while True:
        records = self.search(
            [('state', '=', 'pending')],
            limit=batch_size,
            offset=offset,
        )

        if not records:
            break

        for record in records:
            try:
                record._process_single()
            except Exception as e:
                _logger.error("Failed to process %s: %s", record.id, e)

        # Commit batch and clear cache
        self.env.cr.commit()
        self.env.invalidate_all()

        offset += batch_size
```

## Memory Optimization

### Clear Cache in Long Operations

```python
def process_many_records(self):
    """Process large dataset with memory management"""
    count = 0
    batch_size = 500

    for record in self:
        record._do_processing()
        count += 1

        # Clear cache periodically
        if count % batch_size == 0:
            self.env.invalidate_all()
            self.env.cr.commit()  # Optional: commit in batches
```

### Use Generators for Large Data

```python
# BAD: Load all into memory
all_data = self.env['large.model'].search_read([], ['name', 'value'])
for item in all_data:
    process(item)

# GOOD: Process in batches
def _iter_records(self, domain, batch_size=1000):
    offset = 0
    while True:
        records = self.search(domain, limit=batch_size, offset=offset)
        if not records:
            break
        yield from records
        offset += batch_size

for record in self._iter_records([('state', '=', 'pending')]):
    process(record)
```

## Version-Specific Optimizations

### v16+ Command Class Performance

```python
# Command class is slightly more efficient than tuples
from odoo.fields import Command

# Efficient batch line creation
self.write({
    'line_ids': [Command.create(vals) for vals in vals_list]
})
```

### v18+ Multi-Company Optimization

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # Automatic company checking

    company_id = fields.Many2one('res.company', index=True)
    partner_id = fields.Many2one('res.partner', check_company=True)

    # Company-aware search (v18 pattern)
    def _search_company_records(self):
        # Uses allowed_company_ids automatically
        return self.search([('state', '=', 'active')])
```

## Performance Monitoring

### Using Logging

```python
import logging
import time

_logger = logging.getLogger(__name__)

def _performance_critical_method(self):
    start_time = time.time()

    # Your code here

    elapsed = time.time() - start_time
    _logger.info("Method completed in %.2f seconds", elapsed)

    if elapsed > 5.0:
        _logger.warning("Slow operation detected: %.2f seconds", elapsed)
```

### Query Count Debugging

```python
# In development, enable query logging
# In odoo.conf: log_level = debug_sql

# Or use the profiler
from odoo.tools.profiler import profile

@profile
def slow_method(self):
    # This will log timing and query count
    pass
```

## Performance Checklist

### For New Modules
- [ ] Index all fields used in search domains
- [ ] Use stored computed fields for frequently read values
- [ ] Implement batch operations (`@api.model_create_multi`)
- [ ] Avoid N+1 patterns in computed fields
- [ ] Use `search_count()` instead of `len(search())`
- [ ] Prefetch related records before loops

### For Performance-Critical Code
- [ ] Profile before optimizing
- [ ] Consider raw SQL for bulk operations
- [ ] Use read_group for aggregations
- [ ] Implement batch processing for large datasets
- [ ] Clear cache in long-running operations
- [ ] Use generators for memory efficiency

### For Cron Jobs
- [ ] Process in batches
- [ ] Commit periodically
- [ ] Handle errors gracefully (don't stop entire job)
- [ ] Clear cache between batches
- [ ] Log performance metrics
