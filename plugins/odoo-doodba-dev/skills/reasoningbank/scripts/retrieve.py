#!/usr/bin/env python3
"""
Retrieve relevant reasoning memories for a task.

Implements the retrieval algorithm from ReasoningBank with:
- Semantic similarity (cosine)
- Recency scoring (exponential decay)
- Relevance (confidence)
- Diversity (MMR)
"""

import asyncio
import sys
import json
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import math

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database import get_database
from scripts.utils.config import load_config
from scripts.utils.embeddings import (
    compute_embedding,
    cosine_similarity,
    deserialize_vector,
    maximal_marginal_relevance
)


async def retrieve_memories(
    query: str,
    k: int = 3,
    domain: Optional[str] = None,
    tenant_id: str = "default",
    config = None
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k relevant memories for a query.

    Args:
        query: Task query text
        k: Number of memories to retrieve
        domain: Optional domain filter
        tenant_id: Tenant ID for multi-tenancy
        config: Configuration object

    Returns:
        List of memory items with scores
    """
    if config is None:
        config = load_config()

    start_time = time.time()

    # Get database
    db_path = config.database.path
    if db_path.startswith("~"):
        db_path = str(Path(db_path).expanduser())
    db = get_database(db_path)

    # Compute query embedding
    query_emb = compute_embedding(query, config.retrieve.embedding_model)

    # Fetch all candidate patterns
    patterns = await db.get_all_patterns(
        pattern_type="reasoning_memory",
        tenant_id=tenant_id
    )

    if not patterns:
        return []

    # Filter by domain if specified
    if domain:
        patterns = [
            p for p in patterns
            if json.loads(p['pattern_data']).get('domain') == domain
        ]

    # Get embeddings for all patterns
    candidates = []
    for pattern in patterns:
        emb_data = await db.get_embedding(pattern['id'])
        if emb_data:
            emb = deserialize_vector(emb_data)
            candidates.append({
                'pattern': pattern,
                'embedding': emb
            })

    if not candidates:
        return []

    # Score each candidate
    scored_candidates = []
    for candidate in candidates:
        pattern = candidate['pattern']
        emb = candidate['embedding']

        # Parse pattern data
        pattern_data = json.loads(pattern['pattern_data'])

        # 1. Semantic similarity
        sim = cosine_similarity(query_emb, emb)

        # 2. Recency score (exponential decay)
        created_at = datetime.fromisoformat(pattern['created_at'])
        age_days = (datetime.now() - created_at).days
        half_life = config.retrieve.recency_half_life_days
        recency = math.exp(-age_days * math.log(2) / half_life)

        # 3. Relevance (confidence with usage boost)
        confidence = pattern['confidence']
        usage_count = pattern['usage_count']
        usage_boost = math.tanh(math.log(1 + usage_count))
        relevance = min(1.0, confidence * (1 + 0.2 * usage_boost))

        # 4. Base score (before diversity)
        score = (
            config.retrieve.alpha * sim +
            config.retrieve.beta * recency +
            config.retrieve.gamma * relevance
        )

        scored_candidates.append({
            'pattern_id': pattern['id'],
            'pattern': pattern,
            'pattern_data': pattern_data,
            'embedding': emb,
            'score': score,
            'sim': sim,
            'recency': recency,
            'relevance': relevance,
        })

    # Sort by score
    scored_candidates.sort(key=lambda x: x['score'], reverse=True)

    # Apply MMR for diversity
    selected_indices = []
    selected_results = []

    embeddings = [c['embedding'] for c in scored_candidates]
    scores = [c['score'] for c in scored_candidates]

    for _ in range(min(k, len(scored_candidates))):
        idx = maximal_marginal_relevance(
            query_emb,
            embeddings,
            scores,
            selected_indices,
            delta=config.retrieve.delta
        )

        if idx >= 0:
            selected_indices.append(idx)
            selected_results.append(scored_candidates[idx])

    # Update usage statistics
    for result in selected_results:
        await db.update_pattern_usage(result['pattern_id'])

    # Log retrieval metrics
    elapsed_ms = (time.time() - start_time) * 1000
    await db.log_metric(
        "retrieve_latency_ms",
        elapsed_ms,
        json.dumps({"k": k, "num_candidates": len(candidates)})
    )

    await db.log_event(
        "memory.retrieved",
        data={
            "query": query[:100],
            "k": k,
            "retrieved_ids": [r['pattern_id'] for r in selected_results],
            "latency_ms": elapsed_ms
        }
    )

    return selected_results


def format_memory_for_injection(memories: List[Dict[str, Any]]) -> str:
    """
    Format retrieved memories for system prompt injection.

    Args:
        memories: List of memory items

    Returns:
        Formatted string for system prompt
    """
    if not memories:
        return ""

    lines = ["Strategy memories you can optionally use:\n"]

    for i, mem in enumerate(memories, 1):
        data = mem['pattern_data']
        title = data.get('title', 'Untitled')
        content = data.get('content', '')

        lines.append(f"{i}) [Title] {title}")
        lines.append(f"   Steps: {content}\n")

    return "\n".join(lines)


async def main():
    """CLI entry point for memory retrieval."""
    parser = argparse.ArgumentParser(
        description="Retrieve relevant reasoning memories"
    )
    parser.add_argument("query", help="Task query text")
    parser.add_argument("-k", "--top-k", type=int, default=3,
                        help="Number of memories to retrieve")
    parser.add_argument("--domain", help="Domain filter")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--inject", action="store_true",
                        help="Format for system prompt injection")

    args = parser.parse_args()

    # Retrieve memories
    memories = await retrieve_memories(
        args.query,
        k=args.top_k,
        domain=args.domain
    )

    # Output
    if args.json:
        # JSON output
        output = [
            {
                'id': m['pattern_id'],
                'title': m['pattern_data'].get('title'),
                'description': m['pattern_data'].get('description'),
                'content': m['pattern_data'].get('content'),
                'score': m['score'],
                'confidence': m['pattern']['confidence'],
                'usage_count': m['pattern']['usage_count'],
            }
            for m in memories
        ]
        print(json.dumps(output, indent=2))

    elif args.inject:
        # Injection format
        print(format_memory_for_injection(memories))

    else:
        # Human-readable output
        if not memories:
            print("No relevant memories found.")
            return 0

        print(f"Retrieved {len(memories)} memories:\n")
        for i, mem in enumerate(memories, 1):
            data = mem['pattern_data']
            print(f"{i}. {data.get('title', 'Untitled')}")
            print(f"   Description: {data.get('description', 'N/A')}")
            print(f"   Score: {mem['score']:.3f} "
                  f"(sim={mem['sim']:.2f}, rec={mem['recency']:.2f}, "
                  f"rel={mem['relevance']:.2f})")
            print(f"   Confidence: {mem['pattern']['confidence']:.2f}")
            print(f"   Used: {mem['pattern']['usage_count']} times")
            print(f"   Content: {data.get('content', 'N/A')[:100]}...")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
