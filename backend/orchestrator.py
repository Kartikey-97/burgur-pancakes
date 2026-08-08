from typing import List, Dict, Any
from models import CandidateMission

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
