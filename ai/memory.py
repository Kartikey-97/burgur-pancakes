"""
ai/memory.py — Semantic memory retrieval utility.

Finds semantically similar prior answers from the interview history
using local embeddings and cosine similarity.
"""

from typing import Optional, List, Dict
from ai.embeddings import embed_text
from ai.similarity import cosine_similarity

def find_similar_prior_answer(
    current_answer: str,
    history: List[Dict],
) -> Optional[Dict]:
    """
    Finds the most semantically similar previous interview answer.
    
    Computes embeddings on the fly without relying on external databases.
    Returns the history entry with the highest cosine similarity to the
    current answer.
    
    Parameters
    ----------
    current_answer: str
        The candidate's current answer.
    history: List[Dict]
        The list of prior interview turns. Expected to contain an "answer" key.
        
    Returns
    -------
    Optional[Dict]
        The most similar history entry dict, or None if no valid answer
        is found or if the history is empty.
    """
    if not current_answer or not current_answer.strip() or not history:
        return None
        
    current_emb = embed_text(current_answer)
        
    best_match = None
    best_score = -float('inf')
    
    for entry in history:
        # Invalid/malformed history entries should be skipped
        if not isinstance(entry, dict):
            continue
            
        prior_answer = entry.get("answer", "")
        
        # Skip empty or missing answers in history
        if not prior_answer or not prior_answer.strip():
            continue
            
        prior_emb = embed_text(prior_answer)
        score = cosine_similarity(current_emb, prior_emb)
            
        if score > best_score:
            best_score = score
            best_match = entry
            
    return best_match
