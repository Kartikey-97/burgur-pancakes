import time
import json
from typing import List, Dict, Any, Optional
from models import CandidateMission
from ai_layer_interface import evaluate_and_ask_stream, generate_opening_question, is_off_topic, generate_feedback
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
    full_day = data_loader.get_day_objectives(day)
    if full_day:
        return full_day
    return {"day": day, "title": f"Day {day}"}

def select_opener_and_pool(missions: List[CandidateMission]) -> tuple[Optional[int], List[int]]:
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
    if not unvisited:
        return None

    def get_mod(d: int) -> int:
        return get_module_for_day(d, curriculum)

    current_mod = get_mod(current_topic)
    sorted_unvisited = sorted(unvisited)

    if score < 2.5:
        easier = [d for d in sorted_unvisited if d < current_topic]
        if easier:
            return easier[-1]

    elif score >= 3.5:
        advanced = [d for d in sorted_unvisited if get_mod(d) in (6, 7)]
        if advanced:
            return advanced[0]
        far_ahead = [d for d in sorted_unvisited if d > current_topic + 5]
        if far_ahead:
            return far_ahead[0]

    for d in sorted_unvisited:
        if get_mod(d) != current_mod:
            return d

    return sorted_unvisited[0]


# ---------------------------------------------------------------------------
# Main State Machine (Streaming)
# ---------------------------------------------------------------------------

def process_turn_stream(session_state: dict, candidate_data: dict, user_message: str, curriculum: dict):
    """
    Main state machine, yielding Server-Sent Events (SSE).
    """
    def yield_text(text: str):
        yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"

    def yield_done(reply: str, done: bool, feedback: dict = None):
        payload = {"type": "done", "reply": reply, "done": done, "theta": session_state.get('theta', 0.0)}
        if feedback:
            payload["feedback"] = feedback
        yield f"data: {json.dumps(payload)}\n\n"

    phase = session_state.get('phase', 'INIT')

    # --- Off-topic pre-filter ---
    if phase == 'INTERVIEWING' and user_message and is_off_topic(user_message):
        reply = "I'm not sure I follow. Could you elaborate on how that relates to the question?"
        yield from yield_text(reply)
        yield from yield_done(reply, False)
        return

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------
    if phase == 'INIT':
        candidate_missions_data = candidate_data.get('missions', [])
        missions = [CandidateMission(**m) for m in candidate_missions_data]
        opener_day, unvisited = select_opener_and_pool(missions)

        if opener_day is None:
            opener_question = "Welcome! Since you're new to the cohort material, let's have a general conversation about what you know about AI engineering. What draws you to this field?"
            session_state.update({
                'unvisited_topics': [], 'current_topic': 0, 'questions_asked': 0, 'distinct_days_covered': 0,
                'followups_used_this_topic': 0, 'theta': 0.0, 'history': [], 'pending_question': opener_question,
                'phase': 'INTERVIEWING', 'last_question_timestamp': time.time(), 'cheat_flags': 0,
            })
            yield from yield_text(opener_question)
            yield from yield_done(opener_question, False)
            return

        try:
            opener_question = generate_opening_question(candidate_data, f"Day {opener_day}")
        except Exception as e:
            print(f"[WARN] AI Layer Error (INIT): {e}")
            opener_question = "Welcome to the interview! Let's start. Can you tell me about a recent AI project you built?"

        session_state.update({
            'unvisited_topics': unvisited, 'current_topic': opener_day, 'questions_asked': 0, 'distinct_days_covered': 1,
            'followups_used_this_topic': 0, 'theta': 0.0, 'history': [], 'pending_question': opener_question,
            'phase': 'INTERVIEWING', 'last_question_timestamp': time.time(), 'cheat_flags': 0,
        })
        yield from yield_text(opener_question)
        yield from yield_done(opener_question, False)
        return

    # ------------------------------------------------------------------
    # INTERVIEWING
    # ------------------------------------------------------------------
    elif phase == 'INTERVIEWING':
        current_topic = session_state['current_topic']
        day_obj = get_day_obj(current_topic)

        # --- Cheat Detection ---
        last_timestamp = session_state.get('last_question_timestamp', time.time())
        latency = time.time() - last_timestamp
        cheat_detected = latency < 5.0 and len(user_message or '') > 150

        final_answer = user_message
        if cheat_detected:
            session_state['cheat_flags'] = session_state.get('cheat_flags', 0) + 1
            final_answer = (
                f"[SYSTEM ALERT: Answer submitted in {latency:.1f}s with {len(user_message)} chars. "
                f"Potential copy-paste (flag #{session_state['cheat_flags']}). "
                f"Ask a highly specific, high-pressure follow-up to verify genuine understanding.]\n\n"
                f"{user_message}"
            )

        # --- Streaming Evaluation Call ---
        # The stream will output plain text: SCORE:, NEEDS_FOLLOWUP:, NOTABLE_QUOTE:, NEXT_QUESTION:
        accumulated_text = ""
        in_question_phase = False
        next_question_str = ""

        try:
            stream = evaluate_and_ask_stream(
                pending_question=session_state['pending_question'],
                answer=final_answer,
                day_obj=day_obj,
                candidate_profile=candidate_data,
                theta=session_state['theta'],
                history=session_state['history']
            )

            for chunk in stream:
                if in_question_phase:
                    next_question_str += chunk
                    yield from yield_text(chunk)
                else:
                    accumulated_text += chunk
                    marker = "NEXT_QUESTION:"
                    idx = accumulated_text.find(marker)
                    if idx != -1:
                        in_question_phase = True
                        rest = accumulated_text[idx + len(marker):].lstrip()
                        if rest:
                            next_question_str += rest
                            yield from yield_text(rest)

        except Exception as e:
            print(f"[ERROR] AI Layer Error during evaluate_and_ask_stream: {e}")
            next_question_str = "I see. Let's move on to the next topic. What can you tell me about your approach to production AI systems?"
            yield from yield_text(next_question_str)
            accumulated_text = f"SCORE: 2.0\nNEEDS_FOLLOWUP: false\nNOTABLE_QUOTE: \nNEXT_QUESTION:\n{next_question_str}"

        # Now parse the accumulated text to get metadata
        score = 2.0
        needs_followup = False
        notable_quote = ""

        for line in accumulated_text.split("\n"):
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    score = float(line.replace("SCORE:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("NEEDS_FOLLOWUP:"):
                val = line.replace("NEEDS_FOLLOWUP:", "").strip().lower()
                needs_followup = val == "true"
            elif line.startswith("NOTABLE_QUOTE:"):
                notable_quote = line.replace("NOTABLE_QUOTE:", "").strip()

        # Update theta (IRT approximation)
        LEARNING_RATE = 0.5
        session_state['theta'] += LEARNING_RATE * (score / 4.0 - 2.0 / 4.0)

        session_state['history'].append({
            "day": current_topic,
            "question": session_state['pending_question'],
            "answer": user_message,
            "score": score,
            "notable_quote": notable_quote,
            "cheat_flagged": cheat_detected,
        })
        session_state['questions_asked'] += 1

        # Topic Routing
        if not needs_followup or session_state['followups_used_this_topic'] >= 2:
            next_topic = select_next_topic(current_topic, score, session_state['unvisited_topics'], curriculum)
            if next_topic:
                session_state['current_topic'] = next_topic
                session_state['unvisited_topics'].remove(next_topic)
                session_state['distinct_days_covered'] += 1
            else:
                session_state['current_topic'] = None
            session_state['followups_used_this_topic'] = 0
        else:
            session_state['followups_used_this_topic'] += 1

        session_state['pending_question'] = next_question_str.strip()
        session_state['last_question_timestamp'] = time.time()

        # Termination Check
        questions_done = session_state['questions_asked'] >= 8
        days_done = session_state['distinct_days_covered'] >= 4
        topics_exhausted = not session_state['current_topic']

        if (questions_done and days_done) or topics_exhausted:
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
            yield from yield_done(next_question_str.strip(), True, feedback)
            return

        yield from yield_done(next_question_str.strip(), False)
        return

    # ------------------------------------------------------------------
    # CLOSING
    # ------------------------------------------------------------------
    elif phase == 'CLOSING':
        reply = "Your interview is already complete. Here is your feedback."
        try:
            feedback = generate_feedback(candidate_data, session_state['history'])
        except Exception:
            feedback = {"summary": "Interview complete.", "strengths": [], "gaps": [], "next": []}
        
        yield from yield_text(reply)
        yield from yield_done(reply, True, feedback)
        return

