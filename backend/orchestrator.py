from typing import List, Dict, Any
from models import CandidateMission
from ai_layer_interface import evaluate_and_ask, generate_opening_question, is_off_topic, generate_feedback

def get_module_for_day(day: int, curriculum: Dict[str, Any]) -> int:
    for module in curriculum.get('modules', []):
        days = module.get('days', [])
        if len(days) == 2 and days[0] <= day <= days[1]:
            return module.get('n', -1)
    return -1

def select_topics(missions: List[CandidateMission], curriculum: Dict[str, Any]) -> List[int]:
    """
    Select topics for the interview based on deterministic rules:
    - Only passed missions.
    - One easy opener (attempts <= 1).
    - Sort remaining by interest_score.
    - Enforce distinct modules for breadth.
    - Handle sparse candidates (< 4 passed missions).
    Returns a list of day numbers representing the topic queue.
    """
    passed_missions = [m for m in missions if m.passed]
    
    if not passed_missions:
        return []

    # Find the opener
    opener = None
    for m in passed_missions:
        if m.attempts <= 1:
            opener = m
            break
    
    # If no easy opener exists, pick the one with lowest attempts
    if not opener:
        opener = min(passed_missions, key=lambda m: m.attempts)
        
    selected_days = [opener.day]
    selected_modules = {get_module_for_day(opener.day, curriculum)}
    
    # Pool for remaining topics (ensuring opener is not double-counted)
    remaining_pool = [m for m in passed_missions if m.day != opener.day]
    
    def calculate_interest(m: CandidateMission) -> int:
        score = 0
        if m.attempts >= 4:
            score += 2
        elif m.attempts in (2, 3):
            score += 1
            
        module_num = get_module_for_day(m.day, curriculum)
        # Agentic AI/MCP is module 6, Evaluation/Security/Deployment is module 7
        if module_num in (6, 7):
            score += 1
            
        return score
        
    # Sort remaining pool by interest score descending
    remaining_pool.sort(key=calculate_interest, reverse=True)
    
    # Fill remaining slots ensuring module diversity
    for m in remaining_pool:
        if len(selected_days) >= 5:
            break
            
        mod = get_module_for_day(m.day, curriculum)
        if mod not in selected_modules:
            selected_days.append(m.day)
            selected_modules.add(mod)
            
    # If we still need more topics to hit our target (e.g., ran out of distinct modules),
    # relax the distinct module constraint for the remaining ones.
    if len(selected_days) < 5:
        for m in remaining_pool:
            if len(selected_days) >= 5:
                break
            if m.day not in selected_days:
                selected_days.append(m.day)
                
    return selected_days

def process_turn(session_state: dict, candidate_data: dict, user_message: str, curriculum: dict) -> dict:
    """
    Main state machine orchestrator function for the interview.
    Updates session_state in place and returns a dict with the response to send back to the user.
    """
    phase = session_state.get('phase', 'INIT')
    
    # 1. Pre-filter
    if phase == 'INTERVIEWING' and is_off_topic(user_message):
        return {
            "reply": "I'm not sure I follow. Could you elaborate on how that relates to the question?",
            "done": False
        }
    
    if phase == 'INIT':
        # Initialization
        candidate_missions_data = candidate_data.get('missions', [])
        missions = [CandidateMission(**m) for m in candidate_missions_data]
        topics = select_topics(missions, curriculum)
        
        session_state['topic_queue'] = topics
        session_state['topic_index'] = 0
        session_state['questions_asked'] = 0
        session_state['distinct_days_covered'] = 0
        session_state['followups_used_this_topic'] = 0
        session_state['theta'] = 0.0
        session_state['history'] = []
        
        first_topic = topics[0] if topics else "general software engineering"
        question = generate_opening_question(candidate_data, f"Day {first_topic}")
        
        session_state['pending_question'] = question
        session_state['phase'] = 'INTERVIEWING'
        session_state['distinct_days_covered'] = 1
        
        session_state['history'].append({"role": "assistant", "content": question})
        
        return {
            "reply": question,
            "done": False
        }
    
    elif phase == 'INTERVIEWING':
        # Evaluate user answer
        session_state['history'].append({"role": "user", "content": user_message})
        
        # Prepare context for next question if we don't need a followup
        current_topic = session_state['topic_queue'][session_state['topic_index']]
        next_topic_idx = session_state['topic_index'] + 1
        next_topic = session_state['topic_queue'][next_topic_idx] if next_topic_idx < len(session_state['topic_queue']) else None
        next_topic_context = f"Day {next_topic}" if next_topic else None
        
        # LLM Call
        try:
            evaluation = evaluate_and_ask(
                candidate_data, 
                session_state['history'], 
                session_state['pending_question'], 
                user_message,
                next_topic_context=next_topic_context
            )
        except Exception as e:
            # Fallback handling
            print(f"AI Layer Error: {e}")
            return {
                "reply": "I see. Let's move on to the next topic.",
                "done": False
            }
        
        # Update theta (simple IRT approximation)
        LEARNING_RATE = 0.5
        actual_score = evaluation.get('score', 2.0)
        # expected score could be a function of theta, mock it as 2.0 for now
        expected_score = 2.0
        session_state['theta'] += LEARNING_RATE * (actual_score / 4.0 - expected_score / 4.0)
        
        # Determine next state
        session_state['questions_asked'] += 1
        
        needs_followup = evaluation.get('needs_followup', False)
        if not needs_followup or session_state['followups_used_this_topic'] >= 2:
            # Move to next topic
            session_state['topic_index'] += 1
            session_state['followups_used_this_topic'] = 0
            if session_state['topic_index'] < len(session_state['topic_queue']):
                session_state['distinct_days_covered'] += 1
        else:
            session_state['followups_used_this_topic'] += 1
            
        next_question = evaluation.get('next_question', "Let's move on.")
        session_state['pending_question'] = next_question
        session_state['history'].append({"role": "assistant", "content": next_question})
        
        # Termination check
        if session_state['questions_asked'] >= 8 and session_state['distinct_days_covered'] >= 4:
            session_state['phase'] = 'CLOSING'
            
        return {
            "reply": next_question,
            "done": False
        }
        
    elif phase == 'CLOSING':
        feedback = generate_feedback(candidate_data, session_state['history'])
        return {
            "reply": "Thank you for your time. Here is your feedback.",
            "done": True,
            "feedback": feedback
        }
