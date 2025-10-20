# Feature Specification: {FEATURE_NAME}

**Created**: {DATE}
**Status**: Draft → Review → Approved
**Module**: `{module_name}`
**Odoo Version**: {VERSION}

---

## 1. Requirements

### User Story
```
As a {user_role}
I want to {action}
So that {benefit}
```

### Functional Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Non-Functional Requirements
- Performance: {expectations}
- Security: {requirements}
- Compatibility: {constraints}

---

## 2. Module Information

| Property | Value |
|----------|-------|
| **Name** | `{module_name}` |
| **Location** | `odoo/custom/src/private/{module_name}` |
| **Type** | [New Module / Extension] |
| **Version** | 18.0.1.0.0 |
| **License** | LGPL-3 |
| **Category** | {category} |
| **Author** | {author} |

### Dependencies
```python
'depends': [
    'base',
    'module1',
    'module2',
]
```

**Dependency Validation** (via indexer):
- [x] `base` - Available
- [x] `module1` - Available (version X.X)
- [x] `module2` - Available (version X.X)

---

## 3. Data Model

### 3.1 New Models

#### Model: `{model.name}`

**Description**: {model_description}

**Inherits**: `mail.thread`, `mail.activity.mixin`

**Fields**:

| Field Name | Type | Required | Tracking | Description | Indexer Status |
|------------|------|----------|----------|-------------|----------------|
| `name` | `Char` | ✓ | ✓ | The name/title | N/A (new field) |
| `partner_id` | `Many2one('res.partner')` | ✓ | ✓ | Related partner | ✓ Model `res.partner` exists |
| `date_start` | `Date` | ✓ | ✗ | Start date | N/A (new field) |
| `state` | `Selection` | ✓ | ✓ | Current state | N/A (new field) |
| `description` | `Html` | ✗ | ✗ | Detailed description | N/A (new field) |

**Selection Field Values**:
```python
STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
]
```

**Computed Fields**:
| Field Name | Type | Compute Method | Store | Depends On |
|------------|------|----------------|-------|------------|
| `total_amount` | `Float` | `_compute_total` | Yes | `line_ids.amount` |

**Relational Fields**:
| Field Name | Type | Related Model | Inverse Field | Indexer Status |
|------------|------|---------------|---------------|----------------|
| `line_ids` | `One2many` | `{model}.line` | `parent_id` | ✓ Will create |
| `tag_ids` | `Many2many` | `{model}.tag` | - | ✓ Will create |

**Methods**:
- `action_confirm()`: Transition to confirmed state
- `action_cancel()`: Cancel the record
- `_compute_total()`: Calculate total from lines

**Constraints**:
```python
# SQL Constraints
_sql_constraints = [
    ('name_unique', 'UNIQUE(name)', 'Name must be unique'),
]

# Python Constraints
@api.constrains('date_start', 'date_end')
def _check_dates(self):
    # Date validation logic
```

---

### 3.2 Extended Models

#### Model: `{existing.model}`

**Extension Purpose**: {reason_for_extension}

**Indexer Validation**:
- [x] Model `{existing.model}` exists in module `{module}`
- [x] Model is extensible (not TransientModel)

**Added Fields**:

| Field Name | Type | Required | Description | Conflicts Check |
|------------|------|----------|-------------|-----------------|
| `custom_field` | `Char` | ✗ | Custom field | ✓ No conflict (indexer) |
| `related_id` | `Many2one('{model}')` | ✗ | Link to new model | ✓ No conflict (indexer) |

**Modified Methods**:
| Method | Modification Type | Purpose |
|--------|-------------------|---------|
| `action_confirm()` | Override (super call) | Add custom validation |
| `write()` | Override (super call) | Track changes |

**Method Implementation Notes**:
```python
def action_confirm(self):
    # Custom logic before
    self._custom_validation()
    # Call parent
    result = super().action_confirm()
    # Custom logic after
    self._post_confirm_actions()
    return result
```

---

## 4. Views

### 4.1 List View

**Model**: `{model.name}`
**XML ID**: `{module}.{model_name}_view_list`

**Displayed Fields**:
| Field | Widget | Indexer Validated |
|-------|--------|-------------------|
| `name` | - | ✓ |
| `partner_id` | - | ✓ res.partner exists |
| `date_start` | - | ✓ |
| `state` | `badge` | ✓ |

**Filters**:
- My Records
- Active Records
- By State

**Group By**:
- Partner
- State
- Date

---

### 4.2 Form View

**Model**: `{model.name}`
**XML ID**: `{module}.{model_name}_view_form`

**Layout Structure**:
```xml
<form>
    <header>
        <button name="action_confirm" states="draft"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <group>
                <field name="name"/>
                <field name="partner_id"/>
            </group>
            <group>
                <field name="date_start"/>
                <field name="state"/>
            </group>
        </group>
        <notebook>
            <page string="Lines">
                <field name="line_ids">
                    <tree editable="bottom">
                        <field name="name"/>
                        <field name="amount"/>
                    </tree>
                </field>
            </page>
            <page string="Details">
                <field name="description" widget="html"/>
            </page>
        </notebook>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

**Widget Selection**:
| Field | Widget | Reason | Indexer Check |
|-------|--------|--------|---------------|
| `partner_id` | Default | Many2one standard | ✓ Field type validated |
| `state` | `statusbar` | Header display | ✓ Selection field |
| `description` | `html` | Rich text editor | ✓ Html field type |
| `line_ids` | Inline tree | Quick editing | ✓ One2many validated |

---

### 4.3 Search View

**Model**: `{model.name}`
**XML ID**: `{module}.{model_name}_view_search`

**Search Fields**: `name`, `partner_id`

**Filters**:
- Domain filters
- Date filters
- State filters

**Group By**:
- Partner
- State

---

### 4.4 View Inheritance

#### Inherit: `{parent_view_xmlid}`

**Indexer Validation**:
- [x] Parent view `{parent_view_xmlid}` exists in module `{module}`
- [x] Parent view model is `{model_name}`
- [x] Parent view type is `form`

**XPath Modifications**:

| Position | XPath | Action | Element | Indexer Notes |
|----------|-------|--------|---------|---------------|
| after | `//field[@name='partner_id']` | Add field | `<field name="custom_field"/>` | ✓ partner_id exists in model |
| inside | `//notebook` | Add page | `<page string="Custom">...</page>` | ✓ notebook exists (Odoo 18) |

**Version Compatibility**:
- Odoo 18: Uses `<list>` not `<tree>`
- XPath: `//list` for list views

---

## 5. Actions and Menus

### 5.1 Window Action

**XML ID**: `{module}.action_{model_name}`
**Model**: `{model.name}`

```xml
<record id="action_{model_name}" model="ir.actions.act_window">
    <field name="name">{Model Display Name}</field>
    <field name="res_model">{model.name}</field>
    <field name="view_mode">tree,form</field>
    <field name="context">{}</field>
    <field name="domain">[]</field>
</record>
```

### 5.2 Menu Structure

```
Main Menu ({module}.menu_root)
└── Submenu ({module}.menu_{model_name})
    └── Action: {module}.action_{model_name}
```

**Parent Menu Validation**:
- [x] Parent menu `{parent_menu_xmlid}` exists (indexer)
- [ ] Creating new root menu

---

## 6. Business Logic

### 6.1 Workflows

**State Machine**:
```
Draft → Confirmed → Done
  ↓         ↓
Cancelled  Cancelled
```

**State Transitions**:
| From | To | Method | Validation |
|------|-----|--------|------------|
| draft | confirmed | `action_confirm()` | Check required fields |
| confirmed | done | `action_done()` | Check completion criteria |
| * | cancelled | `action_cancel()` | Check permissions |

### 6.2 Computed Fields

**Field**: `total_amount`
```python
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))
```

**Dependencies Validated**:
- [x] Field `line_ids` exists (new field)
- [x] Related model `{model}.line` has field `amount` (new field)

### 6.3 CRUD Overrides

**Create**:
```python
@api.model_create_multi
def create(self, vals_list):
    # Set default values
    # Generate sequence numbers
    return super().create(vals_list)
```

**Write**:
```python
def write(self, vals):
    # Validation logic
    # Track changes
    return super().write(vals)
```

**Unlink**:
```python
def unlink(self):
    # Prevent deletion if state != 'draft'
    if any(rec.state != 'draft' for rec in self):
        raise UserError("Cannot delete confirmed records")
    return super().unlink()
```

---

## 7. Security

### 7.1 Access Rights (`ir.model.access.csv`)

| Model | Group | Read | Write | Create | Delete |
|-------|-------|------|-------|--------|--------|
| `{model.name}` | User | ✓ | ✓ | ✓ | ✗ |
| `{model.name}` | Manager | ✓ | ✓ | ✓ | ✓ |

**Groups Validation**:
- [x] Group `base.group_user` exists (indexer)
- [x] Group `{module}.group_manager` - will create

### 7.2 Record Rules

**Rule**: `{model}_user_own_rule`
```xml
<record id="{model}_user_own_rule" model="ir.rule">
    <field name="name">User: Own Records</field>
    <field name="model_id" ref="model_{model_name}"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

---

## 8. Data Files

### 8.1 Demo Data

**File**: `data/demo_data.xml`

**Records**:
- Demo records for `{model.name}`
- Related demo data

### 8.2 Default Data

**File**: `data/data.xml`

**Records**:
- Default states/types
- System configurations

**XML ID References**:
| Reference | Indexer Status |
|-----------|----------------|
| `base.main_company` | ✓ Exists |
| `base.group_user` | ✓ Exists |

---

## 9. Tests

### 9.1 Test Cases

**File**: `tests/test_{model_name}.py`

**Test Methods**:
1. `test_create_{model}` - Basic creation
2. `test_state_transitions` - Workflow testing
3. `test_computed_fields` - Computation logic
4. `test_constraints` - Validation rules
5. `test_security` - Access rights

**Test Data Setup**:
```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    cls.{model} = cls.env['{model.name}'].create({
        'name': 'Test Record',
        'partner_id': cls.env.ref('base.res_partner_1').id,
    })
```

**External ID Validation**:
- [x] `base.res_partner_1` exists (indexer)

---

## 10. Indexer Validation Summary

### Models Validated
- [x] `res.partner` - Exists in `base`
- [x] `mail.thread` - Exists in `mail`
- [x] `{existing.model}` - Exists in `{module}`

### Fields Validated
- [x] `{existing.model}.partner_id` - Many2one, correct suffix
- [x] `{existing.model}.state` - Selection field

### XML IDs Validated
- [x] `base.group_user` - Exists
- [x] `base.main_company` - Exists
- [x] `{module}.{parent_view}` - Exists

### Version Compatibility
- [x] Odoo version detected: 18.0
- [x] Using `<list>` for list views
- [x] XPath expressions adapted for version

### Naming Conventions
- [x] Many2one fields use `_id` suffix
- [x] Many2many/One2many fields use `_ids` suffix
- [x] Model names follow snake_case
- [x] XML IDs follow module.name pattern

---

## 11. Dependencies & Risks

### Module Dependencies
| Module | Version | Purpose | Available |
|--------|---------|---------|-----------|
| `base` | 18.0 | Core functionality | ✓ |
| `mail` | 18.0 | Chatter/activities | ✓ |
| `{module}` | 18.0 | Base model extension | ✓ |

### External Dependencies
- Python packages: (none)
- System libraries: (none)

### Performance Considerations
- [ ] Computed fields are stored to avoid recalculation
- [ ] Database indexes on frequently searched fields
- [ ] Batch operations for bulk updates
- [ ] Avoid N+1 queries in loops

### Known Risks
1. **Risk**: Large datasets may slow computed field recalculation
   - **Mitigation**: Use stored=True and proper dependencies

2. **Risk**: Complex XPath may break with UI changes
   - **Mitigation**: Use simple, stable XPath expressions

### Compatibility Notes
- Tested for Odoo 18.0 only
- Uses current XML syntax (`<list>` not `<tree>`)
- Widget usage follows Odoo 18 standards

---

## 12. Open Questions

- [ ] Question 1: Should we add kanban view?
- [ ] Question 2: Do we need multi-company support?
- [ ] Question 3: Should records be archived instead of deleted?

---

## 13. Implementation Checklist

### For odoo-implementer Agent:

#### Module Structure
- [ ] Create `__init__.py`
- [ ] Create `__manifest__.py`
- [ ] Create directory structure (models/, views/, security/, etc.)

#### Models
- [ ] Implement `{model.name}` model
- [ ] Implement related models (lines, tags, etc.)
- [ ] Extend existing models
- [ ] Add computed fields
- [ ] Add constraints

#### Views
- [ ] Create list view
- [ ] Create form view
- [ ] Create search view
- [ ] Inherit existing views
- [ ] Create actions
- [ ] Create menus

#### Security
- [ ] Create `ir.model.access.csv`
- [ ] Create record rules in `security.xml`
- [ ] Define user groups if needed

#### Data
- [ ] Create default data file
- [ ] Create demo data file

#### Tests
- [ ] Create test file
- [ ] Implement all test methods
- [ ] Add test data setup

#### Documentation
- [ ] Create README.md
- [ ] Add inline code comments
- [ ] Document public methods

---

## 14. Approval

**Status**: [ ] Draft / [ ] Ready for Review / [ ] Approved

**Reviewed By**: _________________

**Date**: _________________

**Comments**:
```
(User feedback and approval notes)
```

---

**Next Step**: Once approved, proceed to implementation with `odoo-implementer` agent.
