"""
ai/off_topic.py — Local pre-filter for non-substantive interview answers.

The public entry point is :func:`is_off_topic`, which matches the signature
expected by ``backend/ai_layer_interface.py``.

Design constraints
------------------
* **Fast** — synchronous, no I/O, no network, no external dependencies.
* **Safe** — must never raise; an uncaught exception would crash the
  orchestrator's ``process_turn()`` with no try/except around this call.
* **Permissive** — a false positive silences a legitimate answer entirely:
  no LLM call, no score, no history entry.  Err on the side of letting
  borderline answers through.

What this filter catches
------------------------
Only surface-level signals that are unambiguously non-substantive,
detectable without question context or semantic knowledge:

1. Empty or whitespace-only input.
2. All non-whitespace characters are the same glyph (e.g. ``"aaaaaa"``,
   ``"!!!!!!!!"``).
3. Zero alphabetic characters — pure digit or symbol strings
   (e.g. ``"123456789"``, ``"<><><>"``).
4. One letter dominates > 75 % of all alphabetic characters, in strings
   with at least 8 alpha chars (keyboard mash, e.g. ``"aaaaaab"``).

What this filter deliberately does NOT catch
--------------------------------------------
* Single-word answers — ``"Yes"``, ``"No"``, ``"Python"``, ``"REST"``,
  ``"gibberish"`` all must reach the LLM; their relevance cannot be
  determined without knowing the question.
* Code-heavy or number-heavy answers — ``"x = 10 + y"``, ``"top_k = 10"``,
  ``"O(n^2) = O(n log n)"`` are legitimate technical responses.  Without
  question context, a low alphabetic-character ratio is not a reliable
  signal of noise.
* Semantically off-topic but grammatically valid answers — delegated to
  the LLM's ``confidence_flags: ["off-topic"]`` in the evaluation response.
"""

from typing import Final

# ── Thresholds ────────────────────────────────────────────────────────────────

# If a single alphabetic character makes up more than this fraction of all
# alphabetic characters, the string is likely keyboard-mashed gibberish.
# Applied only when there are at least _REPEAT_RATIO_MIN_ALPHA alpha chars.
_MAX_DOMINANT_CHAR_RATIO: Final[float] = 0.75
_REPEAT_RATIO_MIN_ALPHA: Final[int] = 8


# ── Public API ────────────────────────────────────────────────────────────────

def is_off_topic(user_answer: str) -> bool:
    """
    Return ``True`` only when *user_answer* is clearly non-substantive.

    Parameters
    ----------
    user_answer:
        The candidate's raw answer string, exactly as received from the
        HTTP request body.

    Returns
    -------
    bool
        ``True``  → reject the turn; the orchestrator will prompt the
                    candidate to elaborate without calling the LLM.
        ``False`` → proceed normally; ``evaluate_and_ask()`` will run.
    """
    try:
        return _check(user_answer)
    except Exception:  # safety net — this call site has no try/except wrapper
        return False


# ── Internal logic ────────────────────────────────────────────────────────────

def _check(text: str) -> bool:
    """Run all heuristic checks, cheapest first."""

    # 1. Empty or whitespace-only ─────────────────────────────────────────────
    stripped = text.strip()
    if not stripped:
        return True

    # 2. All non-whitespace characters are the same glyph ────────────────────
    #    Catches: "aaaaaa", "......", "!!!!!!!!"
    non_ws = stripped.replace(" ", "")
    if len(set(non_ws)) <= 1:
        return True

    # 3. Zero alphabetic characters — pure digit / symbol string ──────────────
    #    Catches: "123456789", "<><><>"
    #    Does not affect: "x = 10 + y" (has x, y), "O(n)" (has O, n)
    alpha_count = sum(1 for c in stripped if c.isalpha())
    if alpha_count == 0:
        return True

    # 4. One alphabetic character dominates (keyboard mashing) ────────────────
    #    Catches: "aaaaaab" (a: 6/7 ≈ 0.86), "qqqqqqqq" (q: 8/8 = 1.0).
    #    Does not catch normal text or code: "committee", "x = 10 + y".
    alpha_chars = [c.lower() for c in stripped if c.isalpha()]
    if len(alpha_chars) >= _REPEAT_RATIO_MIN_ALPHA:
        most_common = max(alpha_chars.count(c) for c in set(alpha_chars))
        if most_common / len(alpha_chars) > _MAX_DOMINANT_CHAR_RATIO:
            return True

    return False
