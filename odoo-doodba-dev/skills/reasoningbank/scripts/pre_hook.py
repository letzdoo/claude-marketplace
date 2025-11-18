#!/usr/bin/env python3
"""
Pre-task hook for ReasoningBank.

Retrieves relevant memories and injects them into the system prompt.
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.retrieve import retrieve_memories, format_memory_for_injection
from scripts.utils.config import load_config


async def pre_task_hook(
    task_id: str,
    agent_id: str,
    query: str,
    domain: str = None
) -> Dict[str, Any]:
    """
    Pre-task hook: Retrieve and inject memories.

    Args:
        task_id: Task ID
        agent_id: Agent ID
        query: Task query
        domain: Optional domain filter

    Returns:
        Hook result with memories and injection text
    """
    config = load_config()

    # Retrieve memories
    memories = await retrieve_memories(
        query,
        k=config.retrieve.k,
        domain=domain,
        config=config
    )

    # Format for injection
    injection_text = format_memory_for_injection(memories)

    # Log metrics
    from scripts.database import get_database
    import time

    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    await db.log_event(
        "pre_task_hook.executed",
        entity_id=task_id,
        entity_type="task",
        data={
            "agent_id": agent_id,
            "query": query[:100],
            "memories_retrieved": len(memories),
            "memory_ids": [m['pattern_id'] for m in memories]
        }
    )

    return {
        "task_id": task_id,
        "agent_id": agent_id,
        "memories_count": len(memories),
        "memories": [
            {
                "id": m['pattern_id'],
                "title": m['pattern_data'].get('title'),
                "score": m['score']
            }
            for m in memories
        ],
        "injection_text": injection_text
    }


async def main():
    """CLI entry point for pre-task hook."""
    parser = argparse.ArgumentParser(
        description="Pre-task hook: Retrieve and inject memories"
    )
    parser.add_argument("--task-id", required=True, help="Task ID")
    parser.add_argument("--agent-id", default="default", help="Agent ID")
    parser.add_argument("--query", required=True, help="Task query")
    parser.add_argument("--domain", help="Domain filter")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--inject-only", action="store_true",
                        help="Output only injection text")

    args = parser.parse_args()

    # Execute hook
    result = await pre_task_hook(
        args.task_id,
        args.agent_id,
        args.query,
        args.domain
    )

    # Output
    if args.inject_only:
        print(result['injection_text'])
    elif args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Pre-task hook executed for task {args.task_id}")
        print(f"Retrieved {result['memories_count']} memories:")
        for mem in result['memories']:
            print(f"  - {mem['title']} (score: {mem['score']:.3f})")
        print(f"\nInjection text ({len(result['injection_text'])} chars):")
        print(result['injection_text'][:200] + "..." if len(result['injection_text']) > 200 else result['injection_text'])

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
