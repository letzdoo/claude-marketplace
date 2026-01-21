# Odoo Security Guide - Core Concepts (All Versions)

This document covers security concepts that are consistent across all Odoo versions (14-19+). For version-specific implementation details, see the version-specific files.

## Security Architecture Overview

Odoo implements a multi-layered security model:

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Request                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Authentication                                        │
│  - User login verification                                      │
│  - Session management                                           │
│  - 2FA (if enabled)                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Menu/Action Access                                    │
│  - Menu visibility (groups attribute)                           │
│  - Action access (groups attribute)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Model Access Rights                                   │
│  - ir.model.access.csv                                          │
│  - CRUD permissions per group                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Record Rules                                          │
│  - ir.rule records                                              │
│  - Row-level filtering                                          │
│  - Domain-based access control                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: Field-Level Security                                  │
│  - groups attribute on fields                                   │
│  - Visibility in views                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Security Components

### 1. Security Groups (res.groups)

Groups are the foundation of Odoo's permission system. Users are assigned to groups, and permissions are granted to groups.

**Key Concepts:**
- **Category**: Groups can be organized into categories for the UI
- **Implied Groups**: Group inheritance - a manager group implies user group
- **Users**: Direct assignment of users to groups

**Group Hierarchy Pattern:**
```
Administrator
    └── Manager (implies Administrator permissions)
        └── User (implies Manager permissions)
```

### 2. Access Rights (ir.model.access)

Access rights define CRUD (Create, Read, Update, Delete) permissions at the model level.

**Key Concepts:**
- One record per model/group combination
- Permissions are additive (if any group grants access, user has access)
- Missing access rights = no access (secure by default)

**Permission Matrix:**
| Permission | Meaning |
|------------|---------|
| perm_read | Can view records |
| perm_write | Can modify existing records |
| perm_create | Can create new records |
| perm_unlink | Can delete records |

### 3. Record Rules (ir.rule)

Record rules filter which records a user can access within a model they have access rights to.

**Key Concepts:**
- **Domain-based**: Uses Odoo domain syntax
- **Global Rules**: Apply to all users (no group specified)
- **Group Rules**: Apply only to specific groups
- **Combination**: Multiple rules are OR'd within a group, AND'd across groups

**Rule Evaluation:**
```
Final Access = (Global Rules AND'd) AND (Group Rules OR'd per group)
```

### 4. Field-Level Security

Individual fields can be restricted to specific groups using the `groups` attribute.

**Key Concepts:**
- Field is invisible and inaccessible to users not in the group
- Applies to both UI and API access
- Can specify multiple groups (comma-separated)

## Security Best Practices (All Versions)

### Principle of Least Privilege

Always grant the minimum permissions necessary:

```
✓ GOOD: User can only read and create, manager can also edit and delete
✗ BAD: Everyone has full access "for convenience"
```

### Defense in Depth

Use multiple security layers:

```
✓ GOOD: Access rights + Record rules + Field groups
✗ BAD: Relying only on UI hiding for security
```

### Secure by Default

When no permissions are defined, access should be denied:

```
✓ GOOD: New model has no access until explicitly granted
✗ BAD: New model accessible to everyone by default
```

### Avoid sudo() Abuse

The `sudo()` method bypasses security checks. Use it sparingly:

```python
# ✓ GOOD: sudo() for system operations only
sequence = self.env['ir.sequence'].sudo().next_by_code('my.model')

# ✗ BAD: sudo() to bypass permission checks
record.sudo().write({'sensitive_field': value})  # DANGEROUS
```

### Never Hardcode IDs

Use XML IDs for references:

```python
# ✓ GOOD: Using XML ID
manager_group = self.env.ref('my_module.group_manager')

# ✗ BAD: Hardcoded database ID
manager_group = self.env['res.groups'].browse(7)
```

## Multi-Company Security

Multi-company is a critical security concern in Odoo.

### Core Concepts

- **company_id**: Field linking record to a company
- **company_ids**: User's allowed companies
- **Record Rules**: Filter records by company

### Standard Pattern

```
User has access to companies: [1, 3]
Record has company_id: 1
→ User CAN access (1 is in [1, 3])

Record has company_id: 2
→ User CANNOT access (2 is not in [1, 3])

Record has company_id: False (no company)
→ User CAN access (shared record)
```

### Multi-Company Domain Pattern

```python
# Standard multi-company domain (all versions)
[
    '|',
    ('company_id', '=', False),
    ('company_id', 'in', company_ids)
]
```

## Portal and Public Access

### Portal Users

Portal users are external users (customers, vendors) with limited access:

- Belong to `base.group_portal`
- Cannot access internal data
- Access controlled via specific record rules

### Public Users

Public users are anonymous website visitors:

- Belong to `base.group_public`
- Very restricted access
- Used for public website pages

### Security Pattern for Portal

```
Internal Users → Full access to their scope
Portal Users → Access only to their own records
Public Users → Access only to published/public records
```

## Audit and Compliance

### Tracking Changes

Odoo provides built-in change tracking via `mail.thread`:

- Records who changed what and when
- Visible in the chatter
- Configurable per field with `tracking=True`

### Audit Log Considerations

For compliance requirements:
- Track all CRUD operations
- Record user, timestamp, IP address
- Store old and new values
- Make logs immutable

## Common Security Vulnerabilities

### SQL Injection

**Risk**: Raw SQL without proper escaping

```python
# ✗ DANGEROUS
self.env.cr.execute(f"SELECT * FROM res_partner WHERE name = '{user_input}'")

# ✓ SAFE: Use parameters
self.env.cr.execute("SELECT * FROM res_partner WHERE name = %s", [user_input])

# ✓ SAFER: Use ORM
self.env['res.partner'].search([('name', '=', user_input)])
```

### Cross-Site Scripting (XSS)

**Risk**: Unescaped user input in views

```xml
<!-- ✗ DANGEROUS: Using t-raw with user input -->
<t t-raw="record.user_input"/>

<!-- ✓ SAFE: Using t-esc (default escaping) -->
<t t-esc="record.user_input"/>
```

### Insecure Direct Object Reference (IDOR)

**Risk**: Accessing records without proper permission checks

```python
# ✗ DANGEROUS: No access check
record = self.env['my.model'].browse(user_provided_id)
return record.sensitive_data

# ✓ SAFE: Access check performed
record = self.env['my.model'].browse(user_provided_id)
record.check_access_rights('read')
record.check_access_rule('read')
return record.sensitive_data
```

## Security Testing Checklist

### Before Deployment

- [ ] All models have access rights defined
- [ ] Sensitive models have record rules
- [ ] Multi-company rules are in place
- [ ] Portal access is properly restricted
- [ ] No sudo() usage without justification
- [ ] No hardcoded IDs or credentials
- [ ] SQL queries use parameters or ORM
- [ ] User input is escaped in views
- [ ] Field groups restrict sensitive data
- [ ] Audit logging for compliance

### Testing Approach

1. Test as each user role (admin, manager, user, portal)
2. Verify each security layer independently
3. Test edge cases (no company, inactive records)
4. Attempt unauthorized access deliberately
5. Review sudo() usage in code

## Glossary

| Term | Definition |
|------|------------|
| Access Rights | Model-level CRUD permissions |
| Record Rules | Row-level domain filters |
| Security Groups | Collections of permissions assigned to users |
| sudo() | Method to bypass security checks |
| Domain | List of tuples for filtering records |
| Multi-company | Support for multiple legal entities |
| Portal | External user access (customers, vendors) |

---

**Note**: This document covers concepts that apply to all Odoo versions. For version-specific implementation syntax and patterns, refer to the appropriate version-specific file (e.g., `odoo-security-guide-18.md`).
