"""
ai/schemas.py — Typed data schemas for the AI layer.

Deliberately minimal: only the types needed by the AI modules themselves.
Person A's database/session models live in backend/models.py and are not
duplicated here.
"""

from typing import Optional
from pydantic import BaseModel


class TurnResult(BaseModel):
    """
    The combined per-turn result returned by evaluate_and_ask().

    Maps directly to the public contract:

        evaluate_and_ask(
            pending_question, answer, day_obj,
            candidate_profile, theta, history,
        ) -> dict

    All four fields correspond to the agreed response shape:

        {
            "score":         int (0-4),
            "needs_followup": bool,
            "next_question": str,
            "notable_quote": str | None,
        }

    Confidence/hedging scoring is handled internally by a separate local
    function and is NOT part of this response schema.
    """

    score: int
    needs_followup: bool
    next_question: str
    notable_quote: Optional[str] = None
