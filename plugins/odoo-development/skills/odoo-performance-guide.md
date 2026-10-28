# Odoo Performance Optimization Guide

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PERFORMANCE OPTIMIZATION GUIDE                                              ║
║  Best practices for high-performance Odoo modules across all versions        ║
║  Critical for modules marked as "performance_critical": true                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
> Includes rules from Odoo's official skill library (odoo/odoo skills/, branch 20.0), verified against the 14.0-19.0 source.

## Performance Principles

1. **Minimize database queries** - Batch operations, prefetch, avoid N+1
2. **Use stored computed fields** - When values don't change frequently
3. **Index search fields** - For frequently filtered/searched fields
4. **Avoid sudo() in loops** - Cache environment when needed
5. **Use SQL for bulk operations** - Only when ORM overhead is prohibitive: raw SQL bypasses access rights, record rules, `active` handling, translations and cache invalidation

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

# GOOD: Batch create (all versions 14-19; overrides use @api.model_create_multi)
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

Make **one** ORM call for the whole collection. An ORM call (`search`, `search_count`, aggregates, `create`) inside a `for` loop over records or vals is one query per iteration - O(n) round-trips instead of O(1). For per-record counts and sums use a grouped query (see "Optimizing Computed Fields").

Exceptions: a loop that only computes in memory on already-read fields is fine; when a per-record call is truly unavoidable (e.g. an external API per record), bound the batch size.

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
# Standard B-tree index
state = fields.Selection([...], index=True)
company_id = fields.Many2one('res.company', index=True)
date = fields.Date(index=True)

# Trigram index for ILIKE searches (16.0+)
name = fields.Char(index='trigram')  # For pattern searches

# Index types (16.0+)
code = fields.Char(index='btree_not_null')  # Exclude NULL values
```

| Index form | 14.0-15.0 | 16.0-18.0 | 19.0 |
|---|---|---|---|
| `index=True` (btree) | yes (bool only) | yes (`True`/`'btree'`) | yes |
| `index='btree_not_null'`, `index='trigram'` | - | yes | yes |
| multi-column / unique index | `init()` + `odoo.tools.create_index` / `create_unique_index` | same | `_my_idx = models.Index('(col1, col2)')` / `models.UniqueIndex(...)` |

Index selectively: every index slows down writes. Index fields used in search domains, record rules and `ORDER BY`, not every field.

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
# BAD (all versions): one aggregate query per record in compute
@api.depends('partner_id')
def _compute_partner_orders(self):
    for record in self:
        record.order_count = self.env['sale.order'].search_count([
            ('partner_id', '=', record.partner_id.id)
        ])
```

The grouped replacement depends on the version:

```python
# 14.0-16.0 (also works in 17.0-18.0; deprecated in 19.0): read_group -> list of dicts
groups = Book.read_group(
    [('author_id', 'in', authors.ids)], ['author_id'], ['author_id'],
)
# lazy=True (default): count key is '<groupby>_count'; many2one value is (id, display_name)
counts = {g['author_id'][0]: g['author_id_count'] for g in groups if g['author_id']}
for author in authors:
    author.book_count = counts.get(author.id, 0)

# Sum per group, 14.0-16.0
groups = Book.read_group(
    [('author_id', 'in', authors.ids)], ['price:sum'], ['author_id'], lazy=False,
)
totals = {g['author_id'][0]: g['price'] for g in groups if g['author_id']}  # count in g['__count']
```

```python
# 17.0+: _read_group(domain, groupby, aggregates) -> list of tuples, groupby values are records
counts = {
    author.id: count
    for author, count in Book._read_group(
        [('author_id', 'in', authors.ids)], ['author_id'], ['__count'],
    )
}
for author in authors:
    author.book_count = counts.get(author.id, 0)

# Sum per group, 17.0+
totals = dict(Book._read_group([('author_id', 'in', authors.ids)], ['author_id'], ['price:sum']))
# keys are author records: totals.get(author, 0.0)
```

In 16.0 `_read_group` exists but has the **old** `read_group` signature (fields, groupby, lazy) and returns dicts - do not use the 17.0 tuple form there. In 19.0 `read_group` is deprecated; use `_read_group` (or `formatted_read_group` when dicts are needed).

## SQL Optimization

### When to Use Raw SQL

Use raw SQL for:
- Bulk updates/deletes
- Complex aggregations
- Performance-critical read operations
- Operations on millions of records

### Version-Specific SQL Patterns

```python
# All versions 14-19: string SQL with parameters (never %, .format, f-strings or +)
self.env.cr.execute("""
    UPDATE sale_order
    SET state = %s
    WHERE id IN %s
""", ('done', tuple(order_ids)))

# 17.0+: odoo.tools.SQL builder (composable; SQL.identifier() for dynamic names).
# Not available in 14.0-16.0 - in 16.0 `odoo.tools.SQL` is psycopg2's sql.SQL, a different API.
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
# Before raw SQL: flush pending ORM writes (flush API differs per version - see model-patterns-<version>)
# After raw SQL updates, invalidate ORM cache

# 16.0+
self.browse(updated_ids).invalidate_recordset()   # specific records
self.invalidate_model()                            # whole model
self.env.invalidate_all()                          # everything

# 14.0-15.0
self.browse(updated_ids).invalidate_cache()
self.invalidate_cache()
```

## Prefetching

### Understanding Prefetch

```python
# Odoo automatically prefetches in batches of up to 1000 records (PREFETCH_MAX, all versions)
# When you access a field on one record, it fetches for all in recordset.
# Records browsed together share one prefetch set (see "Avoid Repeated Environment Access").

orders = self.env['sale.order'].search([], limit=500)

# First access triggers prefetch for all 500 orders
for order in orders:
    print(order.name)  # First iteration: 1 query for all names
    print(order.partner_id.name)  # First iteration: 1 query for all partners

# Manual prefetch for related records
orders.mapped('order_line.product_id')  # Prefetch all products
```

### Prefetch Groups

```python
# Efficient related record access
def process_orders(self, orders):
    # Prefetch all related data upfront
    orders.mapped('partner_id')
    orders.mapped('order_line')
    orders.mapped('order_line.product_id')

    # Now process without additional queries
    for order in orders:
        for line in order.order_line:
            print(line.product_id.name)  # No additional queries
```

## ORM Performance Tips

### Use filtered() Efficiently

Official guideline (all versions): put conditions in the **search domain**, not in `filtered()` on the result - `filtered` runs in Python on records already fetched. Reserve `filtered()` for predicates a domain cannot express or for small recordsets already in memory.

```python
# BAD: fetch everything, filter in Python
orders = self.env['sale.order'].search([('partner_id', '=', partner.id)])
confirmed_orders = orders.filtered(lambda o: o.state == 'sale')

# GOOD: let the database filter
confirmed_orders = self.env['sale.order'].search([
    ('partner_id', '=', partner.id),
    ('state', '=', 'sale'),
])

# OK: recordset already loaded, predicate in memory
confirmed_orders = orders.filtered(lambda o: o.state == 'sale')
```

Reduce complexity: pre-map results into a dict (`{r.id: r for r in records}`) instead of nested loops; use `set` (or recordset arithmetic like `records - invalid`) for membership tests.

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

# GOOD: browse(ids) once, never browse(id) per loop step - one shared prefetch set
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
                with self.env.cr.savepoint():  # isolate the failing record, see below
                    record._process_single()
            except Exception as e:
                _logger.error("Failed to process %s: %s", record.id, e)

        # Commit batch and clear cache (cron context only; never commit in business code
        # or tests). Cache clearing: 16.0+ self.env.invalidate_all(); 14.0-15.0 self.invalidate_cache()
        self.env.cr.commit()
        self.env.invalidate_all()

        offset += batch_size
```

### Savepoints for per-record error isolation

A failed SQL statement aborts the whole transaction. To survive one bad record in a batch, wrap it in a savepoint (`with self.env.cr.savepoint():`, as in the cron loop above) instead of catching the exception bare (all versions 14-19).

Each savepoint costs a round-trip; do not open one per record in very large loops when errors are not expected - process in chunks instead. (Opening very many savepoints in one transaction degrades PostgreSQL performance.)

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

        # Clear cache periodically (16.0+; 14.0-15.0: self.invalidate_cache())
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

### Batch x2many Line Creation (15.0+ Command; 14.0 tuples)

```python
# One write creating all lines (Command is an IntEnum: same cost as tuples)
from odoo.fields import Command

self.write({
    'line_ids': [Command.create(vals) for vals in vals_list]
})
# 14.0: [(0, 0, vals) for vals in vals_list]
```

### Multi-Company (all versions 14-19)

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # Opt-in consistency check on create/write

    company_id = fields.Many2one('res.company', index=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
```

Company filtering of searches comes from the multi-company record rule (`company_ids`), so index `company_id`.

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
# 14.0 only: decorator
from odoo.tools.profiler import profile

@profile
def slow_method(self):
    pass

# 15.0+: no `profile` decorator - use the Profiler context manager
from odoo.tools.profiler import Profiler

with Profiler():
    records.slow_method()
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
- [ ] Use grouped queries for aggregations (`read_group` 14.0-16.0, `_read_group` 17.0+)
- [ ] No ORM call (`search`, `search_count`, aggregates, `create`) inside a loop
- [ ] Implement batch processing for large datasets
- [ ] Clear cache in long-running operations
- [ ] Use generators for memory efficiency

### For Cron Jobs
- [ ] Process in batches
- [ ] Commit periodically
- [ ] Handle errors gracefully (don't stop entire job)
- [ ] Clear cache between batches
- [ ] Log performance metrics
