"""
ai/confidence.py — Local heuristic for detecting confidence flags in answers.

This is a fast, deterministic local function that flags hedging or uncertainty
in the candidate's answer without requiring an LLM call or embeddings.
It fulfills the requirement that confidence/hedging scoring is handled internally
by a separate local function.
"""

from typing import List

_HEDGING_PHRASES = (
    "i think",
    "i guess",
    "maybe",
    "probably",
    "not sure",
    "might be",
    "could be",
    "i believe",
    "if i recall",
    "if i remember",
    "something like",
    "i'm not completely sure",
    "i'm not certain"
)

def analyze_confidence(user_answer: str) -> List[str]:
    """
    Analyzes the candidate's raw answer string for confidence signals.
    
    Parameters
    ----------
    user_answer: str
        The candidate's raw answer string.
        
    Returns
    -------
    List[str]
        A list of confidence flags, such as ["hedging"]. Returns an empty list
        if no signals are detected.
    """
    flags: List[str] = []
    
    if not user_answer:
        return flags
        
    text_lower = user_answer.lower()
    
    for phrase in _HEDGING_PHRASES:
        if phrase in text_lower:
            flags.append("hedging")
            break  # We only need to flag it once
            
    return flags
