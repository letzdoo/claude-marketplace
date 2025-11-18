"""Embedding computation and similarity utilities using Voyage AI."""

import numpy as np
from typing import List, Union, Optional
import os
import hashlib


def compute_embedding(text: str, model: str = "voyage-3") -> np.ndarray:
    """
    Compute embedding for text using Voyage AI.

    Args:
        text: Input text to embed
        model: Voyage AI model name (default: voyage-3)

    Returns:
        numpy array of embedding vector (1024-dim for voyage-3)

    Raises:
        ImportError: If voyageai package not installed
        ValueError: If VOYAGE_API_KEY not set
    """
    try:
        import voyageai
    except ImportError:
        print("Warning: voyageai not installed, using fallback embeddings", flush=True)
        return _compute_embedding_fallback(text, model)

    # Get API key
    api_key = os.environ.get('VOYAGE_API_KEY')
    if not api_key:
        print("Warning: VOYAGE_API_KEY not set, using fallback embeddings", flush=True)
        return _compute_embedding_fallback(text, model)

    try:
        # Create client
        client = voyageai.Client(api_key=api_key)

        # Compute embedding
        result = client.embed([text], model=model, input_type="document")

        # Extract embedding and convert to numpy array
        embedding = np.array(result.embeddings[0], dtype=np.float32)

        return embedding

    except Exception as e:
        print(f"Warning: Voyage AI error ({e}), using fallback embeddings", flush=True)
        return _compute_embedding_fallback(text, model)


def _compute_embedding_fallback(text: str, model: str = "voyage-3") -> np.ndarray:
    """
    Fallback deterministic embedding for when Voyage AI is unavailable.

    Uses hash-based pseudo-random generation for consistent embeddings.
    Not suitable for production but useful for testing/development.
    """
    # Create a deterministic hash
    hash_obj = hashlib.sha256(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()

    # Use 1024 dimensions for compatibility with voyage-3
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
    # Vectors are already normalized
    return float(np.dot(vec1, vec2))


def serialize_vector(vector: np.ndarray) -> bytes:
    """Serialize numpy vector to bytes for database storage."""
    return vector.tobytes()


def deserialize_vector(data: bytes, dims: int = 1024) -> np.ndarray:
    """Deserialize bytes back to numpy vector."""
    return np.frombuffer(data, dtype=np.float32).reshape(-1)


def batch_embeddings(texts: List[str], model: str = "voyage-3") -> List[np.ndarray]:
    """
    Compute embeddings for multiple texts in a batch.

    More efficient than calling compute_embedding individually.

    Args:
        texts: List of texts to embed
        model: Voyage AI model name

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    try:
        import voyageai
    except ImportError:
        print("Warning: voyageai not installed, using fallback embeddings", flush=True)
        return [_compute_embedding_fallback(text, model) for text in texts]

    api_key = os.environ.get('VOYAGE_API_KEY')
    if not api_key:
        print("Warning: VOYAGE_API_KEY not set, using fallback embeddings", flush=True)
        return [_compute_embedding_fallback(text, model) for text in texts]

    try:
        # Create client
        client = voyageai.Client(api_key=api_key)

        # Batch embed
        result = client.embed(texts, model=model, input_type="document")

        # Convert to numpy arrays
        embeddings = [np.array(emb, dtype=np.float32) for emb in result.embeddings]

        return embeddings

    except Exception as e:
        print(f"Warning: Voyage AI batch error ({e}), using fallback", flush=True)
        return [_compute_embedding_fallback(text, model) for text in texts]


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


def get_embedding_dimensions(model: str = "voyage-3") -> int:
    """
    Get the embedding dimensions for a model.

    Args:
        model: Model name

    Returns:
        Number of dimensions
    """
    # Voyage AI model dimensions
    model_dims = {
        "voyage-3": 1024,
        "voyage-3-lite": 512,
        "voyage-code-3": 1024,
        "voyage-finance-2": 1024,
        "voyage-law-2": 1024,
        "voyage-2": 1024,
        "voyage-large-2": 1536,
        "voyage-code-2": 1536,
    }

    return model_dims.get(model, 1024)
