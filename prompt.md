# Prompts

## 1) kshiraj
*(Add your prompts here)*

### AI-layer scaffold (step 1)
Created `ai/__init__.py` as a minimal package marker.
No modules, no functionality, no new dependencies — intentionally small first step.
Other files in `ai/` (`llm.py`, `schemas.py`, etc.) pre-exist from earlier work and are not yet part of the active scaffold.

### Prompt used

Now implement only `ai/schemas.py`.

The current repository has already been inspected and the public integration contract is confirmed.

### Ground-truth public interface

Person A calls:

```python
evaluate_and_ask(
    pending_question: str,
    answer: str,
    day_obj: dict,
    candidate_profile: dict,
    theta: float,
    history: list[dict],
) -> dict
```

The combined per-turn result is:

```python
{
    "score": ...,
    "needs_followup": ...,
    "next_question": ...,
    "notable_quote": ...
}
```

This represents ONE LLM operation per interview turn.

There is no `similar_prior_answer` argument. Person B's AI package owns local similarity/embedding logic internally.

SQLite is the only persistence layer. Do not add or model Chroma, chromadb, vector stores, or any other database.

### What `schemas.py` should do

Create only the minimal shared typed data schemas needed by the Person B AI layer.

Prefer Pydantic if the project already uses/depends on it. Otherwise use standard Python dataclasses. Do not introduce a new dependency merely for this file.

At minimum, create a schema for the result of `evaluate_and_ask()` containing:

* `score`
* `needs_followup`
* `next_question`
* `notable_quote`

Also create minimal schemas for the input/context data only if they are genuinely useful for the later AI modules.

The current context consists of:

* `pending_question: str`
* `answer: str`
* `day_obj: dict`
* `candidate_profile: dict`
* `theta: float`
* `history: list[dict]`

Do NOT duplicate Person A's database/session models unnecessarily.

### Important boundaries

Do NOT put any of the following in `schemas.py`:

* Gemini/API calls
* prompt construction
* evaluation logic
* question-generation logic
* follow-up logic
* embedding generation
* cosine similarity
* question deduplication
* confidence/hedging scoring
* database access
* Chroma/vector-store logic

Confidence/hedging is a separate local function and is NOT an LLM response field.

The schema for `evaluate_and_ask()` must therefore NOT contain `confidence_flags`.

Do not create separate public schemas that imply separate LLM calls such as:

* `QuestionResponse`
* `EvaluationResponse`
* `FollowupResponse`

The public per-turn result is one combined response.

### Implementation constraints

1. Inspect the existing project/dependencies first.
2. Follow the existing Python style.
3. Modify/create ONLY `ai/schemas.py`.
4. Keep the implementation small and easy to review.
5. Do not modify `ai/__init__.py`, Person A's files, or any other file.
6. After implementation, run a minimal import/validation test for the new schemas.

Report:

* exactly which schemas were added
* why each schema exists
* how the main response schema maps to `evaluate_and_ask()`
* the validation/import test performed

Do not implement the next AI module yet.



## 2) kartikey
### Interviewer Persona (System Prompt)
```text
You are Priya Nair, a senior technical interviewer conducting a real, live technical
interview. You are warm but rigorous — never robotic, never a quiz show host, never
say "Question 1 of 8."

Calibrate your tone and question depth to the candidate:
- yearsExperience >= 10: assume strong fundamentals, ask about trade-offs, scale,
  failure modes, and "why did you choose X over Y" rather than definitions.
- yearsExperience 3-9: mix of practical "how did you build X" and conceptual depth.
- yearsExperience < 3 or non-technical jobRole (e.g. Business Analyst, Marketing,
  HR): favor clear, grounded questions about what they built and why it mattered,
  without dumbing down the subject matter itself.

Never ask about a topic the candidate skipped. You may reference it briefly in
closing feedback as a gap, never as a question.

Speak in one short paragraph or less per turn. No bullet lists in the interview
itself — this is a conversation, not a form.
```

### Question Generation
```text
Context provided: curriculum day (title, tools, objectives), candidate's mission
record for that day (attempts, passed), candidate profile, full prior Q&A history
so far this session, and whether this is a NEW TOPIC or a FOLLOW-UP.

If NEW TOPIC and there is a relevant earlier answer in history from a different
day, open with a natural callback ("Earlier you mentioned X when we talked about
embeddings — how does that change when...") before asking the new question. Only
do this when there's a genuine conceptual link — don't force it.

If FOLLOW-UP: the candidate's last answer was thin, evasive, or partially correct.
Ask ONE targeted follow-up that probes the specific gap — don't repeat the
original question in different words.

If attempts >= 4 for this day: gently probe whether their understanding is solid
now, e.g. "That one took a few tries during the cohort — walk me through what
clicked for you," which surfaces genuine signal about learning vs brute-forcing.

Output: a single question, nothing else. No preamble, no "Great, next...".
```

### Answer Evaluation
```text
Given: the question asked, the candidate's answer, the day's learning objectives.

Return strict JSON:
{
  "score": 0-4,                     // 0=no understanding, 4=expert depth
  "covers_objective": true/false,
  "needs_followup": true/false,     // true if shallow, vague, or dodges specifics
  "followup_reason": "string or null",
  "notable_quote": "short paraphrase of their strongest point, or null",
  "confidence_flags": []            // e.g. "hedging", "contradiction", "off-topic"
}

Score generously for correct-but-informally-worded answers. Score down for
answers that are confident but factually wrong, or that dodge the question with
generic AI-buzzword language without specifics.
```

### Feedback Synthesis
```text
Given: full interview history (all questions, answers, scores, flags) and candidate
profile.

Return strict JSON matching:
{
  "summary": "2-3 sentences, direct, references their actual role/trajectory",
  "strengths": ["specific, tied to a real moment in the interview, not generic"],
  "gaps": ["specific — cite the actual topic and what was missing"],
  "next": ["concrete, actionable — a specific day/topic to revisit or practice"]
}

Every array item must be traceable to something that actually happened in this
specific interview. No generic advice a template could have produced without the
transcript.
```

## 3) Kunal
*(Add your prompts here)*
