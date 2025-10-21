# Agent Memory System

## Overview

The Odoo Doodba Dev workflow includes a **memory persistence system** that allows specialized agents to save their findings and progress between invocations. This is critical for human-in-the-loop workflows where agents need to pause and wait for user approval before continuing.

## Problem Solved

**Before Memory System:**
- Agent completes 50% of work, pauses for user approval
- After approval, agent is re-invoked
- Agent starts from scratch, repeating all previous work
- Wastes time, tokens, and may lose context

**With Memory System:**
- Agent completes 50% of work, saves findings to memory
- Pauses for user approval
- After approval, agent is re-invoked
- Agent loads memory, sees what's already done
- Agent continues from 50% mark, no repetition

## Architecture

### Memory Storage Location

All agent memory files are stored in:
```
specs/.agent-memory/
├── odoo-analyst-memory.json
├── odoo-implementer-memory.json
├── odoo-validator-memory.json
├── odoo-tester-memory.json
└── odoo-documenter-memory.json
```

### Agent Workflow

Each agent follows this pattern:

```
1. Agent invoked
2. ↓
3. Load memory (if exists)
   ├─ Memory exists → Load and review findings
   │  └─ Continue from where left off
   └─ No memory → Fresh start
4. ↓
5. Do work (research, implement, validate, test, document)
6. ↓
7. Save memory (with all findings and progress)
8. ↓
9. Return summary to orchestrator
```

## Memory File Formats

### odoo-analyst-memory.json

**Purpose**: Stores analysis findings, model discoveries, and architectural decisions

```json
{
  "agent": "odoo-analyst",
  "feature_name": "quality_project_task",
  "timestamp": "2025-10-21T10:30:00Z",
  "stage": "module_architecture_proposed|specification_creation|completed",
  "findings": {
    "odoo_version": "18.0",
    "user_requirements": "Brief summary",
    "models_discovered": [
      {
        "name": "project.task",
        "exists": true,
        "module": "project",
        "key_fields": ["name", "partner_id"],
        "decision": "extend"
      }
    ],
    "fields_validated": [
      {
        "model": "project.task",
        "field": "partner_id",
        "type": "Many2one",
        "comodel": "res.partner",
        "exists": true
      }
    ],
    "xml_ids_validated": [
      {
        "xmlid": "quality_control.test_type_passfail",
        "module": "quality_control",
        "exists": true
      }
    ],
    "module_architecture": {
      "proposed": true,
      "approved": false,
      "recommendation": "Create new module",
      "rationale": "Feature is independent...",
      "awaiting_user_approval": true
    },
    "dependencies": ["project", "quality_control"],
    "views_researched": [...],
    "spec_file": "specs/SPEC-quality-project-task.md"
  }
}
```

**Critical Fields:**
- `module_architecture.approved` - Did user approve the proposed architecture?
- `stage` - What phase is the agent in?
- `fields_validated` - Cache of indexer validations to avoid re-checking

### odoo-implementer-memory.json

**Purpose**: Tracks implementation progress and files created

```json
{
  "agent": "odoo-implementer",
  "feature_name": "quality_project_task",
  "module_name": "quality_project_task",
  "module_path": "odoo/custom/src/private/quality_project_task",
  "timestamp": "2025-10-21T11:00:00Z",
  "stage": "manifest_created|models_implemented|views_created|completed",
  "progress": {
    "module_structure_created": true,
    "manifest_created": true,
    "models_implemented": [
      {
        "model": "quality.check",
        "file": "models/quality_check.py",
        "status": "completed"
      }
    ],
    "models_extended": [...],
    "views_created": [...],
    "security_created": {...},
    "data_files_created": [...]
  },
  "validation_cache": {
    "fields_validated": [...],
    "xml_ids_validated": [...]
  }
}
```

**Critical Fields:**
- `progress.*` - What files/components have been created?
- `stage` - How far along is implementation?
- `validation_cache` - Avoid re-validating with indexer

### odoo-validator-memory.json

**Purpose**: Stores validation results and issues found

```json
{
  "agent": "odoo-validator",
  "feature_name": "quality_project_task",
  "module_name": "quality_project_task",
  "timestamp": "2025-10-21T12:00:00Z",
  "stage": "structure_validated|models_validated|installation_attempted|completed",
  "validation_results": {
    "structure_check": {"status": "pass", "issues": []},
    "models_validated": [...],
    "views_validated": [...],
    "installation": {
      "attempted": true,
      "success": false,
      "error": "Full error message",
      "fixes_applied": ["Fix description"]
    }
  },
  "issues_summary": {
    "critical": 2,
    "warnings": 5,
    "fixed": 1
  }
}
```

**Critical Fields:**
- `installation.success` - Did module install successfully?
- `issues_summary` - What problems were found?
- `validation_results.*` - Detailed results per component

### odoo-tester-memory.json

**Purpose**: Tracks test creation, execution, and results

```json
{
  "agent": "odoo-tester",
  "feature_name": "quality_project_task",
  "module_name": "quality_project_task",
  "timestamp": "2025-10-21T13:00:00Z",
  "stage": "tests_created|tests_running|tests_completed|fixing_failures",
  "test_progress": {
    "test_files_created": [...],
    "tests_implemented": [...],
    "test_runs": [
      {
        "run_number": 1,
        "total_tests": 8,
        "passed": 6,
        "failed": 2,
        "execution_time": "12.5s",
        "failures": [...]
      }
    ],
    "fixes_applied": [...]
  }
}
```

**Critical Fields:**
- `test_runs` - History of test executions
- `test_runs[].failures` - What tests failed and why?
- `fixes_applied` - What has been fixed?

### odoo-documenter-memory.json

**Purpose**: Tracks documentation progress and content gathered

```json
{
  "agent": "odoo-documenter",
  "feature_name": "quality_project_task",
  "module_name": "quality_project_task",
  "timestamp": "2025-10-21T14:00:00Z",
  "stage": "readme_created|user_guide_created|developer_guide_created|completed",
  "documentation_progress": {
    "files_created": [
      {
        "file": "README.md",
        "status": "completed",
        "sections": [...]
      }
    ],
    "content_gathered": {
      "from_spec": {...},
      "from_code": {...},
      "from_tests": {...}
    }
  }
}
```

## How Agents Use Memory

### Loading Memory (Step 0)

Every agent starts with:

```bash
# Check if memory exists
if [ -f "specs/.agent-memory/{agent-name}-memory.json" ]; then
    cat specs/.agent-memory/{agent-name}-memory.json
fi
```

**If memory exists:**
- Parse JSON and review all previous findings
- Identify what stage was reached
- Identify what work is complete
- **Skip completed work**
- Continue from where left off

**If memory doesn't exist:**
- Fresh start, no previous context
- Proceed normally from beginning

### Saving Memory (Before Completion)

Before returning final summary, agents save memory:

```bash
# Create directory if needed
mkdir -p specs/.agent-memory

# Save memory file
cat > specs/.agent-memory/{agent-name}-memory.json << 'EOF'
{
  "agent": "{agent-name}",
  "feature_name": "{feature_name}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "stage": "{current_stage}",
  ... (all findings as JSON)
}
EOF
```

**When to save:**
- Before pausing for user approval
- After completing major milestones
- Before returning final summary
- After any significant work that shouldn't be repeated

## Usage Examples

### Example 1: Analyst Pauses for Architecture Approval

```
User: "I want quality checks on project tasks"

Orchestrator invokes: odoo-analyst

Analyst:
1. Loads memory → None exists, fresh start
2. Detects Odoo version: 18.0
3. Researches models: project.task, quality_control.*
4. Validates fields with indexer (saves 50+ validations)
5. Proposes module architecture:
   - Option 1: New module (RECOMMENDED)
   - Option 2: Extend project module
6. SAVES MEMORY with:
   - All validated fields/models/XML IDs
   - Architecture proposal
   - stage: "module_architecture_proposed"
   - awaiting_user_approval: true
7. Returns summary to orchestrator

[PAUSE - WAITING FOR USER APPROVAL]

User: "Option 1 looks good, proceed"

Orchestrator invokes: odoo-analyst (again)

Analyst:
1. Loads memory → Exists!
2. Reads memory:
   - Architecture was proposed
   - User approved Option 1
   - 50+ fields already validated
   - Models already researched
3. SKIPS all research and validation (already done!)
4. Proceeds directly to creating detailed spec
5. SAVES MEMORY with:
   - Updated stage: "completed"
   - spec_file location
6. Returns final summary
```

**Without memory**: Agent would re-research everything, wasting 10+ minutes

**With memory**: Agent continues directly, saves 10+ minutes and thousands of tokens

### Example 2: Validator Finds Issues, Fixes Applied

```
Orchestrator invokes: odoo-validator

Validator:
1. Loads memory → None, fresh start
2. Validates module structure → PASS
3. Validates models → PASS
4. Validates views → 2 ERRORS found
5. Attempts installation → FAILS
6. SAVES MEMORY with:
   - validation_results (structure: pass, models: pass, views: fail)
   - issues_summary: critical=2
   - installation.success: false
   - installation.error: "Field 'invalid_field' does not exist"
7. Returns summary: "2 critical issues found"

[PAUSE - USER OR IMPLEMENTER FIXES ISSUES]

Orchestrator invokes: odoo-validator (again)

Validator:
1. Loads memory → Exists!
2. Reads memory:
   - Structure already validated (PASS)
   - Models already validated (PASS)
   - Views had issues
   - Installation failed
3. SKIPS structure and model validation (already passed!)
4. Re-validates only views → PASS (issues fixed)
5. Re-attempts installation → SUCCESS
6. SAVES MEMORY with:
   - Updated validation_results
   - installation.success: true
   - stage: "completed"
7. Returns: "All validations passed!"
```

### Example 3: Tester Retries Failed Tests

```
Orchestrator invokes: odoo-tester

Tester:
1. Loads memory → None, fresh start
2. Creates test file with 8 tests
3. Runs tests → 6 passed, 2 failed
4. SAVES MEMORY with:
   - test_runs[0]: 6/8 passed
   - failures: ["test_03_state_transitions", "test_05_security"]
5. Returns: "6/8 tests passed, 2 failures"

[PAUSE - FIXES APPLIED TO CODE OR TESTS]

Orchestrator invokes: odoo-tester (again)

Tester:
1. Loads memory → Exists!
2. Reads memory:
   - Tests already created
   - Previous run: 6/8 passed
   - Known failures: test_03, test_05
3. SKIPS test creation (already done!)
4. Re-runs tests → 8/8 passed!
5. SAVES MEMORY with:
   - test_runs[1]: 8/8 passed
   - stage: "completed"
6. Returns: "All 8 tests passed!"
```

## Memory Lifecycle

```
Project Start
    ↓
Create specs/.agent-memory/ directory
    ↓
[Agent 1: Analyst]
    ├─ No memory → Fresh start
    ├─ Do work → Save findings
    └─ Return summary
    ↓
[Human approval checkpoint]
    ↓
[Agent 1: Analyst] (continued)
    ├─ Load memory → Resume
    ├─ Do remaining work → Update memory
    └─ Return summary
    ↓
[Agent 2: Implementer]
    ├─ No memory → Fresh start
    ├─ Implement code → Save progress
    └─ Return summary
    ↓
[Continue through all agents...]
    ↓
Project Complete
    ↓
(Optional) Clean memory:
    rm -f specs/.agent-memory/*.json
```

## Benefits

1. **No Repeated Work**: Agents skip already-completed tasks
2. **Context Preservation**: Critical decisions (like approved architecture) are remembered
3. **Efficient Resumption**: After pauses, agents know exactly where they left off
4. **Validation Caching**: Expensive indexer checks are cached and reused
5. **Token Savings**: Dramatic reduction in repeated API calls and token usage
6. **Better UX**: Faster iterations, no frustrating "starting over" behavior

## Best Practices

### For Agent Developers

1. **Always load memory first** - Make it Step 0 in your workflow
2. **Save frequently** - Before any pause, after any milestone
3. **Use clear stage markers** - Makes it easy to know where to resume
4. **Cache expensive operations** - Validation results, API calls, etc.
5. **Include timestamps** - Helps debug and understand agent timeline
6. **Be detailed** - More context in memory = better resumption

### For Orchestrators

1. **Trust the memory system** - Agents will handle loading/saving
2. **Don't repeat context** - Agent already knows from memory
3. **Inspect memory when debugging** - Files are human-readable JSON
4. **Clean memory between projects** - Start fresh for new features

### For Users

1. **Memory is automatic** - Agents handle it, you don't need to worry
2. **Faster iterations** - Approvals and feedback loops are much faster
3. **Context is preserved** - Your decisions and approvals are remembered
4. **Transparent** - Memory files are in `specs/.agent-memory/` if you want to check

## Troubleshooting

### Agent starts over despite memory existing

**Check:**
1. Memory file exists: `ls specs/.agent-memory/`
2. Memory file is valid JSON: `cat specs/.agent-memory/{agent}-memory.json | jq .`
3. Agent is actually loading it (check agent prompts)

**Fix:**
- Verify agent prompt includes "Step 0: Load Previous Memory"
- Check for JSON syntax errors in memory file

### Memory file is corrupt or invalid

**Fix:**
```bash
# Delete corrupted memory
rm specs/.agent-memory/{agent}-memory.json

# Agent will start fresh on next invocation
```

### Memory from wrong feature/project

**Fix:**
```bash
# Clear all memories for fresh start
rm -f specs/.agent-memory/*.json
```

### Agent re-validates already validated items

This is expected behavior! Agents intentionally re-validate critical items even if cached, but they can skip expensive research steps.

## Technical Details

### Memory Format: JSON

- Human-readable and debuggable
- Easy to parse and manipulate
- Standard format across all agents

### Storage: File System

- Simple, no database needed
- Easy to inspect, backup, version control
- Located with project specs for co-location

### Persistence: Per-Agent

- Each agent has its own memory file
- No shared memory between agents (keeps it simple)
- Agents can reference each other's artifacts (e.g., spec files)

## Future Enhancements

Possible improvements:

1. **Memory versioning** - Track multiple versions of memory for rollback
2. **Memory compression** - For very large projects with lots of validations
3. **Memory sharing** - Allow agents to read each other's memories
4. **Memory expiration** - Auto-clean old memories after N days
5. **Memory visualization** - UI to inspect agent progress and findings

## Conclusion

The Agent Memory System is a critical feature that enables efficient human-in-the-loop workflows. By persisting findings between invocations, agents can resume work intelligently without starting from scratch, saving time, tokens, and frustration.

All agents in the Odoo Doodba Dev workflow now include memory persistence as a core feature. Use it, trust it, and enjoy faster, smarter development workflows!
