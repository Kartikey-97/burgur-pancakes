"""
ai/embeddings.py — Local embedding utility for the AI layer.

Provides a deterministic local embedding function using sentence-transformers,
ensuring embeddings are generated completely locally without remote API calls
or external vector databases.
"""

from typing import List

# Module-level variable for lazy loading
_model = None


def embed_text(text: str) -> List[float]:
    """
    Generates a deterministic embedding vector for the given text using a local model.
    
    The model (BAAI/bge-small-en-v1.5) is loaded lazily on the first call to minimize
    module import time and resource usage.
    
    Parameters
    ----------
    text: str
        The input text to embed. Empty or whitespace-only strings are safely handled
        and will return a valid embedding vector of the same dimensionality.
        
    Returns
    -------
    List[float]
        The embedding vector as a standard Python list of floats.
    """
    global _model
    
    # 1. Lazy load the model on first use
    if _model is None:
        import torch
        from sentence_transformers import SentenceTransformer
        
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        _model = SentenceTransformer("BAAI/bge-small-en-v1.5", device=device)
        
    # 2. Safely handle empty or whitespace-only inputs
    # Embedding an empty string is a simple deterministic representation that maintains
    # the exact same dimensionality as normal text embeddings.
    if not text or not text.strip():
        text = ""
        
    # 3. Generate embedding and return as plain Python list[float]
    embedding = _model.encode(text, convert_to_numpy=True)
    return embedding.tolist()
