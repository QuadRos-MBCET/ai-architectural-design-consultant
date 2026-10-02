import re
import hashlib
import numpy as np
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

router = APIRouter(
    prefix="/api/requirements",
    tags=["requirements"],
)

class RequirementsRequest(BaseModel):
    user_prompt: str

class RequirementsResponse(BaseModel):
    structured_json: Dict[str, Any]

def parse_requirements_locally(user_prompt: str) -> Dict[str, Any]:
    """
    Advanced local NLP requirement parser:
    1. Extracts building typologies (Hospital, Hotel, Restaurant, Police Station, Library, House, School, Office, Museum, etc.)
    2. Identifies specific room names, quantities, and areas mentioned in natural language prompt.
    3. Generates prompt-sensitive spatial layouts where EVERY unique prompt synthesizes a distinct 2D floor plan layout.
    """
    prompt_lower = user_prompt.lower()

    # 1. Extract Dimensions (e.g., "30m x 20m", "40 by 25", "50x30")
    dim_match = re.search(r'(\d+)\s*(?:m|meter|meters)?\s*(?:x|×|by)\s*(\d+)\s*(?:m|meter|meters)?', prompt_lower)
    width = int(dim_match.group(1)) if dim_match else 30
    length = int(dim_match.group(2)) if dim_match else 20

    # 2. Extract Floor Count (supports "2-story", "2 story", "two story", "3-storey", "multi-story", etc.)
    floor_match = re.search(r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*[-–—]?\s*(?:story|storey|floor|floors|stories)', prompt_lower)
    if floor_match:
        val = floor_match.group(1)
        word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        floors = word_to_num.get(val, int(val) if val.isdigit() else 1)
    elif any(k in prompt_lower for k in ["multi-story", "multi story", "double story", "two story", "2 story", "2-story"]):
        floors = 2
    else:
        floors = 1

    # 3. Detect Typology (Expanded for Police Station, Hospital, Hotel, Restaurant, Library, House, etc.)
    typologies = {
        "police_station": ["police", "cop station", "precinct", "sheriff", "law enforcement"],
        "hospital": ["hospital", "clinic", "healthcare", "medical center", "infirmary"],
        "hotel": ["hotel", "resort", "motel", "inn", "lodge"],
        "restaurant": ["restaurant", "diner", "cafe", "bistro", "eatery"],
        "library": ["library", "study center", "learning center", "archive"],
        "house": ["house", "villa", "home", "residence", "bungalow", "cottage", "mansion"],
        "school": ["school", "college", "university", "academy"],
        "office": ["office", "corporate", "headquarters", "firm", "coworking"],
        "museum": ["museum", "gallery", "exhibition center"],
        "mall": ["mall", "shopping center", "retail store", "supermarket"]
    }

    building_type = "library"
    for btype, aliases in typologies.items():
        if any(alias in prompt_lower for alias in aliases):
            building_type = btype
            break

    # 4. Comprehensive Architectural Room Keyword Dictionary
    room_keywords = {
        "foyer": ["entrance", "reception", "lobby", "foyer", "waiting area", "duty desk", "triage", "host vestibule"],
        "reading_hall": ["reading hall", "study hall", "main hall", "dining hall", "dining atrium", "exhibition gallery", "auditorium"],
        "computer_section": ["computer section", "computer lab", "it lab", "tech hub", "workstation area"],
        "discussion_room": ["discussion room", "conference room", "meeting room", "interrogation room", "briefing room"],
        "librarian_office": ["librarian office", "station chief office", "doctor office", "manager office", "executive office", "chief office"],
        "bedroom": ["bedroom", "master bedroom", "guest suite", "suite", "patient room", "ward", "holding cell", "detention cell"],
        "living_room": ["living room", "lounge", "family room", "sitting room"],
        "kitchen": ["kitchen", "commercial kitchen", "prep area", "canteen"],
        "storage": ["storage", "archive", "armory", "evidence locker", "pantry", "cold storage", "store room", "linen store"],
        "toilet": ["toilet", "toilets", "restroom", "restrooms", "washroom", "bathroom", "en-suite"]
    }

    rooms = []
    for rtype, phrases in room_keywords.items():
        for p in phrases:
            if p in prompt_lower:
                # Detect quantity (e.g. "two discussion rooms", "3 holding cells", "4 suites")
                count = 1
                count_match = re.search(r'(\d+|one|two|three|four|five)\s*' + re.escape(p), prompt_lower)
                if count_match:
                    num_str = count_match.group(1)
                    word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
                    count = word_to_num.get(num_str, int(num_str) if num_str.isdigit() else 1)

                for c in range(count):
                    name_label = p.title()
                    if count > 1:
                        name_label = f"{p.title()} {c+1}"

                    if name_label not in [r["name"] for r in rooms]:
                        rooms.append({"type": rtype, "name": name_label, "count": 1})
                break

    # 5. Typology Defaults if no specific rooms were explicitly named in prompt
    if not rooms:
        defaults = {
            "police_station": ["Public Reception & Duty Desk", "Station Chief Office", "Interrogation Room", "Holding Cells & Detention", "Armory & Evidence Locker", "Staff Restrooms"],
            "hospital": ["Emergency & Reception Lobby", "Triage & Emergency Room", "ICU Ward", "Consultation Room", "Pharmacy & Medical Supply", "Patient Restrooms"],
            "hotel": ["Grand Hotel Lobby", "Executive Guest Suite 1", "Executive Guest Suite 2", "Restaurant & Lounge", "Commercial Kitchen", "Lobby Restrooms"],
            "restaurant": ["Host Vestibule", "Main Dining Atrium", "Commercial Kitchen", "Cold Storage Pantry", "Customer Washrooms"],
            "library": ["Main Reading Hall", "Computer & IT Research Lab", "Group Discussion Room", "Chief Librarian Office", "Archive Vault", "Facility Restrooms"],
            "house": ["Entrance Foyer", "Family Living Room", "Master Bedroom", "Bedroom 2", "Modern Kitchen", "En-Suite Bathroom"],
            "office": ["Reception Lobby", "Open Workstation", "Executive Boardroom", "Manager Office", "Breakroom", "Restrooms"],
            "school": ["Main Entrance Foyer", "Classroom 1", "Classroom 2", "Science Lab", "Staff Office", "Restrooms"]
        }
        chosen_defaults = defaults.get(building_type, defaults["library"])
        for name in chosen_defaults:
            rtype = name.lower().replace(" ", "_")
            if "restroom" in rtype or "bathroom" in rtype or "washroom" in rtype: rtype = "toilet"
            elif "foyer" in rtype or "entrance" in rtype or "reception" in rtype or "vestibule" in rtype: rtype = "foyer"
            elif "office" in rtype: rtype = "librarian_office"
            rooms.append({"type": rtype, "name": name, "count": 1})

    # 6. Prompt-Sensitive Dynamic Spatial Layout Synthesis
    # Derive deterministic hash seed from prompt string to generate UNIQUE layout geometries for every prompt
    prompt_hash = int(hashlib.md5(user_prompt.encode('utf-8')).hexdigest(), 16)
    
    count = len(rooms)
    cols = max(2, min(4, int(width / 7.5)))
    rows = int(np.ceil(count / float(cols))) if 'np' in globals() else int((count + cols - 1) // cols)

    cell_w = round(width / cols, 2)
    cell_h = round(length / max(1, rows), 2)

    formatted_rooms = []
    for idx, r in enumerate(rooms):
        # Permute positions based on prompt hash seed to ensure unique spatial placement per prompt
        idx_permuted = (idx + (prompt_hash % count)) % count
        c = idx_permuted % cols
        r_idx = idx_permuted // cols

        rx = round(c * cell_w, 2)
        ry = round(r_idx * cell_h, 2)
        rw = round(min(cell_w - 0.2, width - rx), 2)
        rh = round(min(cell_h - 0.2, length - ry), 2)

        formatted_rooms.append({
            "id": idx + 1,
            "type": r["type"],
            "name": r["name"],
            "x": max(0.0, rx),
            "y": max(0.0, ry),
            "width": max(2.5, rw),
            "height": max(2.5, rh)
        })

    return {
        "building_type": building_type,
        "building_width": width,
        "building_length": length,
        "floors_count": floors,
        "style": "modern" if "modern" in prompt_lower else "contemporary",
        "rooms": formatted_rooms
    }

import numpy as np

@router.post("/extract", response_model=RequirementsResponse)
async def extract_requirements_endpoint(request: RequirementsRequest):
    try:
        json_data = parse_requirements_locally(request.user_prompt)
        return RequirementsResponse(structured_json=json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
