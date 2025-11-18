---
name: ReasoningBank
description: **AUTO-USE** Learning memory system that improves over time. Use AUTOMATICALLY when starting complex multi-step tasks, after completing tasks, or when user mentions learning, memories, or improvement. AUTO-TRIGGER on keywords like "learn from this", "remember this pattern", "improve performance", "test-time scaling", or when tasks fail repeatedly. CRITICAL - Use proactively to build up knowledge base that makes future tasks more efficient and successful.
allowed-tools: Bash, Read
---

# ReasoningBank Memory System

Adaptive learning memory system that learns from both successes and failures to improve agent performance over time.

## When to Auto-Use

✅ **Before complex tasks**: Retrieve relevant memories
✅ **After task completion**: Distill new learnings
✅ **On repeated failures**: Extract guardrails
✅ **User mentions**: "learn", "remember", "improve", "scale"

## Quick Start

### Check Status

```bash
cd odoo-doodba-dev/skills/reasoningbank
uv run scripts/status.py
```

### Initialize Database (First Time)

```bash
cd odoo-doodba-dev/skills/reasoningbank
uv run scripts/init_db.py
```

### Retrieve Memories

```bash
uv run scripts/retrieve.py "implement user authentication" -k 3
```

### Judge a Trajectory

```bash
uv run scripts/judge.py "fix login bug" trajectory.json
```

### Distill Memories

```bash
uv run scripts/distill.py "implement API endpoint" trajectory.json --label Success --confidence 0.9
```

### Consolidate Memories

```bash
uv run scripts/consolidate.py
```

### Test-Time Scaling (MaTTS)

```bash
# Parallel mode - run k attempts and aggregate learnings
uv run scripts/matts.py "complex task" --mode parallel -k 6

# Sequential mode - iteratively refine
uv run scripts/matts.py "complex task" --mode sequential -r 3
```

## Key Features

### 1. Semantic Retrieval
- Finds relevant past experiences for new tasks
- Scores by similarity, recency, and confidence
- Injects top-k memories into system prompt

### 2. LLM-as-Judge
- Evaluates task outcomes as Success/Failure
- Provides confidence scores and reasoning
- No ground truth needed

### 3. Memory Distillation
- Extracts reusable strategies from successes
- Creates guardrails from failures
- Automatically redacts PII

### 4. Consolidation
- Deduplicates similar memories
- Detects contradictions
- Prunes old, unused memories
- Applies aging decay

### 5. MaTTS (Memory-aware Test-Time Scaling)
- **Parallel**: Run k attempts, aggregate insights
- **Sequential**: Iteratively refine single attempt
- Converts extra compute into better memories

## How It Works

### Learning Loop

```
1. Pre-Task Hook
   ↓
   Retrieve relevant memories
   ↓
   Inject into system prompt
   ↓
2. Execute Task
   ↓
   Record trajectory
   ↓
3. Post-Task Hook
   ↓
   Judge outcome (Success/Failure)
   ↓
   Distill new memories
   ↓
   Upsert to database
   ↓
   Consolidate (every N items)
```

### Memory Structure

Each memory has:
- **Title**: Short descriptor
- **Description**: One sentence summary
- **Content**: Numbered actionable steps
- **Tags**: Categorization
- **Domain**: Optional scope
- **Source**: Origin metadata
- **Confidence**: Quality score (0-1)
- **Usage Count**: Reuse tracking

## Configuration

Edit `skills/reasoningbank/config.yaml`:

```yaml
reasoningbank:
  retrieve:
    k: 3                        # Top memories to retrieve
    recency_half_life_days: 45  # Recency decay

  consolidate:
    run_every_new_items: 20     # Auto-consolidate frequency
    prune_age_days: 180         # Delete threshold

  matts:
    parallel_k: 6               # Parallel attempts
    sequential_r: 3             # Refinement iterations
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

## Examples

### Example 1: Learn from Success

```bash
# Task succeeds
echo '{"steps": [...], "result": "success"}' > traj.json

# Distill learnings
uv run scripts/distill.py \
  "implement OAuth login" \
  traj.json \
  --label Success \
  --confidence 0.9
```

### Example 2: Learn from Failure

```bash
# Task fails
echo '{"steps": [...], "error": "CSRF token missing"}' > traj.json

# Extract guardrails
uv run scripts/distill.py \
  "implement login form" \
  traj.json \
  --label Failure \
  --confidence 0.8
```

### Example 3: Test-Time Scaling

```bash
# Run 6 parallel attempts and aggregate best strategies
uv run scripts/matts.py \
  "solve complex algorithm problem" \
  --mode parallel \
  -k 6
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

## Best Practices

1. **Use pre-hook for all complex tasks** - Retrieves relevant context
2. **Always run post-hook** - Captures learnings even from failures
3. **Consolidate regularly** - Keeps memory bank high-quality
4. **Use MaTTS for critical tasks** - Extra compute yields better memories
5. **Monitor success rate** - Validates system is learning

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

## Integration

ReasoningBank hooks can be integrated into your workflow:

```yaml
# .claude/settings.json
{
  "hooks": {
    "preTaskHook": {
      "command": "uv",
      "args": ["run", "-m", "reasoningbank", "pre-hook", ...],
      "alwaysRun": true
    },
    "postTaskHook": {
      "command": "uv",
      "args": ["run", "-m", "reasoningbank", "post-hook", ...],
      "alwaysRun": true
    }
  }
}
```

---

**Remember**: ReasoningBank learns from both successes AND failures. Every task makes the system smarter!
