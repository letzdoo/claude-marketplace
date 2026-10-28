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
- **Implied Groups**: `implied_ids` on group A means every member of A also gets group B - the higher group implies the lower one (manager implies user), never the reverse
- **Users**: Direct assignment of users to groups

**Group Hierarchy Pattern:**
```
Manager   (implied_ids -> User: every manager is also a user)
    └── User   (implied_ids -> base.group_user)
```

Core example (`base/security/base_groups.xml`): `base.group_system` (Settings) implies `base.group_erp_manager` (Access Rights), which implies `base.group_user` (Internal User).

```xml
<record id="group_my_module_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
</record>
```

### 2. Access Rights (ir.model.access)

Access rights define CRUD (Create, Read, Update, Delete) permissions at the model level.

**Key Concepts:**
- One record per model/group combination
- Permissions are additive (if any group grants access, user has access)
- Missing access rights = no access (secure by default)
- Defined in `security/ir.model.access.csv`: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`. The access model is `ir.model.access` + `ir.rule`; there is **no** `ir.access` model and **no** `base.group_everyone` in 14.0-19.0 (both are master/20.0 only)
- A row with an empty `group_id` applies to every user. Flag any create/write/unlink granted to `base.group_portal`, `base.group_public` or to an empty `group_id`; scrutinize even read on personal or business-sensitive models

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
- **Global Rules**: Apply to all users (no group specified). Do not set `<field name="global" eval="True"/>`: `global` is computed from `groups` (no groups = global)
- **Group Rules**: Apply only to specific groups
- **Combination**: Global rules are AND-ed together; all group rules that apply to the user (from any of the user's groups) are OR-ed together, and that union is then AND-ed with the global rules
- **Per operation**: Each rule applies only to the operations flagged on it (`perm_read`, `perm_write`, `perm_create`, `perm_unlink`); a rule restricting only read leaves write governed by the other rules - cover all operations that need restricting
- **No rules under sudo**: `sudo()` skips record rules entirely
- **Domain eval context**: `user`, `time` (14.0-18.0), `company_ids`, `company_id`. `allowed_company_ids` is **not** available in record rules in any of 14.0-19.0

**Rule Evaluation (14.0-19.0):**
```
Final Access = (Global Rule 1 AND Global Rule 2 AND ...)
               AND (Group Rule A OR Group Rule B OR ...)   # only rules of the user's groups
```

Two disjoint global rules lock everyone out; a group rule can only widen access among the user's group rules, never beyond the global rules.

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

It is a finding when `sudo()` masks an `AccessError`, or an attacker controls the model/record/field read, the values created/written, or the domain searched; `record.sudo().write(post)` with raw request params (whitelist keys); a `with_user`/`with_company` switch driven by request data. `sudo(user)` in 14.0-15.0 is deprecated (warns, delegates to `with_user`); 16.0+ `sudo()` takes a bool only.

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
- **Record Rules**: Filter records by company - every multi-company model needs a company rule

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

- Values: always `cr.execute(query, params)` (all versions); never `%`, `.format`, f-strings or `+` to put values into SQL.
- Identifiers from user input: 14.0-16.0 `psycopg2.sql.Identifier`; 17.0+ `odoo.tools.SQL` + `SQL.identifier()` (validated by `assert`, skipped under `python -O`). In 16.0 `odoo.tools.SQL` is psycopg2's `sql.SQL` - a different API.
- Raw SQL where the ORM would do is itself a finding: it bypasses ACL, record rules, `active`, translations and cache.
- ORM-filtered custom SQL: 14.0-16.0 `query = Model._search(dom)` then `query.select('"t"."col"')` -> `(sql, params)` (may return `[]`, do not test `if query:`); 17.0+ `cr.execute(query.select(SQL(...)))`.

### Cross-Site Scripting (XSS)

**Risk**: Unescaped user input in views

```xml
<!-- ✗ DANGEROUS: t-raw renders unescaped (14.0; deprecated but still raw in 15.0-19.0) -->
<t t-raw="record.user_input"/>

<!-- ✓ SAFE 15.0+: t-out escapes by default (only Markup values render as HTML) -->
<t t-out="record.user_input"/>

<!-- ✓ SAFE 14.0 only: t-out does not exist yet; t-esc escapes -->
<t t-esc="record.user_input"/>
```

`t-esc` still renders (escaped) in 15.0-19.0 as a deprecated alias of `t-out`; use `t-out` in new code from 15.0. In 15.0+ the raw-HTML vector is a `Markup` value (Python) or `markup()` (Owl 2, 16.0+) built from non-literal content and reaching `t-out`.

- `Markup(f"...{x}")` is a finding: the f-string defeats escaping. `_()` escapes Markup args only from 17.0.
- JS sinks (`markup(`, `innerHTML`, `insertAdjacentHTML`) are findings when user/low-privilege content reaches them. 14.0-15.0 Owl 1 (no `markup`); 16.0+ Owl 2 `markup`/`htmlEscape` from `@odoo/owl`; 18.0+ `@web/core/utils/html` (`setElementContent`, ...); there is no `setInnerHtml` in 14-19.

### Insecure Direct Object Reference (IDOR)

**Risk**: Accessing records by an attacker-chosen id in an elevated environment

`browse()` itself performs no check, but reading a field in a normal (non-sudo) environment **does**: the fetch checks access rights and record rules and raises `AccessError`. The IDOR happens when the record is read through `sudo()` (or a sudo-computed `related` field) with an id the user controls.

```python
# ✗ DANGEROUS: sudo() read with a user-provided id - no ACL, no record rules
record = self.env['my.model'].sudo().browse(user_provided_id)
return record.sensitive_data

# ✓ SAFE: read in the user's environment - ACL + record rules enforced on fetch
record = self.env['my.model'].browse(user_provided_id)
return record.sensitive_data

# ✓ Explicit check before a justified sudo() (14.0-17.0)
record = self.env['my.model'].browse(user_provided_id)
record.check_access_rights('read')
record.check_access_rule('read')
value = record.sudo().sensitive_data

# ✓ Explicit check before a justified sudo() (18.0+; the two methods above are deprecated)
record = self.env['my.model'].browse(user_provided_id)
record.check_access('read')
value = record.sudo().sensitive_data
```

## Additional Rules from Odoo's Official Guidelines (verified for 14.0-19.0)

These rules come from Odoo's official skill library (odoo/odoo, `skills/odoo-security`, branch 20.0) and were checked against the 14.0-19.0 sources; master-only APIs are translated to the version equivalent or marked as not available.

### Security Audit Sweep

**Process:** review the `security/` data files against the access model (see Access Rights and Record Rules), then sweep the addon for every pattern in the table and judge each hit against its rule. A hit is not a finding by itself; the "finding when" column says what makes it one. Report each finding with severity, exact file/line and a minimal fix. The audit is complete when every pattern has been swept and every hit judged.

| Sweep for | Finding when | Version notes |
|---|---|---|
| `sudo(`, `with_user(`, `with_company(` | elevated or switched env driven by attacker input | see Avoid sudo() Abuse |
| x2many values written under `sudo()` | raw request values contain command lists: commands run as sudo **on the comodel** unless it sets `_allow_sudo_commands = False` - whitelist command lists too | 14.0: tuples `(0, 0, vals)`; 15.0+: `Command.*` (tuples still accepted) |
| `related=` crossing models | sensitive value reachable through a user-writable Many2one (related fields are computed as superuser by default, `related_sudo=True`); related onto `ir.attachment` = arbitrary file read | set `related_sudo=False` on sensitive chains (all versions) |
| `cr.execute`, `SQL(`, `%`/`.format`/f-string/`+` near SQL | interpolated values, user-supplied identifiers, raw SQL where the ORM would do | see SQL Injection |
| domain built from request/RPC/stored values | a user-supplied list concatenated onto a security domain (`'|'` injection widens access) | 14.0-18.0 `odoo.osv.expression.AND([...])`/`OR`; 19.0 `odoo.fields.Domain` (`&`, `|`, `~`; `expression.*` deprecated) |
| public (non-`_`) model methods | method callable over RPC trusts `self` or its arguments (access control is enforced on CRUD, not on method calls) | RPC guard 14.0-15.0: `check_method_name` blocks `_*` and `init`; 16.0+: `get_public_method` also honours `@api.private` and unsafe attributes; 19.0 also blocks classmethod/staticmethod. `@api.private` is 16.0+ - in 14.0-15.0 rename with `_` |
| `@http.route(`, bare `@route(` | `public`/`none` route exposing internal data or privileged writes; state change on GET; `csrf=False` on a `type='http'` route that is not a dedicated webhook; POST template without `csrf_token` input | `auth`: `user`/`public`/`none`; 18.0+ also `bearer` (no `bearer_scope`). `type`: `http`/`json`; 19.0 `http`/`jsonrpc`/`json2` (`json` = deprecated alias). JSON routes have no CSRF token check by design. Overriding a route method without `@http.route()`: 14.0-15.0 silently drops the URL; 16.0+ auto-decorates with a warning |
| `t-raw`, `Markup(`, `markup(` (JS), `innerHTML`, `insertAdjacentHTML` | user/low-privilege content reaches a raw sink | see Cross-Site Scripting (XSS) |
| password/token/secret fields | readable via `search_read` because of a permissive access row | `groups="base.group_system"` or `groups=fields.NO_ACCESS` (all versions) |
| `open(` | path can be influenced | `odoo.tools.file_open` (all versions; confined to addons paths, root path and registered temp dirs, existing files only; it is a path confinement, not a write protection) |
| `eval(`, `exec(`, `safe_eval` | builtin `eval`/`exec` at all; `safe_eval` on input from non-privileged users | prefer `json.loads`/`ast.literal_eval`; `odoo.tools.safe_eval` rejects `__` names and unsafe attributes (all versions); `--unsafe-policy` does not exist in 14-19 |
| `pickle` | any unpickling of untrusted data | use `json`. A restricted `odoo.tools.misc.pickle` exists in 14.0-17.0, removed in 18.0 |
| `getattr(`, `setattr(` on records | field name from input (reaches private attributes) | use `record[name]` and validate the name against `_fields` |
| `==` comparing a secret/token | timing leak | `odoo.tools.consteq` (all versions), or look the token up in the database |
| `def f(..., x=[])` / `x={}` | mutable default argument | `None` + create inside |
| public methods returning rich objects | reachable from `safe_eval`'d code (server actions, automation rules) | move to a module-level function or a dunder name |

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
