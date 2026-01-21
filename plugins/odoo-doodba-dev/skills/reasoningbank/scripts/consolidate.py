#!/usr/bin/env python3
"""
Consolidate and govern reasoning memories.

Implements:
- Deduplication via clustering
- Contradiction detection
- Aging and pruning
- Quality scoring
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
import math

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database import get_database
from scripts.utils.config import load_config
from scripts.utils.embeddings import (
    deserialize_vector,
    cosine_similarity,
    batch_cosine_similarity
)


async def deduplicate_memories(
    db,
    config,
    threshold: float = 0.87
) -> Tuple[int, List[Tuple[str, str]]]:
    """
    Find and mark duplicate memories.

    Args:
        db: Database instance
        config: Configuration
        threshold: Cosine similarity threshold for duplicates

    Returns:
        Tuple of (num_duplicates, duplicate_pairs)
    """
    # Get all patterns
    patterns = await db.get_all_patterns("reasoning_memory")

    if len(patterns) < 2:
        return 0, []

    # Get embeddings
    embeddings = {}
    for pattern in patterns:
        emb_data = await db.get_embedding(pattern['id'])
        if emb_data:
            embeddings[pattern['id']] = deserialize_vector(emb_data)

    # Find duplicates using clustering
    duplicate_pairs = []
    processed = set()

    pattern_ids = list(embeddings.keys())

    for i, id_i in enumerate(pattern_ids):
        if id_i in processed:
            continue

        cluster = [id_i]
        emb_i = embeddings[id_i]

        # Find similar items
        for id_j in pattern_ids[i+1:]:
            if id_j in processed:
                continue

            emb_j = embeddings[id_j]
            sim = cosine_similarity(emb_i, emb_j)

            if sim >= threshold:
                cluster.append(id_j)
                processed.add(id_j)

        # If cluster has duplicates, keep the best one
        if len(cluster) > 1:
            # Get patterns for cluster
            cluster_patterns = [
                p for p in patterns if p['id'] in cluster
            ]

            # Sort by: confidence desc, usage_count desc, created_at desc
            cluster_patterns.sort(
                key=lambda p: (
                    -p['confidence'],
                    -p['usage_count'],
                    p['created_at']
                ),
                reverse=True
            )

            # Keep first (best), mark others as duplicates
            best_id = cluster_patterns[0]['id']

            for pattern in cluster_patterns[1:]:
                dup_id = pattern['id']
                duplicate_pairs.append((dup_id, best_id))

                # Create link
                await db.insert_link(
                    src_id=dup_id,
                    dst_id=best_id,
                    relation="duplicate_of",
                    weight=cosine_similarity(embeddings[dup_id], embeddings[best_id])
                )

    return len(duplicate_pairs), duplicate_pairs


async def detect_contradictions(
    db,
    config,
    threshold: float = 0.60
) -> List[Tuple[str, str, float]]:
    """
    Detect contradicting memories.

    Uses simple heuristic: high similarity but different outcomes or tags.
    In production, would use NLI model.

    Args:
        db: Database instance
        config: Configuration
        threshold: Confidence threshold for contradiction

    Returns:
        List of (id1, id2, contradiction_score) tuples
    """
    patterns = await db.get_all_patterns("reasoning_memory")

    if len(patterns) < 2:
        return []

    contradictions = []

    # Get embeddings
    embeddings = {}
    for pattern in patterns:
        emb_data = await db.get_embedding(pattern['id'])
        if emb_data:
            embeddings[pattern['id']] = deserialize_vector(emb_data)

    # Simple contradiction detection heuristic:
    # - Similar embeddings (> 0.7)
    # - Different outcomes (Success vs Failure)
    # - Overlapping tags

    for i, p1 in enumerate(patterns):
        if p1['id'] not in embeddings:
            continue

        p1_data = json.loads(p1['pattern_data'])
        p1_outcome = p1_data.get('source', {}).get('outcome')

        for p2 in patterns[i+1:]:
            if p2['id'] not in embeddings:
                continue

            p2_data = json.loads(p2['pattern_data'])
            p2_outcome = p2_data.get('source', {}).get('outcome')

            # Skip if same outcome
            if p1_outcome == p2_outcome:
                continue

            # Check similarity
            sim = cosine_similarity(embeddings[p1['id']], embeddings[p2['id']])

            if sim > 0.7:  # Similar content but different outcomes
                # Check tag overlap
                p1_tags = set(p1_data.get('tags', []))
                p2_tags = set(p2_data.get('tags', []))

                if p1_tags & p2_tags:  # Has overlapping tags
                    # Contradiction score based on similarity and tag overlap
                    tag_overlap = len(p1_tags & p2_tags) / max(len(p1_tags), len(p2_tags), 1)
                    contra_score = sim * tag_overlap

                    if contra_score >= threshold:
                        contradictions.append((p1['id'], p2['id'], contra_score))

                        # Create link
                        await db.insert_link(
                            src_id=p1['id'],
                            dst_id=p2['id'],
                            relation="contradicts",
                            weight=contra_score
                        )

    return contradictions


async def apply_aging(
    db,
    config,
    half_life_days: int = 90
) -> int:
    """
    Apply exponential decay to memory confidence based on age.

    Args:
        db: Database instance
        config: Configuration
        half_life_days: Half-life for confidence decay

    Returns:
        Number of memories updated
    """
    patterns = await db.get_all_patterns("reasoning_memory")

    updated_count = 0

    for pattern in patterns:
        # Skip if recently used
        if pattern['usage_count'] > 5:
            continue

        # Calculate age
        from datetime import datetime
        created_at = datetime.fromisoformat(pattern['created_at'])
        age_days = (datetime.now() - created_at).days

        if age_days < 30:  # Don't decay young memories
            continue

        # Apply exponential decay
        decay_factor = math.exp(-age_days * math.log(2) / half_life_days)
        new_confidence = pattern['confidence'] * decay_factor

        # Update if significant change
        if abs(new_confidence - pattern['confidence']) > 0.01:
            import aiosqlite
            async with aiosqlite.connect(db.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                await conn.execute("PRAGMA foreign_keys=ON")
                await conn.execute("""
                    UPDATE patterns
                    SET confidence = ?
                    WHERE id = ?
                """, (new_confidence, pattern['id']))
                await conn.commit()

            updated_count += 1

    return updated_count


async def prune_memories(
    db,
    config
) -> int:
    """
    Prune old, low-confidence, unused memories.

    Args:
        db: Database instance
        config: Configuration

    Returns:
        Number of memories pruned
    """
    count = await db.prune_old_patterns(
        min_confidence=config.consolidate.min_confidence_keep,
        max_age_days=config.consolidate.prune_age_days
    )

    return count


async def consolidate(config = None) -> Dict[str, Any]:
    """
    Run full consolidation process.

    Args:
        config: Configuration

    Returns:
        Summary of consolidation results
    """
    if config is None:
        config = load_config()

    # Get database
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    results = {
        "duplicates_found": 0,
        "contradictions_found": 0,
        "memories_aged": 0,
        "memories_pruned": 0
    }

    # 1. Deduplicate
    num_dups, dup_pairs = await deduplicate_memories(
        db, config, config.consolidate.dedup_threshold
    )
    results["duplicates_found"] = num_dups
    results["duplicate_pairs"] = [
        {"duplicate": d[0], "original": d[1]} for d in dup_pairs
    ]

    # 2. Detect contradictions
    contradictions = await detect_contradictions(
        db, config, config.consolidate.contradiction_threshold
    )
    results["contradictions_found"] = len(contradictions)
    results["contradictions"] = [
        {"id1": c[0], "id2": c[1], "score": c[2]} for c in contradictions
    ]

    # 3. Apply aging
    aged_count = await apply_aging(db, config)
    results["memories_aged"] = aged_count

    # 4. Prune
    pruned_count = await prune_memories(db, config)
    results["memories_pruned"] = pruned_count

    # Log event
    await db.log_event(
        "consolidation.completed",
        data=results
    )

    return results


async def main():
    """CLI entry point for consolidation."""
    parser = argparse.ArgumentParser(
        description="Consolidate and govern reasoning memories"
    )
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--skip-dedup", action="store_true",
                        help="Skip deduplication")
    parser.add_argument("--skip-contradictions", action="store_true",
                        help="Skip contradiction detection")
    parser.add_argument("--skip-aging", action="store_true",
                        help="Skip aging")
    parser.add_argument("--skip-pruning", action="store_true",
                        help="Skip pruning")

    args = parser.parse_args()

    # Run consolidation
    results = await consolidate()

    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("Consolidation Results:")
        print(f"  Duplicates found: {results['duplicates_found']}")
        print(f"  Contradictions found: {results['contradictions_found']}")
        print(f"  Memories aged: {results['memories_aged']}")
        print(f"  Memories pruned: {results['memories_pruned']}")

        if results['duplicates_found'] > 0:
            print("\nDuplicate pairs:")
            for pair in results['duplicate_pairs'][:5]:
                print(f"  {pair['duplicate'][:16]}... -> {pair['original'][:16]}...")

        if results['contradictions_found'] > 0:
            print("\nContradictions:")
            for contra in results['contradictions'][:5]:
                print(f"  {contra['id1'][:16]}... <-> {contra['id2'][:16]}... "
                      f"(score: {contra['score']:.2f})")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
