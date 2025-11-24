#!/usr/bin/env python3
"""
Post-task hook for ReasoningBank.

Judges trajectory, distills memories, and optionally consolidates.
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.judge import judge_trajectory
from scripts.distill import (
    distill_from_success,
    distill_from_failure,
    upsert_memories
)
from scripts.consolidate import consolidate
from scripts.database import get_database
from scripts.utils.config import load_config
from scripts.consent_manager import ConsentManager
from scripts.sync_manager import SyncManager


# Counter for consolidation trigger
_new_items_since_consolidation = 0


async def post_task_hook(
    task_id: str,
    agent_id: str,
    query: str,
    trajectory: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Post-task hook: Judge, distill, and consolidate.

    Args:
        task_id: Task ID
        agent_id: Agent ID
        query: Task query
        trajectory: Task trajectory data

    Returns:
        Hook result with judgment and new memories
    """
    global _new_items_since_consolidation

    config = load_config()

    # Get database
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    # 1. Judge trajectory
    label, confidence, reasons = await judge_trajectory(
        query, trajectory, config
    )

    # Update trajectory in database
    await db.insert_trajectory(
        task_id=task_id,
        agent_id=agent_id,
        query=query,
        trajectory_json=json.dumps(trajectory),
        judge_label=label,
        judge_conf=confidence
    )

    # 2. Distill memories
    if label == "Success":
        memories = await distill_from_success(
            query, trajectory, confidence, task_id, agent_id, config
        )
    else:
        memories = await distill_from_failure(
            query, trajectory, confidence, task_id, agent_id, config
        )

    # 3. Upsert memories
    inserted_ids = []
    if memories:
        inserted_ids = await upsert_memories(
            memories, label, confidence, config
        )
        _new_items_since_consolidation += len(inserted_ids)

    # 4. Request consent and queue for central upload (if enabled)
    consent_results = []
    upload_queued = 0
    central_config = config.reasoningbank.get('central', {})

    if central_config.get('enabled', False) and inserted_ids:
        consent_mgr = ConsentManager(db, config)
        sync_mgr = SyncManager(db, config.reasoningbank)

        for pattern_id in inserted_ids:
            try:
                # Get pattern data
                pattern = await db.get_pattern(pattern_id)
                if not pattern:
                    continue

                pattern_data = json.loads(pattern['pattern_data']) if isinstance(pattern['pattern_data'], str) else pattern['pattern_data']

                # Check if consent is required
                consent_required = await consent_mgr.check_consent_required(pattern)

                if consent_required:
                    # Request user consent
                    consent_given, consent_mode = await consent_mgr.request_consent(
                        pattern_id,
                        pattern_data,
                        pattern.get('confidence', 0.7)
                    )

                    consent_results.append({
                        'pattern_id': pattern_id,
                        'consent_given': consent_given,
                        'consent_mode': consent_mode
                    })

                    # Queue for upload if consent given
                    if consent_given:
                        queue_id = await sync_mgr.queue_pattern_upload(
                            pattern_id,
                            pattern_data,
                            pattern.get('confidence', 0.7)
                        )
                        if queue_id:
                            upload_queued += 1
                else:
                    # Auto-approved, queue for upload
                    queue_id = await sync_mgr.queue_pattern_upload(
                        pattern_id,
                        pattern_data,
                        pattern.get('confidence', 0.7)
                    )
                    if queue_id:
                        upload_queued += 1
                        consent_results.append({
                            'pattern_id': pattern_id,
                            'consent_given': True,
                            'consent_mode': 'auto_approved'
                        })

            except Exception as e:
                print(f"⚠️  Error processing consent for pattern {pattern_id}: {e}", file=sys.stderr)

        # Trigger background upload (non-blocking)
        if upload_queued > 0:
            try:
                # Process upload queue asynchronously
                asyncio.create_task(sync_mgr.process_upload_queue(immediate=True))
            except Exception as e:
                print(f"⚠️  Error starting upload queue: {e}", file=sys.stderr)

    # 5. Maybe consolidate
    consolidation_result = None
    if _new_items_since_consolidation >= config.consolidate.run_every_new_items:
        consolidation_result = await consolidate(config)
        _new_items_since_consolidation = 0

    # Log event
    await db.log_event(
        "post_task_hook.executed",
        entity_id=task_id,
        entity_type="task",
        data={
            "agent_id": agent_id,
            "query": query[:100],
            "judgment": label,
            "confidence": confidence,
            "memories_created": len(inserted_ids),
            "consolidation_triggered": consolidation_result is not None,
            "consent_requested": len(consent_results),
            "upload_queued": upload_queued
        }
    )

    return {
        "task_id": task_id,
        "agent_id": agent_id,
        "judgment": {
            "label": label,
            "confidence": confidence,
            "reasons": reasons
        },
        "memories_created": len(inserted_ids),
        "memory_ids": inserted_ids,
        "consolidation": consolidation_result,
        "central_sync": {
            "enabled": central_config.get('enabled', False),
            "consent_results": consent_results,
            "upload_queued": upload_queued
        }
    }


async def main():
    """CLI entry point for post-task hook."""
    parser = argparse.ArgumentParser(
        description="Post-task hook: Judge, distill, consolidate"
    )
    parser.add_argument("--task-id", required=True, help="Task ID")
    parser.add_argument("--agent-id", default="default", help="Agent ID")
    parser.add_argument("--query", required=True, help="Task query")
    parser.add_argument("--trajectory", required=True,
                        help="Path to trajectory JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--skip-consolidate", action="store_true",
                        help="Skip consolidation even if threshold reached")

    args = parser.parse_args()

    # Load trajectory
    with open(args.trajectory, 'r') as f:
        trajectory = json.load(f)

    # Execute hook
    result = await post_task_hook(
        args.task_id,
        args.agent_id,
        args.query,
        trajectory
    )

    # Output
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Post-task hook executed for task {args.task_id}")
        print(f"Judgment: {result['judgment']['label']} "
              f"(confidence: {result['judgment']['confidence']:.2f})")
        print(f"Reasons:")
        for reason in result['judgment']['reasons']:
            print(f"  - {reason}")
        print(f"\nMemories created: {result['memories_created']}")
        if result['memory_ids']:
            print(f"Memory IDs:")
            for mid in result['memory_ids']:
                print(f"  - {mid}")

        if result['consolidation']:
            print(f"\nConsolidation triggered:")
            print(f"  Duplicates: {result['consolidation']['duplicates_found']}")
            print(f"  Contradictions: {result['consolidation']['contradictions_found']}")
            print(f"  Pruned: {result['consolidation']['memories_pruned']}")

        if result['central_sync']['enabled']:
            print(f"\nCentral Sync:")
            print(f"  Patterns queued for upload: {result['central_sync']['upload_queued']}")
            if result['central_sync']['consent_results']:
                approved = sum(1 for c in result['central_sync']['consent_results'] if c['consent_given'])
                print(f"  Consent approved: {approved}/{len(result['central_sync']['consent_results'])}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
