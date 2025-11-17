"""Embedding computation and similarity utilities."""

import numpy as np
from typing import List, Union
import struct
import os


def compute_embedding(text: str, model: str = "voyage-3") -> np.ndarray:
    """
    Compute embedding for text.

    For production use, this should call an actual embedding API.
    For now, we use a simple hash-based deterministic embedding for demo purposes.

    TODO: Integrate with actual embedding providers:
    - Voyage AI (voyage-3)
    - OpenAI (text-embedding-3-large)
    - Anthropic embedding endpoints when available
    """
    # Simple deterministic embedding based on text hash
    # In production, replace with actual API calls
    import hashlib

    # Create a deterministic hash
    hash_obj = hashlib.sha256(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()

    # Convert to float vector (normalize to unit length)
    # Use 1024 dimensions for compatibility with modern embedding models
    dims = 1024

    # Expand hash to desired dimensions
    vector = []
    for i in range(dims):
        # Use hash as seed for deterministic random values
        seed_bytes = hash_bytes + i.to_bytes(4, 'big')
        seed_hash = hashlib.sha256(seed_bytes).digest()
        # Convert to float in range [-1, 1]
        value = int.from_bytes(seed_hash[:4], 'big') / (2**31) - 1.0
        vector.append(value)

    # Normalize to unit length
    vector = np.array(vector, dtype=np.float32)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm

    return vector


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    # Vectors are already normalized in compute_embedding
    return float(np.dot(vec1, vec2))


def serialize_vector(vector: np.ndarray) -> bytes:
    """Serialize numpy vector to bytes for database storage."""
    return vector.tobytes()


def deserialize_vector(data: bytes, dims: int = 1024) -> np.ndarray:
    """Deserialize bytes back to numpy vector."""
    return np.frombuffer(data, dtype=np.float32).reshape(-1)


def batch_cosine_similarity(
    query: np.ndarray,
    vectors: List[np.ndarray]
) -> List[float]:
    """Compute cosine similarity between query and multiple vectors."""
    if not vectors:
        return []

    # Stack vectors for efficient computation
    matrix = np.vstack(vectors)

    # Compute dot products (vectors are normalized)
    similarities = np.dot(matrix, query)

    return similarities.tolist()


def maximal_marginal_relevance(
    query_embedding: np.ndarray,
    candidate_embeddings: List[np.ndarray],
    candidate_scores: List[float],
    selected_indices: List[int],
    delta: float = 0.10
) -> int:
    """
    Select next item using Maximal Marginal Relevance.

    Args:
        query_embedding: Query vector
        candidate_embeddings: List of candidate vectors
        candidate_scores: List of base scores for candidates
        selected_indices: Indices of already selected items
        delta: Diversity penalty weight

    Returns:
        Index of the next item to select
    """
    best_score = -float('inf')
    best_idx = -1

    for i, (emb, score) in enumerate(zip(candidate_embeddings, candidate_scores)):
        if i in selected_indices:
            continue

        # Compute diversity penalty
        max_sim = 0.0
        if selected_indices:
            selected_embs = [candidate_embeddings[j] for j in selected_indices]
            similarities = batch_cosine_similarity(emb, selected_embs)
            max_sim = max(similarities) if similarities else 0.0

        # MMR score: base score - diversity penalty
        mmr_score = score - delta * max_sim

        if mmr_score > best_score:
            best_score = mmr_score
            best_idx = i

    return best_idx


# Production-ready embedding function (requires API key)
def compute_embedding_production(
    text: str,
    model: str = "voyage-3"
) -> np.ndarray:
    """
    Compute embedding using actual API (production version).

    This is a placeholder for production implementation.
    Integrate with:
    - Voyage AI API
    - OpenAI Embeddings API
    - Or other embedding providers
    """
    # Example for Voyage AI (requires voyage-ai package)
    # import voyageai
    # client = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))
    # result = client.embed([text], model=model)
    # return np.array(result.embeddings[0], dtype=np.float32)

    # For now, use the deterministic version
    return compute_embedding(text, model)
