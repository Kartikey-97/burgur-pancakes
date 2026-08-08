"""
ai/service.py — AI layer orchestrator for turn execution.

Assembles the context, calls the LLM via the internal client, and maps
the response to the public schema expected by the backend.
"""

import json
from typing import List, Dict, Optional
from ai.schemas import TurnResult
from ai.llm import call_llm
from ai.memory import find_similar_prior_answer
from ai.deduplication import is_duplicate_question

_SYSTEM_PROMPT = """You are Priya Nair, a senior technical interviewer conducting a real, live technical
interview. You are warm but rigorous — never robotic, never a quiz show host, never
say "Question 1 of 8."

Calibrate your tone and question depth to the candidate based on their profile:
- yearsExperience >= 10: assume strong fundamentals, ask about trade-offs, scale, failure modes.
- yearsExperience 3-9: mix of practical and conceptual depth.
- yearsExperience < 3 or non-technical jobRole: favor clear, grounded questions.

Never ask about a topic the candidate skipped.
Speak in one short paragraph or less per turn. No bullet lists.

EVALUATION & QUESTION GENERATION:
You must evaluate the candidate's last answer and generate the next question.
If the candidate's last answer was thin, evasive, or partially correct, ask ONE targeted follow-up that probes the specific gap.
Otherwise, move to a new topic based on the context provided.
If NEW TOPIC and there is a relevant earlier answer in history (provided in Memory Trigger), open with a natural callback before asking the new question. Only do this if there's a genuine conceptual link.

Return strict JSON matching this schema exactly:
{
  "score": integer (0-4, 0=no understanding, 4=expert depth),
  "needs_followup": boolean (true if shallow, vague, or dodges specifics),
  "next_question": string (A single question, nothing else. No preamble),
  "notable_quote": string or null (short paraphrase of their strongest point)
}
"""

def execute_turn(
    pending_question: str,
    answer: str,
    day_obj: dict,
    candidate_profile: dict,
    theta: float,
    history: list[dict]
) -> TurnResult:
    """
    Executes a single interview turn by composing context and calling the LLM.
    Returns the strict public TurnResult schema.
    """
    # 1. Semantic Memory Integration
    memory_match = find_similar_prior_answer(answer, history)
    
    # 2. Assemble context
    user_prompt = _build_user_prompt(
        pending_question, answer, day_obj, candidate_profile, theta, history, memory_match
    )
    
    # 3. Call LLM (Exactly ONE call)
    llm_response = call_llm(_SYSTEM_PROMPT, user_prompt)
    
    # 4. Question Deduplication (Zero-retry deterministic fallback)
    next_question = llm_response.next_question
    if is_duplicate_question(next_question, history):
        fallback_title = day_obj.get('title', 'this topic')
        next_question = f"Let's explore another aspect of {fallback_title}. What else can you tell me about your approach here?"
        
    # 5. Map internal LLM response to public TurnResult
    return TurnResult(
        score=llm_response.score,
        needs_followup=llm_response.needs_followup,
        next_question=next_question,
        notable_quote=llm_response.notable_quote
    )


def _build_user_prompt(
    pending_question: str,
    answer: str,
    day_obj: dict,
    candidate_profile: dict,
    theta: float,
    history: list[dict],
    memory_match: Optional[Dict]
) -> str:
    """Formats the raw parameters into a clean string for the LLM."""
    history_str = ""
    if not history:
        history_str = "No prior questions this session."
    else:
        for idx, entry in enumerate(history, 1):
            history_str += f"Turn {idx}:\n"
            history_str += f"  Q: {entry.get('question')}\n"
            history_str += f"  A: {entry.get('answer')}\n"
            history_str += f"  Score: {entry.get('score')}\n"

    memory_str = ""
    if memory_match:
        memory_str = (
            "Memory Trigger (Candidate previously discussed a related topic):\n"
            f"Prior Question: {memory_match.get('question')}\n"
            f"Prior Answer: {memory_match.get('answer')}\n"
        )

    # Assemble full context
    return f"""Context provided:
Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Current Topic / Day:
{json.dumps(day_obj, indent=2)}

Current Estimated Ability (theta): {theta}

Full Interview History:
{history_str}

{memory_str}
---
Pending Question:
{pending_question}

Candidate's Answer:
{answer}
"""
