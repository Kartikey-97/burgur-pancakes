import time
from typing import List, Dict, Any, Optional
from models import CandidateMission
from ai_layer_interface import evaluate_and_ask, generate_opening_question, is_off_topic, generate_feedback
import data_loader

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_module_for_day(day: int, curriculum: Dict[str, Any]) -> int:
    """Return the module number that contains the given day, or -1 if not found."""
    for module in curriculum.get('modules', []):
        days = module.get('days', [])
        if len(days) == 2 and days[0] <= day <= days[1]:
            return module.get('n', -1)
    return -1

def get_day_obj(day: int) -> dict:
    """
    Fetch the full curriculum day object (title, objectives, tools).
    Falls back to a minimal placeholder if the day is not in the curriculum.
    This is passed to Person B's evaluate_and_ask so the LLM has real context.
    """
    full_day = data_loader.get_day_objectives(day)
    if full_day:
        return full_day
    return {"day": day, "title": f"Day {day}"}

def select_opener_and_pool(missions: List[CandidateMission]) -> tuple[Optional[int], List[int]]:
    """
    Pick the opening topic (easiest passed day) and return the full unvisited pool.
    Returns (None, []) if the candidate has no passed missions.
    """
    passed_missions = [m for m in missions if m.passed]
    if not passed_missions:
        return None, []

    opener = next((m for m in passed_missions if m.attempts <= 1), None)
    if not opener:
        opener = min(passed_missions, key=lambda m: m.attempts)

    unvisited = [m.day for m in passed_missions if m.day != opener.day]
    return opener.day, unvisited

def select_next_topic(
    current_topic: int,
    score: float,
    unvisited: List[int],
    curriculum: Dict[str, Any]
) -> Optional[int]:
    """
    Adaptive topic routing engine.
    - Score < 2.5 (struggling): pivot to an easier, earlier prerequisite day.
    - Score >= 3.5 (excelling): skip ahead to an advanced module (6 or 7).
    - Otherwise: pick the next chronological day from a different module for breadth.
    Returns None if there are no topics left.
    """
    if not unvisited:
        return None

    def get_mod(d: int) -> int:
        return get_module_for_day(d, curriculum)

    current_mod = get_mod(current_topic)
    sorted_unvisited = sorted(unvisited)

    if score < 2.5:
        # Pivot backwards — find the latest day that's still earlier than current
        easier = [d for d in sorted_unvisited if d < current_topic]
        if easier:
            return easier[-1]  # Closest prerequisite

    elif score >= 3.5:
        # Pivot forward — jump to advanced modules
        advanced = [d for d in sorted_unvisited if get_mod(d) in (6, 7)]
        if advanced:
            return advanced[0]
        # Fallback: any day more than 5 days ahead
        far_ahead = [d for d in sorted_unvisited if d > current_topic + 5]
        if far_ahead:
            return far_ahead[0]

    # Standard: next chronological day from a different module (ensures breadth)
    for d in sorted_unvisited:
        if get_mod(d) != current_mod:
            return d

    # Last resort: just the next chronological day
    return sorted_unvisited[0]


# ---------------------------------------------------------------------------
# Main State Machine
# ---------------------------------------------------------------------------

def process_turn(session_state: dict, candidate_data: dict, user_message: str, curriculum: dict) -> dict:
    """
    Main state machine. Call once per HTTP request.
    Mutates session_state in place. Returns the response dict for the API.
    """
    phase = session_state.get('phase', 'INIT')

    # --- Off-topic pre-filter (only during active interview) ---
    if phase == 'INTERVIEWING' and user_message and is_off_topic(user_message):
        return {
            "reply": "I'm not sure I follow. Could you elaborate on how that relates to the question?",
            "done": False
        }

    # ------------------------------------------------------------------
    # INIT — first call, no candidate answer yet
    # ------------------------------------------------------------------
    if phase == 'INIT':
        candidate_missions_data = candidate_data.get('missions', [])
        missions = [CandidateMission(**m) for m in candidate_missions_data]
        opener_day, unvisited = select_opener_and_pool(missions)

        if opener_day is None:
            # Candidate has no passed missions — graceful degradation
            opener_day_obj = {"day": 0, "title": "General AI Engineering"}
            opener_question = "Welcome! Since you're new to the cohort material, let's have a general conversation about what you know about AI engineering. What draws you to this field?"
            session_state.update({
                'unvisited_topics': [],
                'current_topic': 0,
                'questions_asked': 0,
                'distinct_days_covered': 0,
                'followups_used_this_topic': 0,
                'theta': 0.0,
                'history': [],
                'pending_question': opener_question,
                'phase': 'INTERVIEWING',
                'last_question_timestamp': time.time(),
                'cheat_flags': 0,
            })
            return {"reply": opener_question, "done": False}

        try:
            opener_question = generate_opening_question(candidate_data, f"Day {opener_day}")
        except Exception as e:
            print(f"[WARN] AI Layer Error (INIT): {e}")
            opener_question = "Welcome to the interview! Let's start. Can you tell me about a recent AI project you built?"

        session_state.update({
            'unvisited_topics': unvisited,
            'current_topic': opener_day,
            'questions_asked': 0,
            'distinct_days_covered': 1,
            'followups_used_this_topic': 0,
            'theta': 0.0,
            'history': [],
            'pending_question': opener_question,
            'phase': 'INTERVIEWING',
            'last_question_timestamp': time.time(),
            'cheat_flags': 0,
        })

        return {"reply": opener_question, "done": False}

    # ------------------------------------------------------------------
    # INTERVIEWING — standard turn
    # ------------------------------------------------------------------
    elif phase == 'INTERVIEWING':
        current_topic = session_state['current_topic']
        day_obj = get_day_obj(current_topic)  # Full curriculum context for Person B

        # --- Cheat Detection ---
        last_timestamp = session_state.get('last_question_timestamp', time.time())
        latency = time.time() - last_timestamp
        cheat_detected = latency < 5.0 and len(user_message or '') > 150

        final_answer = user_message
        if cheat_detected:
            session_state['cheat_flags'] = session_state.get('cheat_flags', 0) + 1
            print(f"[CHEAT DETECTED] {latency:.1f}s / {len(user_message)} chars (total flags: {session_state['cheat_flags']})")
            final_answer = (
                f"[SYSTEM ALERT: Answer submitted in {latency:.1f}s with {len(user_message)} chars. "
                f"Potential copy-paste (flag #{session_state['cheat_flags']}). "
                f"Ask a highly specific, high-pressure follow-up to verify genuine understanding.]\n\n"
                f"{user_message}"
            )

        # --- LLM Evaluation Call ---
        try:
            evaluation = evaluate_and_ask(
                pending_question=session_state['pending_question'],
                answer=final_answer,
                day_obj=day_obj,
                candidate_profile=candidate_data,
                theta=session_state['theta'],
                history=session_state['history']
            )
        except Exception as e:
            print(f"[ERROR] AI Layer Error during evaluate_and_ask: {e}")
            # On AI failure: log the turn with a neutral score and skip topic gracefully
            session_state['history'].append({
                "day": current_topic,
                "question": session_state['pending_question'],
                "answer": user_message,
                "score": 2.0,  # Neutral score
                "notable_quote": "",
                "cheat_flagged": cheat_detected,
                "ai_error": True
            })
            session_state['questions_asked'] += 1
            # Skip to next topic
            next_topic = select_next_topic(current_topic, 2.0, session_state['unvisited_topics'], curriculum)
            if next_topic:
                session_state['unvisited_topics'].remove(next_topic)
                session_state['current_topic'] = next_topic
                session_state['distinct_days_covered'] += 1
            else:
                session_state['current_topic'] = None
            session_state['last_question_timestamp'] = time.time()
            return {"reply": "I see. Let's move on to the next topic. What can you tell me about your approach to production AI systems?", "done": False}

        # --- Update theta (IRT approximation) ---
        LEARNING_RATE = 0.5
        actual_score = evaluation.get('score', 2.0)
        expected_score = 2.0  # Neutral baseline
        session_state['theta'] += LEARNING_RATE * (actual_score / 4.0 - expected_score / 4.0)

        # --- Append to history (clean answer, not the injected prompt) ---
        session_state['history'].append({
            "day": current_topic,
            "question": session_state['pending_question'],
            "answer": user_message,
            "score": actual_score,
            "notable_quote": evaluation.get('notable_quote', ""),
            "cheat_flagged": cheat_detected,
        })

        session_state['questions_asked'] += 1
        needs_followup = evaluation.get('needs_followup', False)

        # --- Topic Routing ---
        if not needs_followup or session_state['followups_used_this_topic'] >= 2:
            next_topic = select_next_topic(current_topic, actual_score, session_state['unvisited_topics'], curriculum)
            if next_topic:
                session_state['current_topic'] = next_topic
                session_state['unvisited_topics'].remove(next_topic)
                session_state['distinct_days_covered'] += 1
            else:
                session_state['current_topic'] = None
            session_state['followups_used_this_topic'] = 0
        else:
            session_state['followups_used_this_topic'] += 1

        next_question = evaluation.get('next_question', "Let's continue. What else did you learn during the cohort?")
        session_state['pending_question'] = next_question
        session_state['last_question_timestamp'] = time.time()

        # --- Termination Check ---
        questions_done = session_state['questions_asked'] >= 8
        days_done = session_state['distinct_days_covered'] >= 4
        topics_exhausted = not session_state['current_topic']

        if (questions_done and days_done) or topics_exhausted:
            # Transition to CLOSING and immediately generate feedback
            session_state['phase'] = 'CLOSING'
            try:
                feedback = generate_feedback(candidate_data, session_state['history'])
            except Exception as e:
                print(f"[ERROR] Feedback generation failed: {e}")
                feedback = {
                    "summary": "Interview complete. Review your performance notes.",
                    "strengths": ["Completed the interview"],
                    "gaps": ["Could not generate detailed feedback"],
                    "next": ["Review the cohort curriculum"]
                }
            return {
                "reply": "Thank you for your time today. I have prepared your feedback report below.",
                "done": True,
                "feedback": feedback
            }

        return {"reply": next_question, "done": False}

    # ------------------------------------------------------------------
    # CLOSING — in case client calls the API again after interview ends
    # ------------------------------------------------------------------
    elif phase == 'CLOSING':
        try:
            feedback = generate_feedback(candidate_data, session_state['history'])
        except Exception as e:
            print(f"[ERROR] Feedback generation failed: {e}")
            feedback = {
                "summary": "Interview complete.",
                "strengths": [],
                "gaps": [],
                "next": []
            }
        return {
            "reply": "Your interview is already complete. Here is your feedback.",
            "done": True,
            "feedback": feedback
        }
