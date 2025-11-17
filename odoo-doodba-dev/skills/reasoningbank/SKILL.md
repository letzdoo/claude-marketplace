---
name: ReasoningBank
description: Adaptive learning memory system for Claude Code. USE AUTOMATICALLY before complex tasks to retrieve relevant past experiences and after task completion to distill new learnings. AUTO-TRIGGER when user mentions learning, improvement, memory, test-time scaling, or when facing repeated failures. CRITICAL for building institutional knowledge that improves performance over time. Learns from both successes and failures.
allowed-tools: Bash, Read, Write
---

# ReasoningBank Skill

**⚡ PROACTIVE USAGE**: Auto-use before complex multi-step tasks and after task completion.

Learning memory system that improves agent performance through experience.

---

## When to Auto-Use This Skill

✅ **Before complex tasks**: Retrieve relevant memories
- Auto-use: `uv run scripts/retrieve.py "<task_query>" -k 3 --inject`

✅ **After task completion**: Distill learnings
- Auto-use: `uv run scripts/post_hook.py --task-id <id> --query "<query>" --trajectory <file>`

✅ **On user request**: "learn from this", "remember this pattern"
- Auto-use: `uv run scripts/distill.py "<query>" <trajectory> --label Success`

✅ **For critical tasks**: Test-time scaling
- Auto-use: `uv run scripts/matts.py "<query>" --mode parallel -k 6`

---

## Trigger Keywords

**Automatically use when user mentions**:
- "learn from this"
- "remember this pattern"
- "improve performance"
- "test-time scaling"
- "why did this fail"
- "avoid this mistake"
- "similar to before"
- "past experience"

---

## Prerequisites

This skill requires:
- Python 3.10+
- `uv` package manager
- Anthropic API key

**Setup**:

```bash
export ANTHROPIC_API_KEY="sk-..."
cd odoo-doodba-dev/skills/reasoningbank
uv sync
uv run scripts/init_db.py
```

---

## Core Operations

### 1. Retrieve Memories

Find relevant past experiences:

```bash
uv run scripts/retrieve.py "implement authentication" -k 3
```

**Returns**:
- Top-k memories by score (similarity + recency + confidence)
- Memory titles and content
- Usage statistics

**Options**:
- `-k, --top-k`: Number of memories (default: 3)
- `--domain`: Filter by domain
- `--json`: JSON output
- `--inject`: Format for system prompt injection

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

### 3. Distill Memories

Extract reusable strategies:

```bash
# From success
uv run scripts/distill.py \
  "implement feature" \
  trajectory.json \
  --label Success \
  --confidence 0.9

# From failure
uv run scripts/distill.py \
  "fix issue" \
  trajectory.json \
  --label Failure \
  --confidence 0.8
```

**Creates**:
- Success → Strategy memories (what worked)
- Failure → Guardrail memories (what to avoid)

**Automatically**:
- Redacts PII
- Computes embeddings
- Assigns confidence scores

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

## Examples

### Example 1: Learning from Success

```bash
# Task succeeds
cat > traj.json <<EOF
{
  "steps": [
    "Loaded login page",
    "Parsed CSRF token from form",
    "Posted credentials with token",
    "Redirected to dashboard"
  ],
  "result": "success"
}
EOF

# Distill
uv run scripts/distill.py \
  "implement login with CSRF protection" \
  traj.json \
  --label Success \
  --confidence 0.92

# Output:
# Distilled 2 memories from Success trajectory:
# 1. Handle CSRF tokens in login forms
#    Extract token from page before submission
#    Tags: web, auth, csrf
# 2. Verify redirect after successful login
#    Check for dashboard URL in response
#    Tags: web, auth, validation
```

### Example 2: Learning from Failure

```bash
# Task fails
cat > traj.json <<EOF
{
  "steps": [
    "Loaded login page",
    "Posted credentials without token",
    "Received 403 Forbidden"
  ],
  "error": "CSRF validation failed"
}
EOF

# Extract guardrails
uv run scripts/distill.py \
  "implement login" \
  traj.json \
  --label Failure \
  --confidence 0.85

# Output:
# Distilled 1 memories from Failure trajectory:
# 1. Avoid missing CSRF tokens in POST requests
#    1) Failure mode: 403 on POST without CSRF
#    2) Detection: Check form for hidden token field
#    3) Prevention: Always parse and include token
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

## Best Practices

### 1. Always Retrieve Before Complex Tasks

```bash
# Step 1: Retrieve
uv run scripts/retrieve.py "<task>" -k 3 --inject > preamble.txt

# Step 2: Inject preamble into system prompt

# Step 3: Execute task
```

### 2. Always Learn from Outcomes

```bash
# After task completes
uv run scripts/post_hook.py \
  --task-id <id> \
  --query "<original_query>" \
  --trajectory <traj_file>
```

### 3. Consolidate Regularly

Automatic at threshold, or manual:

```bash
# Weekly
uv run scripts/consolidate.py
```

### 4. Use MaTTS for Critical Tasks

```bash
# When accuracy matters more than speed
uv run scripts/matts.py "<task>" --mode parallel -k 6
```

### 5. Monitor Success Rate

```bash
# Check if system is learning
uv run scripts/status.py

# Should see:
# - Success rate trending up
# - Memory reuse increasing
# - Average confidence stable/increasing
```

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

**Remember**: ReasoningBank gets smarter with every task. Use it proactively to build institutional knowledge!
