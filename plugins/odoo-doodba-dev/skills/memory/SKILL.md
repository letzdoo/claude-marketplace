---
name: Odoo Development Memory
description: |
  Persistent Odoo project memory system for tracking models, fields, views, constraints, and implementation decisions across agent sessions.

  **MANDATORY AUTO-TRIGGER RULES:**

  1. **At Session Start**: IMMEDIATELY get context summary (get_context.py) to understand Odoo project state
  2. **Before Agent Transitions**: ALWAYS store important context before launching subagents
  3. **After Important Decisions**: STORE key decisions about models, fields, views, security, and architecture
  4. **When User Says**: "remember this", "keep track of", "note that", "for future reference"
  5. **When User Asks**: "what's the status", "what have we decided", "what's the context"
  6. **Multi-Step Tasks**: Store context between steps to maintain continuity in Odoo development
  7. **Error Recovery**: Store Odoo-specific error patterns and solutions for future reference

  **Auto-Trigger Keywords:**
  - Context summary: "get context", "what's the status", "project state", "current situation", "where are we"
  - Memory operations: "remember", "recall", "retrieve", "store", "save context"
  - Session context: "what did we decide", "previous decision", "earlier finding"
  - Task continuity: "continue from", "pick up where", "resume"
  - Knowledge sharing: "for next time", "future reference", "keep this"
  - Agent coordination: "pass to next agent", "share with team", "context handoff"
  - Odoo-specific: "model design", "field structure", "view layout", "security rules", "module architecture"

  **Critical Usage Patterns for Odoo:**
  - Store model design decisions with category="model_design"
  - Store field configurations with category="field_config"
  - Store view and UI decisions with category="view_design"
  - Store security and access rules with category="security"
  - Store workflow and automation decisions with category="workflow"
  - Store user requirements with category="requirement"
  - Store important findings with category="finding"
  - Store task context with category="context"
  - Always use Odoo-specific tags (e.g., "model", "field", "view", "qweb", "wizard", "report")
  - Always provide context to explain why something is stored

allowed-tools: Read, Bash, Grep, Glob
---

# Odoo Development Memory Skill

## Overview

The **Odoo Development Memory** skill provides persistent storage for Odoo project context, model designs, field configurations, view layouts, security rules, and implementation decisions across different Claude agent sessions and subagents. This solves the problem of context loss when using subagents or when resuming Odoo development work after interruptions.

**Odoo-Specific Focus:**
- Track model designs (_name, _inherit, _inherits patterns)
- Document field configurations (Many2one, One2many, Many2many, computed fields)
- Store view and UI decisions (form, tree, kanban, qweb templates)
- Remember security configurations (record rules, access rights)
- Track workflow and automation logic (scheduled actions, server actions)
- Document controller routes and API endpoints
- Keep module dependency information
- Store user interaction patterns and Q&A context

## Core Capabilities

### 0. Get Context Summary (START HERE)

**ALWAYS use this first when starting a session or task** to get a coherent overview of the project state:

```bash
# Get a formatted context summary
python -m scripts.get_context

# Markdown format (better for LLMs)
python -m scripts.get_context --format markdown

# Recent changes only (last 7 days)
python -m scripts.get_context --days 7

# JSON format for programmatic use
python -m scripts.get_context --format json
```

This provides a structured, cache-friendly summary organized by Odoo-specific categories:
- **Model Design**: Model architecture decisions (_name, _inherit patterns)
- **Field Configuration**: Field type and relationship decisions
- **View Design**: UI/UX decisions for forms, trees, kanban, qweb
- **Security Rules**: Access rights and record rule decisions
- **Workflow & Automation**: Business logic, computed fields, scheduled actions
- **Requirements**: User stories and functional requirements
- **Current Context**: Active development tasks and progress
- **User Interactions**: Questions, clarifications, and decisions from user Q&A
- **Important Findings**: Discoveries about existing code and constraints
- **Known Issues & Solutions**: Odoo-specific error patterns and fixes
- **Module Dependencies**: Module relationships and dependencies
- **References**: Odoo documentation and external resources

### 1. Store Memory

Store important information that should persist across sessions:

```bash
# Example: Store a model design decision
python -m scripts.store "model.sale_order.extend" "Extended sale.order with custom_field for tracking special requirements" \
  --category model_design \
  --context "User requested tracking of special customer requirements per order" \
  --tags "model,sale,inheritance,extension"

# Example: Store a field configuration decision
python -m scripts.store "field.partner.custom_rating" "Added Many2one to custom rating model with required=True" \
  --category field_config \
  --context "Business rule: all partners must have a rating assigned" \
  --tags "field,partner,many2one,required,constraint"
```

### 2. Retrieve Memory

Retrieve specific memory items by key:

```bash
# Retrieve a model design decision
python -m scripts.retrieve "model.sale_order.extend"

# Retrieve a field configuration
python -m scripts.retrieve "field.partner.custom_rating"
```

### 3. Search Memory

Search across all stored memory:

```bash
# Search for model-related memories
python -m scripts.search "sale.order"

# Search for view designs
python -m scripts.search --category view_design

# Search by Odoo-specific tags
python -m scripts.search --tags "model,inheritance"

# Search for security configurations
python -m scripts.search --category security --tags "access,record_rule"
```

### 4. List Memory

List all stored memory items:

```bash
# List all items
python -m scripts.list_memory

# Show statistics
python -m scripts.list_memory --stats

# List all model design decisions
python -m scripts.list_memory --category model_design

# List all user interaction context
python -m scripts.list_memory --category user_interaction
```

### 5. Export/Import

Share memory between projects or backup:

```bash
# Export
python -m scripts.export_memory --output memory-backup.json --pretty

# Import
python -m scripts.import_memory memory-backup.json --overwrite
```

### 6. Clear Memory

Clean up old or irrelevant memory:

```bash
# Delete specific item
python -m scripts.clear --key "model.old.approach" --yes

# Clear temporary user interaction notes
python -m scripts.clear --category "temp" --yes

# Clear all (use with caution!)
python -m scripts.clear --all --yes
```

## Memory Categories for Odoo Development

Use these Odoo-specific categories for consistency:

- **model_design**: Model architecture decisions (_name, _inherit, _inherits, _description)
- **field_config**: Field type, relationships, and constraint decisions (Many2one, One2many, computed, related)
- **view_design**: View and UI layout decisions (form, tree, kanban, search, qweb templates)
- **security**: Security configurations (access rights, record rules, groups)
- **workflow**: Workflow and automation logic (scheduled actions, server actions, state machines)
- **requirement**: User requirements and functional specifications
- **user_interaction**: User questions, clarifications, and Q&A context
- **finding**: Important discoveries about existing Odoo code, modules, or constraints
- **context**: Current development task context and progress
- **error**: Odoo-specific error patterns and solutions
- **module_dependency**: Module dependencies and relationships
- **performance**: Performance optimization decisions
- **data_migration**: Data migration strategies and decisions
- **reference**: Odoo documentation and external references

## Usage Workflow for Odoo Development

### At Session Start

```bash
# Get complete context summary
python -m scripts.get_context --format markdown

# List recent Odoo development context
python -m scripts.list_memory --limit 20

# Search for specific model or module
python -m scripts.search "sale.order"
```

### During Odoo Development

```bash
# Store model design decision
python -m scripts.store "model.product.template.extend" \
  "Extended product.template with _inherit to add custom_category_id Many2one field" \
  --category model_design \
  --context "User needs custom product categorization beyond standard categories" \
  --tags "model,product,inheritance,many2one"

# Store field configuration decision
python -m scripts.store "field.sale_order.delivery_note" \
  "Added Text field 'delivery_note' with help text for special delivery instructions" \
  --category field_config \
  --context "Warehouse team requested per-order delivery notes field" \
  --tags "field,sale,text,delivery"

# Store view design decision
python -m scripts.store "view.partner.form.custom" \
  "Modified partner form view to add custom rating field in header after title" \
  --category view_design \
  --context "Rating should be prominently visible when viewing partner" \
  --tags "view,form,partner,xpath,inheritance"

# Store user requirement with Q&A context
python -m scripts.store "requirement.invoice.auto_validate" \
  "Auto-validate invoices when sale order is confirmed, but only for trusted customers" \
  --category requirement \
  --context "User clarified: trusted = has credit_limit > 10000 and no overdue invoices" \
  --tags "requirement,invoice,automation,workflow"

# Store user interaction/clarification
python -m scripts.store "interaction.user_q1.product_variant" \
  "Q: Should variant creation be automatic? A: Yes, auto-create variants based on attribute combinations" \
  --category user_interaction \
  --context "Critical decision: affects product configuration workflow" \
  --tags "qa,product,variant,automation"
```

### Before Agent Transition

```bash
# Store current context for next agent
python -m scripts.store "context.current.task" \
  "Implementing custom invoice validation workflow: completed model extension, next: add security rules" \
  --category context \
  --tags "current,handoff,invoice,workflow"
```

### Error Recovery

```bash
# Store Odoo-specific error solution
python -m scripts.store "error.constraint.unique_violation" \
  "PostgreSQL unique constraint violation: resolved by adding _sql_constraints to model for unique name per company" \
  --category error \
  --context "Error occurred in multi-company setup when creating duplicate records" \
  --tags "error,constraint,postgresql,multicompany"
```

## JSON Output

All commands support `--json` flag for programmatic usage:

```bash
python -m scripts.search "authentication" --json | jq '.results[0].value'
```

## Environment Variables

Configure the skill using environment variables:

- `CLAUDE_MEMORY_DB_PATH`: Custom database location (default: `~/.claude-memory/project_memory.sqlite3`)
- `CLAUDE_PROJECT_PATH`: Project path for scoping memory (default: current directory)
- `CLAUDE_MEMORY_MAX_RESULTS`: Maximum search results (default: 50)
- `CLAUDE_SESSION_ID`: Session identifier for tracking

## Database Schema

The skill uses SQLite with the following schema:

```sql
memory_items:
  - id: Primary key
  - key: Unique identifier (per project)
  - value: Memory content
  - context: Additional context
  - category: Memory category
  - project_path: Project this belongs to
  - tags: JSON array of tags
  - created_at: Creation timestamp
  - updated_at: Last update timestamp

memory_sessions:
  - session_id: Unique session identifier
  - project_path: Associated project
  - started_at: Session start time
  - last_accessed: Last access time
```

## Best Practices

1. **Use Descriptive Keys**: Use dot-notation for hierarchical keys (e.g., `decision.auth.method`)
2. **Always Add Context**: Explain WHY something is stored, not just WHAT
3. **Tag Generously**: Use multiple tags for better searchability
4. **Categorize Consistently**: Use standard categories for easier filtering
5. **Regular Cleanup**: Periodically review and clear outdated memory
6. **Export for Backups**: Regular exports ensure memory preservation

## Integration with Agents

### Developer Agent Pattern

```python
# At start of task
memory_items = search_memory(query="current task")
for item in memory_items:
    print(f"Recalled: {item['key']} = {item['value']}")

# During implementation
store_memory(
    key="decision.api.design",
    value="Using REST with JSON:API spec",
    category="decision",
    tags=["api", "architecture"]
)

# Before handing off
store_memory(
    key="context.handoff.verifier",
    value="Completed API endpoints, ready for testing",
    category="context",
    tags=["handoff", "testing"]
)
```

### Verifier Agent Pattern

```python
# Retrieve context from previous agent
context = retrieve_memory("context.handoff.verifier")

# Store test results
store_memory(
    key="finding.test.coverage",
    value="Test coverage at 87%, missing edge cases for error handling",
    category="finding",
    tags=["testing", "coverage"]
)
```

## Troubleshooting

### Memory Not Found

Check the project path:
```bash
python -m scripts.list_memory --stats
```

### Slow Searches

The database automatically creates indexes. For very large datasets, consider:
- Using more specific search queries
- Filtering by category
- Using tags instead of full-text search

### Database Corruption

Rebuild from export:
```bash
# Export first
python -m scripts.export_memory --output backup.json

# Delete database
rm ~/.claude-memory/project_memory.sqlite3

# Re-import
python -m scripts.import_memory backup.json --overwrite
```

## Examples

### Complete Odoo Development Workflow Example

```bash
# Starting a new Odoo feature
python -m scripts.store "task.current" \
  "Implementing custom purchase approval workflow with multi-level approval" \
  --category context

# Recording user interaction/requirement
python -m scripts.store "interaction.user_q1.approval_levels" \
  "Q: How many approval levels? A: 3 levels - Manager, Director, CFO based on amount thresholds" \
  --category user_interaction \
  --context "User clarified: <10k=Manager, <50k=Director, 50k+=CFO" \
  --tags "qa,requirement,approval,workflow"

# Recording a model design decision
python -m scripts.store "model.purchase_approval.new" \
  "Created new model purchase.approval with fields: order_id, approver_id, level, status, amount" \
  --category model_design \
  --context "Need to track approval history and current approval state per purchase order" \
  --tags "model,purchase,approval,workflow,newmodel"

# Recording a field configuration decision
python -m scripts.store "field.purchase_order.approval_state" \
  "Added Selection field 'approval_state' with states: draft, pending, approved, rejected" \
  --category field_config \
  --context "State machine to track overall approval status of purchase order" \
  --tags "field,purchase,selection,state,workflow"

# Recording a view design decision
python -m scripts.store "view.purchase_order.form_approval" \
  "Extended purchase.order form view with approval statusbar widget and One2many list of approvals" \
  --category view_design \
  --context "Users need to see approval history and current status at top of form" \
  --tags "view,form,purchase,statusbar,one2many"

# Recording security decision
python -m scripts.store "security.purchase_approval.rules" \
  "Added record rule: users can only approve if they match approver_id and order is in pending state" \
  --category security \
  --context "Security critical: prevent unauthorized approvals and approval of non-pending orders" \
  --tags "security,recordrule,purchase,approval"

# Later, retrieving context
python -m scripts.search "approval" --category model_design
python -m scripts.search "approval" --category user_interaction

# Completing the task
python -m scripts.store "context.approval.complete" \
  "Purchase approval workflow completed: model, fields, views, security, workflow logic all implemented" \
  --category context \
  --tags "complete,review,purchase,approval"
```

## Performance

- **Store operation**: ~5ms
- **Retrieve operation**: ~2ms
- **Search operation**: ~10-50ms depending on result count
- **Database size**: ~1KB per memory item
- **Concurrent access**: Thread-safe with SQLite locking

## Security Notes

- Memory is stored locally on the filesystem
- Database location can be configured for shared storage
- No encryption by default (use encrypted filesystem if needed)
- Project-scoped to prevent cross-contamination

---

**Remember**: The goal of this skill is to maintain continuity across sessions and agents. Use it liberally to store context, decisions, and findings. Over-storage is better than under-storage!
