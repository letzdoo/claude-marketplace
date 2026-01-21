---
name: odoo-upgrade
description: Analyze module compatibility and generate upgrade migration plan. Use when user asks to "upgrade module", "migrate to odoo 18", "check upgrade compatibility", "version migration".
arguments:
  - name: path
    description: Path to the module to upgrade
    required: false
  - name: from_version
    description: Current Odoo version
    required: false
  - name: to_version
    description: Target Odoo version
    required: false
input_examples:
  - description: "Upgrade module from Odoo 16 to 18"
    arguments:
      path: "./my_module"
      from_version: "16.0"
      to_version: "18.0"
  - description: "Analyze upgrade for module in current directory"
    arguments:
      to_version: "18.0"
  - description: "Multi-version jump analysis"
    arguments:
      path: "./legacy_module"
      from_version: "14.0"
      to_version: "18.0"
---

# /odoo-upgrade Command

Analyze an Odoo module for version compatibility and generate a detailed migration plan.

## CRITICAL: VERSION IDENTIFICATION

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  Migration requirements differ significantly between version jumps.          ║
║  You MUST identify both source and target versions before analysis.          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Execution Flow

### Step 1: Identify Source and Target Versions

If not provided:
1. Check `__manifest__.py` for current version
2. Ask user for target version

### Step 2: Load Migration Guides

Based on the version jump, load appropriate guides:

```
Read: odoo-development/skills/odoo-module-generator-{from}-{to}.md
Read: odoo-development/skills/odoo-security-guide-{from}-{to}.md
Read: odoo-development/skills/odoo-model-patterns-{from}-{to}.md
Read: odoo-development/skills/odoo-owl-components-{from}-{to}.md
```

### Step 3: Analyze Module

Scan all module files for:
- Deprecated patterns
- Removed APIs
- Changed syntax
- New requirements

### Step 4: Generate Migration Plan

## Migration Categories

### 1. Breaking Changes (Must Fix)
Code that will cause errors in the target version:
- Removed decorators
- Removed view syntax
- Changed method signatures
- Renamed parameters

### 2. Deprecations (Should Fix)
Code that works but is deprecated:
- Deprecated APIs
- Old patterns
- Legacy syntax

### 3. New Features (Optional)
New capabilities available in target version:
- New decorators
- New fields
- New view features
- Performance improvements

### 4. Security Updates
Security-related changes:
- New security features
- Changed rule syntax
- New validation options

## Output Format

```markdown
# Upgrade Analysis: {module_name}
## Migration: {from_version} → {to_version}

### Migration Complexity
- **Estimated Effort**: Low/Medium/High
- **Breaking Changes**: X items
- **Deprecations**: X items
- **Files Affected**: X files

### Breaking Changes (Must Fix Before Upgrade)

#### 1. {Category}: {Description}
**Files affected**: `models/model.py:45`, `views/view.xml:23`

**Before ({from_version}):**
```python
# Old code
```

**After ({to_version}):**
```python
# New code
```

**Migration steps:**
1. Step 1
2. Step 2

---

### Deprecation Warnings (Fix After Upgrade)

#### 1. {Description}
**Impact**: Warning in logs
**Files affected**: ...

---

### New Features Available

#### 1. {Feature Name}
**Benefit**: Description
**How to use**: ...

---

### Migration Checklist

- [ ] Update `__manifest__.py` version
- [ ] Fix breaking change 1
- [ ] Fix breaking change 2
- [ ] Update deprecated code
- [ ] Run tests
- [ ] Test on staging environment

### Automated Migration Script

```python
# migration/{to_version}/pre-migration.py
def migrate(cr, version):
    # Pre-migration code
    pass
```

```python
# migration/{to_version}/post-migration.py
def migrate(cr, version):
    # Post-migration code
    pass
```
```

## Version-Specific Migration Paths

### 14 → 15
- Remove `@api.multi`
- Replace `track_visibility` with `tracking`
- Update chatter widgets

### 15 → 16
- Add `Command` class imports
- Start replacing `attrs` (optional)
- Update asset definitions in manifest

### 16 → 17
- **CRITICAL**: Replace ALL `attrs` with direct attributes
- Update to `@api.model_create_multi`
- Update view visibility syntax

### 17 → 18
- Add `_check_company_auto`
- Add `check_company` to fields
- Update record rules to `allowed_company_ids`
- Add type hints (recommended)
- Use `SQL()` builder (recommended)

### 18 → 19
- Add full type annotations (required)
- Convert all SQL to `SQL()` builder (required)
- Update OWL components to 3.x

## Example Usage

```
# Analyze for upgrade
/odoo-upgrade ./my_module

# Specify versions
/odoo-upgrade ./my_module 17.0 18.0

# Multi-version jump
/odoo-upgrade ./my_module 14.0 18.0
```

## Multi-Version Jumps

For jumps spanning multiple versions (e.g., 14→18):

1. Load ALL intermediate migration guides
2. Combine breaking changes from each step
3. Note cumulative deprecations
4. Recommend incremental testing

## AI Agent Instructions

1. **IDENTIFY**: Source and target versions
2. **LOAD**: All relevant migration guides
3. **SCAN**: Module files systematically
4. **MATCH**: Code patterns against known changes
5. **CATEGORIZE**: By severity (breaking, deprecated, new)
6. **GENERATE**: Detailed migration plan with code examples
7. **PROVIDE**: Migration scripts where applicable
