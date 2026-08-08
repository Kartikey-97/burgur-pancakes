import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_curriculum():
    path = os.path.join(DATA_DIR, 'curriculum.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_candidates():
    path = os.path.join(DATA_DIR, 'candidates.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

CURRICULUM = load_curriculum()
CANDIDATES = load_candidates()

def get_day_objectives(day_number: int):
    for day in CURRICULUM.get('days', []):
        if day.get('day') == day_number:
            return day
    return None
