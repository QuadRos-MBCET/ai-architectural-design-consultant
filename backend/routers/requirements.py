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

    # 1. Extract Dimensions (e.g., "30m x 20m" or "30 by 20")
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

    # 4. Extract Key Specified Rooms
    room_keywords = {
        "reading_hall": ["reading hall", "reading room", "study area"],
        "computer_section": ["computer section", "computer lab", "it lab", "pc area"],
        "discussion_room": ["discussion room", "conference room", "group study"],
        "librarian_office": ["librarian office", "admin office", "office"],
        "storage": ["storage", "archive", "store room"],
        "toilet": ["toilet", "toilets", "restroom", "restrooms", "washroom"],
        "foyer": ["foyer", "entrance", "lobby", "reception"],
        "cafeteria": ["cafeteria", "canteen", "cafe"],
        "exhibition_hall": ["exhibition hall", "display hall", "gallery"]
    }

    rooms = []
    for rtype, phrases in room_keywords.items():
        found = False
        for p in phrases:
            if p in prompt_lower:
                found = True
                # Check for explicit counts (e.g., "two discussion rooms")
                count = 1
                if f"two {p}" in prompt_lower or f"2 {p}" in prompt_lower:
                    count = 2
                elif f"three {p}" in prompt_lower or f"3 {p}" in prompt_lower:
                    count = 3

                for c in range(count):
                    rooms.append({
                        "type": rtype,
                        "name": rtype.replace("_", " ").title() + (f" {c+1}" if count > 1 else ""),
                        "count": 1
                    })
                break

    # Default fallback room suite if none matched
    if not rooms:
        rooms = [
            {"type": "reading_hall", "name": "Main Reading Hall", "count": 1},
            {"type": "librarian_office", "name": "Office", "count": 1},
            {"type": "storage", "name": "Storage Room", "count": 1},
            {"type": "toilet", "name": "Restroom", "count": 1}
        ]

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
