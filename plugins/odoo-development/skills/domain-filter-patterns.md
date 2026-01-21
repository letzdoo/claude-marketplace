# Domain and Filter Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  DOMAIN & FILTER PATTERNS                                                    ║
║  Search domains, record filtering, and query optimization                    ║
║  Use for search views, record rules, and programmatic filtering              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Domain Syntax

### Basic Operators
| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equal | `('state', '=', 'draft')` |
| `!=` | Not equal | `('state', '!=', 'cancel')` |
| `>` | Greater than | `('amount', '>', 100)` |
| `>=` | Greater or equal | `('date', '>=', '2024-01-01')` |
| `<` | Less than | `('quantity', '<', 10)` |
| `<=` | Less or equal | `('date', '<=', today)` |
| `like` | Pattern match (case sensitive) | `('name', 'like', 'Test%')` |
| `ilike` | Pattern match (case insensitive) | `('name', 'ilike', '%test%')` |
| `=like` | SQL LIKE | `('code', '=like', 'ABC%')` |
| `=ilike` | SQL ILIKE | `('code', '=ilike', 'abc%')` |
| `in` | In list | `('state', 'in', ['draft', 'sent'])` |
| `not in` | Not in list | `('state', 'not in', ['cancel'])` |
| `child_of` | Hierarchical child | `('category_id', 'child_of', parent_id)` |
| `parent_of` | Hierarchical parent | `('category_id', 'parent_of', child_id)` |

### Logical Operators
```python
# AND (implicit between tuples)
domain = [
    ('state', '=', 'confirmed'),
    ('date', '>=', '2024-01-01'),
]

# OR (prefix notation)
domain = [
    '|',
    ('state', '=', 'draft'),
    ('state', '=', 'sent'),
]

# NOT
domain = [
    '!',
    ('state', '=', 'cancel'),
]

# Complex: (A AND B) OR (C AND D)
domain = [
    '|',
    '&', ('state', '=', 'draft'), ('user_id', '=', uid),
    '&', ('state', '=', 'confirmed'), ('amount', '>', 1000),
]
```

---

## Common Domain Patterns

### Date Ranges
```python
from datetime import date, datetime, timedelta
from odoo import fields

# Today
today = fields.Date.today()
domain = [('date', '=', today)]

# This week
week_start = today - timedelta(days=today.weekday())
week_end = week_start + timedelta(days=6)
domain = [
    ('date', '>=', week_start),
    ('date', '<=', week_end),
]

# This month
month_start = today.replace(day=1)
next_month = (month_start + timedelta(days=32)).replace(day=1)
domain = [
    ('date', '>=', month_start),
    ('date', '<', next_month),
]

# Last 30 days
domain = [('date', '>=', today - timedelta(days=30))]

# Between dates
domain = [
    ('date', '>=', date_from),
    ('date', '<=', date_to),
]
```

### Company Filtering
```python
# Current company only
domain = [('company_id', '=', self.env.company.id)]

# User's companies
domain = [('company_id', 'in', self.env.user.company_ids.ids)]

# Or no company (shared)
domain = [
    '|',
    ('company_id', '=', False),
    ('company_id', '=', self.env.company.id),
]
```

### User/Partner Filtering
```python
# Current user
domain = [('user_id', '=', self.env.uid)]

# Current user's partner
domain = [('partner_id', '=', self.env.user.partner_id.id)]

# Team members
domain = [('user_id', 'in', self.env.user.team_id.member_ids.ids)]

# No assigned user
domain = [('user_id', '=', False)]
```

### Related Field Filtering
```python
# Filter by related field
domain = [('partner_id.country_id', '=', country_id)]

# Multiple levels
domain = [('order_id.partner_id.is_company', '=', True)]

# Related Many2many
domain = [('tag_ids.name', 'ilike', 'important')]
```

### Null/Empty Checks
```python
# Field is empty
domain = [('name', '=', False)]

# Field is not empty
domain = [('name', '!=', False)]

# Empty string vs False
domain = [('name', 'in', [False, ''])]

# Has related records
domain = [('line_ids', '!=', False)]
```

---

## Dynamic Domains

### In Python Methods
```python
def _get_records_domain(self):
    """Build domain dynamically."""
    domain = [('active', '=', True)]

    if self.partner_id:
        domain.append(('partner_id', '=', self.partner_id.id))

    if self.date_from:
        domain.append(('date', '>=', self.date_from))

    if self.date_to:
        domain.append(('date', '<=', self.date_to))

    if self.state_filter:
        domain.append(('state', '=', self.state_filter))

    return domain

def action_search(self):
    domain = self._get_records_domain()
    records = self.env['my.model'].search(domain)
    return records
```

### In Field Definitions
```python
# Static domain
partner_id = fields.Many2one(
    'res.partner',
    domain=[('is_company', '=', True)],
)

# Dynamic domain (string)
partner_id = fields.Many2one(
    'res.partner',
    domain="[('company_id', '=', company_id)]",
)

# Complex dynamic domain
def _get_partner_domain(self):
    return [
        ('is_company', '=', True),
        ('country_id', '=', self.env.company.country_id.id),
    ]

partner_id = fields.Many2one(
    'res.partner',
    domain=lambda self: self._get_partner_domain(),
)
```

### In Views (XML)
```xml
<!-- Static domain -->
<field name="partner_id" domain="[('is_company', '=', True)]"/>

<!-- Dynamic using other fields -->
<field name="product_id"
       domain="[('categ_id', '=', category_id)]"/>

<!-- With context -->
<field name="user_id"
       domain="[('company_id', '=', company_id)]"
       context="{'default_company_id': company_id}"/>

<!-- Complex domain -->
<field name="location_id"
       domain="[
           ('usage', '=', 'internal'),
           '|',
           ('company_id', '=', company_id),
           ('company_id', '=', False)
       ]"/>
```

---

## Search Views

### Basic Search View
```xml
<record id="my_model_view_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search string="Search">
            <!-- Search fields -->
            <field name="name"/>
            <field name="partner_id"/>
            <field name="reference" filter_domain="[
                '|',
                ('name', 'ilike', self),
                ('reference', 'ilike', self)
            ]"/>

            <!-- Filters -->
            <filter string="My Records" name="my_records"
                    domain="[('user_id', '=', uid)]"/>
            <filter string="Today" name="today"
                    domain="[('date', '=', context_today().strftime('%Y-%m-%d'))]"/>
            <filter string="This Month" name="this_month"
                    domain="[
                        ('date', '>=', (context_today() + relativedelta(day=1)).strftime('%Y-%m-%d')),
                        ('date', '&lt;', (context_today() + relativedelta(months=1, day=1)).strftime('%Y-%m-%d'))
                    ]"/>
            <separator/>
            <filter string="Draft" name="draft"
                    domain="[('state', '=', 'draft')]"/>
            <filter string="Confirmed" name="confirmed"
                    domain="[('state', '=', 'confirmed')]"/>
            <separator/>
            <filter string="Archived" name="archived"
                    domain="[('active', '=', False)]"/>

            <!-- Group By -->
            <group expand="0" string="Group By">
                <filter string="Partner" name="group_partner"
                        context="{'group_by': 'partner_id'}"/>
                <filter string="State" name="group_state"
                        context="{'group_by': 'state'}"/>
                <filter string="Date" name="group_date"
                        context="{'group_by': 'date:month'}"/>
            </group>
        </search>
    </field>
</record>
```

### Advanced Search Features
```xml
<search>
    <!-- Multi-field search -->
    <field name="name" string="Name/Reference"
           filter_domain="[
               '|', '|',
               ('name', 'ilike', self),
               ('reference', 'ilike', self),
               ('partner_id.name', 'ilike', self)
           ]"/>

    <!-- Search related fields -->
    <field name="partner_id" operator="child_of"/>

    <!-- Date range filters -->
    <filter string="Last 7 Days" name="last_7_days"
            domain="[('create_date', '>=', (context_today() - relativedelta(days=7)).strftime('%Y-%m-%d'))]"/>

    <!-- Negative filter -->
    <filter string="Without Partner" name="no_partner"
            domain="[('partner_id', '=', False)]"/>

    <!-- Combined AND filter -->
    <filter string="Urgent Draft" name="urgent_draft"
            domain="[('state', '=', 'draft'), ('priority', '=', 'high')]"/>

    <!-- Dynamic context filter -->
    <filter string="My Team" name="my_team"
            domain="[('user_id.team_id', '=', %(sales_team.team_id)d)]"/>
</search>
```

---

## Record Rules

### Basic Record Rule
```xml
<!-- Users see only their own records -->
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: User Rule</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### Manager Rule (Override)
```xml
<!-- Managers see all records -->
<record id="rule_my_model_manager" model="ir.rule">
    <field name="name">My Model: Manager Rule</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('my_module.group_manager'))]"/>
</record>
```

### Global Rule (No Groups)
```xml
<!-- Global rule applying to everyone -->
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Company Rule</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
    <field name="global" eval="True"/>
</record>
```

---

## Domain Helper Functions

### Domain Utilities
```python
from odoo.osv import expression


class DomainHelper(models.AbstractModel):
    _name = 'domain.helper'

    def combine_domains(self, *domains):
        """Combine multiple domains with AND."""
        return expression.AND(list(domains))

    def combine_domains_or(self, *domains):
        """Combine multiple domains with OR."""
        return expression.OR(list(domains))

    def normalize_domain(self, domain):
        """Normalize domain to standard form."""
        return expression.normalize_domain(domain)

    def is_false_domain(self, domain):
        """Check if domain is always false."""
        return expression.is_false(self, domain)

    def distribute_not(self, domain):
        """Push NOT operators down in domain."""
        return expression.distribute_not(domain)


# Usage
domain1 = [('state', '=', 'draft')]
domain2 = [('user_id', '=', self.env.uid)]

# AND combination
combined = expression.AND([domain1, domain2])
# Result: [('state', '=', 'draft'), ('user_id', '=', uid)]

# OR combination
combined = expression.OR([domain1, domain2])
# Result: ['|', ('state', '=', 'draft'), ('user_id', '=', uid)]
```

### Domain Parsing
```python
from odoo.osv.expression import DOMAIN_OPERATORS

def parse_domain(domain):
    """Parse and analyze domain."""
    result = {
        'fields': set(),
        'operators': [],
    }

    for element in domain:
        if isinstance(element, tuple):
            result['fields'].add(element[0])
            result['operators'].append(element[1])
        elif element in DOMAIN_OPERATORS:
            pass  # Logical operator

    return result
```

---

## Performance Tips

### Indexed Fields
```python
# Add index for frequently filtered fields
name = fields.Char(string='Name', index=True)
date = fields.Date(string='Date', index=True)
state = fields.Selection([...], index=True)
partner_id = fields.Many2one('res.partner', index=True)
```

### Efficient Domains
```python
# Good - Uses index
domain = [('state', '=', 'confirmed')]

# Bad - Function prevents index usage
domain = [('state', '=like', 'conf%')]

# Good - Specific IDs
domain = [('id', 'in', record_ids)]

# Bad - Too many OR conditions
domain = ['|'] * 99 + [('field', '=', v) for v in range(100)]
# Better - Use 'in'
domain = [('field', 'in', list(range(100)))]
```

### Limit Results
```python
# Always limit when possible
records = self.env['my.model'].search(domain, limit=100)

# Use search_count for counts
count = self.env['my.model'].search_count(domain)
```

---

## Best Practices

1. **Use `in` operator** for multiple values instead of multiple OR
2. **Index filtered fields** for better performance
3. **Limit results** when full result set not needed
4. **Use expression module** for combining domains
5. **Test complex domains** with actual data
6. **Document complex domains** with comments
7. **Use `child_of`/`parent_of`** for hierarchical data
8. **Prefer `ilike`** over `like` for user searches
9. **Handle empty values** explicitly
10. **Use record rules** for security, not business logic
