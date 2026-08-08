import json
import os
from typing import Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def _load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# In-memory cache — loaded once at startup, reused for every request
CURRICULUM: Dict[str, Any] = _load_json('curriculum.json')
CANDIDATES: Dict[str, Any] = _load_json('candidates.json')

# Pre-built O(1) lookup dict: {day_number: day_object}
# Avoids O(n) linear scan through all 31 days on every evaluate_and_ask call
_DAY_LOOKUP: Dict[int, Dict[str, Any]] = {
    d['day']: d for d in CURRICULUM.get('days', [])
}

def get_day_objectives(day_number: int) -> Optional[Dict[str, Any]]:
    """
    Return the full curriculum day object for a given day number.
    Includes title, type, tools list, and learning objectives.
    Returns None if the day is not found in the curriculum.
    """
    return _DAY_LOOKUP.get(day_number)
