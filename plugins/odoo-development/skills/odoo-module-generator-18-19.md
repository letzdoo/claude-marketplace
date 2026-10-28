# Odoo Module Migration Guide: 18.0 → 19.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MIGRATION GUIDE: Odoo 18.0 → 19.0                                           ║
║  This document covers ONLY changes between these specific versions.          ║
║  Verified against the 18.0 and 19.0 (final) source trees.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Breaking Changes Summary

| Component | v18 Status | v19 Status | Action Required |
|-----------|------------|------------|-----------------|
| `_sql_constraints` | Supported: `_sql_constraints = [...]` | **Ignored** (warning) | Convert to `_name_uniq = models.Constraint(...)` |
| `groups_id` (res.users, ir.ui.view, act_window) | Field name | **`group_ids`** | Rename in Python and XML |
| Manifest empty `depends` | Stays empty (no automatic `base`; declare `['base']` if nothing else) | `['base']` injected | None (declare deps explicitly) |
| Route `type` | `http`, `json` | `http`, `jsonrpc`, `json2`; `json` = deprecated alias of `jsonrpc` | Optional |
| Type hints | Optional | Optional | None |
| `SQL()` builder | Recommended | Recommended (plain parameterized SQL still works) | None |
| OWL | 2.x | 2.x (2.8.4) | None |
| Python | 3.10+ | 3.10+ | None |
| `_check_company_auto` | Opt-in | Opt-in | None |

## Type Hints (optional in both versions)

### Without hints (valid in v18 and v19)
```python
def calculate_total(self, include_tax=True, discount=None):
    discount = discount or 0
    total = sum(self.mapped('amount'))
    if include_tax:
        total *= 1.21
    return total - discount
```

### With hints (optional style)
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

## SQL Builder (recommended in both versions)

### Never do this (SQL injection risk in any version)
```python
# Values and identifiers formatted into the string
query = """
    SELECT id, name FROM %s WHERE company_id = %s
""" % (self._table, self.env.company.id)
self.env.cr.execute(query)
```

### Preferred (v18 and v19)
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

## OWL (2.x in both versions)

Odoo 19.0 ships Owl 2.8.4 (`addons/web/static/lib/owl/owl.js`); there is no Owl 3
migration. v18 components work unchanged in v19.

### Component Structure (v18 and v19)

```javascript
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
                        <span t-out="item.name"/>
                    </div>
                </t>
            </t>
        </div>
    </t>
</templates>
```

## Python Requirements

Both 18.0 and 19.0 require Python 3.10+ (`MIN_PY_VERSION = (3, 10)`). Generated code must
stay 3.10-compatible: no PEP 695 type parameters, no `except*`.

```python
# Match statements (Python 3.10+)
match self.state:
    case 'draft':
        self.action_confirm()
    case 'confirmed':
        self.action_done()
    case _:
        raise UserError(_("Invalid state"))
```

## Manifest Version Update

```python
# v18
'version': '18.0.1.0.0',

# v19
'version': '19.0.1.0.0',
```

## Additional deltas from Odoo's official guidelines (18.0 -> 19.0)

Verified official-guideline items that matter for generated modules, change between 18.0 and 19.0 and are not in the Breaking Changes Summary:

| Topic | 18.0 | 19.0 |
|-------|------|------|
| Multi-column index | `init()` + `tools.sql.create_index` | `models.Index(...)` |
| `@api.model` create | DeprecationWarning | converted silently (generate `@api.model_create_multi` anyway) |
| ir.rule domain names | `user`, `time`, `company_ids`, `company_id` | `user`, `company_ids`, `company_id` |
| `BaseCommon` in generated tests | superuser env, mail disabled | optional independent user/company (`setup_independent_user/company`) |

Unchanged: `license` defaults to LGPL-3 (with warning), `auto_install` may be a subset list of `depends`, `assets` manifest key, `security/ir.model.access.csv` (no `ir.access`), default test tags `standard` + `at_install`, post-install via `@tagged('post_install', '-at_install')`, test files `tests/test_*.py` imported in `tests/__init__.py`, imported TestCase classes skipped, inherited `test_*` methods need `allow_inherited_tests_method = True`, `patch(obj, extension)`.

## Migration Checklist

### Models (Python) - CRITICAL
- [ ] Convert every `_sql_constraints` to `models.Constraint()` / `models.UniqueIndex()`
- [ ] Rename `groups_id` -> `group_ids` (Python, XML data, tests)
- [ ] Remove `time` from record rule domains
- [ ] Replace `read_group()` with `_read_group()` / `formatted_read_group()`
- [ ] Review all `cr.execute()` calls (parameters, never string formatting)

### OWL Components (JavaScript)
- [ ] No framework migration needed (Owl 2.x in both); re-test components
- [ ] Optionally use the new `@web/core/utils/html` helpers (`htmlJoin`, `htmlSprintf`)

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
- [ ] Verify asset declarations (unchanged format)

### Testing
- [ ] Run all tests (Python 3.10+)
- [ ] Add tests that violate each SQL constraint (catches ignored `_sql_constraints`)
- [ ] Test all OWL components
- [ ] Verify all SQL queries execute correctly

## Common Migration Errors

### Warning: `_sql_constraints` no longer supported
**Solution**: Convert to `models.Constraint` attributes; the old constraints are not applied in 19.

### Error: Invalid field 'groups_id'
**Solution**: Use `group_ids`.

## Type Hint Helper Script (optional)

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
- https://github.com/odoo/odoo/tree/19.0
- Odoo 19.0 release notes
- Community upgrade scripts

---

**Note**: 19.0 is released (`odoo/release.py`: FINAL). Always verify patterns against the 19.0 source.
