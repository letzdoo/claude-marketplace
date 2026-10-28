# Odoo Security Guide - Version Dispatcher

## CRITICAL: VERSION-SPECIFIC REQUIREMENTS

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ⚠️  MANDATORY VERSION MATCHING ⚠️                                          ║
║                                                                              ║
║   You MUST use the version-specific security guide that matches your         ║
║   target Odoo version. Using patterns from the wrong version WILL            ║
║   cause errors, security vulnerabilities, or deprecated code.                ║
║                                                                              ║
║   BEFORE proceeding, identify your target Odoo version and load the          ║
║   corresponding file. This is NOT optional.                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Version-Specific Files

| Target Version | File to Use | Status |
|----------------|-------------|--------|
| Odoo 14.0 | `odoo-security-guide-14.md` | Legacy |
| Odoo 15.0 | `odoo-security-guide-15.md` | Legacy |
| Odoo 16.0 | `odoo-security-guide-16.md` | Supported |
| Odoo 17.0 | `odoo-security-guide-17.md` | Supported |
| Odoo 18.0 | `odoo-security-guide-18.md` | Supported |
| Odoo 19.0 | `odoo-security-guide-19.md` | Current (released) |
| All versions | `odoo-security-guide-all.md` | Core concepts |

## Migration Guides

When upgrading modules between versions, use the migration guides:

| Migration Path | File |
|----------------|------|
| 14.0 → 15.0 | `odoo-security-guide-14-15.md` |
| 15.0 → 16.0 | `odoo-security-guide-15-16.md` |
| 16.0 → 17.0 | `odoo-security-guide-16-17.md` |
| 17.0 → 18.0 | `odoo-security-guide-17-18.md` |
| 18.0 → 19.0 | `odoo-security-guide-18-19.md` |

## How to Use This Skill

### Step 1: Identify Target Version

```
QUESTION: What Odoo version are you targeting?
- If generating NEW code → Use single version file (e.g., odoo-security-guide-18.md)
- If UPGRADING code → Use migration file (e.g., odoo-security-guide-17-18.md)
- If learning CONCEPTS → Use odoo-security-guide-all.md
```

### Step 2: Load the Correct File

**For AI Agents**: You MUST read the version-specific file before generating any security code:

```
# Example for Odoo 18.0 project
Read: skills/odoo-security-guide-18.md

# Example for upgrading from 17.0 to 18.0
Read: skills/odoo-security-guide-17-18.md
```

### Step 3: Apply Patterns

Only use patterns from the loaded version-specific file. Never mix patterns from different versions.

## Version Detection Hints

If the version is not explicitly stated, look for these clues:

| Indicator | Version |
|-----------|---------|
| `@api.multi` decorator | 12.0 or older (removed before 14.0) |
| `track_visibility` parameter | legacy (only a warning in 14.0-16.0) |
| `tracking` parameter | 14.0+ (no hint) |
| no manifest `assets` key, `qweb` key | 14.0 |
| `Command` class usage | 15.0+ |
| `t-out` in server QWeb | 15.0+ |
| `@api.private` | 16.0+ |
| `attrs` in views | 14.0-16.0 |
| Direct `invisible="<expression>"` | 17.0+ |
| `odoo.tools.SQL("...", args)` builder | 17.0+ |
| `<list>` views, `check_access()` | 18.0+ |
| `fields.Domain`, `models.Constraint`, `group_ids` on users | 19.0 |

`_check_company_auto` / `check_company=True` exist in every version 14-19 and are no version hint.

## Quick Reference: Major Security Changes by Version

### v14 → v15
- `t-out` introduced (escapes); `t-raw` deprecated (still renders raw), `t-esc` becomes an alias
- `Command` class introduced for x2many values (tuples still accepted)

### v15 → v16
- `sudo()` accepts only a bool (no more `sudo(user)` - use `with_user`)
- RPC guard `get_public_method` + `@api.private`
- Route methods overridden without `@http.route()` are auto-decorated with a warning (15.0: route silently dropped)
- Owl 2: `markup()` / `htmlEscape` in JS

### v16 → v17
- `attrs`/`states` removed from views (validation error) - use direct expressions
- `odoo.tools.SQL` builder with `SQL.identifier()`
- `_()` escapes its arguments when one of them is `Markup`

### v17 → v18
- `check_access_rights`/`check_access_rule` deprecated -> `check_access()`/`has_access()`
- Route `auth='bearer'` (API keys)
- Restricted `pickle` wrapper removed; `@web/core/utils/html` helpers in JS

### v18 → v19
- `odoo.fields.Domain` for combining domains (`expression.AND/OR` deprecated)
- Route types `jsonrpc`/`json2` (`json` kept as alias)
- `res.users.groups_id` renamed `group_ids`; `time` removed from the record-rule eval context
- RPC guard also blocks classmethods/staticmethods

For the version-aware audit sweep (pattern -> what makes it a finding -> per-version form), see `odoo-security-guide-all.md`, section "Additional Rules from Odoo's Official Guidelines" -> "Security Audit Sweep".

---

**REMINDER**: Do not use this dispatcher file for actual security implementation. Always load and follow the version-specific file for your target Odoo version.
