"""
ai/embeddings.py — Minimal embedding client for the AI layer.

Provides a local utility to fetch embedding vectors for text using
the Gemini API. This allows Person B's layer to compute similarity
internally without introducing heavy local ML dependencies (like torch
or sentence-transformers) or external vector databases.
"""

import os
import requests
from typing import List

def get_embedding(text: str) -> List[float]:
    """
    Fetches the embedding vector for the given text using the Gemini REST API.
    
    Parameters
    ----------
    text: str
        The input text to embed.
        
    Returns
    -------
    List[float]
        The embedding vector.
        
    Raises
    ------
    ValueError
        If GEMINI_API_KEY is not set or the API response is malformed.
    requests.HTTPError
        If the API request fails.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
        
    # Using text-embedding-004, the standard Gemini embedding model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{"text": text}]
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30.0
    )
    response.raise_for_status()
    
    data = response.json()
    try:
        return data["embedding"]["values"]
    except KeyError as e:
        raise ValueError(f"Unexpected response structure from Gemini Embeddings API: {e}")
