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
| Odoo 18.0 | `odoo-security-guide-18.md` | Current |
| Odoo 19.0 | `odoo-security-guide-19.md` | Development |
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
| `@api.multi` decorator | 14.0 (deprecated in 15.0+) |
| `track_visibility` parameter | 14.0-15.0 |
| `tracking` parameter | 15.0+ |
| `Command` class usage | 16.0+ |
| `attrs` in views | 14.0-16.0 |
| Direct `invisible`/`readonly` | 17.0+ |
| `_check_company_auto` | 18.0+ |
| Type hints on fields | 18.0+ |
| `SQL()` builder | 18.0+ |

## Quick Reference: Major Security Changes by Version

### v14 → v15
- No major security API changes

### v15 → v16
- `Command` class introduced for x2many security patterns
- Enhanced record rule evaluation

### v16 → v17
- `attrs` removed from views - security visibility changed
- `invisible` attribute now takes Python expressions

### v17 → v18
- `_check_company_auto` for automatic company validation
- `check_company` parameter on Many2one fields
- Enhanced field-level security

### v18 → v19
- Stricter type checking
- Enhanced audit capabilities

---

**REMINDER**: Do not use this dispatcher file for actual security implementation. Always load and follow the version-specific file for your target Odoo version.
