# Claude Memory Skill

> Persistent project memory for sharing context across agent sessions and subagents

## Overview

The **Claude Memory** skill solves a critical problem in AI-assisted development: **context loss across agent sessions and subagent transitions**. When working with Claude Code, especially with complex tasks that involve multiple subagents, important decisions, requirements, and context often get lost. This skill provides a persistent memory system to maintain continuity.

## The Problem

Without persistent memory:

1. **Subagents start fresh** - Each subagent launch loses previous context
2. **Session interruptions** - Resuming work requires re-explaining everything
3. **Repeated questions** - User must answer the same questions multiple times
4. **Lost decisions** - Architectural decisions made earlier are forgotten
5. **Context duplication** - Wasted time re-establishing context

## The Solution

With Claude Memory:

1. **Persistent storage** - Context survives across sessions and subagents
2. **Quick retrieval** - Fast search and retrieval of stored information
3. **Structured organization** - Categories and tags for easy filtering
4. **Project-scoped** - Each project has its own isolated memory
5. **Export/import** - Share context between team members or projects

## Quick Start

### Installation

The skill is automatically available when the `odoo-doodba-dev` plugin is installed. No additional setup required.

### Basic Usage

```bash
# Store a decision
python -m scripts.store "decision.auth.method" \
  "Using JWT tokens for authentication" \
  --category decision \
  --tags "authentication,security"

# Retrieve it later
python -m scripts.retrieve "decision.auth.method"

# Search for related information
python -m scripts.search "authentication"

# List all memories
python -m scripts.list_memory
```

## Core Features

### 1. Store Information

Store any project-related information with context:

```bash
python -m scripts.store <key> <value> \
  --category <category> \
  --context <additional-context> \
  --tags <tag1,tag2,tag3>
```

**Categories:**
- `decision` - Architectural/design decisions
- `requirement` - User requirements
- `finding` - Important discoveries
- `context` - General project context
- `error` - Error solutions
- `config` - Configuration details
- `todo` - Future work items
- `reference` - External references

### 2. Retrieve Information

Get specific information by key:

```bash
python -m scripts.retrieve "decision.db.schema"
```

### 3. Search

Search across all stored information:

```bash
# Full-text search
python -m scripts.search "database design"

# Filter by category
python -m scripts.search --category decision

# Filter by tags
python -m scripts.search --tags "database,performance"

# Combine filters
python -m scripts.search "optimization" --category finding --tags "performance"
```

### 4. List & Stats

View all stored information:

```bash
# List all items
python -m scripts.list_memory

# Show statistics
python -m scripts.list_memory --stats

# Filter by category
python -m scripts.list_memory --category requirement
```

### 5. Export & Import

Share or backup memory:

```bash
# Export to file
python -m scripts.export_memory --output project-memory.json --pretty

# Import from file
python -m scripts.import_memory project-memory.json

# Overwrite existing items
python -m scripts.import_memory project-memory.json --overwrite
```

### 6. Clear Memory

Clean up old information:

```bash
# Delete specific item
python -m scripts.clear --key "decision.old.approach"

# Clear by category
python -m scripts.clear --category "temp"

# Clear all (careful!)
python -m scripts.clear --all
```

## Usage Patterns

### Pattern 1: Project Initialization

Store initial project context:

```bash
# Project goals
python -m scripts.store "project.goal" \
  "Build a scalable e-commerce platform with real-time inventory" \
  --category context \
  --tags "goals,overview"

# Tech stack decisions
python -m scripts.store "decision.stack" \
  "Python/FastAPI backend, React frontend, PostgreSQL database" \
  --category decision \
  --tags "stack,architecture"

# Key requirements
python -m scripts.store "requirement.performance" \
  "API response time under 200ms, support 10k concurrent users" \
  --category requirement \
  --tags "performance,scalability"
```

### Pattern 2: Before Launching Subagent

Store context for the subagent:

```bash
python -m scripts.store "context.current.task" \
  "Implementing user authentication. Completed: JWT setup, password hashing. Next: email verification" \
  --category context \
  --tags "current,handoff,authentication"
```

### Pattern 3: After Receiving Subagent Results

Store findings from the subagent:

```bash
python -m scripts.store "finding.performance.bottleneck" \
  "Database queries in product listing are slow. Need to add indexes on category_id and created_at" \
  --category finding \
  --tags "performance,database,optimization"
```

### Pattern 4: Session Resume

Retrieve context at session start:

```bash
# Get current task
python -m scripts.retrieve "context.current.task"

# Get recent decisions
python -m scripts.search --category decision --limit 10

# Get pending items
python -m scripts.search --category todo
```

### Pattern 5: Error Documentation

Store solutions to errors:

```bash
python -m scripts.store "error.cors.nginx" \
  "CORS errors resolved by adding 'add_header Access-Control-Allow-Origin *' in nginx.conf" \
  --category error \
  --context "Error occurred when frontend tried to call API from different domain" \
  --tags "cors,nginx,troubleshooting"
```

## Integration with Claude Agents

The skill is designed to work seamlessly with Claude agents:

### Auto-Trigger Behavior

Claude automatically uses this skill when:
- Starting a new task (retrieves relevant context)
- User says "remember this" or "keep track of"
- Before launching a subagent (stores context)
- After receiving important information (stores findings)

### Manual Invocation

You can also explicitly ask Claude to use memory:

- "Remember that we decided to use PostgreSQL"
- "What did we decide about authentication?"
- "Show me all decisions we made"
- "Store this requirement for later"

## Advanced Features

### JSON Output

All commands support `--json` for programmatic access:

```bash
python -m scripts.search "authentication" --json | jq '.results[0].value'
```

### Environment Variables

Customize behavior with environment variables:

```bash
# Custom database location
export CLAUDE_MEMORY_DB_PATH="/shared/project-memory.sqlite3"

# Custom project path
export CLAUDE_PROJECT_PATH="/path/to/project"

# Max search results
export CLAUDE_MEMORY_MAX_RESULTS=100
```

### Shell Wrappers

Create convenient shell aliases:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias mem-store='python -m scripts.store'
alias mem-get='python -m scripts.retrieve'
alias mem-find='python -m scripts.search'
alias mem-list='python -m scripts.list_memory'
```

## Best Practices

### 1. Use Hierarchical Keys

Use dot notation for organization:

```bash
decision.auth.method
decision.auth.provider
decision.db.schema
decision.db.migrations
```

### 2. Always Add Context

Explain WHY, not just WHAT:

```bash
# Good
python -m scripts.store "decision.db.postgres" \
  "Using PostgreSQL" \
  --context "Chose over MySQL for better JSON support and advanced indexing"

# Better
python -m scripts.store "decision.db.postgres" \
  "Using PostgreSQL instead of MySQL" \
  --context "Need JSON column support for flexible product attributes. Also requires advanced indexing (GiST, GIN) for spatial and full-text search"
```

### 3. Tag Generously

More tags = better searchability:

```bash
--tags "database,postgresql,architecture,decision,backend"
```

### 4. Regular Reviews

Periodically review stored memory:

```bash
# Monthly review
python -m scripts.list_memory --limit 100 > memory-review.txt
```

### 5. Export for Backups

Regular backups ensure data safety:

```bash
# Weekly backup
python -m scripts.export_memory --output "backups/memory-$(date +%Y%m%d).json"
```

## Technical Details

### Database

- **Storage**: SQLite database at `~/.claude-memory/project_memory.sqlite3`
- **Size**: ~1KB per memory item
- **Performance**: 2-50ms queries
- **Indexes**: Automatic on key, category, project_path, created_at

### Schema

```sql
memory_items:
  - id (PK)
  - key (unique per project)
  - value
  - context
  - category
  - project_path
  - tags (JSON array)
  - created_at
  - updated_at

memory_sessions:
  - session_id
  - project_path
  - started_at
  - last_accessed
```

### Project Scoping

Memory is automatically scoped to the project path. This prevents:
- Memory leakage between projects
- Namespace collisions
- Unrelated results in searches

## Troubleshooting

### Memory Not Found

Check which project you're in:

```bash
python -m scripts.list_memory --stats
```

### Slow Searches

- Use more specific queries
- Filter by category or tags
- Reduce limit with `--limit`

### Database Issues

Rebuild from backup:

```bash
# Export first
python -m scripts.export_memory --output backup.json

# Delete database
rm ~/.claude-memory/project_memory.sqlite3

# Reimport
python -m scripts.import_memory backup.json
```

## Examples

### Complete Feature Development

```bash
# 1. Start feature
python -m scripts.store "task.current" \
  "Implementing payment integration with Stripe" \
  --category context

# 2. Record decision
python -m scripts.store "decision.payment.provider" \
  "Using Stripe for payment processing" \
  --context "Evaluated Stripe, PayPal, and Square. Stripe has best API and webhook support" \
  --tags "payment,stripe,decision"

# 3. Record requirement
python -m scripts.store "requirement.payment.retry" \
  "Failed payments must retry 3 times with exponential backoff" \
  --category requirement \
  --tags "payment,reliability"

# 4. Launch subagent (context automatically stored)

# 5. Record finding from subagent
python -m scripts.store "finding.payment.webhook" \
  "Stripe webhooks require signature verification for security" \
  --category finding \
  --tags "payment,security,webhooks"

# 6. Complete feature
python -m scripts.store "context.payment.complete" \
  "Payment integration complete, tested with test cards" \
  --category context \
  --tags "complete"

# 7. Later retrieval
python -m scripts.search "payment" --json
```

## FAQ

**Q: Is memory shared between projects?**
A: No, memory is automatically scoped to the project path.

**Q: Can I share memory with team members?**
A: Yes, export the memory and share the JSON file, or use a shared database location.

**Q: How much data can I store?**
A: There's no hard limit, but keep values reasonably sized (under 10KB per item recommended).

**Q: Does memory expire?**
A: No, memory persists indefinitely unless explicitly deleted.

**Q: Can I edit stored memory?**
A: Yes, storing with the same key updates the value.

**Q: Is memory encrypted?**
A: No, use an encrypted filesystem if needed.

## Contributing

To improve this skill:

1. Add new scripts in `scripts/`
2. Update `SKILL.md` with new capabilities
3. Add tests for new features
4. Update this README

## License

Part of the `odoo-doodba-dev` plugin by Letzdoo.

---

**Remember**: Memory is meant to reduce friction and improve continuity. Use it liberally!
