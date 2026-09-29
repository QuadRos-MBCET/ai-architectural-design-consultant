import re
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
    Deterministic local parser extracting structured architectural requirements from natural language.
    Guarantees reliable operation without relying on external cloud APIs (e.g. Gemini).
    """
    prompt_lower = user_prompt.lower()

    # 1. Extract Dimensions (e.g., "30m x 20m", "30 x 20", "40 by 25")
    dim_match = re.search(r'(\d+)\s*(?:m|meter|meters)?\s*(?:x|×|by)\s*(\d+)\s*(?:m|meter|meters)?', prompt_lower)
    width = int(dim_match.group(1)) if dim_match else 30
    length = int(dim_match.group(2)) if dim_match else 20

    # 2. Extract Floor Count
    floor_match = re.search(r'(\d+)\s*(?:story|storey|floor)', prompt_lower)
    floors = int(floor_match.group(1)) if floor_match else 1

    # 3. Detect Typology
    typologies = ["library", "hospital", "mall", "office", "school", "museum", "house", "villa", "warehouse", "hotel", "clinic", "restaurant"]
    building_type = "library"
    for t in typologies:
        if t in prompt_lower:
            building_type = t
            break

    # 4. Comprehensive Room Keyword Dictionary
    room_keywords = {
        "reading_hall": ["reading hall", "reading room", "study hall", "study area"],
        "computer_section": ["computer section", "computer lab", "it lab", "pc area"],
        "discussion_room": ["discussion room", "conference room", "meeting room", "group study"],
        "librarian_office": ["librarian office", "admin office", "manager office", "doctor office", "office"],
        "storage": ["storage", "archive", "store room", "pantry"],
        "toilet": ["toilet", "toilets", "restroom", "restrooms", "washroom", "bathroom"],
        "foyer": ["foyer", "entrance", "main entrance", "lobby", "reception", "waiting hall", "waiting area"],
        "cafeteria": ["cafeteria", "canteen", "cafe", "dining area", "dining hall"],
        "exhibition_hall": ["exhibition hall", "display hall", "gallery", "main hall"],
        "classroom": ["classroom", "lecture hall", "training room"],
        "lab": ["lab", "laboratory", "research lab", "icu", "surgery room", "emergency room", "operating room"],
        "bedroom": ["bedroom", "master suite", "guest room", "patient room", "ward"],
        "living_room": ["living room", "lounge", "sitting room", "family room"],
        "kitchen": ["kitchen", "cooking area"]
    }

    rooms = []
    for rtype, phrases in room_keywords.items():
        found = False
        for p in phrases:
            if p in prompt_lower:
                found = True
                # Check for explicit word/number counts (e.g., "two discussion rooms", "3 offices")
                count = 1
                count_match = re.search(r'(\d+|one|two|three|four|five)\s*' + re.escape(p), prompt_lower)
                if count_match:
                    num_str = count_match.group(1)
                    word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
                    count = word_to_num.get(num_str, int(num_str) if num_str.isdigit() else 1)

                for c in range(count):
                    display_name = p.title() if p.title() not in [r["name"] for r in rooms] else f"{p.title()} {c+1}"
                    rooms.append({
                        "type": rtype,
                        "name": display_name,
                        "count": 1
                    })
                break

    # Typology-specific defaults if no specific room keywords were mentioned in prompt
    if not rooms:
        if building_type == "hospital" or building_type == "clinic":
            default_names = ["Reception & Lobby", "Emergency Room", "Doctor Office", "Pharmacy", "ICU Ward", "Restroom"]
        elif building_type == "house" or building_type == "villa":
            default_names = ["Living Room", "Master Bedroom", "Kitchen", "Dining Area", "Bathroom", "Entrance Foyer"]
        elif building_type == "office":
            default_names = ["Reception Lobby", "Open Workstation", "Executive Office", "Conference Room", "Breakroom", "Restroom"]
        elif building_type == "school":
            default_names = ["Main Entrance", "Classroom 1", "Classroom 2", "Science Lab", "Staff Office", "Restroom"]
        else:
            default_names = ["Main Reading Hall", "Computer Section", "Librarian Office", "Storage Room", "Restroom"]

        for idx, name in enumerate(default_names):
            rtype = name.lower().replace(" ", "_")
            if "restroom" in rtype or "bathroom" in rtype: rtype = "toilet"
            elif "foyer" in rtype or "entrance" in rtype or "reception" in rtype: rtype = "foyer"
            elif "office" in rtype: rtype = "librarian_office"
            rooms.append({"type": rtype, "name": name, "count": 1})

    return {
        "building_type": building_type,
        "building_width": width,
        "building_length": length,
        "floors_count": floors,
        "style": "modern" if "modern" in prompt_lower else "contemporary",
        "rooms": rooms
    }

@router.post("/extract", response_model=RequirementsResponse)
async def extract_requirements_endpoint(request: RequirementsRequest):
    try:
        json_data = parse_requirements_locally(request.user_prompt)
        return RequirementsResponse(structured_json=json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
