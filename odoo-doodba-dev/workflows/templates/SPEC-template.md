# Specification: {FEATURE_NAME}

**Date**: {DATE}
**Module**: `{module_name}`
**Odoo Version**: {VERSION}
**Type**: New Module / Extension

---

## 1. Requirements

**User Story**:
As a {role}, I want to {action}, so that {benefit}.

**Functional Requirements**:
- Requirement 1
- Requirement 2

**Non-Functional**:
- Performance: {expectations}
- Security: {requirements}

---

## 2. Module Architecture

**Decision**: New Module / Extend Existing

**Rationale**:
- {Why this approach}

**Location**: `odoo/custom/src/private/{module_name}/`

**Dependencies**:
```python
'depends': ['base', 'module1', 'module2']
```

**Indexer Validated**:
- [x] All dependencies available

---

## 3. Data Model

### 3.1 New Models

#### `{model.name}`

**Description**: {purpose}

**Inherits**: `mail.thread`, `mail.activity.mixin`

**Fields**:
| Field | Type | Required | Description | Indexer |
|-------|------|----------|-------------|---------|
| `name` | Char | ✓ | Name/title | New |
| `partner_id` | Many2one(res.partner) | ✓ | Partner | ✓ Validated |
| `state` | Selection | ✓ | Status | New |
| `line_ids` | One2many | - | Lines | New |

**Computed Fields**:
| Field | Depends | Store |
|-------|---------|-------|
| `total` | `line_ids.amount` | Yes |

**Constraints**:
- SQL: `name_unique` - Name must be unique
- Python: `_check_dates()` - End after start

**Methods**:
- `action_confirm()`: Transition to confirmed
- `action_cancel()`: Cancel record

---

### 3.2 Extended Models

#### `{existing.model}`

**Indexer**: [x] Model exists

**New Fields**:
| Field | Type | Description | Conflicts |
|-------|------|-------------|-----------|
| `custom_field` | Char | Custom field | ✓ None |

**Modified Methods**:
- `action_confirm()`: Add custom validation (calls super)

---

## 4. Views

### List View
**Fields**: name, partner_id, state
**Indexer**: [x] All fields validated

### Form View
**Layout**:
- Header: buttons, statusbar
- Body: groups, notebook with pages
- Chatter: messages, activities

**Indexer**: [x] All fields validated

### Search View
**Fields**: name, partner_id
**Filters**: My Records, By State
**Group By**: Partner, State

### View Inheritance
**Parent**: `{module}.{view}` (Indexer: [x] Validated)
**Modifications**:
- Add field after partner_id
- Add page to notebook

---

## 5. Actions & Menus

**Action**: `{module}.action_{model}`
- Model: `{model.name}`
- Views: list, form

**Menu**: `{module}.menu_{model}`
- Parent: `{parent_menu}` (Indexer: [x] Validated)

---

## 6. Business Logic

**Workflows**:
```
Draft → Confirmed → Done
  ↓         ↓
Cancelled  Cancelled
```

**State Transitions**:
| From | To | Method | Validation |
|------|-----|--------|------------|
| draft | confirmed | `action_confirm()` | Check required |
| confirmed | done | `action_done()` | Check complete |

---

## 7. Security

**Access Rights** (`ir.model.access.csv`):
| Model | Group | R | W | C | D |
|-------|-------|---|---|---|---|
| `{model}` | User | ✓ | ✓ | ✓ | - |
| `{model}` | Manager | ✓ | ✓ | ✓ | ✓ |

**Indexer**: [x] All groups validated

**Record Rules**:
- User: Own records only
- Manager: All records

---

## 8. Data Files

**Default Data** (`data/data.xml`):
- Default configurations
- System records

**Demo Data** (`data/demo_data.xml`):
- Demo records for testing

**Indexer**: [x] All XML ID references validated

---

## 9. Tests

**Test Cases**:
1. `test_create` - Basic creation
2. `test_workflow` - State transitions
3. `test_computed` - Computed fields
4. `test_constraints` - Validation
5. `test_security` - Access rights

---

## 10. Indexer Validation Summary

**Models**: {X} validated
**Fields**: {Y} validated
**XML IDs**: {Z} validated
**Version**: Odoo {VERSION} - syntax validated

**Critical Checks**:
- [x] Field naming conventions (_id, _ids)
- [x] All comodel references exist
- [x] All XML IDs have correct module prefix
- [x] View syntax appropriate for version

---

## 11. Risks & Considerations

**Performance**:
- Computed fields are stored
- Indexes on search fields

**Compatibility**:
- Odoo {VERSION} only
- Dependencies available

**Risks**:
1. {Risk}: {Mitigation}

---

## 12. Approval

**Status**: [ ] Draft / [ ] Review / [ ] Approved

**Reviewer**: _________________
**Date**: _________________

---

**Next**: Implement with `odoo-implementer` agent
