"""
ai/deduplication.py — Question deduplication utility.

Determines whether a newly generated interview question is semantically
too similar to a question that has already been asked in the interview history.
"""

from typing import List, Dict
from ai.embeddings import embed_text
from ai.similarity import cosine_similarity

def is_duplicate_question(
    new_question: str,
    history: List[Dict],
    threshold: float = 0.85,
) -> bool:
    """
    Checks if a new question is a semantic duplicate of a previously asked question.
    
    Parameters
    ----------
    new_question: str
        The newly generated question to check.
    history: List[Dict]
        The list of prior interview turns. Expected to contain a "question" key.
    threshold: float
        The cosine similarity threshold above which a question is considered
        a duplicate. Defaults to 0.85.
        
    Returns
    -------
    bool
        True if the question is a duplicate of any prior question, False otherwise.
    """
    if not new_question or not new_question.strip() or not history:
        return False
        
    new_emb = embed_text(new_question)
    
    for entry in history:
        if not isinstance(entry, dict):
            continue
            
        prior_question = entry.get("question", "")
        if not prior_question or not prior_question.strip():
            continue
            
        prior_emb = embed_text(prior_question)
        score = cosine_similarity(new_emb, prior_emb)
        
        if score >= threshold:
            return True
            
    return False
