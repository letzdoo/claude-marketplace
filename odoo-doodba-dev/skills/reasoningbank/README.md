# ReasoningBank - Learning Memory System for Claude Code

ReasoningBank is an adaptive learning memory system that improves agent performance by learning from both successful and failed task executions. Based on the ReasoningBank research paper, it implements semantic memory retrieval, LLM-as-judge trajectory evaluation, memory distillation, and Memory-aware Test-Time Scaling (MaTTS).

## 🎯 Overview

ReasoningBank creates a closed-loop learning system that:

1. **Retrieves** relevant past experiences before task execution
2. **Judges** task outcomes using Claude as an LLM-judge
3. **Distills** reusable strategies from successes and guardrails from failures
4. **Consolidates** memories with deduplication and quality control
5. **Scales** at test-time using MaTTS for critical tasks

## 🚀 Quick Start

### Installation

```bash
# Navigate to skill directory
cd odoo-doodba-dev/skills/reasoningbank

# Install dependencies
uv sync

# Set API key
export ANTHROPIC_API_KEY="sk-..."

# Initialize database
uv run scripts/init_db.py
```

### Basic Usage

```bash
# Check status
uv run scripts/status.py

# Retrieve memories for a task
uv run scripts/retrieve.py "implement user authentication" -k 3

# Judge a trajectory
uv run scripts/judge.py "fix login bug" trajectory.json

# Distill memories from success
uv run scripts/distill.py "implement feature" traj.json --label Success --confidence 0.9

# Consolidate memories
uv run scripts/consolidate.py

# Test-time scaling
uv run scripts/matts.py "complex task" --mode parallel -k 6
```

## 📋 Key Features

### 1. Semantic Memory Retrieval

Finds relevant past experiences using:
- **Semantic similarity** (cosine similarity on embeddings)
- **Recency** (exponential decay with configurable half-life)
- **Relevance** (confidence scores from judge and reuse frequency)
- **Diversity** (MMR to avoid redundancy)

```python
score = α*similarity + β*recency + γ*relevance - δ*diversity
```

### 2. LLM-as-Judge

Evaluates task trajectories without ground truth:
- Uses Claude with deterministic decoding (temperature=0)
- Returns "Success" or "Failure" label
- Provides confidence score (0-1)
- Explains reasoning

### 3. Memory Distillation

Extracts generalizable knowledge:
- **From successes**: Strategy patterns
- **From failures**: Guardrails and pitfalls
- Automatically redacts PII
- Creates embeddings for retrieval

### 4. Consolidation & Governance

Maintains memory quality:
- **Deduplication**: Clusters similar memories (>87% similarity)
- **Contradiction detection**: Flags conflicting advice
- **Aging**: Exponential confidence decay
- **Pruning**: Removes old, unused, low-confidence items

### 5. MaTTS (Memory-aware Test-Time Scaling)

Converts extra compute into better memories:

**Parallel Mode**: Run k independent attempts, aggregate insights
- Identifies common success patterns
- Extracts failure pitfalls
- Creates high-quality distilled memories

**Sequential Mode**: Iteratively refine single attempt
- Check and correct approach
- Uses intermediate notes
- Progressively improves

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

### Memory Item Structure

```json
{
  "id": "rm_01HZX...",
  "type": "reasoning_memory",
  "pattern_data": {
    "title": "Handle CSRF tokens in forms",
    "description": "Always fetch and include CSRF token before POST.",
    "content": "1) Load page and parse CSRF from form. 2) Attach token to POST. 3) Retry once if 403.",
    "source": {
      "task_id": "task_...",
      "outcome": "Success",
      "judge_confidence": 0.85
    },
    "tags": ["web", "auth", "csrf"],
    "domain": "webarena.admin"
  },
  "confidence": 0.76,
  "usage_count": 12
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

## 📖 Usage Examples

### Example 1: Complete Learning Loop

```bash
# 1. Retrieve relevant memories
uv run scripts/retrieve.py "implement OAuth login" -k 3 --inject > preamble.txt

# 2. Execute task (with preamble in system prompt)
# ... task execution with memories injected ...

# 3. Post-task: judge and learn
uv run scripts/post_hook.py \
  --task-id task_123 \
  --query "implement OAuth login" \
  --trajectory trajectory.json
```

### Example 2: Learning from Failure

```bash
# Create failure trajectory
cat > failure_traj.json <<EOF
{
  "steps": ["Load login page", "POST without CSRF", "Received 403"],
  "error": "CSRF validation failed"
}
EOF

# Extract guardrails
uv run scripts/distill.py \
  "implement login form" \
  failure_traj.json \
  --label Failure \
  --confidence 0.85
```

### Example 3: Test-Time Scaling

```bash
# Parallel: Run 6 attempts, aggregate best practices
uv run scripts/matts.py \
  "solve complex algorithm problem" \
  --mode parallel \
  -k 6

# Sequential: Iteratively refine
uv run scripts/matts.py \
  "optimize database query" \
  --mode sequential \
  -r 3
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

## 📚 Research Foundation

Based on **ReasoningBank** research paper:
- arXiv:2501.xxxxx
- Learns from both successes and failures
- LLM-as-judge for trajectory evaluation
- Memory-aware test-time scaling
- Semantic retrieval with MMR

Key innovations:
1. No ground truth needed (LLM-as-judge)
2. Learns from failures (guardrails)
3. Test-time scaling converts compute → quality
4. Consolidation maintains memory bank health

## 🤝 Contributing

This is part of the Claude marketplace odoo-doodba-dev plugin.

## 📄 License

MIT License - See LICENSE file

## 🔗 Links

- [Claude Code Documentation](https://docs.claude.com/)
- [ReasoningBank Paper](https://arxiv.org/abs/...)
- [Plugin Repository](https://github.com/...)

---

**Remember**: ReasoningBank learns from every task execution. Use it proactively to build institutional knowledge that makes your agents smarter over time!
