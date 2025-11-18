#!/usr/bin/env python3
"""
Distill reasoning memories from task trajectories.

Implements memory extraction from both successful and failed trajectories
as described in the ReasoningBank paper.
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database import get_database
from scripts.utils.config import load_config, get_anthropic_api_key
from scripts.utils.pii import redact_memory_item
from scripts.utils.ulid_gen import generate_memory_id
from scripts.utils.embeddings import compute_embedding, serialize_vector

try:
    from anthropic import AsyncAnthropic
except ImportError:
    print("Error: anthropic package not installed. Run: uv sync", file=sys.stderr)
    sys.exit(1)


SUCCESS_DISTILL_PROMPT = """Extract reusable strategy principles as concise, general rules from a successful task trajectory.

Given a task and its successful trajectory, produce up to {max_items} memory items.

Each item must be a JSON object with these keys:
- title: Short descriptive title (5-10 words)
- description: One sentence summary of the strategy
- content: 3-8 numbered steps with clear decision criteria
- tags: List of relevant tags (e.g., ["web", "auth", "api"])
- domain: Optional domain categorization

IMPORTANT:
- Avoid copying low-level URLs, IDs, PII, or task-specific constants
- Focus on generalizable patterns and strategies
- Make steps actionable and decision criteria clear
- Keep content concise but complete

Task: {task_query}

Trajectory:
{trajectory_json}

Respond with pure JSON in this format:
{{
  "memories": [
    {{
      "title": "...",
      "description": "...",
      "content": "1) ... 2) ... 3) ...",
      "tags": ["tag1", "tag2"],
      "domain": "optional_domain"
    }},
    ...
  ]
}}
"""


FAILURE_DISTILL_PROMPT = """Extract failure guardrails as preventative rules from a failed task trajectory.

Given a task and its failed trajectory, produce up to {max_items} guardrail items.

Each item must be a JSON object with these keys:
- title: Short descriptive title (5-10 words)
- description: One sentence summary of the failure mode
- content: Numbered steps specifying: 1) failure modes to detect, 2) checks to perform, 3) recovery steps
- tags: List of relevant tags
- domain: Optional domain categorization

IMPORTANT:
- Focus on what went wrong and how to avoid it
- Specify clear detection criteria for the failure mode
- Provide actionable recovery or prevention steps
- Avoid task-specific details

Task: {task_query}

Trajectory (FAILED):
{trajectory_json}

Respond with pure JSON in this format:
{{
  "memories": [
    {{
      "title": "...",
      "description": "...",
      "content": "1) Failure mode: ... 2) Detection: ... 3) Prevention: ...",
      "tags": ["tag1", "tag2"],
      "domain": "optional_domain"
    }},
    ...
  ]
}}
"""


async def distill_from_success(
    task_query: str,
    trajectory: Dict[str, Any],
    judge_confidence: float,
    task_id: str,
    agent_id: str = "default",
    config = None
) -> List[Dict[str, Any]]:
    """
    Distill memories from a successful trajectory.

    Args:
        task_query: Original task query
        trajectory: Trajectory data
        judge_confidence: Confidence from judge
        task_id: Task ID for tracking
        agent_id: Agent ID
        config: Configuration

    Returns:
        List of memory items
    """
    if config is None:
        config = load_config()

    api_key = get_anthropic_api_key()
    client = AsyncAnthropic(api_key=api_key)

    # Format trajectory
    trajectory_json = json.dumps(trajectory, indent=2)

    # Build prompt
    prompt = SUCCESS_DISTILL_PROMPT.format(
        max_items=config.distill.max_items_per_traj,
        task_query=task_query,
        trajectory_json=trajectory_json
    )

    # Call Claude
    response = await client.messages.create(
        model=config.distill.model,
        max_tokens=config.distill.max_tokens,
        temperature=config.distill.temperature,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse response
    try:
        response_text = response.content[0].text

        # Extract JSON
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        result = json.loads(response_text)
        memories = result.get("memories", [])

        # Enrich with metadata
        for mem in memories:
            mem["source"] = {
                "task_id": task_id,
                "agent_id": agent_id,
                "outcome": "Success",
                "judge_confidence": judge_confidence
            }

        return memories

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing distill response: {e}", file=sys.stderr)
        return []


async def distill_from_failure(
    task_query: str,
    trajectory: Dict[str, Any],
    judge_confidence: float,
    task_id: str,
    agent_id: str = "default",
    config = None
) -> List[Dict[str, Any]]:
    """
    Distill guardrail memories from a failed trajectory.

    Args:
        task_query: Original task query
        trajectory: Trajectory data
        judge_confidence: Confidence from judge
        task_id: Task ID for tracking
        agent_id: Agent ID
        config: Configuration

    Returns:
        List of guardrail memory items
    """
    if config is None:
        config = load_config()

    api_key = get_anthropic_api_key()
    client = AsyncAnthropic(api_key=api_key)

    # Format trajectory
    trajectory_json = json.dumps(trajectory, indent=2)

    # Build prompt
    prompt = FAILURE_DISTILL_PROMPT.format(
        max_items=config.distill.max_items_per_traj,
        task_query=task_query,
        trajectory_json=trajectory_json
    )

    # Call Claude
    response = await client.messages.create(
        model=config.distill.model,
        max_tokens=config.distill.max_tokens,
        temperature=config.distill.temperature,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse response
    try:
        response_text = response.content[0].text

        # Extract JSON
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        result = json.loads(response_text)
        memories = result.get("memories", [])

        # Enrich with metadata
        for mem in memories:
            mem["source"] = {
                "task_id": task_id,
                "agent_id": agent_id,
                "outcome": "Failure",
                "judge_confidence": judge_confidence
            }

        return memories

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing distill response: {e}", file=sys.stderr)
        return []


async def upsert_memories(
    memories: List[Dict[str, Any]],
    label: str,
    judge_confidence: float,
    config = None
) -> List[str]:
    """
    Upsert memories into the database.

    Args:
        memories: List of memory items
        label: "Success" or "Failure"
        judge_confidence: Judge confidence score
        config: Configuration

    Returns:
        List of inserted memory IDs
    """
    if config is None:
        config = load_config()

    # Get database
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    inserted_ids = []

    for mem in memories:
        # Redact PII if enabled
        if config.distill.redact_pii:
            mem = redact_memory_item(mem)

        # Generate ID
        mem_id = generate_memory_id()

        # Compute initial confidence
        if label == "Success":
            confidence = config.learning.initial_confidence_success * judge_confidence
        else:
            confidence = config.learning.initial_confidence_failure * judge_confidence

        # Compute embedding
        content_for_embedding = f"{mem['title']} {mem['description']} {mem['content']}"
        embedding = compute_embedding(content_for_embedding, config.retrieve.embedding_model)

        # Insert pattern
        await db.insert_pattern(
            pattern_id=mem_id,
            pattern_type="reasoning_memory",
            pattern_data=mem,
            confidence=confidence
        )

        # Insert embedding
        await db.insert_embedding(
            pattern_id=mem_id,
            model=config.retrieve.embedding_model,
            vector=serialize_vector(embedding),
            dims=len(embedding)
        )

        # Log event
        await db.log_event(
            "reasoning_memory.created",
            entity_id=mem_id,
            entity_type="pattern",
            data={
                "title": mem["title"],
                "source_outcome": label,
                "confidence": confidence
            }
        )

        inserted_ids.append(mem_id)

    return inserted_ids


async def main():
    """CLI entry point for distillation."""
    parser = argparse.ArgumentParser(
        description="Distill memories from task trajectory"
    )
    parser.add_argument("query", help="Task query text")
    parser.add_argument("trajectory_file", help="JSON file with trajectory data")
    parser.add_argument("--label", required=True, choices=["Success", "Failure"],
                        help="Outcome label")
    parser.add_argument("--confidence", type=float, default=0.8,
                        help="Judge confidence (0-1)")
    parser.add_argument("--task-id", help="Task ID")
    parser.add_argument("--agent-id", default="default", help="Agent ID")
    parser.add_argument("--no-upsert", action="store_true",
                        help="Don't insert into database")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")

    args = parser.parse_args()

    # Load trajectory
    with open(args.trajectory_file, 'r') as f:
        trajectory = json.load(f)

    # Generate task ID if not provided
    task_id = args.task_id or f"task_{args.trajectory_file}"

    # Distill
    if args.label == "Success":
        memories = await distill_from_success(
            args.query,
            trajectory,
            args.confidence,
            task_id,
            args.agent_id
        )
    else:
        memories = await distill_from_failure(
            args.query,
            trajectory,
            args.confidence,
            task_id,
            args.agent_id
        )

    # Upsert if requested
    inserted_ids = []
    if not args.no_upsert and memories:
        inserted_ids = await upsert_memories(
            memories,
            args.label,
            args.confidence
        )

    # Output
    if args.json:
        output = {
            "memories": memories,
            "inserted_ids": inserted_ids,
            "count": len(memories)
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Distilled {len(memories)} memories from {args.label} trajectory:\n")
        for i, mem in enumerate(memories, 1):
            print(f"{i}. {mem['title']}")
            print(f"   {mem['description']}")
            print(f"   Tags: {', '.join(mem.get('tags', []))}")
            print()

        if inserted_ids:
            print(f"Inserted {len(inserted_ids)} memories into database")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
