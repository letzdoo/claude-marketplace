---
name: xmlrpc-query-patterns
keywords: [xmlrpc, query, api, external, read, search, investigate]
description: Patterns for querying Odoo via XML-RPC API
---

# Odoo XML-RPC Query Patterns

Reference for performing read-only queries against Odoo instances.

## Connection Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Client (Claude)                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  odoo_xmlrpc.py                                                 │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ XML-RPC Connection                                       │   │
│  │   URL/xmlrpc/2/common  → Authentication                 │   │
│  │   URL/xmlrpc/2/object  → Model Operations               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Odoo Server                                                    │
├─────────────────────────────────────────────────────────────────┤
│  /xmlrpc/2/common                                               │
│    - version()          → Server version info                   │
│    - authenticate()     → Get user ID                           │
│                                                                 │
│  /xmlrpc/2/object                                               │
│    - execute_kw()       → Run model methods                     │
│      └─ search          → Find record IDs                       │
│      └─ read            → Read record data                      │
│      └─ search_read     → Search + Read combined                │
│      └─ search_count    → Count matching records                │
│      └─ fields_get      → Get model field definitions           │
└─────────────────────────────────────────────────────────────────┘
```

## Domain Filter Reference

### Basic Operators
| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `[('state', '=', 'draft')]` |
| `!=` | Not equals | `[('state', '!=', 'done')]` |
| `>` | Greater than | `[('amount', '>', 1000)]` |
| `>=` | Greater or equal | `[('date', '>=', '2024-01-01')]` |
| `<` | Less than | `[('qty', '<', 10)]` |
| `<=` | Less or equal | `[('priority', '<=', 2)]` |
| `in` | In list | `[('state', 'in', ['draft', 'sent'])]` |
| `not in` | Not in list | `[('state', 'not in', ['done', 'cancel'])]` |
| `like` | SQL LIKE (case-sensitive) | `[('name', 'like', 'SO%')]` |
| `ilike` | LIKE (case-insensitive) | `[('email', 'ilike', '%@gmail.com')]` |
| `=like` | Pattern match | `[('name', '=like', 'SO___')]` |
| `=ilike` | Pattern (case-insensitive) | `[('code', '=ilike', 'prod_%')]` |
| `child_of` | Hierarchical child | `[('category_id', 'child_of', 5)]` |
| `parent_of` | Hierarchical parent | `[('category_id', 'parent_of', 10)]` |

### Logical Operators
```python
# AND (implicit - default)
[('state', '=', 'sale'), ('amount', '>', 1000)]

# AND (explicit)
['&', ('state', '=', 'sale'), ('amount', '>', 1000)]

# OR
['|', ('state', '=', 'draft'), ('state', '=', 'sent')]

# NOT
['!', ('active', '=', True)]

# Complex: (A AND B) OR C
['|', '&', ('state', '=', 'sale'), ('amount', '>', 1000), ('priority', '=', 'high')]

# Complex: A AND (B OR C)
['&', ('state', '=', 'sale'), '|', ('amount', '>', 1000), ('priority', '=', 'high')]
```

### Date/Time Filters
```python
# Exact date
[('date_order', '=', '2024-01-15')]

# Date range
[('date_order', '>=', '2024-01-01'), ('date_order', '<=', '2024-12-31')]

# Today (use Python to compute)
# today = datetime.date.today().isoformat()
[('date_order', '=', '2024-01-20')]

# Last 30 days
# thirty_days_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
[('create_date', '>=', '2023-12-21')]
```

### Relational Field Filters
```python
# Filter by related record ID
[('partner_id', '=', 42)]

# Filter by related field value (dot notation)
[('partner_id.country_id.code', '=', 'US')]

# Filter by Many2many (contains)
[('tag_ids', 'in', [1, 2, 3])]

# Empty relation
[('partner_id', '=', False)]

# Non-empty relation
[('partner_id', '!=', False)]
```

## Common Query Patterns

### Sales Investigation
```bash
# Recent confirmed sales
--action search_read --model "sale.order" \
  --domain "[('state', '=', 'sale'), ('date_order', '>=', '2024-01-01')]" \
  --fields "name,partner_id,date_order,amount_total,user_id" \
  --limit 20 --order "date_order desc"

# Large orders
--action search_read --model "sale.order" \
  --domain "[('amount_total', '>', 10000)]" \
  --fields "name,partner_id,amount_total,state"

# Orders by specific salesperson
--action search_read --model "sale.order" \
  --domain "[('user_id.name', 'ilike', 'john')]" \
  --fields "name,partner_id,amount_total,state"
```

### Invoice Investigation
```bash
# Overdue invoices
--action search_read --model "account.move" \
  --domain "[('move_type', '=', 'out_invoice'), ('payment_state', '!=', 'paid'), ('invoice_date_due', '<', '2024-01-20')]" \
  --fields "name,partner_id,amount_total,invoice_date_due,payment_state"

# Invoices for specific customer
--action search_read --model "account.move" \
  --domain "[('partner_id', '=', 42), ('move_type', '=', 'out_invoice')]" \
  --fields "name,amount_total,state,payment_state,invoice_date"
```

### Inventory Investigation
```bash
# Low stock products
--action search_read --model "stock.quant" \
  --domain "[('quantity', '<', 10), ('location_id.usage', '=', 'internal')]" \
  --fields "product_id,location_id,quantity,reserved_quantity"

# Product availability
--action search_read --model "product.product" \
  --domain "[('type', '=', 'product'), ('qty_available', '>', 0)]" \
  --fields "name,default_code,qty_available,virtual_available"
```

### Customer/Partner Investigation
```bash
# Customers with credit
--action search_read --model "res.partner" \
  --domain "[('customer_rank', '>', 0), ('credit', '>', 0)]" \
  --fields "name,email,credit,credit_limit"

# Partners by country
--action search_read --model "res.partner" \
  --domain "[('country_id.code', '=', 'FR')]" \
  --fields "name,city,email,phone"
```

### User/Access Investigation
```bash
# Users in specific group
--action search_read --model "res.users" \
  --domain "[('groups_id.name', 'ilike', 'sales')]" \
  --fields "name,login,groups_id"

# Inactive users
--action search_read --model "res.users" \
  --domain "[('active', '=', False)]" \
  --fields "name,login,write_date"
```

### Custom Model Investigation
```bash
# Step 1: Discover the model structure
--action fields_get --model "custom.model.name"

# Step 2: Check for state/status field
--action search_read --model "custom.model.name" \
  --domain "[]" \
  --fields "name,state" \
  --limit 5

# Step 3: Query based on findings
--action search_read --model "custom.model.name" \
  --domain "[('state', '=', 'active')]" \
  --fields "name,field1,field2,create_date"
```

## Troubleshooting

### Authentication Errors
- Verify URL includes protocol (https://)
- Check database name is exact (case-sensitive)
- Ensure API key is valid (Settings > Users > API Keys)
- Confirm user is active

### Access Denied Errors
- User may not have read access to the model
- Check user's groups and access rights
- Try with admin user to verify

### Model Not Found
- Verify model technical name (e.g., `sale.order` not `Sales Order`)
- Use `list_models` action to see available models
- Module containing model may not be installed

### Field Not Found
- Use `fields_get` to see available fields
- Field may have different technical name
- Field may be computed and not stored

## Security Best Practices

1. **Use API Keys** - Prefer API keys over passwords
2. **Minimal Permissions** - Use a user with only necessary read access
3. **No Credentials in Code** - Pass credentials as arguments
4. **Audit Trail** - Queries are logged in Odoo's access logs
5. **Rate Limiting** - Don't overwhelm the server with rapid queries
