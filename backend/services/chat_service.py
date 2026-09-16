import re

def process_simulated_chat(chat_msg: str, current_prompt: str) -> tuple[str, str]:
    """
    Simulated NLP Chatbot for the mini-project.
    Modifies the core prompt based on heuristic keyword extraction.
    Returns: (new_prompt, bot_response_text)
    """
    msg_lower = chat_msg.lower()
    new_prompt = current_prompt
    
    # Find current floor count in the prompt
    floor_match = re.search(r'(\d+)\s*floor', current_prompt.lower())
    current_floors = int(floor_match.group(1)) if floor_match else 3
    
    if "add" in msg_lower and "floor" in msg_lower:
        if floor_match:
            new_prompt = re.sub(r'\d+\s*floor', f"{current_floors + 1} floor", new_prompt, flags=re.IGNORECASE)
        else:
            new_prompt = f"design a {current_floors + 1} floor " + new_prompt
        return new_prompt, f"Got it! I have dynamically recalculated the structural loads, updated the Bill of Materials, and added Level {current_floors + 1} to the blueprint."
        
    elif "remove" in msg_lower and "floor" in msg_lower:
        if current_floors > 1:
            new_prompt = re.sub(r'\d+\s*floor', f"{current_floors - 1} floor", new_prompt, flags=re.IGNORECASE)
            return new_prompt, f"I have safely removed the top floor and optimized the VAE latent space for {current_floors - 1} floors."
        else:
            return current_prompt, "The building is already at 1 floor! I cannot remove any more floors."
            
    convert_match = re.search(r'convert (?:floor|level)\s+(\d+)\s+to\s+(?:a |an )?(.*)', msg_lower)
    if convert_match:
        f_num = convert_match.group(1)
        new_usage = convert_match.group(2).strip()
        new_prompt = new_prompt + f" [MOD: Floor {f_num} = {new_usage.title()}]"
        return new_prompt, f"I have dynamically recalculated the spatial logic. Floor {f_num} has been converted into a {new_usage.title()}!"

    add_room_match = re.search(r'add (?:a |an |1 )?(bathroom|wardrobe|closet|bedroom|music studio|en-suite|dress closet)', msg_lower)
    if add_room_match and "floor" not in msg_lower:
        room_type = add_room_match.group(1)
        new_prompt = new_prompt + f" [ADD: {room_type.title()}]"
        return new_prompt, f"I have nested a {room_type.title()} into the layout. Generating interior partitions now..."
            
    elif "change" in msg_lower or "make it" in msg_lower:
        # Check if they are requesting a new building type
        supported_types = ["mall", "hospital", "museum", "library", "school", "office", "cinema"]
        for b_type in supported_types:
            if b_type in msg_lower:
                # Find the old building type in the prompt and replace it
                words = new_prompt.split()
                ignore_words = ["design", "a", "an", "floor", "eco", "friendly", "public", "for", "hot", "humid", "climate", "with", "natural", "ventilation"]
                extracted = [w for w in words if w.lower() not in ignore_words and not w.isdigit()]
                
                if extracted:
                    old_type = extracted[0]
                    new_prompt = new_prompt.replace(old_type, b_type)
                else:
                    new_prompt = new_prompt + f" {b_type}"
                    
                return new_prompt, f"I have completely refactored the architectural style! The Generative Pipeline has synthesized a new {b_type.title()}."
                
    return current_prompt, "I am a simulated AI Consultant for this mini-project! Try asking me to **'add a floor'**, **'remove a floor'**, or **'change it to a hospital'**."
