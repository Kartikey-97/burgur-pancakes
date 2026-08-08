from typing import Dict, Any, List

def evaluate_and_ask(candidate: Dict[str, Any], history: List[Dict[str, str]], pending_question: str, user_answer: str, next_topic_context: str = None) -> Dict[str, Any]:
    """
    Mock function for evaluating an answer and generating the next question.
    Returns:
        {
            "score": float, # 0.0 to 4.0
            "covers_objective": bool,
            "needs_followup": bool,
            "followup_reason": str,
            "notable_quote": str,
            "confidence_flags": list,
            "next_question": str
        }
    """
    # Simple mock logic
    return {
        "score": 3.0,
        "covers_objective": True,
        "needs_followup": False,
        "followup_reason": "",
        "notable_quote": user_answer[:20] if user_answer else "",
        "confidence_flags": [],
        "next_question": f"This is a mock question for topic context: {next_topic_context}" if next_topic_context else "This is a mock follow-up question."
    }

def generate_opening_question(candidate: Dict[str, Any], topic_context: str) -> str:
    """
    Mock function for the initial opening question.
    """
    return f"Welcome! Let's start by talking about {topic_context}. Can you explain what you learned?"

def is_off_topic(user_answer: str) -> bool:
    """
    Mock function for local ML pre-filter.
    """
    if user_answer and "gibberish" in user_answer.lower():
        return True
    return False

def generate_feedback(candidate: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Mock function to synthesize final feedback report.
    Returns the Feedback dict matching the API response.
    """
    return {
        "summary": "Great job! You showed solid understanding.",
        "strengths": ["Clear communication", "Good grasp of fundamentals"],
        "gaps": ["Could dive deeper into trade-offs"],
        "next": ["Review advanced concepts"]
    }
