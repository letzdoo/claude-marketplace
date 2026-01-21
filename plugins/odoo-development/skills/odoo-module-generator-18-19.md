# Odoo Module Migration Guide: 18.0 → 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: Odoo 18.0 → 19.0                                           ║
║  This document covers ONLY changes between these specific versions.          ║
║  Note: v19 is in development - patterns may change.                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Component | v18 Status | v19 Status | Action Required |
|-----------|------------|------------|-----------------|
| Type hints | Recommended | **Mandatory** | Must add |
| `SQL()` builder | Recommended | **Mandatory** | Must migrate |
| Raw SQL strings | Deprecated | **Removed** | Must migrate |
| OWL | 2.x | **3.x** | Must update |
| Python 3.10 | Required | 3.12+ required | Upgrade Python |
| `_check_company_auto` | Recommended | Standard | Already adopted |

## MANDATORY: Type Hints

### Before (v18 - Recommended)
```python
def calculate_total(self, include_tax=True, discount=None):
    discount = discount or 0
    total = sum(self.mapped('amount'))
    if include_tax:
        total *= 1.21
    return total - discount
```

### After (v19 - Required)
```python
from typing import Optional

def calculate_total(
    self,
    include_tax: bool = True,
    discount: Optional[float] = None,
) -> float:
    discount = discount or 0.0
    total = sum(self.mapped('amount'))
    if include_tax:
        total *= 1.21
    return total - discount
```

### Complete Type Hint Examples

```python
from typing import Optional, Any, Union
from collections.abc import Iterable, Mapping

class MyModel(models.Model):
    _name = 'my.model'

    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> 'MyModel':
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        return super().write(vals)

    def unlink(self) -> bool:
        return super().unlink()

    def copy(self, default: Optional[dict[str, Any]] = None) -> 'MyModel':
        return super().copy(default)

    def action_confirm(self) -> None:
        self.write({'state': 'confirmed'})

    def get_partner_data(self) -> dict[str, Any]:
        return {
            'id': self.partner_id.id,
            'name': self.partner_id.name,
        }

    @api.model
    def search_by_criteria(
        self,
        domain: list[tuple[str, str, Any]],
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> 'MyModel':
        return self.search(domain, limit=limit, offset=offset)
```

## MANDATORY: SQL Builder

### Before (v18 - Allowed)
```python
# This will FAIL in v19
query = """
    SELECT id, name FROM %s WHERE company_id = %s
""" % (self._table, self.env.company.id)
self.env.cr.execute(query)
```

### After (v19 - Required)
```python
from odoo.tools import SQL

query = SQL(
    """
    SELECT id, name FROM %s WHERE company_id = %s
    """,
    SQL.identifier(self._table),
    self.env.company.id,
)
self.env.cr.execute(query)
```

### SQL Builder Complete Reference

```python
from odoo.tools import SQL

# Basic query with parameters
query = SQL(
    "SELECT * FROM %s WHERE id = %s AND active = %s",
    SQL.identifier('res_partner'),
    123,
    True,
)

# Table and column identifiers
table = SQL.identifier('my_table')
column = SQL.identifier('my_table', 'my_column')

# Dynamic ORDER BY
order_sql = SQL('ORDER BY %s %s', SQL.identifier('create_date'), SQL('DESC'))

# Combining queries
union_query = SQL(
    "%s UNION ALL %s",
    SQL("SELECT id, name FROM table1 WHERE type = %s", 'a'),
    SQL("SELECT id, name FROM table2 WHERE type = %s", 'b'),
)

# Complex query
report_query = SQL(
    """
    SELECT
        p.id,
        p.name,
        COALESCE(SUM(o.amount_total), 0) as total_sales
    FROM %s p
    LEFT JOIN %s o ON o.partner_id = p.id
    WHERE p.company_id = %s
      AND p.active = %s
      AND o.state IN %s
    GROUP BY p.id, p.name
    HAVING SUM(o.amount_total) > %s
    ORDER BY %s
    LIMIT %s
    """,
    SQL.identifier('res_partner'),
    SQL.identifier('sale_order'),
    self.env.company.id,
    True,
    ('sale', 'done'),
    1000.0,
    SQL('total_sales DESC'),
    100,
)
```

## OWL 3.x Migration

### Major OWL Changes

| Feature | OWL 2.x (v18) | OWL 3.x (v19) |
|---------|---------------|---------------|
| Reactivity | `useState` | Enhanced reactivity |
| Component class | `Component` | Updated patterns |
| Lifecycle | Hooks-based | Refined hooks |
| Templates | QWeb | Enhanced QWeb |

### Component Structure Changes

```javascript
// v19: OWL 3.x patterns
/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
        onSelect: { type: Function, optional: true },
    };

    setup() {
        // Services
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        // Reactive state
        this.state = useState({
            data: [],
            loading: true,
        });

        // Refs
        this.containerRef = useRef("container");

        // Lifecycle
        onMounted(() => {
            this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state"]
            );
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("my_module.my_component", MyComponent);
```

### Template Updates

```xml
<!-- v19: Enhanced QWeb -->
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div t-ref="container" class="o_my_component">
            <t t-if="state.loading">
                <div class="o_loading">Loading...</div>
            </t>
            <t t-else="">
                <t t-foreach="state.data" t-as="item" t-key="item.id">
                    <div class="o_item" t-on-click="() => this.onItemClick(item)">
                        <span t-esc="item.name"/>
                    </div>
                </t>
            </t>
        </div>
    </t>
</templates>
```

## Python 3.12+ Requirements

### New Python Features Available

```python
# Type parameter syntax (PEP 695)
def process_items[T](items: list[T]) -> list[T]:
    return [item for item in items if item]

# Match statements (enhanced)
match self.state:
    case 'draft':
        self.action_confirm()
    case 'confirmed':
        self.action_done()
    case _:
        raise UserError(_("Invalid state"))

# Exception groups (if needed)
try:
    self.validate_all()
except* ValidationError as eg:
    for e in eg.exceptions:
        self.notification.add(str(e), type='warning')
```

## Manifest Version Update

```python
# v18
'version': '18.0.1.0.0',

# v19
'version': '19.0.1.0.0',
```

## Migration Checklist

### Models (Python) - CRITICAL
- [ ] Add type hints to ALL method signatures
- [ ] Add type hints to ALL method return types
- [ ] Replace ALL raw SQL with `SQL()` builder
- [ ] Verify `from odoo.tools import SQL` is imported
- [ ] Update to Python 3.12+ syntax where beneficial
- [ ] Review all `cr.execute()` calls

### OWL Components (JavaScript) - CRITICAL
- [ ] Update to OWL 3.x patterns
- [ ] Review all component lifecycle hooks
- [ ] Update reactivity patterns
- [ ] Test all UI components thoroughly

### Views (XML)
- [ ] Verify all views work with v19
- [ ] Test all dynamic visibility rules
- [ ] Verify template inheritance

### Security
- [ ] Verify record rules with new patterns
- [ ] Test multi-company scenarios
- [ ] Review group assignments

### Manifest
- [ ] Update version from `18.0.x.x.x` to `19.0.x.x.x`
- [ ] Verify all dependencies are v19 compatible
- [ ] Update asset declarations for OWL 3.x

### Testing
- [ ] Run all tests with Python 3.12+
- [ ] Test all OWL components
- [ ] Verify all SQL queries execute correctly
- [ ] Performance testing

## Common Migration Errors

### Error: Missing type hints
```
TypeError: Missing type annotation for parameter 'vals'
```
**Solution**: Add type hints to all method parameters and return types.

### Error: Raw SQL not allowed
```
SecurityError: Raw SQL strings are not allowed. Use SQL() builder.
```
**Solution**: Convert all raw SQL to use `SQL()` builder.

### Error: OWL component failure
```
Error: Component lifecycle hook not found
```
**Solution**: Update component to OWL 3.x patterns.

### Error: Python version incompatibility
```
SyntaxError: invalid syntax (requires Python 3.12+)
```
**Solution**: Upgrade Python to 3.12 or later.

## Type Hint Migration Script

```python
#!/usr/bin/env python3
"""
Helper to identify methods missing type hints.
Run on your Python files to find what needs updating.
"""
import ast
import sys
from pathlib import Path

def check_type_hints(filepath: Path) -> list[str]:
    """Check for missing type hints in a Python file."""
    issues = []
    with open(filepath) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check return type
            if node.returns is None and node.name != '__init__':
                issues.append(f"{filepath}:{node.lineno} - {node.name}() missing return type")

            # Check parameters
            for arg in node.args.args:
                if arg.arg != 'self' and arg.annotation is None:
                    issues.append(f"{filepath}:{node.lineno} - {node.name}({arg.arg}) missing type")

    return issues

if __name__ == '__main__':
    for path in Path('.').rglob('*.py'):
        issues = check_type_hints(path)
        for issue in issues:
            print(issue)
```

## GitHub Reference

For official migration notes, consult:
- https://github.com/odoo/odoo/tree/19.0 (when available)
- Odoo 19.0 release notes
- Community upgrade scripts

---

**IMPORTANT**: v19 is currently in development. These patterns are based on announced changes and may be refined. Always verify against official documentation when available.
