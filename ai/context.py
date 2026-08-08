"""
ai/context.py — AI-side history types for the interview loop.

Person B owns the structure of interview history.  These types are used
internally by the AI modules (prompts, LLM calls, context assembly) and
are serialised into the opaque session-state JSON blob that backend/session.py
stores in SQLite.  No backend models are duplicated here.
"""

from typing import Optional
from pydantic import BaseModel

from ai.schemas import TurnResult


class HistoryEntry(BaseModel):
    """
    One completed interview turn, as stored in the session history.

    A turn is considered complete once evaluate_and_ask() has returned and
    the result has been accepted (follow-up or topic advance).  The entry
    is built directly from the inputs and the TurnResult so the prompt and
    question-generation modules can reconstruct full conversational context.

    Fields
    ------
    day:           Curriculum day number the question came from.
    question:      The question that was asked.
    answer:        The candidate's verbatim answer.
    score:         LLM-assigned quality score, 0-4, from TurnResult.
    notable_quote: Strongest paraphrase from TurnResult (may be None).
    """

    day: int
    question: str
    answer: str
    score: int
    notable_quote: Optional[str] = None

    @classmethod
    def from_turn(
        cls,
        day: int,
        question: str,
        answer: str,
        result: TurnResult,
    ) -> "HistoryEntry":
        """
        Convenience constructor — build a HistoryEntry from a TurnResult.

        Usage (in service.py, once implemented):

            entry = HistoryEntry.from_turn(
                day=current_day,
                question=pending_question,
                answer=answer,
                result=turn_result,
            )
            history.append(entry.model_dump())
        """
        return cls(
            day=day,
            question=question,
            answer=answer,
            score=result.score,
            notable_quote=result.notable_quote,
        )
