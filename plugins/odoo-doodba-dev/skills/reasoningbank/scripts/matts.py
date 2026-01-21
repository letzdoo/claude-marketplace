#!/usr/bin/env python3
"""
MaTTS (Memory-aware Test-Time Scaling) Orchestrator.

Implements parallel and sequential test-time scaling to convert
extra inference compute into better memories.
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Callable, Awaitable

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database import get_database
from scripts.utils.config import load_config, get_anthropic_api_key
from scripts.utils.ulid_gen import generate_run_id
from scripts.retrieve import retrieve_memories, format_memory_for_injection
from scripts.judge import judge_trajectory
from scripts.distill import distill_from_success, distill_from_failure, upsert_memories

try:
    from anthropic import AsyncAnthropic
except ImportError:
    print("Error: anthropic package not installed. Run: uv sync", file=sys.stderr)
    sys.exit(1)


AGGREGATION_PROMPT = """You are aggregating insights across multiple attempts of the same task.

Task: {task_query}

We have {k} trajectories with their judgments:

{trajectories_summary}

Your job:
1. Identify patterns present in most successful attempts but absent in failures
2. Identify pitfalls present in failures but not in successes
3. Produce 1-3 distilled memory items that generalize beyond this specific task

Each memory item should have:
- title: Short descriptive title (5-10 words)
- description: One sentence summary
- content: 3-8 numbered steps with clear decision criteria
- tags: Relevant tags
- domain: Optional domain

Respond with pure JSON:
{{
  "memories": [
    {{
      "title": "...",
      "description": "...",
      "content": "1) ... 2) ... 3) ...",
      "tags": ["tag1", "tag2"],
      "domain": "optional"
    }},
    ...
  ],
  "notes": ["Insight 1", "Insight 2", ...]
}}
"""


async def run_single_trajectory(
    task_query: str,
    task_executor: Callable[[str, str], Awaitable[Dict[str, Any]]],
    memories_preamble: str,
    diversity_seed: int = 0
) -> Dict[str, Any]:
    """
    Run a single trajectory with memory injection.

    Args:
        task_query: Task query
        task_executor: Async function that executes the task
        memories_preamble: Memory injection text for system prompt
        diversity_seed: Seed for diversity (used in temperature/sampling)

    Returns:
        Trajectory result
    """
    # In production, this would call your actual agent/executor
    # For now, this is a placeholder that simulates a trajectory

    result = await task_executor(task_query, memories_preamble)

    return result


async def matts_parallel(
    task_query: str,
    task_executor: Callable[[str, str], Awaitable[Dict[str, Any]]],
    k: int = 6,
    task_id: str = None,
    config = None
) -> Dict[str, Any]:
    """
    Parallel MaTTS: Run k independent trajectories and aggregate.

    Args:
        task_query: Task query
        task_executor: Async function that executes tasks
        k: Number of parallel rollouts
        task_id: Task ID for tracking
        config: Configuration

    Returns:
        Aggregation results with new memories
    """
    if config is None:
        config = load_config()

    if task_id is None:
        from scripts.utils.ulid_gen import generate_task_id
        task_id = generate_task_id()

    run_id = generate_run_id()

    # 1. Retrieve current memories
    memories = await retrieve_memories(task_query, k=3, config=config)
    memories_preamble = format_memory_for_injection(memories)

    # 2. Launch k parallel rollouts with diversity
    print(f"Launching {k} parallel rollouts...")
    rollout_tasks = []

    for i in range(k):
        task = run_single_trajectory(
            task_query,
            task_executor,
            memories_preamble,
            diversity_seed=i
        )
        rollout_tasks.append(task)

    trajectories = await asyncio.gather(*rollout_tasks)

    # 3. Judge each trajectory
    print("Judging trajectories...")
    judgments = []

    for traj in trajectories:
        label, confidence, reasons = await judge_trajectory(
            task_query, traj, config
        )
        judgments.append({
            "label": label,
            "confidence": confidence,
            "reasons": reasons
        })

    # 4. Self-contrast aggregation
    print("Aggregating insights...")

    # Build trajectories summary
    traj_summaries = []
    for i, (traj, judge) in enumerate(zip(trajectories, judgments)):
        summary = {
            "run": i + 1,
            "label": judge["label"],
            "confidence": judge["confidence"],
            "trajectory": traj
        }
        traj_summaries.append(summary)

    # Call Claude for aggregation
    api_key = get_anthropic_api_key()
    client = AsyncAnthropic(api_key=api_key)

    prompt = AGGREGATION_PROMPT.format(
        task_query=task_query,
        k=k,
        trajectories_summary=json.dumps(traj_summaries, indent=2)
    )

    response = await client.messages.create(
        model=config.distill.model,
        max_tokens=config.distill.max_tokens,
        temperature=config.distill.temperature,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse aggregation result
    try:
        response_text = response.content[0].text

        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        result = json.loads(response_text)
        aggregated_memories = result.get("memories", [])
        notes = result.get("notes", [])

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing aggregation response: {e}", file=sys.stderr)
        aggregated_memories = []
        notes = []

    # 5. Upsert aggregated memories
    # Use average success confidence
    success_count = sum(1 for j in judgments if j["label"] == "Success")
    avg_confidence = sum(j["confidence"] for j in judgments) / len(judgments)

    label = "Success" if success_count > k / 2 else "Failure"

    inserted_ids = []
    if aggregated_memories:
        # Enrich with source metadata
        for mem in aggregated_memories:
            mem["source"] = {
                "task_id": task_id,
                "matts_run_id": run_id,
                "outcome": "Aggregated",
                "num_trajectories": k,
                "success_rate": success_count / k
            }

        inserted_ids = await upsert_memories(
            aggregated_memories,
            label,
            avg_confidence,
            config
        )

    # 6. Record MaTTS run
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    summary = {
        "trajectories": len(trajectories),
        "success_count": success_count,
        "failure_count": k - success_count,
        "avg_confidence": avg_confidence,
        "memories_created": len(inserted_ids),
        "notes": notes
    }

    await db.insert_matts_run(
        run_id=run_id,
        task_id=task_id,
        mode="parallel",
        k=k,
        summary=json.dumps(summary)
    )

    return {
        "run_id": run_id,
        "mode": "parallel",
        "k": k,
        "judgments": judgments,
        "memories": aggregated_memories,
        "inserted_ids": inserted_ids,
        "notes": notes,
        "summary": summary
    }


async def matts_sequential(
    task_query: str,
    task_executor: Callable[[str, str], Awaitable[Dict[str, Any]]],
    r: int = 3,
    task_id: str = None,
    config = None
) -> Dict[str, Any]:
    """
    Sequential MaTTS: Iteratively refine a single trajectory.

    Args:
        task_query: Task query
        task_executor: Async function that executes tasks
        r: Number of refinement iterations
        task_id: Task ID for tracking
        config: Configuration

    Returns:
        Results with refined memories
    """
    if config is None:
        config = load_config()

    if task_id is None:
        from scripts.utils.ulid_gen import generate_task_id
        task_id = generate_task_id()

    run_id = generate_run_id()

    # 1. Retrieve current memories
    memories = await retrieve_memories(task_query, k=3, config=config)
    memories_preamble = format_memory_for_injection(memories)

    # 2. Run initial trajectory
    print("Running initial trajectory...")
    trajectory = await task_executor(task_query, memories_preamble)

    # 3. Iterative refinement
    refinement_notes = []

    for i in range(r):
        print(f"Refinement iteration {i+1}/{r}...")

        # Judge current state
        label, confidence, reasons = await judge_trajectory(
            task_query, trajectory, config
        )

        refinement_notes.append({
            "iteration": i + 1,
            "label": label,
            "confidence": confidence,
            "reasons": reasons
        })

        # If successful, stop refining
        if label == "Success" and confidence > 0.8:
            break

        # Otherwise, add check-and-correct instruction
        # In production, this would feed back into the executor
        # For now, we just record the iteration

    # 4. Final judgment
    final_label, final_confidence, final_reasons = await judge_trajectory(
        task_query, trajectory, config
    )

    # 5. Distill from final trajectory
    print("Distilling from final trajectory...")

    if final_label == "Success":
        memories_list = await distill_from_success(
            task_query, trajectory, final_confidence, task_id, config=config
        )
    else:
        memories_list = await distill_from_failure(
            task_query, trajectory, final_confidence, task_id, config=config
        )

    # Enrich with sequential metadata
    for mem in memories_list:
        mem["source"]["matts_run_id"] = run_id
        mem["source"]["refinement_iterations"] = len(refinement_notes)

    # 6. Upsert memories
    inserted_ids = await upsert_memories(
        memories_list,
        final_label,
        final_confidence,
        config
    )

    # 7. Record MaTTS run
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    summary = {
        "iterations": len(refinement_notes),
        "final_label": final_label,
        "final_confidence": final_confidence,
        "memories_created": len(inserted_ids),
        "refinement_notes": refinement_notes
    }

    await db.insert_matts_run(
        run_id=run_id,
        task_id=task_id,
        mode="sequential",
        k=r,
        summary=json.dumps(summary)
    )

    return {
        "run_id": run_id,
        "mode": "sequential",
        "iterations": r,
        "final_judgment": {
            "label": final_label,
            "confidence": final_confidence,
            "reasons": final_reasons
        },
        "memories": memories_list,
        "inserted_ids": inserted_ids,
        "refinement_notes": refinement_notes,
        "summary": summary
    }


async def main():
    """CLI entry point for MaTTS."""
    parser = argparse.ArgumentParser(
        description="MaTTS orchestrator for test-time scaling"
    )
    parser.add_argument("query", help="Task query")
    parser.add_argument("--mode", choices=["parallel", "sequential"],
                        required=True, help="MaTTS mode")
    parser.add_argument("-k", type=int, help="Number of parallel runs (parallel mode)")
    parser.add_argument("-r", type=int, help="Number of refinement iterations (sequential mode)")
    parser.add_argument("--task-id", help="Task ID")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Load config
    config = load_config()

    # Determine k or r
    if args.mode == "parallel":
        k = args.k or config.matts.parallel_k
    else:
        r = args.r or config.matts.sequential_r

    # Placeholder task executor
    # In production, replace with actual agent executor
    async def dummy_executor(query: str, preamble: str) -> Dict[str, Any]:
        return {
            "query": query,
            "steps": ["step1", "step2", "step3"],
            "result": "dummy result for demo",
            "preamble_used": bool(preamble)
        }

    # Run MaTTS
    if args.mode == "parallel":
        result = await matts_parallel(
            args.query,
            dummy_executor,
            k=k,
            task_id=args.task_id,
            config=config
        )
    else:
        result = await matts_sequential(
            args.query,
            dummy_executor,
            r=r,
            task_id=args.task_id,
            config=config
        )

    # Output
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"MaTTS {result['mode']} completed")
        print(f"Run ID: {result['run_id']}")

        if result['mode'] == 'parallel':
            print(f"Trajectories: {result['k']}")
            print(f"Memories created: {len(result['inserted_ids'])}")
        else:
            print(f"Refinement iterations: {result['iterations']}")
            print(f"Final: {result['final_judgment']['label']} "
                  f"({result['final_judgment']['confidence']:.2f})")
            print(f"Memories created: {len(result['inserted_ids'])}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
