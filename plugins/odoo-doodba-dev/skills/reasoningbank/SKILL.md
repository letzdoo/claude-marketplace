---
name: OdooPatterns
description: Odoo Design Patterns learning system. USE AUTOMATICALLY when encountering Odoo errors/bugs and after fixing them to capture anti-patterns. AUTO-TRIGGER on Odoo failures (ORM errors, security issues, test failures, performance problems). Focus on WHAT DOESN'T WORK and HOW IT WAS FIXED. Captures generalized patterns, not specific code. CRITICAL for avoiding repeated Odoo mistakes across projects.
allowed-tools: Bash, Read, Write
---

# Odoo Design Patterns Skill

**⚡ PROACTIVE USAGE**: Auto-use when encountering Odoo issues and after fixing them.

**Philosophy**: "What works works" - we capture what DOESN'T work and how it was FIXED.

Learning system specialized for Odoo/doodba anti-patterns and best practices.

---

## When to Auto-Use This Skill

✅ **Before Odoo implementation**: Retrieve anti-patterns to avoid
- Auto-use: `uv run scripts/retrieve.py "computed field ORM" -k 5 --domain odoo.orm`
- When: Starting new Odoo feature, model, security, view

✅ **After fixing Odoo bug**: Distill the anti-pattern
- Auto-use: `uv run scripts/distill.py "fix N+1 query" <trajectory> --label Failure --domain odoo.orm`
- When: Fixed ORM issue, security bug, test failure, performance problem

✅ **On Odoo errors**: Capture what didn't work
- Auto-use when: ORM errors, XML validation fails, AccessError, performance issues
- Extract: Problem → Why → Fix → Recognition

✅ **Complex architecture**: Test-time scaling
- Auto-use: `uv run scripts/matts.py "refactor circular deps" --mode parallel -k 6`
- When: Module refactoring, architecture changes

---

## Trigger Keywords - Odoo Specific

**Automatically use when encountering**:
- Odoo ORM errors (N+1, search in loop)
- Security issues (AccessError, sudo abuse)
- Test failures (isolation, transaction issues)
- Performance problems (slow queries, missing indexes)
- XML errors (XPath, inheritance)
- Architecture issues (circular deps, coupling)

**Automatically use when user mentions**:
- "anti-pattern", "pattern", "best practice"
- "Odoo guideline", "Odoo way"
- "why doesn't this work", "fix this bug"
- "avoid this mistake", "repeated error"
- "performance issue", "slow query"
- "security issue", "access denied"

---

## Prerequisites

This skill requires:
- Python 3.10+
- `uv` package manager
- Anthropic API key

**Setup**:

```bash
export ANTHROPIC_API_KEY="sk-..."
export VOYAGE_API_KEY="pa-..."  # For embeddings (voyage-3)
cd odoo-doodba-dev/skills/reasoningbank
uv sync
uv run scripts/init_db.py
```

---

## Core Operations

### 1. Retrieve Anti-Patterns

Find relevant Odoo anti-patterns to avoid:

```bash
uv run scripts/retrieve.py "computed field performance" -k 5 --domain odoo.orm
```

**Returns**:
- Top-k anti-patterns by score (similarity + recency + confidence)
- Pattern: Problem → Why → Fix → Recognition
- Usage statistics (how often pattern helped)

**Options**:
- `-k, --top-k`: Number of patterns (default: 5 for Odoo)
- `--domain`: Odoo domain (odoo.orm, odoo.security, etc.)
- `--json`: JSON output
- `--inject`: Format for system prompt injection

**Odoo Domains**:
- `odoo.orm` - ORM, search, recordsets, computed fields
- `odoo.security` - Access rights, record rules
- `odoo.views` - XML views, QWeb
- `odoo.tests` - Test isolation, mocking
- `odoo.architecture` - Module structure, dependencies
- `odoo.performance` - Query optimization
- `odoo.deployment` - Doodba, docker

**Performance**: <100ms

---

### 2. Judge Trajectories

Evaluate task outcomes:

```bash
uv run scripts/judge.py "fix bug" trajectory.json
```

**Returns**:
- Label: "Success" or "Failure"
- Confidence: 0-1
- Reasons: List of justifications

**Uses**: Claude as LLM-judge with deterministic decoding (temperature=0)

---

### 3. Distill Anti-Patterns

Extract GENERALIZED patterns from Odoo failures (this is the key!):

```bash
# From Odoo bug/issue - capture what DIDN'T work
uv run scripts/distill.py \
  "fix N+1 query in computed field" \
  trajectory.json \
  --label Failure \
  --confidence 0.9 \
  --domain odoo.orm

# From architecture issue
uv run scripts/distill.py \
  "fix circular dependency" \
  trajectory.json \
  --label Failure \
  --confidence 0.85 \
  --domain odoo.architecture
```

**Focuses on FAILURES** (anti-patterns):
- Problem: What didn't work
- Why: Root cause / Odoo principle violated
- Fix: How to solve properly
- Recognition: How to spot similar issues

**Automatically**:
- **Generalizes** (extracts principles, not specific code)
- Redacts instance-specific details (variable names, modules)
- Computes embeddings
- Tags by Odoo domain and anti-pattern category

**DO NOT capture**:
- Specific variable/module names
- Instance-specific solutions
- Success stories (what works works!)

---

### 4. Consolidate

Maintain memory quality:

```bash
uv run scripts/consolidate.py
```

**Actions**:
- **Deduplicates**: Merges similar memories (>87% similarity)
- **Detects contradictions**: Flags conflicting advice
- **Applies aging**: Decays confidence over time
- **Prunes**: Removes old unused low-confidence items

**Auto-runs**: Every N new items (configurable)

---

### 5. MaTTS (Test-Time Scaling)

Convert extra compute into better memories:

```bash
# Parallel: Run k attempts, aggregate insights
uv run scripts/matts.py "complex task" --mode parallel -k 6

# Sequential: Iteratively refine
uv run scripts/matts.py "complex task" --mode sequential -r 3
```

**Parallel Mode**:
1. Launches k independent rollouts
2. Judges each
3. Aggregates common success patterns
4. Extracts failure pitfalls
5. Creates high-quality distilled memories

**Sequential Mode**:
1. Runs initial attempt
2. Checks and corrects r times
3. Uses intermediate notes for extraction
4. Creates refined memories

---

## Configuration

Edit `config.yaml`:

```yaml
reasoningbank:
  retrieve:
    k: 3                          # Top-k to retrieve
    alpha: 0.65                   # Similarity weight
    beta: 0.15                    # Recency weight
    gamma: 0.20                   # Relevance weight
    delta: 0.10                   # Diversity penalty
    recency_half_life_days: 45
    duplicate_threshold: 0.87
    embedding_model: "voyage-3"

  judge:
    model: "claude-sonnet-4-5-20250929"
    temperature: 0
    max_tokens: 1024

  distill:
    max_items_per_traj: 3
    redact_pii: true
    model: "claude-sonnet-4-5-20250929"
    temperature: 0.3
    max_tokens: 2048

  consolidate:
    run_every_new_items: 20
    contradiction_threshold: 0.60
    prune_age_days: 180
    min_confidence_keep: 0.30
    dedup_threshold: 0.87

  matts:
    enabled: true
    parallel_k: 6
    sequential_r: 3

  database:
    path: "~/.reasoningbank/memory.db"

  learning:
    initial_confidence_success: 0.75
    initial_confidence_failure: 0.65
    learning_rate: 0.05
```

---

## Hooks Integration

### Pre-Task Hook

Retrieves memories before task execution:

```bash
uv run scripts/pre_hook.py \
  --task-id task_123 \
  --agent-id agent_main \
  --query "implement login" \
  --inject-only
```

Outputs system prompt preamble with relevant memories.

### Post-Task Hook

Learns from task execution:

```bash
uv run scripts/post_hook.py \
  --task-id task_123 \
  --agent-id agent_main \
  --query "implement login" \
  --trajectory trajectory.json
```

**Actions**:
1. Judges outcome
2. Distills memories
3. Upserts to database
4. Consolidates if threshold reached

---

## Memory Schema

```json
{
  "id": "rm_01HZX...",
  "type": "reasoning_memory",
  "pattern_data": {
    "title": "Handle CSRF tokens in forms",
    "description": "Always fetch and include CSRF token before POST.",
    "content": "1) Load page and parse CSRF. 2) Attach token to POST. 3) Retry once if 403.",
    "source": {
      "task_id": "task_...",
      "agent_id": "agent_web",
      "outcome": "Success",
      "judge_confidence": 0.85
    },
    "tags": ["web", "auth", "csrf"],
    "domain": "webarena.admin",
    "created_at": "2025-10-10T12:00:00Z"
  },
  "confidence": 0.76,
  "usage_count": 12,
  "last_used": "2025-11-17T10:30:00Z"
}
```

---

## Database Schema

**Tables**:
- `patterns`: Reasoning memories
- `pattern_embeddings`: Semantic vectors
- `pattern_links`: Relationships (duplicates, contradictions)
- `task_trajectories`: Task execution history
- `matts_runs`: Test-time scaling runs
- `events`: Audit trail
- `performance_metrics`: Analytics

**Location**: `~/.reasoningbank/memory.db`

---

## Performance Metrics

View status:

```bash
uv run scripts/status.py
```

**Shows**:
- Total memories
- Success rate over time
- Average confidence
- Top memories by usage
- Database size
- Configuration

---

## Algorithms

### Retrieval Scoring

```
score_i = α*sim_i + β*rec_i + γ*rel_i - δ*div_i

where:
  sim_i  = cosine(query, embedding_i)
  rec_i  = exp(-age_days / H)
  rel_i  = confidence_i * usage_boost_i
  div_i  = max similarity to already selected
```

Uses **MMR** (Maximal Marginal Relevance) for diversity.

### Confidence Updates

```
new_conf = clamp(
  old_conf + η * (success_delta),
  0, 1
)

where:
  η = 0.05 (learning rate)
  success_delta = +1.0 if cited and success
                  -0.5 if cited and failure
```

### Aging Decay

```
conf_t = conf_0 * exp(-age_days * ln(2) / H)

where H = half_life (45-90 days)
```

---

## Odoo-Specific Examples

### Example 1: ORM N+1 Anti-Pattern

```bash
# Problem: Computed field taking 30 seconds
# What didn't work: search() in loop
cat > traj.json <<EOF
{
  "steps": [
    "Implemented: for rec in self: rec.order_count = self.env['sale.order'].search_count([('partner_id', '=', rec.id)])",
    "Problem: 500 partners = 500 SQL queries, 30s load",
    "Fix: Used read_group() - single query",
    "Result: 30s → 0.3s"
  ],
  "anti_pattern": "search in loop causing N+1 queries"
}
EOF

# Distill the GENERALIZED anti-pattern
uv run scripts/distill.py \
  "fix N+1 query in computed field" \
  traj.json \
  --label Failure \
  --confidence 0.95 \
  --domain odoo.orm

# Pattern extracted:
# Problem: Using search/browse in loop over self
# Why: Each iteration triggers separate SQL query
# Fix: Use read_group() or single search with 'in' operator
# Recognition: @api.depends + loop over self + search/browse inside
```

### Example 2: Security sudo() Abuse Anti-Pattern

```bash
# Problem: Used sudo() to "fix" AccessError
cat > traj.json <<EOF
{
  "problem": "User got AccessError, added sudo() everywhere",
  "consequence": "All users can now see all records - data leak!",
  "fix": "Created proper ir.rule with domain filter",
  "lesson": "Never use sudo() as shortcut for access control"
}
EOF

# Extract security anti-pattern
uv run scripts/distill.py \
  "fix security data leak from sudo abuse" \
  traj.json \
  --label Failure \
  --confidence 0.90 \
  --domain odoo.security

# Pattern extracted:
# Problem: Using sudo() to bypass security instead of proper access rules
# Why: sudo() completely bypasses all security, creates data leaks
# Fix: Use ir.rule with proper domain, or grant appropriate access rights
# Recognition: sudo() used in business logic, not admin operations
```

### Example 3: Retrieval with Injection

```bash
# Retrieve memories
uv run scripts/retrieve.py \
  "implement OAuth authentication" \
  -k 3 \
  --inject

# Output (formatted for system prompt):
# Strategy memories you can optionally use:
#
# 1) [Title] Handle CSRF tokens in login forms
#    Steps: Load page and parse CSRF. Attach token to POST...
#
# 2) [Title] Implement OAuth redirect flow
#    Steps: 1) Generate state token. 2) Redirect to provider...
#
# 3) [Title] Store OAuth tokens securely
#    Steps: 1) Encrypt tokens. 2) Use httponly cookies...
```

### Example 4: Parallel MaTTS

```bash
# Run 6 parallel attempts
uv run scripts/matts.py \
  "solve algorithm challenge" \
  --mode parallel \
  -k 6

# Output:
# Launching 6 parallel rollouts...
# Judging trajectories...
# Results: 4 Success, 2 Failure
# Aggregating insights...
# Created 3 high-quality memories
```

---

## Best Practices for Odoo Pattern Learning

### 1. Retrieve Anti-Patterns Before Odoo Implementation

```bash
# Before adding computed field
uv run scripts/retrieve.py "computed field ORM performance" -k 5 --domain odoo.orm

# Before adding security
uv run scripts/retrieve.py "access rights security" -k 5 --domain odoo.security

# Before writing tests
uv run scripts/retrieve.py "test isolation" -k 5 --domain odoo.tests
```

### 2. ALWAYS Distill After Fixing Odoo Bugs

```bash
# After fixing any Odoo issue, capture the anti-pattern!
uv run scripts/distill.py \
  "fix <what-was-wrong>" \
  <trajectory> \
  --label Failure \
  --domain odoo.<appropriate-domain>
```

**Remember**: Focus on FAILURES, not successes!

### 3. Generalize, Don't Memorize

✅ **Good**: "Search in loops causes N+1, use read_group instead"
❌ **Bad**: "Changed line 42 in sale_order.py to use read_group"

Extract **principles**, not code snippets.

### 4. Always Tag by Odoo Domain

- `odoo.orm` - ORM issues
- `odoo.security` - Security issues
- `odoo.tests` - Test issues
- `odoo.views` - XML/view issues
- `odoo.architecture` - Module structure
- `odoo.performance` - Performance issues
- `odoo.deployment` - Doodba/docker issues

### 5. Consolidate Regularly

```bash
# Weekly or after fixing multiple bugs
uv run scripts/consolidate.py
```

### 6. Use MaTTS for Complex Architecture Problems

```bash
# When refactoring modules or fixing architecture
uv run scripts/matts.py "refactor circular deps" --mode parallel -k 6 --domain odoo.architecture
```

### 7. Monitor Pattern Database Quality

```bash
# Check pattern database status
uv run scripts/status.py

# Should see:
# - Patterns covering common Odoo anti-patterns
# - High usage count for useful patterns
# - Odoo-specific domains populated
```

### 8. Include Context in Patterns

Every pattern should have:
1. **Problem**: What didn't work
2. **Why**: Root cause / Odoo principle
3. **Fix**: Proper solution
4. **Recognition**: How to spot it

### 9. Build Institutional Knowledge

Goal: **Capture mistakes once, avoid them forever**

Every Odoo developer makes similar mistakes. Build a database that helps everyone.

---

## Troubleshooting

### Database Not Initialized

```bash
uv run scripts/init_db.py
```

### No Memories Retrieved

Possible causes:
- Empty database (no trajectories processed yet)
- Query too specific (try broader terms)
- All memories have low confidence (run consolidation)

### Low Success Rate

1. Check memory quality: `uv run scripts/status.py`
2. Run consolidation: `uv run scripts/consolidate.py`
3. Use MaTTS for hard tasks: `uv run scripts/matts.py ... -k 6`

### Slow Retrieval

- Reduce k: `-k 2`
- Prune database: `uv run scripts/consolidate.py`
- Check database size: `uv run scripts/status.py`

---

## Architecture

```
┌─────────────────────────────────────────┐
│           ReasoningBank                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐        ┌──────────┐      │
│  │ Retrieve │───────>│ Inject   │      │
│  │          │        │ Prompt   │      │
│  └──────────┘        └──────────┘      │
│       ▲                                 │
│       │                                 │
│       │              ┌──────────┐       │
│       └──────────────│  Memory  │       │
│                      │   Bank   │       │
│                      └──────────┘       │
│                           ▲             │
│                           │             │
│  ┌──────────┐        ┌───┴──────┐      │
│  │  Judge   │───────>│ Distill  │      │
│  │          │        │          │      │
│  └──────────┘        └──────────┘      │
│       ▲                    │            │
│       │                    │            │
│       │                    ▼            │
│  ┌────┴────┐        ┌──────────┐       │
│  │Trajectory│       │Consolidate│       │
│  │         │        │          │       │
│  └─────────┘        └──────────┘       │
│                                         │
└─────────────────────────────────────────┘
```

---

## Research Foundation

Based on **ReasoningBank** (arXiv:2501.xxxxx):
- Learns from both successes and failures
- Uses LLM-as-judge for outcome evaluation
- Retrieves memories via semantic similarity
- Implements MaTTS for test-time scaling
- Consolidates with deduplication and contradiction detection

---

## 🎯 Philosophy: Learning from Mistakes

**"What works works" - we don't capture those.**

Focus on:
- ❌ What **doesn't work** in Odoo
- 🔍 **Why** it doesn't work
- ✅ How it was **fixed**
- 👁️ How to **recognize** similar issues

**Every Odoo developer makes similar mistakes. Capture them once, avoid them forever.**

---

**Remember**: Odoo Design Patterns learns from FAILURES. Use it after every bug fix to build institutional knowledge that prevents repeated mistakes across projects!
