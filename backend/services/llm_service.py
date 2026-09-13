import os
import json

# This is a placeholder for the actual LLM integration (e.g., via Ollama or an external API).
# For now, it returns a mock response so the frontend and backend can be connected.

def extract_requirements(user_prompt: str) -> dict:
    """
    Calls Llama 3.1 8B to extract structured architectural requirements from the user prompt.
    """
    
    # TODO: Implement actual Llama 3.1 8B call here.
    # We will need to know how the user is hosting the model (e.g., Ollama).
    
    mock_response = {
        "building_type": "Public Library",
        "climate": "Hot and humid",
        "key_features": ["3 floors", "Natural ventilation", "Adequate daylight"],
        "sustainability_goals": ["Eco-friendly", "Low energy consumption"],
        "user_capacity": "Approximately 300 users",
        "raw_extraction": "This is a mock extraction for phase 1. Real LLM connection pending."
    }
    
    return mock_response
