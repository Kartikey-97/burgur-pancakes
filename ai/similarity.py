"""
ai/similarity.py — Local semantic similarity utility.

Provides a fast, dependency-free function to compute cosine similarity
between two embedding vectors. This allows Person B's layer to evaluate
semantic similarity internally without relying on external libraries
like FAISS, Chroma, or even numpy if it's absent.
"""

import math
from typing import List

def cosine_similarity(
    embedding_a: List[float],
    embedding_b: List[float],
) -> float:
    """
    Computes the cosine similarity between two embedding vectors.
    
    Parameters
    ----------
    embedding_a: List[float]
        The first embedding vector.
    embedding_b: List[float]
        The second embedding vector.
        
    Returns
    -------
    float
        The cosine similarity score, ranging from -1.0 to 1.0.
        Returns 0.0 if either vector has a zero magnitude or is empty.
        
    Raises
    ------
    ValueError
        If the two vectors do not have the same dimensionality.
    """
    if len(embedding_a) != len(embedding_b):
        raise ValueError(
            f"Embeddings must have the same dimensionality. "
            f"Got {len(embedding_a)} and {len(embedding_b)}."
        )
        
    if not embedding_a:
        raise ValueError("Cannot compute similarity on empty vectors.")
        
    dot_product = sum(a * b for a, b in zip(embedding_a, embedding_b))
    norm_a = math.sqrt(sum(a * a for a in embedding_a))
    norm_b = math.sqrt(sum(b * b for b in embedding_b))
    
    if norm_a == 0.0 or norm_b == 0.0:
        raise ValueError("Cannot compute similarity on zero-magnitude vectors.")
        
    return dot_product / (norm_a * norm_b)
