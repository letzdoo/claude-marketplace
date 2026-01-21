# Odoo Model Patterns - Version Dispatcher

## CRITICAL: VERSION-SPECIFIC REQUIREMENTS

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ⚠️  MANDATORY VERSION MATCHING ⚠️                                          ║
║                                                                              ║
║   You MUST use the version-specific model patterns that match your           ║
║   target Odoo version. Using patterns from the wrong version WILL            ║
║   cause errors or deprecated code warnings.                                  ║
║                                                                              ║
║   BEFORE implementing ANY model code, identify your target Odoo version      ║
║   and load the corresponding file. This is NOT optional.                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Files

| Target Version | File to Use | Status |
|----------------|-------------|--------|
| Odoo 14.0 | `odoo-model-patterns-14.md` | Legacy |
| Odoo 15.0 | `odoo-model-patterns-15.md` | Legacy |
| Odoo 16.0 | `odoo-model-patterns-16.md` | Supported |
| Odoo 17.0 | `odoo-model-patterns-17.md` | Supported |
| Odoo 18.0 | `odoo-model-patterns-18.md` | Current |
| Odoo 19.0 | `odoo-model-patterns-19.md` | Development |
| All versions | `odoo-model-patterns-all.md` | Core concepts |

## Migration Guides

| Migration Path | File |
|----------------|------|
| 14.0 → 15.0 | `odoo-model-patterns-14-15.md` |
| 15.0 → 16.0 | `odoo-model-patterns-15-16.md` |
| 16.0 → 17.0 | `odoo-model-patterns-16-17.md` |
| 17.0 → 18.0 | `odoo-model-patterns-17-18.md` |
| 18.0 → 19.0 | `odoo-model-patterns-18-19.md` |

## Quick Reference: Major Model Pattern Changes

### v14 Patterns
- `@api.multi` deprecated (still works)
- `track_visibility='onchange'`
- Single record `create(vals)`

### v15 Patterns
- `@api.multi` removed
- `tracking=True` replaces `track_visibility`
- Simplified chatter

### v16 Patterns
- `Command` class for x2many
- `@api.model_create_multi` recommended

### v17 Patterns
- `@api.model_create_multi` mandatory
- Enhanced ORM methods

### v18 Patterns
- `_check_company_auto = True`
- `check_company=True` on fields
- Type hints recommended
- `SQL()` builder recommended

### v19 Patterns
- Type hints mandatory
- `SQL()` builder mandatory

## Version Detection in Existing Code

| Indicator | Version |
|-----------|---------|
| `@api.multi` decorator | 14.0 |
| `track_visibility` | 14.0 |
| `tracking=True` | 15.0+ |
| Tuple syntax for x2many | 14.0-15.0 |
| `Command` class | 16.0+ |
| `_check_company_auto` | 18.0+ |
| Type hints on fields | 18.0+ |
| Full type annotations | 19.0+ |

---

**REMINDER**: Always load the version-specific file before implementing model patterns.
