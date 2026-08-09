import re

with open("orchestrator.py", "r") as f:
    content = f.read()

# Replace import
content = content.replace(
    "from ai_layer_interface import evaluate_and_ask, generate_opening_question, is_off_topic, generate_feedback",
    "from ai_layer_interface import evaluate_and_ask_stream, generate_opening_question, is_off_topic, generate_feedback\nimport json"
)

# Rename process_turn
content = content.replace(
    "def process_turn(session_state: dict, candidate_data: dict, user_message: str, curriculum: dict) -> dict:",
    "def process_turn_stream(session_state: dict, candidate_data: dict, user_message: str, curriculum: dict):"
)

# Replace returns with yields
def replace_return_with_yield(match):
    # This might be tricky with regex, so I'll write the replacement manually using Python code parsing or specific replacements
    pass

