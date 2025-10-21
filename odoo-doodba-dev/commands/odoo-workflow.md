---
name: odoo-workflow
description: Orchestrate multi-stage Odoo development with human-in-the-loop checkpoints
---

# Odoo Development Workflow Orchestration

This command helps you orchestrate the full Odoo development lifecycle with clear human approval checkpoints between stages.

## Overview

The Odoo development workflow consists of 5 distinct stages, each handled by a specialized agent:

```
User Request
    ↓
[1] ANALYSIS → SPEC.md → ✓ User Approval
    ↓
[2] IMPLEMENTATION → Code Files → ✓ User Approval
    ↓
[3] VALIDATION → VALIDATION.md → ✓ User Approval
    ↓
[4] TESTING → Tests + REPORT.md → ✓ User Approval
    ↓
[5] DOCUMENTATION → Docs → ✓ Final Approval
    ↓
COMPLETE
```

## Your Role as Orchestrator

As the main Claude CLI agent, you are responsible for:

1. **Understanding** the user's Odoo development request
2. **Creating** the `specs/` directory if it doesn't exist
3. **Invoking** the appropriate specialized agent for each stage
4. **Waiting** for explicit user approval before proceeding to next stage
5. **Managing** state between stages using `.workflow-state.json`
6. **Handling** iterations when user requests changes

## Workflow Stages

### Stage 1: Analysis & Planning

**Agent**: `odoo-analyst`
**Input**: User's feature request
**Output**: `specs/SPEC-{feature-name}.md`

**What to do**:
1. Create `specs/` directory if needed:
   ```bash
   mkdir -p specs
   ```

2. Invoke the analyst agent:
   ```
   Task(
     subagent_type="odoo-analyst",
     description="Analyze Odoo feature requirements",
     prompt="Analyze the following Odoo development request and create a detailed specification:

     User Request: {user_request}

     Requirements:
     - Use the Odoo indexer extensively to validate all models, fields, and XML IDs
     - Research existing codebase for similar patterns
     - CRITICAL: Present module architecture proposal with options before completing spec
     - Wait for user approval on module granularity decision
     - Create complete specification in specs/SPEC-{feature-name}.md
     - Use the template from workflows/templates/SPEC-template.md
     - Validate all dependencies and references
     - Check Odoo version compatibility

     IMPORTANT: The analyst will pause to get approval on module architecture before finalizing the spec."
   )
   ```

3. **CRITICAL**: The analyst will present a **Module Architecture Proposal** with options:
   - Should it be a new module or extend existing?
   - Module naming and granularity
   - Pros/cons of different approaches

   **You MUST wait for the analyst to present this proposal, then get USER APPROVAL before the analyst continues.**

4. Once module architecture is approved, the analyst completes the specification

5. When spec is complete, review `specs/SPEC-{feature-name}.md`

6. **STOP and ask user**: "The specification is complete in `specs/SPEC-{feature-name}.md`. Please review:
   - Module architecture (approved earlier)
   - Data model design
   - Views and UI
   - Business logic
   - Security rules

   Would you like me to proceed with implementation or make changes?"

7. **DO NOT proceed** to stage 2 until user explicitly approves the full specification

---

### Stage 2: Implementation

**Agent**: `odoo-implementer`
**Input**: `specs/SPEC-{feature-name}.md` (approved)
**Output**: Complete module code

**What to do**:
1. Verify spec file exists and is approved

2. Invoke the implementer agent:
   ```
   Task(
     subagent_type="odoo-implementer",
     description="Implement Odoo module",
     prompt="Implement the Odoo module based on the approved specification:

     Specification File: specs/SPEC-{feature-name}.md

     Requirements:
     - Read and follow the specification exactly
     - Use the Odoo indexer to validate EVERY field and XML ID before using them
     - Create all module files (models, views, security, data, tests)
     - Follow Odoo 18 conventions (use <list> not <tree>)
     - Ensure all field naming follows conventions (_id for Many2one, _ids for Many2many/One2many)
     - Validate widget compatibility (no inline tree for many2many_tags)
     - Create clean, well-documented code

     CRITICAL: Validate with indexer before writing code to prevent errors."
   )
   ```

3. When agent completes, show the user which files were created

4. **STOP and ask user**: "I've implemented the module based on your specification. The following files were created: [list files]. Would you like to review the code before validation?"

5. **DO NOT proceed** to stage 3 until user approves

---

### Stage 3: Validation

**Agent**: `odoo-validator`
**Input**: Generated module code
**Output**: `specs/VALIDATION-{feature-name}.md`

**What to do**:
1. Verify module files exist

2. Invoke the validator agent:
   ```
   Task(
     subagent_type="odoo-validator",
     description="Validate Odoo module",
     prompt="Validate the implemented Odoo module:

     Module: {module_name}
     Location: odoo/custom/src/private/{module_name}

     Validation Steps:
     - Check module structure and manifest
     - Validate all model definitions
     - Validate all views (syntax, fields existence via indexer)
     - Validate security rules
     - Run static analysis (pylint/flake8)
     - Attempt module installation
     - Create validation report: specs/VALIDATION-{feature-name}.md

     Use the indexer to verify all references are correct."
   )
   ```

3. When agent completes, review `specs/VALIDATION-{feature-name}.md`

4. **STOP and ask user**:
   - If PASSED: "Validation passed! The module is ready for testing. Proceed?"
   - If FAILED: "Validation found {X} issues. Would you like me to fix them or would you prefer to review manually?"

5. **DO NOT proceed** to stage 4 until validation passes and user approves

---

### Stage 4: Testing

**Agent**: `odoo-tester`
**Input**: Validated module
**Output**: Test files + `specs/TEST-REPORT-{feature-name}.md`

**What to do**:
1. Verify module is installed successfully

2. Invoke the tester agent:
   ```
   Task(
     subagent_type="odoo-tester",
     description="Test Odoo module",
     prompt="Create and run comprehensive tests for the module:

     Module: {module_name}
     Specification: specs/SPEC-{feature-name}.md

     Testing Steps:
     - Create test file: tests/test_{model_name}.py
     - Implement tests for all features in specification
     - Test model creation, CRUD operations
     - Test computed fields and constraints
     - Test state transitions and workflows
     - Test security rules
     - Run test suite: invoke test --modules={module_name}
     - Create test report: specs/TEST-REPORT-{feature-name}.md

     Aim for high coverage of specification requirements."
   )
   ```

3. When agent completes, review `specs/TEST-REPORT-{feature-name}.md`

4. **STOP and ask user**:
   - If ALL PASSED: "All {X} tests passed! Ready for documentation?"
   - If SOME FAILED: "{X} tests failed. Would you like me to fix the issues or investigate manually?"

5. **DO NOT proceed** to stage 5 until all tests pass and user approves

---

### Stage 5: Documentation

**Agent**: `odoo-documenter`
**Input**: Working module with passing tests
**Output**: README.md, USER-GUIDE.md, DEVELOPER-GUIDE.md

**What to do**:
1. Verify all previous stages are complete

2. Invoke the documenter agent:
   ```
   Task(
     subagent_type="odoo-documenter",
     description="Document Odoo module",
     prompt="Create comprehensive documentation for the module:

     Module: {module_name}
     Specification: specs/SPEC-{feature-name}.md
     Test Report: specs/TEST-REPORT-{feature-name}.md

     Documentation to Create:
     - README.md: Overview, installation, features, license
     - USER-GUIDE.md: How to use the module (UI walkthrough)
     - DEVELOPER-GUIDE.md: Technical details, architecture, extension points

     Make it clear, complete, and useful for both users and developers."
   )
   ```

3. When agent completes, show user the generated documentation

4. **STOP and ask user**: "Documentation is complete! Please review:
   - README.md
   - USER-GUIDE.md (if applicable)
   - DEVELOPER-GUIDE.md (if applicable)

   Is this ready for final delivery?"

5. Wait for final approval

---

## State Management

### Workflow State Tracking

Create and maintain `specs/.workflow-state.json` to track progress:

```json
{
  "feature": "quality_project_task",
  "started": "2025-10-20T10:00:00Z",
  "current_stage": "implementation",
  "completed_stages": [
    {
      "stage": "analysis",
      "agent": "odoo-analyst",
      "completed": "2025-10-20T10:30:00Z",
      "artifacts": ["specs/SPEC-quality-project-task.md"],
      "approved": true,
      "approved_at": "2025-10-20T10:35:00Z"
    }
  ],
  "pending_stages": ["validation", "testing", "documentation"],
  "spec_file": "specs/SPEC-quality-project-task.md",
  "module_name": "quality_project_task",
  "module_path": "odoo/custom/src/private/quality_project_task"
}
```

**Update this file** after each stage completion and user approval.

### Agent Memory System (CRITICAL)

**Each agent automatically persists its findings in memory files** located at `specs/.agent-memory/`:

- `odoo-analyst-memory.json` - Analysis findings, model discoveries, architecture decisions
- `odoo-implementer-memory.json` - Implementation progress, files created, validation cache
- `odoo-validator-memory.json` - Validation results, issues found, fixes applied
- `odoo-tester-memory.json` - Test execution results, failures, coverage analysis
- `odoo-documenter-memory.json` - Documentation progress, sections completed

**Why Memory Matters:**

When you invoke an agent after a human-in-the-loop checkpoint, the agent will:
1. **Load its previous memory** to see what it already discovered/completed
2. **Continue from where it left off** instead of starting from scratch
3. **Avoid repeating work** (e.g., re-validating fields, re-analyzing models)
4. **Remember user decisions** (e.g., approved module architecture)

**As Orchestrator, you should:**
- Trust that agents will load their memory automatically
- Don't worry about repeating instructions the agent already completed
- If resuming after a pause, simply invoke the agent normally - it will check its memory
- Memory files are in JSON format and can be inspected if needed

**Example Scenario:**

```
Stage 1: Analysis
→ Analyst researches codebase, proposes module architecture
→ Analyst saves findings to memory
→ User reviews and approves architecture
→ [PAUSE - human checkpoint]

Stage 1 Continued: Analysis
→ Analyst loads memory, sees architecture was approved
→ Analyst continues with detailed spec creation (skips re-research)
→ Analyst saves updated memory with completed spec
```

This prevents agents from starting over and losing context between human checkpoints!

**Memory Cleanup (Optional):**

If starting a completely new feature, you may want to clear old memory files:

```bash
# Clear all agent memories
rm -f specs/.agent-memory/*.json

# Or clear specific agent memory
rm -f specs/.agent-memory/odoo-analyst-memory.json
```

Memory files are feature-specific, so they automatically get overwritten when working on a new feature with the same agent.

---

## Handling User Feedback

### Scenario 1: User wants changes during spec review

```
User: "The specification looks good but I want to add field X"

You:
1. Update the spec file OR re-run analyst with the change request
2. Ask user to review again
3. Wait for approval before proceeding
```

### Scenario 2: Validation fails

```
Validation Result: 5 errors found

You:
1. Show user the errors from VALIDATION-{feature}.md
2. Ask: "Would you like me to fix these automatically or review first?"
3. If user approves auto-fix:
   - Fix the issues
   - Re-run validator
4. If user wants to review:
   - Wait for user to make changes
   - Offer to re-run validator when ready
```

### Scenario 3: User wants to resume from a checkpoint

```
User: "Let's continue with testing"

You:
1. Check specs/.workflow-state.json
2. Verify previous stages are complete
3. Resume from the requested stage
4. Continue with normal flow
```

---

## Important Rules

### Always Wait for Approval
- **NEVER** automatically proceed to the next stage
- **ALWAYS** explicitly ask user for approval
- Use clear language: "Ready to proceed?" or "Should I continue?"

### Always Use Indexer
- Analyst uses indexer for discovery and validation
- Implementer uses indexer before writing any code
- Validator uses indexer for verification

### Save All Artifacts
- All specs go in `specs/` directory
- All reports go in `specs/` directory
- Use consistent naming: `SPEC-{feature}.md`, `VALIDATION-{feature}.md`, etc.

### Track State
- Update `.workflow-state.json` after each stage
- Record when user approves
- Track all generated artifacts

### Be Transparent
- Show user what files are being created
- Explain what each agent is doing
- Share results of each stage

### Handle Errors Gracefully
- If agent fails, explain what happened
- Offer to retry or troubleshoot
- Don't proceed to next stage if current stage failed

---

## Example Complete Workflow

```
User: "I need a quality check feature for project tasks"

Claude (You):
> I'll help you build this step-by-step using our Odoo development workflow.
> Let me start by analyzing your requirements and creating a detailed specification.

[Calls odoo-analyst agent]
[Agent creates specs/SPEC-quality-project-task.md]

> ✓ Specification complete: specs/SPEC-quality-project-task.md
>
> Summary:
> - New module: quality_project_task
> - Extends: project.task and project.task.type
> - Adds: Quality checks at task stage entry/exit
> - Dependencies: quality_control, project, hr_timesheet
>
> Please review the specification. Would you like me to proceed with implementation?

User: "Looks great, go ahead"

Claude (You):
> Proceeding with implementation...

[Calls odoo-implementer agent]
[Agent creates all module files]

> ✓ Implementation complete. Created files:
> - models/project_task.py
> - models/project_task_type.py
> - views/project_task_views.xml
> - security/ir.model.access.csv
> - tests/test_quality_project_task.py
>
> Would you like to review the code or proceed with validation?

User: "Validate it"

Claude (You):
> Running validation...

[Calls odoo-validator agent]
[Agent validates and installs module]

> ✓ Validation passed! No errors found.
> Module installed successfully.
>
> Ready to run tests?

User: "Yes"

Claude (You):
> Running comprehensive tests...

[Calls odoo-tester agent]
[Agent runs tests]

> ✓ All 8 tests passed! Success rate: 100%
> Test report: specs/TEST-REPORT-quality-project-task.md
>
> Ready to generate documentation?

User: "Yes please"

Claude (You):
> Generating documentation...

[Calls odoo-documenter agent]
[Agent creates docs]

> ✓ Documentation complete:
> - README.md
> - USER-GUIDE.md
> - DEVELOPER-GUIDE.md
>
> Your module is ready! All stages completed successfully.
```

---

## Quick Start for Common Scenarios

### New Feature Request
```
User: "I want to add [feature]"

Steps:
1. Create specs/ dir
2. Call odoo-analyst
3. Wait for approval
4. Call odoo-implementer
5. Wait for approval
6. Call odoo-validator
7. If pass → wait for approval → call odoo-tester
8. If all pass → wait for approval → call odoo-documenter
9. Final delivery
```

### Resume from Checkpoint
```
User: "Continue with testing"

Steps:
1. Read specs/.workflow-state.json
2. Verify previous stages complete
3. Call odoo-tester
4. Continue workflow
```

### Fix and Re-validate
```
User: "Fix the errors and re-validate"

Steps:
1. Review VALIDATION-{feature}.md
2. Fix issues
3. Call odoo-validator again
4. Continue workflow if pass
```

---

## Templates Available

All templates are in `workflows/templates/`:
- `SPEC-template.md` - Used by odoo-analyst
- `VALIDATION-template.md` - Used by odoo-validator
- `TEST-REPORT-template.md` - Used by odoo-tester

Agents should use these templates to maintain consistency.

---

## Summary

Your job as orchestrator is to:
1. ✅ Guide the user through the workflow
2. ✅ Call the right agent at the right time
3. ✅ Wait for approval at each checkpoint
4. ✅ Track state and artifacts
5. ✅ Handle errors and iterations gracefully
6. ✅ Deliver a complete, tested, documented module

Remember: **Human-in-the-loop is key**. Never skip approval steps!
