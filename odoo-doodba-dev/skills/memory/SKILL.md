---
name: Claude Memory
description: |
  Persistent project memory system for sharing context across agent sessions and subagents.

  **MANDATORY AUTO-TRIGGER RULES:**

  1. **At Session Start**: IMMEDIATELY retrieve relevant project memory when starting any task
  2. **Before Agent Transitions**: ALWAYS store important context before launching subagents
  3. **After Important Decisions**: STORE key decisions, requirements, and findings
  4. **When User Says**: "remember this", "keep track of", "note that", "for future reference"
  5. **Multi-Step Tasks**: Store context between steps to maintain continuity
  6. **Error Recovery**: Store error patterns and solutions for future reference

  **Auto-Trigger Keywords:**
  - Memory operations: "remember", "recall", "retrieve", "store", "save context"
  - Session context: "what did we decide", "previous decision", "earlier finding"
  - Task continuity: "continue from", "pick up where", "resume"
  - Knowledge sharing: "for next time", "future reference", "keep this"
  - Agent coordination: "pass to next agent", "share with team", "context handoff"

  **Critical Usage Patterns:**
  - Store architectural decisions with category="decision"
  - Store user requirements with category="requirement"
  - Store important findings with category="finding"
  - Store task context with category="context"
  - Always use tags for better searchability
  - Always provide context to explain why something is stored

allowed-tools: Read, Bash, Grep, Glob
---

# Claude Memory Skill

## Overview

The **Claude Memory** skill provides persistent storage for project context, decisions, and findings across different Claude agent sessions and subagents. This solves the problem of context loss when using subagents or when resuming work after interruptions.

## Core Capabilities

### 1. Store Memory

Store important information that should persist across sessions:

```bash
python -m scripts.store "decision.auth.method" "Using JWT tokens for authentication" \
  --category decision \
  --context "Discussed with team, chose JWT over sessions for scalability" \
  --tags "authentication,architecture,security"
```

### 2. Retrieve Memory

Retrieve specific memory items by key:

```bash
python -m scripts.retrieve "decision.auth.method"
```

### 3. Search Memory

Search across all stored memory:

```bash
# Search by query
python -m scripts.search "authentication"

# Filter by category
python -m scripts.search --category decision

# Filter by tags
python -m scripts.search --tags "security,architecture"
```

### 4. List Memory

List all stored memory items:

```bash
# List all items
python -m scripts.list_memory

# Show statistics
python -m scripts.list_memory --stats

# Filter by category
python -m scripts.list_memory --category requirement
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
python -m scripts.clear --key "decision.old.approach" --yes

# Clear by category
python -m scripts.clear --category "temp" --yes

# Clear all (use with caution!)
python -m scripts.clear --all --yes
```

## Memory Categories

Use these standard categories for consistency:

- **decision**: Architectural or design decisions
- **requirement**: User requirements and specifications
- **finding**: Important discoveries or insights
- **context**: General project context
- **error**: Error patterns and solutions
- **config**: Configuration decisions
- **todo**: Future work items
- **reference**: External references and documentation

## Usage Workflow

### At Session Start

```bash
# Retrieve all recent context
python -m scripts.list_memory --limit 20

# Search for specific topic
python -m scripts.search "database design"
```

### During Work

```bash
# Store important decisions
python -m scripts.store "decision.db.schema" \
  "Using PostgreSQL with TimescaleDB extension for time-series data" \
  --category decision \
  --tags "database,architecture"

# Store user requirements
python -m scripts.store "requirement.performance" \
  "API response time must be under 200ms for 95th percentile" \
  --category requirement \
  --tags "performance,api"
```

### Before Agent Transition

```bash
# Store current context for next agent
python -m scripts.store "context.current.task" \
  "Implementing user authentication flow, completed JWT setup, next: password reset" \
  --category context \
  --tags "current,handoff"
```

### Error Recovery

```bash
# Store error solution
python -m scripts.store "error.cors.solution" \
  "CORS issue resolved by adding Access-Control-Allow-Origin header in nginx config" \
  --category error \
  --tags "cors,nginx,troubleshooting"
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

### Complete Workflow Example

```bash
# Starting a new feature
python -m scripts.store "task.current" \
  "Implementing user profile page with avatar upload" \
  --category context

# Recording a decision
python -m scripts.store "decision.storage.avatar" \
  "Using AWS S3 for avatar storage, signed URLs for access" \
  --category decision \
  --context "Considered local storage but S3 provides better scalability" \
  --tags "storage,aws,avatars"

# Recording a requirement
python -m scripts.store "requirement.avatar.size" \
  "Avatar images must be square, 200x200 to 1000x1000 pixels, under 2MB" \
  --category requirement \
  --tags "avatars,validation"

# Later, retrieving context
python -m scripts.search "avatar" --category decision
python -m scripts.search "avatar" --category requirement

# Completing the task
python -m scripts.store "context.avatar.complete" \
  "Avatar upload feature completed, ready for review" \
  --category context \
  --tags "complete,review"
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
