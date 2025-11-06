---
description: Smart Odoo development with automatic mode detection and streamlined workflow
---

# Odoo Development Command

Intelligent development that automatically adapts to your task complexity. Combines analysis, implementation, validation, and testing in an efficient workflow.

## Your Role

You orchestrate the development process based on task complexity. Automatically detect whether this is a simple change, complex feature, or question.

---

## Auto-Mode Detection

Analyze the user's request and choose the appropriate mode:

### Quick Mode (Simple Tasks)
**Triggers**:
- Adding 1-2 fields to existing model
- Minor view modifications
- Small extensions
- Simple workflow changes

**Characteristics**:
- Single model affected
- < 5 fields involved
- No new models
- Straightforward logic

**Process**: Direct implementation → Verification → Done (5-7 minutes)

### Full Mode (Complex Features)
**Triggers**:
- New module creation
- Multiple models (3+)
- Complex workflows
- Significant business logic
- Integration between modules

**Characteristics**:
- Multiple components
- Requires architectural decisions
- Dependencies between elements
- May need phased approach

**Process**: Architecture discussion → Phased implementation → Verification → Optional docs (20-25 minutes)

### Search Mode (Questions)
**Triggers**:
- "what is..."
- "show me..."
- "find..."
- "how does..."
- "where is..."
- "does...have..."

**Characteristics**:
- User asking about code
- No implementation needed
- Information request

**Process**: Use indexer → Answer immediately (<2 seconds)

---

## Quick Mode Workflow

For simple tasks (most common):

```
1. Analyze Request
   - Understand what needs to be added/changed
   - Identify target model/module

2. Call odoo-developer Agent
   Task(
     subagent_type="odoo-developer",
     description="Implement {brief description}",
     prompt="{user_request}

     This is a SIMPLE task (Quick Mode):
     - Propose architecture inline (brief)
     - Get user approval
     - Implement immediately
     - Auto-validate with indexer"
   )

3. Wait for User Approval
   - Developer presents inline architecture
   - User approves → Continue
   - User requests changes → Adjust

4. Developer Implements
   - Creates/modifies code
   - Auto-validates with indexer
   - Returns completion summary

5. Call odoo-verifier Agent (Automatic)
   Task(
     subagent_type="odoo-verifier",
     description="Verify {module_name}",
     prompt="Verify module: {module_name}
     Location: odoo/custom/src/private/{module_name}

     - Validate structure
     - Run tests
     - Report inline (no file if pass)"
   )

6. If Verifier Passes → Done!
   If Verifier Fails → Show issues, ask to fix

Total Time: 5-7 minutes
User Approvals: 1 (architecture only)
```

---

## Full Mode Workflow

For complex features:

```
1. Analyze Request
   - Understand business requirements
   - Identify scope and complexity
   - List components needed

2. Call odoo-developer Agent
   Task(
     subagent_type="odoo-developer",
     description="Develop {feature name}",
     prompt="{user_request}

     This is a COMPLEX feature (Full Mode):
     - Research codebase thoroughly with indexer
     - Propose detailed architecture
     - Get user approval on:
       * Module structure (new vs extend)
       * Model design
       * Dependencies
       * Implementation phases
     - Implement in phases if needed
     - Auto-validate all references"
   )

3. Architecture Discussion
   - Developer researches and presents detailed proposal
   - User reviews and approves/adjusts
   - May iterate on design

4. Developer Implements
   - Creates full module structure
   - Implements all components
   - Validates references
   - Creates test stubs

5. Call odoo-verifier Agent (Automatic)
   Task(
     subagent_type="odoo-verifier",
     description="Verify {module_name}",
     prompt="Verify module: {module_name}

     - Full structure validation
     - Complete test coverage
     - Security checks
     - Create report if failures"
   )

6. If Verifier Passes:
   Ask: "Documentation needed? (y/n)"

   If yes → Call odoo-documenter Agent
   Task(
     subagent_type="odoo-documenter",
     description="Document {module_name}",
     prompt="Document module: {module_name}

     Create:
     - README.md (overview, installation, features)
     - USER-GUIDE.md (how to use)
     - DEVELOPER-GUIDE.md (architecture, extension)"
   )

7. Done!

Total Time: 20-25 minutes
User Approvals: 1-2 (architecture, optional docs)
```

---

## Search Mode Workflow

For questions about the codebase:

```
1. Detect Question
   User asking: "what is sale.order?"
              "show me fields in res.partner"
              "how does project.task work?"

2. Use Indexer Directly

   For "what is {model}":
   uv run skills/odoo-indexer/scripts/get_details.py model "{model_name}"

   For "what fields does {model} have":
   uv run skills/odoo-indexer/scripts/get_details.py model "{model_name}"

   For "find {element}":
   uv run skills/odoo-indexer/scripts/search.py "{query}" --type TYPE

   For "where is {model} defined":
   uv run skills/odoo-indexer/scripts/search.py "{model}" --type model

3. Format and Present Results
   Present in user-friendly format
   Include: fields, methods, views, location

Total Time: <2 seconds
User Approvals: 0
```

---

## Decision Logic

Use this logic to choose mode:

```python
def detect_mode(user_request):
    # Search mode
    question_keywords = ["what is", "show me", "find", "where is",
                         "how does", "list", "search for", "does...have"]
    if any(kw in user_request.lower() for kw in question_keywords):
        return "SEARCH"

    # Quick mode indicators
    quick_indicators = [
        "add field" and "to" in request,  # Adding field to existing model
        "update view" or "modify view",
        "add menu" or "add action",
        number_of_fields < 5,
        no_new_models,
        "simple" in request
    ]

    # Full mode indicators
    full_indicators = [
        "create module",
        "new module",
        "multiple models" or count(models) >= 3,
        "workflow" and "complex",
        "integration",
        "business process"
    ]

    if any(full_indicators):
        return "FULL"
    elif any(quick_indicators):
        return "QUICK"
    else:
        # Default to quick mode (can always escalate)
        return "QUICK"
```

---

## Progress Indicators

Show clear progress as you work:

### Quick Mode Progress

```
🎯 Detected: Simple Task (Quick Mode)
   Adding {field} to {model}

💻 Developing...
   [Calls odoo-developer agent]

📐 Architecture:
   Extend existing module: {module_name}
   Add field: {field_name} ({type})
   Update: {view_name}

   Proceed? ───────► [Wait for user]

✓ Approved!

💻 Implementing...
   ✓ Field added to model
   ✓ View updated
   ✓ Validated with indexer

🧪 Verifying...
   [Calls odoo-verifier agent]
   ✓ Structure valid
   ✓ References validated
   ✓ 3/3 tests passed

✅ Complete! (6 minutes)
```

### Full Mode Progress

```
🎯 Detected: Complex Feature (Full Mode)
   Creating {module_name} module

🔍 Researching codebase...
   [Developer uses indexer]
   ✓ Found 5 related models
   ✓ Identified dependencies
   ✓ Validated references

📐 Architecture Proposal:
   [Detailed architecture presented]

   Proceed? ───────► [Wait for user]

✓ Approved!

💻 Implementing Phase 1: Data Models...
   ✓ Created 3 models
   ✓ Defined relationships
   ✓ Validated with indexer

💻 Implementing Phase 2: Views...
   ✓ Created 8 views
   ✓ Configured actions and menus

💻 Implementing Phase 3: Security...
   ✓ Access rights defined
   ✓ Record rules created

🧪 Verifying...
   [Calls odoo-verifier agent]
   ✓ All validations passed
   ✓ 15/15 tests passed

📚 Documentation? (y/n) ───────► [Ask user]

✅ Complete! (23 minutes)
```

### Search Mode Progress

```
🔍 Searching codebase...

✓ Found: sale.order (model)

**Details**:
- Module: sale
- Description: Sales Order
- Fields: 127 total
  - partner_id (Many2one → res.partner)
  - order_line (One2many → sale.order.line)
  - amount_total (Monetary, computed)
  - state (Selection: draft/sent/sale/done/cancel)
- Views: 8 (form, list, search, kanban, calendar, pivot, graph, activity)
- Methods: 45 including action_confirm(), action_cancel(), _compute_amount_total()

Query time: 28ms
```

---

## Error Handling

### Validation Failures

If verifier finds issues:

```
⚠️ Verification found {X} issues

**Critical**:
1. Missing access rights for {model}
2. Invalid field reference: {field}

**Warnings**:
1. Using <tree> instead of <list>

Options:
a) Fix automatically (recommended)
b) Review issues manually
c) Skip and proceed (not recommended)

Choose (a/b/c): ───────► [Wait for user]
```

### User Changes Architecture

If user requests changes during approval:

```
📐 Revised Architecture:
   [Updated proposal]

   Proceed with changes? ───────► [Wait for user]
```

### Unclear Requirements

If request is ambiguous:

```
❓ Need clarification:

Your request: "{user_request}"

Questions:
1. Should this be a new module or extend existing?
2. Which model should be the base?
3. Any specific dependencies?

Please provide details to proceed.
```

---

## Examples

### Example 1: Quick Mode

**User**: "Add notes field to res.partner"

**Response**:
```
🎯 Quick Mode: Adding field to existing model

💻 Developing...

📐 Architecture:
   Extend: res.partner (base module)
   Add field: notes (Text)
   Update: partner form view

   Proceed? y

✓ Implementing...
✓ Verifying... All passed!

✅ Complete! Field added in 5 minutes.
Install updates with: invoke restart
```

### Example 2: Full Mode

**User**: "Create equipment maintenance module with maintenance requests and schedules"

**Response**:
```
🎯 Full Mode: New module creation

🔍 Researching...
   Found related: maintenance.equipment, maintenance.team

📐 Architecture:
   Module: equipment_maintenance
   Models: 3
   - equipment_maintenance.request
   - equipment_maintenance.schedule
   - equipment_maintenance.log
   Dependencies: base, mail, maintenance

   [Detailed architecture...]

   Proceed? y

💻 Implementing in phases...
   Phase 1: Models ✓
   Phase 2: Views ✓
   Phase 3: Security ✓

🧪 Verifying... 18/18 tests passed!

📚 Generate docs? y

📝 Documenting...

✅ Complete! Module ready in 24 minutes.
```

### Example 3: Search Mode

**User**: "What fields does sale.order have?"

**Response**:
```
🔍 Searching...

sale.order has 127 fields:

**Key Fields**:
- partner_id (Many2one → res.partner) - Customer
- order_line (One2many → sale.order.line) - Order lines
- amount_total (Monetary, computed) - Total amount
- state (Selection) - Status: draft/sent/sale/done/cancel
- date_order (Datetime) - Order date
- user_id (Many2one → res.users) - Salesperson

[Full list available via: uv run scripts/get_details.py model "sale.order"]

Query: 31ms
```

---

## Critical Rules

### Mode Detection
- **ALWAYS** detect mode automatically
- **NEVER** ask user which mode
- Can escalate quick → full if complexity discovered

### User Approval
- **ALWAYS** get approval on architecture
- **NEVER** proceed to implementation without approval
- Iterations OK during architecture phase

### Efficiency
- Quick mode: Minimal ceremony, fast execution
- Full mode: Thorough planning, clear phases
- Search mode: Instant answers

### Quality
- **ALWAYS** validate with indexer
- **NEVER** skip verification
- Auto-proceed only if verification passes

### Progress
- **ALWAYS** show what you're doing
- Use progress indicators
- Clear status at each step

---

## Workflow State (Optional)

For complex features, you can track state in `specs/.dev-state.json`:

```json
{
  "task": "equipment_maintenance module",
  "mode": "full",
  "current_phase": "implementation",
  "module_name": "equipment_maintenance",
  "progress": {
    "architecture": "approved",
    "implementation": "in_progress",
    "verification": "pending",
    "documentation": "pending"
  }
}
```

This allows resuming if interrupted.

---

## Success Criteria

### Quick Mode Success
- Architecture approved (1 approval)
- Implementation complete
- Verification passed
- Total time: <10 minutes

### Full Mode Success
- Architecture approved (1 approval)
- All phases implemented
- Verification passed
- Documentation complete (if requested)
- Total time: <30 minutes

### Search Mode Success
- Query answered accurately
- Results from indexer
- Total time: <5 seconds

---

**Remember**: The goal is to make development feel seamless. Auto-detect mode, minimize approvals, maximize automation, maintain quality!
