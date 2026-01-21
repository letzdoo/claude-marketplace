---
name: OdooPatterns
description: **AUTO-USE** Odoo Design Patterns learning system - captures what DOESN'T work in Odoo and how it was fixed. Use AUTOMATICALLY when encountering Odoo errors, after fixing Odoo issues, or when user mentions patterns, anti-patterns, or best practices. AUTO-TRIGGER on Odoo failures (ORM errors, security issues, test failures, XML errors, performance problems). Focus on GENERALIZED patterns, not specific solutions. Critical for avoiding repeated mistakes in Odoo/doodba development.
allowed-tools: Bash, Read
---

# Odoo Design Patterns Memory System

Specialized learning system that captures Odoo anti-patterns and their fixes. Focuses on **what doesn't work** and **how it was solved** to avoid repeating mistakes.

## Core Philosophy

**What works works** - We don't need to learn from those.
**What we capture**: Mistakes, anti-patterns, and their generalized solutions.
**Goal**: Build institutional knowledge of Odoo/doodba best practices.

## When to Auto-Use

✅ **On Odoo errors**: ORM errors, XML validation, security issues
✅ **After fixing bugs**: Extract the anti-pattern and solution
✅ **Test failures**: Capture testing patterns and isolation issues
✅ **Performance issues**: N+1 queries, inefficient searches
✅ **Architecture problems**: Circular deps, tight coupling
✅ **User mentions**: "pattern", "anti-pattern", "best practice", "Odoo guideline"

## Quick Start

### Check Pattern Database Status

```bash
cd odoo-doodba-dev/skills/reasoningbank
uv run scripts/status.py
```

### Initialize Database (First Time)

```bash
cd odoo-doodba-dev/skills/reasoningbank
uv run scripts/init_db.py
```

### Retrieve Odoo Patterns

```bash
# Find patterns related to ORM usage
uv run scripts/retrieve.py "ORM search inefficient" -k 5 --domain odoo.orm

# Find security-related patterns
uv run scripts/retrieve.py "security access rights" -k 5 --domain odoo.security
```

### Judge a Fix (Did it solve the problem?)

```bash
uv run scripts/judge.py "fix N+1 query in sale order" trajectory.json
```

### Distill Anti-Patterns from Failures

```bash
# Capture what DIDN'T work and how it was fixed
uv run scripts/distill.py "fix circular dependency" trajectory.json \
  --label Failure \
  --confidence 0.85 \
  --domain odoo.architecture
```

### Consolidate Pattern Database

```bash
# Deduplicate and clean up patterns
uv run scripts/consolidate.py
```

### Test-Time Scaling (For Complex Odoo Issues)

```bash
# Parallel mode - explore multiple approaches to complex Odoo problem
uv run scripts/matts.py "optimize sale order performance" --mode parallel -k 6

# Sequential mode - iteratively refine Odoo module design
uv run scripts/matts.py "refactor invoice workflow" --mode sequential -r 3
```

## Key Features

### 1. Odoo-Specific Pattern Retrieval
- Finds relevant anti-patterns and fixes for Odoo issues
- Categorized by domain: models, views, ORM, security, tests, etc.
- Prioritizes failure-derived patterns (what didn't work)
- Scores by similarity, recency, and fix effectiveness

### 2. Anti-Pattern Detection
- Automatically evaluates if issue follows known anti-patterns
- Detects common Odoo mistakes: ORM misuse, security holes, circular deps
- No manual pattern matching needed - uses LLM understanding

### 3. Generalized Pattern Extraction
- Extracts **principles**, not specific code
- Focuses on: What didn't work → Why → How it was fixed → How to recognize it
- Avoids capturing instance-specific details (variable names, module names)
- Creates reusable knowledge applicable across projects

### 4. Doodba Context Awareness
- Understands docker-compose, doodba environment
- Tracks deployment and testing patterns specific to doodba
- Captures CI/CD and migration issues in containerized context

### 5. Pattern Quality Management
- Deduplicates similar anti-patterns
- Detects contradictory advice
- Validates patterns work in current Odoo version
- Prunes outdated patterns

### 6. MaTTS for Complex Odoo Issues
- **Parallel**: Explore multiple fix approaches, find best pattern
- **Sequential**: Iteratively refine architecture/design
- Especially useful for performance and architecture problems

## How It Works

### Odoo Pattern Learning Loop

```
1. Encounter Odoo Issue (error, bug, performance problem)
   ↓
   Pre-Task: Retrieve similar anti-patterns
   ↓
2. Attempt Fix
   ↓
   Record what was tried, what failed, what worked
   ↓
3. Post-Task Analysis
   ↓
   Judge: Did fix solve the problem?
   ↓
   Distill: Extract GENERALIZED pattern
   - What didn't work initially (anti-pattern)
   - Why it didn't work (root cause)
   - How it was fixed (solution pattern)
   - How to recognize similar issues
   ↓
   Store in pattern database with Odoo domain tags
   ↓
   Consolidate (deduplicate, validate)
```

### Pattern Structure

Each Odoo pattern captures:
- **Title**: Anti-pattern name (e.g., "N+1 Query in Computed Field")
- **Description**: One-sentence problem statement
- **Content**: Generalized pattern in format:
  1. **Problem**: What didn't work
  2. **Why**: Root cause / Odoo principle violated
  3. **Fix**: How to solve it properly
  4. **Recognition**: How to spot similar issues
- **Domain**: Odoo area (odoo.orm, odoo.security, etc.)
- **Anti-Pattern Category**: orm_misuse, security_holes, etc.
- **Odoo Version**: Version context if relevant
- **Confidence**: How reliable this pattern is (0-1)
- **Usage Count**: How often pattern helped

## Configuration

Edit `skills/reasoningbank/config.yaml`:

```yaml
reasoningbank:
  odoo:
    focus: "design_patterns"
    capture_failures: true        # Emphasize anti-patterns
    generalization_level: "high"  # Generalized, not specific

    domains:  # Odoo-specific pattern categories
      - "odoo.models"
      - "odoo.views"
      - "odoo.orm"
      - "odoo.security"
      - "odoo.tests"
      # ... see config.yaml for full list

  retrieve:
    k: 5                          # More patterns for Odoo complexity
    recency_half_life_days: 90    # Odoo patterns stay relevant longer
    failure_boost: 1.2            # Prefer failure-derived patterns

  consolidate:
    run_every_new_items: 15       # More frequent consolidation
    prune_age_days: 365           # Keep stable Odoo patterns longer

  database:
    path: "~/.reasoningbank/odoo_patterns.db"  # Separate Odoo DB
```

## Environment Setup

Required:

```bash
export ANTHROPIC_API_KEY="sk-..."
export VOYAGE_API_KEY="pa-..."  # For embeddings (voyage-3)
```

Optional:

```bash
export REASONINGBANK_DB="~/.reasoningbank/memory.db"
```

**Note**: If `VOYAGE_API_KEY` is not set, the system will fall back to deterministic hash-based embeddings for development/testing.

## Odoo-Specific Examples

### Example 1: Capture ORM Anti-Pattern

```bash
# Problem: N+1 query in computed field was causing performance issues
# What didn't work: Using self.env['model'].search() in loop
# Fix: Used read_group or batch processing

cat > orm_antipattern.json <<EOF
{
  "steps": [
    "Tried: for rec in self: rec.field = self.env['sale.order'].search([('partner_id', '=', rec.id)])",
    "Problem: N+1 queries, 500+ SQL calls",
    "Fix: Used read_group to aggregate in single query",
    "Result: 1 SQL query, 100x faster"
  ]
}
EOF

# Distill the anti-pattern (focus on generalization!)
uv run scripts/distill.py \
  "fix N+1 query in computed field" \
  orm_antipattern.json \
  --label Failure \
  --confidence 0.9 \
  --domain odoo.orm

# Expected pattern extracted:
# Problem: Calling search/browse in loop for related records
# Why: Each iteration triggers separate SQL query
# Fix: Use read_group, or batch all IDs and search_read once
# Recognition: Computed fields iterating over recordsets
```

### Example 2: Security Anti-Pattern

```bash
# Problem: Security rule not applying, data leak
# What didn't work: Using sudo() in wrong place
# Fix: Proper record rules with domain

cat > security_issue.json <<EOF
{
  "problem": "Used sudo() to bypass access check, leaked data",
  "fix": "Created proper ir.rule with domain filter",
  "lesson": "Never use sudo() as shortcut, always use record rules"
}
EOF

uv run scripts/distill.py \
  "fix security data leak" \
  security_issue.json \
  --label Failure \
  --confidence 0.85 \
  --domain odoo.security
```

### Example 3: Test Isolation Issue

```bash
# Problem: Tests passing individually but failing together
# What didn't work: Sharing data between tests via class variables
# Fix: Use setUpClass for shared fixtures, proper tearDown

uv run scripts/distill.py \
  "fix test isolation issue" \
  test_failure.json \
  --label Failure \
  --confidence 0.8 \
  --domain odoo.tests
```

### Example 4: Retrieve Patterns Before Task

```bash
# Before implementing a new computed field, check for ORM anti-patterns
uv run scripts/retrieve.py "computed field performance" \
  -k 5 \
  --domain odoo.orm

# Before adding security, check known pitfalls
uv run scripts/retrieve.py "access rights record rules" \
  -k 5 \
  --domain odoo.security
```

### Example 5: Complex Architecture Problem with MaTTS

```bash
# Multiple approaches to refactoring circular dependencies
uv run scripts/matts.py \
  "refactor circular dependency between sale and stock modules" \
  --mode parallel \
  -k 6 \
  --domain odoo.architecture
```

## Performance Metrics

Tracked automatically:
- Success rate over time
- Average confidence
- Memory reuse frequency
- Retrieval latency
- Consolidation stats

View with:

```bash
uv run scripts/status.py
```

## Best Practices for Odoo Pattern Learning

1. **Capture Failures, Not Successes** - "What works works" - focus on mistakes and fixes
2. **Generalize, Don't Memorize** - Extract principles, not specific code snippets
3. **Always Tag by Domain** - Use odoo.orm, odoo.security, etc. for better retrieval
4. **Include Context**: What didn't work → Why → Fix → How to recognize
5. **Retrieve Before Implementation** - Check anti-patterns before starting
6. **Post-mortem After Fixes** - Always distill the pattern after solving issues
7. **Use MaTTS for Architecture** - Complex refactoring benefits from multiple approaches
8. **Consolidate Regularly** - Keep pattern database clean and contradiction-free
9. **Track Odoo Version** - Some patterns may be version-specific
10. **Doodba Context** - Include docker/deployment context when relevant

## Troubleshooting

### Database not found

```bash
cd odoo-doodba-dev/skills/reasoningbank
uv run scripts/init_db.py
```

### API key error

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Memory quality low

```bash
# Run consolidation to clean up
uv run scripts/consolidate.py
```

## Integration with Doodba Workflow

Odoo Patterns can be integrated into your doodba development workflow:

```yaml
# .claude/settings.json
{
  "hooks": {
    "preTaskHook": {
      "command": "uv",
      "args": ["run", "-m", "reasoningbank", "pre-hook", ...],
      "alwaysRun": true,
      "cwd": "odoo-doodba-dev/skills/reasoningbank"
    },
    "postTaskHook": {
      "command": "uv",
      "args": ["run", "-m", "reasoningbank", "post-hook", ...],
      "alwaysRun": true,
      "cwd": "odoo-doodba-dev/skills/reasoningbank"
    }
  }
}
```

## Common Odoo Anti-Patterns to Track

Build your pattern database with these categories:

### ORM Anti-Patterns
- N+1 queries in computed fields
- Using search in loops instead of batching
- Not using prefetch or read_group
- Modifying self in unsafe contexts

### Security Anti-Patterns
- Using sudo() as a shortcut
- Missing record rules
- Overly permissive access rights
- Not validating user input

### Testing Anti-Patterns
- Tests sharing state
- Missing transaction rollback
- Not mocking external calls
- Environment not properly reset

### Architecture Anti-Patterns
- Circular module dependencies
- Tight coupling between modules
- Monolithic models (God objects)
- Missing abstraction layers

### View/XML Anti-Patterns
- XPath expressions too brittle
- Hardcoded IDs in data files
- Not using proper inheritance
- Missing security groups in views

### Performance Anti-Patterns
- Not using database indexes
- Computed fields without store/depends
- Loading entire recordsets when filtering
- Not using SQL for bulk operations

---

## Philosophy: Learning from Mistakes

**The Pattern Database is not for what works - it's for what doesn't.**

- ✅ Capture: "Tried X, it failed because Y, fixed with Z"
- ❌ Don't capture: "Implemented feature X successfully"

**Generalization is key.**

- ✅ "Search in loops causes N+1, use read_group instead"
- ❌ "Changed line 42 in sale_order.py to use read_group"

**Build institutional knowledge that transfers across projects.**

Every Odoo developer makes similar mistakes. Capture them once, avoid them forever.

---

**Remember**: Focus on anti-patterns and their fixes. Every mistake captured makes the next Odoo project better!
