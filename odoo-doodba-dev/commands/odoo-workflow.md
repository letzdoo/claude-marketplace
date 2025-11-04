---
description: Orchestrate multi-stage Odoo development with human-in-the-loop checkpoints
---

# Odoo Development Workflow

Orchestrate the full Odoo development lifecycle with approval checkpoints.

## Workflow

```
User Request
    ↓
[1] ANALYSIS → SPEC.md → ✓ Approval
    ↓
[2] IMPLEMENTATION → Code → ✓ Approval
    ↓
[3] VALIDATION → VALIDATION.md → ✓ Approval
    ↓
[4] TESTING → TEST-REPORT.md → ✓ Approval
    ↓
[5] DOCUMENTATION → Docs → ✓ Approval
```

## Your Role

1. Understand user's request
2. Create `specs/` directory: `mkdir -p specs`
3. Invoke appropriate agent for each stage
4. **Wait for explicit user approval** before proceeding
5. Handle iterations when user requests changes

---

## Stage 1: Analysis

**Agent**: odoo-analyst
**Output**: `specs/SPEC-{feature}.md`

```
Task(
  subagent_type="odoo-analyst",
  description="Analyze requirements",
  prompt="Analyze this Odoo feature request:

  {user_request}

  - Use indexer to validate all references
  - Research existing codebase
  - Present module architecture options
  - Get user approval on architecture
  - Create specification: specs/SPEC-{feature}.md"
)
```

**CRITICAL**: Analyst will present module architecture proposal. **Get user approval** before analyst finalizes spec.

**After completion**: "Specification complete in `specs/SPEC-{feature}.md`. Ready to implement?"

---

## Stage 2: Implementation

**Agent**: odoo-implementer
**Output**: Module code

```
Task(
  subagent_type="odoo-implementer",
  description="Implement module",
  prompt="Implement module from: specs/SPEC-{feature}.md

  - Validate ALL references with indexer before coding
  - Create all files (models, views, security, tests)
  - Follow Odoo 18 conventions (<list> not <tree>)
  - Ensure field naming conventions (_id, _ids)"
)
```

**After completion**: "Module implemented. Files created: [list]. Ready for validation?"

---

## Stage 3: Validation

**Agent**: odoo-validator
**Output**: `specs/VALIDATION-{feature}.md`

```
Task(
  subagent_type="odoo-validator",
  description="Validate module",
  prompt="Validate module: {module_name}
  Location: odoo/custom/src/private/{module_name}

  - Check structure, models, views, security
  - Validate with indexer
  - Attempt installation
  - Create report: specs/VALIDATION-{feature}.md"
)
```

**After completion**:
- If PASSED: "Validation passed! Ready for testing?"
- If FAILED: "Found {X} issues. Fix automatically or review manually?"

---

## Stage 4: Testing

**Agent**: odoo-tester
**Output**: Test files + `specs/TEST-REPORT-{feature}.md`

```
Task(
  subagent_type="odoo-tester",
  description="Test module",
  prompt="Test module: {module_name}
  Specification: specs/SPEC-{feature}.md

  - Create comprehensive tests
  - Test CRUD, computed fields, constraints, workflows, security
  - Run: invoke test --modules={module_name}
  - Create report: specs/TEST-REPORT-{feature}.md"
)
```

**After completion**:
- If ALL PASSED: "All {X} tests passed! Ready for documentation?"
- If FAILED: "{X} tests failed. Fix issues or investigate manually?"

---

## Stage 5: Documentation

**Agent**: odoo-documenter
**Output**: README.md, USER-GUIDE.md, DEVELOPER-GUIDE.md

```
Task(
  subagent_type="odoo-documenter",
  description="Document module",
  prompt="Document module: {module_name}
  Spec: specs/SPEC-{feature}.md
  Tests: specs/TEST-REPORT-{feature}.md

  Create:
  - README.md: Overview, installation, features
  - USER-GUIDE.md: How to use (UI walkthrough)
  - DEVELOPER-GUIDE.md: Architecture, extension points"
)
```

**After completion**: "Documentation complete! Review and approve for final delivery?"

---

## State Management

Track progress in `specs/.workflow-state.json`:

```json
{
  "feature": "quality_project_task",
  "current_stage": "implementation",
  "completed_stages": ["analysis"],
  "module_name": "quality_project_task",
  "module_path": "odoo/custom/src/private/quality_project_task"
}
```

Update after each stage completion and approval.

---

## Handling Iterations

**User wants changes during spec review**:
1. Update spec or re-run analyst with changes
2. Get approval again

**Validation fails**:
1. Show errors from VALIDATION-{feature}.md
2. Ask: "Fix automatically or review manually?"
3. Re-run validator after fixes

**Resume from checkpoint**:
1. Check `.workflow-state.json`
2. Verify previous stages complete
3. Resume from requested stage

---

## Critical Rules

- **NEVER** automatically proceed to next stage
- **ALWAYS** wait for explicit user approval
- **ALWAYS** use indexer for validation
- Save all artifacts in `specs/`
- Update `.workflow-state.json` after each stage
- Handle errors gracefully - don't proceed if stage fails

---

## Example Flow

```
User: "Add quality checks to project tasks"

You: Analyzing requirements...
[Calls analyst]
→ "Spec complete: specs/SPEC-quality-project-task.md. Proceed?"

User: "Yes"

You: Implementing...
[Calls implementer]
→ "Code created. Ready for validation?"

User: "Yes"

You: Validating...
[Calls validator]
→ "✓ Passed! Ready for testing?"

User: "Yes"

You: Testing...
[Calls tester]
→ "✓ All 8 tests passed! Ready for docs?"

User: "Yes"

You: Generating docs...
[Calls documenter]
→ "✓ Documentation complete! Module ready."
```

---

## Templates

Available in `workflows/templates/`:
- `SPEC-template.md`
- `VALIDATION-template.md`
- `TEST-REPORT-template.md`

Agents use these for consistency.
