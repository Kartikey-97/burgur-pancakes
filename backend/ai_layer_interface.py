from typing import Dict, Any, List

def evaluate_and_ask(
    pending_question: str,
    answer: str,
    day_obj: dict,
    candidate_profile: dict,
    theta: float,
    history: list[dict],
) -> dict:
    """
    Mock function for evaluating an answer and generating the next question.
    Returns:
        {
            "score": float, # 0.0 to 4.0
            "needs_followup": bool,
            "next_question": str,
            "notable_quote": str
        }
    """
    # Simple mock logic
    day_title = day_obj.get("title", "the topic") if day_obj else "the topic"
    return {
        "score": 3.0,
        "needs_followup": False,
        "next_question": f"This is a mock question for topic context: {day_title}",
        "notable_quote": answer[:20] if answer else ""
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
