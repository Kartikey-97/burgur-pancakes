"""
ai/llm.py — Minimal, dependency-free LLM client for the AI layer.

This module handles the physical HTTP request to the LLM API and parses
the response into the strictly-typed internal schema. It uses only the
`requests` and `pydantic` libraries already present in the project.
"""

import os
import requests
from typing import Optional
from pydantic import BaseModel, ValidationError

class LLMTurnResponse(BaseModel):
    """
    The strict internal schema expected from the LLM on every turn.
    
    This must match the fields expected by TurnResult, but is defined here
    independently so the LLM layer is isolated from the public contract.
    """
    score: int
    needs_followup: bool
    next_question: str
    notable_quote: Optional[str] = None


def call_llm(system_prompt: str, user_prompt: str) -> LLMTurnResponse:
    """
    Executes a synchronous request to the Gemini API and parses the JSON response.
    
    Requires the GEMINI_API_KEY environment variable.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [{
            "parts": [{"text": user_prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30.0
    )
    response.raise_for_status()
    
    data = response.json()
    try:
        content_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return LLMTurnResponse.model_validate_json(content_text)
    except (KeyError, IndexError) as e:
        raise ValueError(f"Unexpected response structure from LLM API: {e}")
    except ValidationError as e:
        raise ValueError(f"LLM output failed schema validation: {e}")
