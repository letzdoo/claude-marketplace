# Odoo Design Patterns - Anti-Pattern Learning System

Specialized learning system for Odoo/doodba development that captures **what doesn't work** and **how it was fixed**. Focus on generalized patterns to avoid repeating the same mistakes across projects.

## 🎯 Philosophy

**"What works works" - we don't need to learn from those.**

This system captures:
- ❌ What **doesn't work** in Odoo (anti-patterns)
- 🔍 **Why** it doesn't work (root cause)
- ✅ How it was **fixed** (solution pattern)
- 👁️ How to **recognize** similar issues

**Goal**: Build institutional knowledge of Odoo/doodba best practices that transfers across projects.

## 🎯 Overview

Odoo Design Patterns creates a learning loop specifically for Odoo development:

1. **Retrieves** relevant anti-patterns before starting Odoo tasks
2. **Judges** whether your fix actually solved the problem
3. **Distills** GENERALIZED patterns (not specific code) from failures
4. **Categorizes** by Odoo domain (ORM, security, views, tests, etc.)
5. **Consolidates** to maintain high-quality, contradiction-free pattern database
6. **Scales** using MaTTS for complex architecture and performance issues

## 🚀 Quick Start

### Installation

```bash
# Navigate to skill directory
cd odoo-doodba-dev/skills/reasoningbank

# Install dependencies
uv sync

# Set API keys
export ANTHROPIC_API_KEY="sk-..."
export VOYAGE_API_KEY="pa-..."  # For embeddings (voyage-3)

# Initialize database
uv run scripts/init_db.py
```

### Basic Usage

```bash
# Check Odoo pattern database status
uv run scripts/status.py

# Retrieve anti-patterns before implementing (avoid known pitfalls)
uv run scripts/retrieve.py "computed field performance" -k 5 --domain odoo.orm

# Judge if your fix solved the problem
uv run scripts/judge.py "fix N+1 query issue" trajectory.json

# Distill anti-pattern from failure (THIS IS THE KEY!)
uv run scripts/distill.py "fix ORM N+1 query" traj.json \
  --label Failure \
  --confidence 0.9 \
  --domain odoo.orm

# Consolidate pattern database
uv run scripts/consolidate.py

# Test-time scaling for complex Odoo architecture
uv run scripts/matts.py "refactor circular dependencies" --mode parallel -k 6
```

## 📋 Key Features

### 1. Odoo-Specific Pattern Retrieval

Finds relevant anti-patterns using **Voyage AI embeddings** (voyage-3, 1024 dimensions):
- **Domain-based**: odoo.orm, odoo.security, odoo.views, odoo.tests, etc.
- **Anti-pattern categories**: orm_misuse, security_holes, circular_deps, etc.
- **Failure boost**: Prioritizes patterns learned from failures (1.2x weight)
- **Semantic similarity** + **Recency** (90-day half-life for stable Odoo patterns)

**Note**: If `VOYAGE_API_KEY` is not set, falls back to deterministic hash-based embeddings for development/testing.

### 2. Anti-Pattern Detection (LLM-as-Judge)

Evaluates Odoo fixes without manual verification:
- Uses Claude with deterministic decoding
- Evaluates against Odoo best practices:
  - Follows Odoo guidelines?
  - Proper ORM usage?
  - Security best practices?
  - Test coverage?
  - Doodba compatibility?
- Returns Success/Failure with confidence score

### 3. Generalized Pattern Extraction

Extracts **principles**, not code:
- **Problem**: What didn't work (anti-pattern)
- **Why**: Root cause / Odoo principle violated
- **Fix**: How to solve properly
- **Recognition**: How to spot similar issues

**Avoids** capturing:
- Specific variable/module names
- Instance-specific details
- One-off solutions

**Focus on** generalizable patterns transferable across projects.

### 4. Odoo Domain Categorization

Organizes patterns by Odoo areas:
- **odoo.models**: Model design, inheritance, mixins
- **odoo.orm**: Search, recordsets, computed fields
- **odoo.security**: Access rights, record rules
- **odoo.views**: XML views, QWeb
- **odoo.tests**: Test isolation, mocking
- **odoo.deployment**: Doodba, docker, CI/CD
- **odoo.performance**: Query optimization
- **odoo.architecture**: Module structure, dependencies

### 5. Pattern Quality Management

Maintains high-quality, contradiction-free database:
- **Deduplication**: Merges similar anti-patterns (>87% similarity)
- **Contradiction detection**: Flags conflicting advice
- **Odoo version tracking**: Patterns may be version-specific
- **Longer retention**: 365-day pruning (Odoo patterns stay relevant)

### 6. MaTTS for Complex Odoo Problems

**Parallel Mode**: Explore multiple approaches to complex issues
- Useful for: Architecture refactoring, performance optimization
- Aggregates best fix patterns from multiple attempts

**Sequential Mode**: Iteratively refine Odoo design
- Useful for: Module restructuring, test suite design
- Progressively improves architecture

## 🏗️ Architecture

```
┌─────────────────┐
│  Pre-Task Hook  │
│  Retrieve k     │
│  memories       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute Task   │
│  with memories  │
│  in context     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Post-Task Hook  │
│ 1. Judge        │
│ 2. Distill      │
│ 3. Upsert       │
│ 4. Consolidate  │
└─────────────────┘
```

## 📊 Database Schema

### Tables

- **patterns**: Reasoning memories with metadata
- **pattern_embeddings**: Semantic vectors (1024-dim)
- **pattern_links**: Relationships (duplicates, contradictions)
- **task_trajectories**: Task execution history
- **matts_runs**: Test-time scaling runs
- **events**: Audit trail
- **performance_metrics**: Analytics

### Odoo Pattern Structure

```json
{
  "id": "rm_01HZX...",
  "type": "odoo_antipattern",
  "pattern_data": {
    "title": "N+1 Query in Computed Field",
    "description": "Using search/browse in loop within computed field causes N+1 queries",
    "content": "Problem: Iterating recordset and calling search() for each record triggers separate SQL query per iteration.\n\nWhy: Odoo ORM doesn't batch these automatically, computed field iterates self.\n\nFix: Use read_group() for aggregations, or collect all IDs and search_read() once outside loop. For related fields, use proper field relation instead of compute.\n\nRecognition: @api.depends decorator + loop over self + search/browse inside loop.",
    "source": {
      "task_id": "task_fix_performance",
      "outcome": "Failure",  // The anti-pattern was a failure
      "judge_confidence": 0.90
    },
    "tags": ["performance", "orm", "computed_field"],
    "domain": "odoo.orm",
    "anti_pattern_category": "orm_misuse",
    "odoo_version": "16.0+"  // Applies to Odoo 16+
  },
  "confidence": 0.85,
  "usage_count": 23  // Helped 23 times!
}
```

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
reasoningbank:
  retrieve:
    k: 3                          # Memories to retrieve
    alpha: 0.65                   # Similarity weight
    beta: 0.15                    # Recency weight
    gamma: 0.20                   # Relevance weight
    delta: 0.10                   # Diversity penalty
    recency_half_life_days: 45
    embedding_model: "voyage-3"

  judge:
    model: "claude-sonnet-4-5-20250929"
    temperature: 0                # Deterministic

  distill:
    max_items_per_traj: 3
    redact_pii: true

  consolidate:
    run_every_new_items: 20       # Auto-consolidate threshold
    prune_age_days: 180

  matts:
    parallel_k: 6                 # Parallel attempts
    sequential_r: 3               # Refinement iterations
```

## 📖 Odoo-Specific Usage Examples

### Example 1: ORM Performance Anti-Pattern

```bash
# Problem: Computed field taking 30+ seconds
# What didn't work: search() in loop
# Fix: Used read_group()

cat > orm_antipattern.json <<EOF
{
  "steps": [
    "Implemented: for rec in self: rec.order_count = self.env['sale.order'].search_count([('partner_id', '=', rec.id)])",
    "Problem: 500 partners = 500 SQL queries, 30s load time",
    "Tried batching with _prefetch, still slow",
    "Fix: Used read_group([('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id']) - single query",
    "Result: 30s → 0.3s"
  ],
  "anti_pattern": "search/search_count in loop over self"
}
EOF

# Distill the generalized anti-pattern
uv run scripts/distill.py \
  "fix N+1 query in computed field" \
  orm_antipattern.json \
  --label Failure \
  --confidence 0.95 \
  --domain odoo.orm

# Pattern extracted will be:
# Problem: Search in loop = N+1 queries
# Why: Each iteration = separate SQL
# Fix: read_group or single search with 'in' operator
# Recognition: @api.depends + loop over self + search/browse
```

### Example 2: Security Anti-Pattern

```bash
# Problem: Used sudo() to "fix" access denied
# What didn't work: Hiding security issue with sudo()
# Fix: Proper record rules

cat > security_antipattern.json <<EOF
{
  "problem": "User got AccessError, added sudo() everywhere",
  "consequence": "Now all users can see all records - data leak!",
  "fix": "Created proper ir.rule with domain: [('user_id', '=', user.id)]",
  "lesson": "sudo() bypasses security completely, use record rules instead"
}
EOF

uv run scripts/distill.py \
  "fix security data leak from sudo abuse" \
  security_antipattern.json \
  --label Failure \
  --confidence 0.90 \
  --domain odoo.security
```

### Example 3: Test Isolation Anti-Pattern

```bash
# Problem: Tests pass individually, fail when run together
# What didn't work: Sharing class variables between tests
# Fix: Proper setUp/tearDown and transaction isolation

cat > test_antipattern.json <<EOF
{
  "problem": "TestA passes alone, TestB passes alone, together TestB fails",
  "cause": "TestA modified shared class variable, TestB assumed clean state",
  "fix": "Use self.env.cr.savepoint() or proper setUpClass/tearDown",
  "lesson": "Each test must be independent, no shared mutable state"
}
EOF

uv run scripts/distill.py \
  "fix test isolation failure" \
  test_antipattern.json \
  --label Failure \
  --confidence 0.85 \
  --domain odoo.tests
```

### Example 4: Retrieve Before Implementing

```bash
# Before adding computed field, check known pitfalls
uv run scripts/retrieve.py "computed field performance ORM" \
  -k 5 \
  --domain odoo.orm

# Before adding security, check anti-patterns
uv run scripts/retrieve.py "access rights sudo security" \
  -k 5 \
  --domain odoo.security
```

### Example 5: Complex Architecture Refactoring

```bash
# Circular dependency between modules - try multiple approaches
uv run scripts/matts.py \
  "refactor circular dependency sale stock modules" \
  --mode parallel \
  -k 6 \
  --domain odoo.architecture

# Explores: abstract module, event-driven, interface segregation, etc.
# Aggregates best approach into pattern
```

## 🔧 Command Reference

### Core Scripts

| Script | Purpose | Key Options |
|--------|---------|-------------|
| `init_db.py` | Initialize database | - |
| `status.py` | Show system status | `--json` |
| `retrieve.py` | Retrieve memories | `-k`, `--domain`, `--inject` |
| `judge.py` | Judge trajectory | `--json` |
| `distill.py` | Extract memories | `--label`, `--confidence` |
| `consolidate.py` | Maintain quality | `--json` |
| `matts.py` | Test-time scaling | `--mode`, `-k`, `-r` |
| `pre_hook.py` | Pre-task hook | `--inject-only` |
| `post_hook.py` | Post-task hook | `--skip-consolidate` |

### Entry Points (via `uv run`)

All scripts can be run with `uv run scripts/<name>.py` or via the shortcuts defined in `pyproject.toml`:

```bash
rb-retrieve      # scripts.retrieve:main
rb-judge         # scripts.judge:main
rb-distill       # scripts.distill:main
rb-consolidate   # scripts.consolidate:main
rb-matts         # scripts.matts:main
rb-pre-hook      # scripts.pre_hook:main
rb-post-hook     # scripts.post_hook:main
rb-init-db       # scripts.init_db:main
rb-status        # scripts.status:main
```

## 📈 Monitoring & Metrics

View system performance:

```bash
uv run scripts/status.py
```

Output:
```
ReasoningBank Status
============================================================

Database: /home/user/.reasoningbank/memory.db
Size: 2.34 MB

Memories: 42
Trajectories: 128
Success Rate: 73.4%
Average Confidence: 0.68

Top Memories (by usage):
  1. Handle CSRF tokens in login forms
     Used: 23 times
  2. Implement OAuth redirect flow
     Used: 18 times
  ...
```

## 🧪 Testing

### Unit Tests

```bash
cd odoo-doodba-dev/skills/reasoningbank
python -m pytest tests/
```

### Integration Test

```bash
# Initialize
uv run scripts/init_db.py

# Create test trajectory
cat > test_traj.json <<EOF
{
  "steps": ["step1", "step2", "step3"],
  "result": "success"
}
EOF

# Full cycle
uv run scripts/distill.py "test task" test_traj.json --label Success --confidence 0.9
uv run scripts/retrieve.py "test task" -k 3
uv run scripts/consolidate.py
uv run scripts/status.py
```

## 🔒 Security & Privacy

### PII Redaction

Automatically redacts:
- Email addresses
- Phone numbers
- SSNs
- Credit cards
- IP addresses
- API keys/tokens
- UUIDs
- URLs (partial)

Configure in `config.yaml`:
```yaml
distill:
  redact_pii: true
```

### Multi-Tenancy

Supports tenant isolation:
```python
await retrieve_memories(query, tenant_id="org_123")
```

## 🛠️ Troubleshooting

### Database not found

```bash
uv run scripts/init_db.py
```

### API key not set

```bash
export ANTHROPIC_API_KEY="sk-..."
```

### No memories retrieved

- Database may be empty (no trajectories processed yet)
- Try broader query terms
- Check status: `uv run scripts/status.py`

### Low success rate

1. Run consolidation: `uv run scripts/consolidate.py`
2. Use MaTTS for hard tasks: `--mode parallel -k 6`
3. Check memory quality in status

## 📚 Odoo Anti-Patterns to Build

Start building your pattern database with these common categories:

### ORM Anti-Patterns
- N+1 queries in computed fields, views, reports
- Using search() when search_read() would suffice
- Not using read_group() for aggregations
- Creating records in loops instead of batch create()
- Modifying self outside safe contexts

### Security Anti-Patterns
- Using sudo() to bypass access checks
- Missing record rules (ir.rule)
- Overly permissive access rights
- Not validating user input in controllers
- Exposing sensitive fields without groups

### Testing Anti-Patterns
- Tests sharing state via class variables
- Missing transaction rollback
- Not mocking external APIs
- Hardcoded IDs that break in different DBs
- Not testing with different user groups

### Architecture Anti-Patterns
- Circular module dependencies
- Tight coupling (importing from other modules)
- Monolithic models (too many responsibilities)
- Missing abstract modules for shared logic
- Wrong dependency direction (base depends on specific)

### XML/View Anti-Patterns
- Brittle XPath expressions (position="replace")
- Hardcoded external IDs
- Not using proper view inheritance
- Missing security groups on sensitive views
- Complex business logic in QWeb

### Performance Anti-Patterns
- Missing database indexes on searched fields
- Computed fields without store=True
- Loading full recordsets when filtering needed
- Not using SQL for bulk operations
- Unnecessary sudo() calls (performance overhead)

### Doodba/Deployment Anti-Patterns
- Module not in requirements.txt
- Wrong addon path configuration
- Not using proper git-aggregator
- Missing dependencies in __manifest__.py
- Hardcoded paths not container-compatible

## 🎯 Pattern Learning Best Practices

1. **Focus on Failures** - Success stories don't teach us much
2. **Generalize Aggressively** - Principles, not code snippets
3. **Always Include "Why"** - Root cause, not just symptoms
4. **Tag Properly** - Use correct domain and anti-pattern category
5. **Include Recognition** - How to spot similar issues
6. **Version Awareness** - Note if pattern is version-specific
7. **Doodba Context** - Include deployment context when relevant
8. **Consolidate Regularly** - Keep database clean
9. **Retrieve Before Implementing** - Check anti-patterns first
10. **Post-Mortem Every Fix** - Always distill the pattern

## 📚 Foundation

Based on **ReasoningBank** research, specialized for Odoo development:
- Learns from failures (anti-patterns)
- LLM-as-judge for fix validation
- Generalized pattern extraction
- Domain-specific categorization (Odoo modules/areas)
- Long-term pattern retention (365 days)

Specialized for:
- Odoo framework patterns
- Doodba deployment context
- ORM best practices
- Security patterns
- Testing strategies

## 🤝 Contributing

This is part of the Claude marketplace odoo-doodba-dev plugin.

## 📄 License

MIT License - See LICENSE file

---

## 🎯 Remember: Learning from Mistakes

**"What works works" - we don't capture those.**

We capture:
- ❌ What **doesn't work**
- 🔍 **Why** it doesn't work
- ✅ How it was **fixed**
- 👁️ How to **recognize** similar issues

Every Odoo developer makes similar mistakes. **Capture them once, avoid them forever.**

Build institutional knowledge that transfers across projects and teams!
