# Odoo Version Knowledge - Master Reference

## CRITICAL: VERSION-SPECIFIC DEVELOPMENT

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ⚠️  MANDATORY VERSION AWARENESS ⚠️                                         ║
║                                                                              ║
║   Odoo has BREAKING CHANGES between versions. Code written for one           ║
║   version often WILL NOT WORK in another version.                            ║
║                                                                              ║
║   ALWAYS identify the target Odoo version BEFORE writing any code.           ║
║   This is NOT optional.                                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version Support Status

| Version | Status | Python | End of Support |
|---------|--------|--------|----------------|
| 14.0 | Legacy | 3.6+ | October 2023 |
| 15.0 | Legacy | 3.8+ | October 2024 |
| 16.0 | Supported | 3.8+ | October 2025 |
| 17.0 | Supported | 3.10+ | October 2026 |
| 18.0 | Supported | 3.10+ | October 2027 |
| 19.0 | Current | 3.10+ | TBD |

## Version-Specific Knowledge Files

| Version | File |
|---------|------|
| Odoo 14.0 | `odoo-version-knowledge-14.md` |
| Odoo 15.0 | `odoo-version-knowledge-15.md` |
| Odoo 16.0 | `odoo-version-knowledge-16.md` |
| Odoo 17.0 | `odoo-version-knowledge-17.md` |
| Odoo 18.0 | `odoo-version-knowledge-18.md` |
| Odoo 19.0 | `odoo-version-knowledge-19.md` |

## Breaking Changes Summary

### v14 → v15
| Component | Change | Impact |
|-----------|--------|--------|
| `@api.multi` | Removed | Must remove decorator |
| `track_visibility` | Deprecated | Replace with `tracking` |
| OWL | Introduced | New frontend framework |

### v15 → v16
| Component | Change | Impact |
|-----------|--------|--------|
| x2many commands | `Command` class | New syntax for relations |
| `attrs` | Deprecated | Prepare for removal |
| OWL | 2.x | Module system change |
| Assets | `assets` key | New manifest structure |

### v16 → v17
| Component | Change | Impact |
|-----------|--------|--------|
| `attrs` | Removed | **BREAKING**: Must migrate |
| View visibility | Python expressions | New syntax |
| `@api.model_create_multi` | Mandatory | Must use for create |
| Python | 3.10+ | Version requirement |

### v17 → v18
| Component | Change | Impact |
|-----------|--------|--------|
| Type hints | Recommended | Better IDE support |
| `SQL()` builder | Recommended | Safer SQL queries |

Note: `_check_company_auto` / `check_company=True` are unchanged (opt-in since 14.0), and record rules keep using `company_ids` (there is no rename to `allowed_company_ids`).

### v18 → v19
| Component | Change | Impact |
|-----------|--------|--------|
| `_sql_constraints` | Ignored | **BREAKING**: use `models.Constraint` / `models.Index` / `models.UniqueIndex` |
| `res.users.groups_id` | Renamed `group_ids` | Update code, views and data |
| Type hints | Optional | Recommended, nothing enforces them |
| `SQL()` builder | Recommended | Plain `cr.execute(query, params)` still works |
| OWL | 2.8.x | No Owl 3 (only on master/20.0) |
| Python | 3.10+ | Minimum (`MIN_PY_VERSION = (3, 10)`) |

## GitHub Branch Reference

| Version | Branch | URL |
|---------|--------|-----|
| 14.0 | `14.0` | `github.com/odoo/odoo/tree/14.0` |
| 15.0 | `15.0` | `github.com/odoo/odoo/tree/15.0` |
| 16.0 | `16.0` | `github.com/odoo/odoo/tree/16.0` |
| 17.0 | `17.0` | `github.com/odoo/odoo/tree/17.0` |
| 18.0 | `18.0` | `github.com/odoo/odoo/tree/18.0` |
| 19.0 | `19.0` | `github.com/odoo/odoo/tree/19.0` |

## Version Detection Patterns

Use these patterns to identify the Odoo version of existing code:

### Python Code Indicators

```python
# v14 indicators
@api.multi  # Deprecated in v14, removed in v15
track_visibility='onchange'  # v14 only

# v15 indicators
tracking=True  # v15+

# v16 indicators
from odoo import Command  # v16+

# v17 indicators
@api.model_create_multi  # Mandatory in v17+
# (no attrs in views)

# v18 indicators
name: str = fields.Char()  # Type hints, v18+

# v19 indicators
_name_uniq = models.Constraint('UNIQUE(name)', "Name must be unique")  # replaces _sql_constraints
group_ids  # res.users groups field (was groups_id)
```

### XML/View Indicators

```xml
<!-- v14-v16: attrs syntax -->
<field name="x" attrs="{'invisible': [...]}"/>

<!-- v17+: direct attributes -->
<field name="x" invisible="condition"/>
```

### JavaScript Indicators

```javascript
// v14: Legacy
odoo.define('x', function(require) {
    var Widget = require('web.Widget');
});

// v15: OWL 1.x
odoo.define('x', function(require) {
    const { Component } = owl;
});

// v16+: OWL 2.x
/** @odoo-module **/
import { Component } from "@odoo/owl";
```

## Deprecation Warnings

When you see these in logs, the code needs updating:

| Warning | Version | Action |
|---------|---------|--------|
| `@api.multi is deprecated` | v14 | Remove decorator |
| `track_visibility is deprecated` | v15 | Use `tracking=True` |
| `attrs is deprecated` | v16 | Use direct attributes |

## AI Agent Version Workflow

When working on Odoo development:

1. **FIRST**: Determine the target Odoo version
2. **THEN**: Load the appropriate version-specific skill files
3. **VERIFY**: Check patterns against the version's GitHub branch
4. **GENERATE**: Use only patterns from the correct version
5. **TEST**: Verify code works on the target version

```
Question: "What Odoo version are you targeting?"

If answer is unclear, look for:
- Existing code patterns (use detection table above)
- __manifest__.py version string
- Requirements.txt Python version
- Package.json / assets structure
```

## Version Compatibility Matrix

| Feature | v14 | v15 | v16 | v17 | v18 | v19 |
|---------|-----|-----|-----|-----|-----|-----|
| `@api.multi` | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `tracking` | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Command` class | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `attrs` in views | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Direct invisible | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `_check_company_auto` / `check_company` (opt-in) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Type hints on fields (optional) | ❌ | ❌ | ❌ | ❌ | ⚠️ | ⚠️ |
| `SQL()` builder (recommended, not required) | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| OWL 2.x (19.0: Owl 2.8.x) | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| OWL 3.x (master/20.0 only) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

Legend: ✅ Supported | ⚠️ Deprecated/Optional | ❌ Not available/Removed

---

**CRITICAL**: Never assume version compatibility. Always verify against the specific version documentation.
