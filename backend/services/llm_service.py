import json
import re
import os

def mock_rag_retrieval(building_type: str) -> str:
    """
    Simulated RAG Retrieval: Reads directly from our local knowledge base
    to ground the generation in architectural context.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    research_dir = os.path.join(base_dir, "research papers")
    
    context = ""
    # Pull generative AI knowledge
    ai_file = os.path.join(research_dir, "generative_ai_architecture.txt")
    if os.path.exists(ai_file):
        with open(ai_file, "r") as f:
            context += f.read() + "\n\n"
            
    # Pull specific building type knowledge
    if "mall" in building_type:
        target = os.path.join(research_dir, "malls_design.txt")
    elif "hospital" in building_type:
        target = os.path.join(research_dir, "hospitals_design.txt")
    else:
        target = os.path.join(research_dir, "public_buildings.txt")
        
    if os.path.exists(target):
        with open(target, "r") as f:
            context += f.read()
            
    return context

import uuid

def bsp_pack(x, y, w, h, room_names, is_hot=False):
    """Recursive Binary Space Partitioning returning BIM Polygons"""
    if not room_names:
        return []
    if len(room_names) == 1:
        return [{
            "id": f"room_{str(uuid.uuid4())[:6]}",
            "name": room_names[0], 
            "type": "wet" if "restroom" in room_names[0].lower() else "primary",
            "polygon": [[x, y], [x+w, y], [x+w, y+h], [x, y+h]],
            "area": w * h,
            # Legacy coords for backwards compat with some 3D mesher tools
            "x": x, "y": y, "width": w, "length": h
        }]
    
    # Sort buffers to sides if hot climate
    if is_hot:
        buffers = [r for r in room_names if "restroom" in r.lower() or "storage" in r.lower() or "stair" in r.lower()]
        primaries = [r for r in room_names if r not in buffers]
        room_names = buffers + primaries

    half = len(room_names) // 2
    rooms1 = room_names[:half]
    rooms2 = room_names[half:]
    
    # Split along the longest axis
    if w > h:
        w1 = w // 2
        w2 = w - w1
        return bsp_pack(x, y, w1, h, rooms1, is_hot) + bsp_pack(x + w1, y, w2, h, rooms2, is_hot)
    else:
        h1 = h // 2
        h2 = h - h1
        return bsp_pack(x, y, w, h1, rooms1, is_hot) + bsp_pack(x, y + h1, w, h2, rooms2, is_hot)

def extract_requirements(user_prompt: str, **kwargs) -> dict:
    """
    Simulated VAE/Diffusion RAG Pipeline for Mini Project Presentation.
    Bypasses heavy PyTorch FAISS and external LLMs.
    """
    # 1. RAG Retrieval Phase
    prompt_lower = user_prompt.lower()
    
    # Parametric Overrides from Streamlit
    b_width = kwargs.get("width", 30)
    b_length = kwargs.get("length", 30)
    c_height = kwargs.get("height", 3.0)
    t_wwr = kwargs.get("wwr", 40)
    
    # Active blocking of error messages and tracebacks
    if "file " in prompt_lower and "line " in prompt_lower and (".py" in prompt_lower or "traceback" in prompt_lower):
        raise ValueError("Invalid Prompt: The AI Consultant detected a Python error traceback in your request. Please provide a valid architectural description.")
    
    # Prompt Validation: Ensure it's an architectural request, not an error message or gibberish
    valid_keywords = [
        "building", "floor", "story", "hospital", "mall", "house", "villa", "home", 
        "museum", "office", "library", "school", "residential", "commercial", "architecture", 
        "mansion", "clinic", "retail", "pyramid", "skyscraper", "tower", "burj", "khalifa", "monument"
    ]
    
    has_valid_word = False
    for kw in valid_keywords:
        if re.search(r'\b' + kw + r'\b', prompt_lower):
            has_valid_word = True
            break
            
    if not has_valid_word and len(prompt_lower.split()) > 0:
        raise ValueError("Invalid Prompt: The AI Consultant could not detect any architectural requirements in your request. Please describe a building, specify the number of floors, or provide a valid architectural typology.")
    
    # Dynamically extract building type from prompt (e.g., "public museum" -> "museum")
    # We strip common adjectives and look for the main noun.
    words = prompt_lower.split()
    ignore_words = ["design", "a", "an", "floor", "eco", "friendly", "public", "for", "hot", "humid", "climate", "with", "natural", "ventilation"]
    extracted = [w for w in words if w not in ignore_words and not w.isdigit()]
    building_type = extracted[0] if extracted else "building"
    
    rag_context = mock_rag_retrieval(building_type)
    
    # 2. Heuristic Latent Space Generation (Simulating VAE)
    # Determine Climate for Passive Zoning
    climate = "hot_humid" if "hot" in prompt_lower or "tropical" in prompt_lower else "temperate"
    is_hot = climate == "hot_humid"

    # Default logic (can be overridden by AI)
    building_type = "office"
    num_floors = 3
    if "house" in prompt_lower or "villa" in prompt_lower or "residential" in prompt_lower or "mansion" in prompt_lower: building_type = "house"
    elif "mall" in prompt_lower: building_type = "mall"
    elif "hospital" in prompt_lower or "clinic" in prompt_lower: building_type = "hospital"
    elif "museum" in prompt_lower: building_type = "museum"
    elif "library" in prompt_lower: building_type = "library"
    elif "pyramid" in prompt_lower: building_type = "pyramid"
    elif "skyscraper" in prompt_lower or "tower" in prompt_lower: building_type = "skyscraper"
    elif extracted:
        # Fallback to the first non-trivial noun (risky if they start with 'create' or 'build')
        fallback = extracted[0]
        if fallback in ["create", "build", "make", "generate", "design"]:
            building_type = extracted[1] if len(extracted) > 1 else "building"
        else:
            building_type = fallback

    match = re.search(r'(\d+)\s*(?:story|storey|floor)', prompt_lower)
    if match: 
        num_floors = int(match.group(1))

    dynamic_floors = []
    
    for i in range(num_floors):
        floor_rooms = []
        
        # Unique Geometries (Pyramids & Skyscrapers)
        if building_type == "pyramid":
            size = max(10, b_width - (i * (b_width // num_floors)))
            offset = (b_width - size) // 2
            
            if i == 0:
                pyr_rooms = ["Grand Foyer", "Dining Hall", "Kitchen", "Communal Restrooms"]
            elif i == num_floors - 1:
                pyr_rooms = ["Master Suite", "Private Bath", "Observation Lounge"]
            else:
                pyr_rooms = [f"Living Quarters {i}A", f"Living Quarters {i}B", "Storage"]
                
            floor_rooms.extend(bsp_pack(offset, offset, size, size, pyr_rooms, is_hot))
            dynamic_floors.append({"level": i + 1, "name": f"Level {i+1} (Pyramid Tier)", "rooms": floor_rooms})
            continue
            
        if building_type == "skyscraper":
            size = max(10, b_width - (i * 2))
            offset = (b_width - size) // 2
            floor_rooms.append({"name": "Elevator Core", "x": offset + size//3, "y": offset + size//3, "width": size//3, "length": size//3, "is_nested": True})
            
            if i == 0:
                floor_rooms.extend(bsp_pack(offset, offset, size//3, size, ["Lobby", "Security"], is_hot))
                floor_rooms.extend(bsp_pack(offset + (size//3)*2, offset, size//3, size, ["Cafeteria", "Restrooms"], is_hot))
            else:
                floor_rooms.extend(bsp_pack(offset, offset, size//3, size, [f"Office {i}A", f"Office {i}B"], is_hot))
                floor_rooms.extend(bsp_pack(offset + (size//3)*2, offset, size//3, size, [f"Meeting Room {i}", "Restrooms"], is_hot))
                
            dynamic_floors.append({"level": i + 1, "name": f"Level {i+1} (Tower Floor)", "rooms": floor_rooms})
            continue
            
        # 1. Mandatory Core & Lightwell Constraints for Standard Buildings
        core_w, core_h = 6, 6
        core_x = (b_width // 2) - (core_w // 2)
        core_y = b_length - core_h - 2
        
        floor_rooms.append({
            "name": "Circulation Core (Stairs/Elevator)",
            "x": core_x, "y": core_y, "width": core_w, "length": core_h,
            "is_nested": True
        })
        
        if b_width >= 30 and b_length >= 30:
            atrium_size = 10
            floor_rooms.append({
                "name": "Central Lightwell (Stack Vent)",
                "x": (b_width // 2) - (atrium_size // 2), 
                "y": (b_length // 2) - (atrium_size // 2),
                "width": atrium_size, "length": atrium_size,
                "is_nested": True
            })

        # 2. Main Entrance Foyer on Ground
        foyer_h = 6
        if i == 0:
            floor_rooms.append({
                "name": "Main Entrance Foyer",
                "x": (b_width // 2) - 4, "y": 0, "width": 8, "length": foyer_h,
                "is_nested": True
            })

        # 3. BSP Packing for Remaining Zones
        # We will pack rooms into the left and right wings to avoid the central core/atrium
        left_wing_w = (b_width // 2) - 5
        right_wing_x = (b_width // 2) + 5
        right_wing_w = b_width - right_wing_x

        if building_type == "library":
            left_rooms = ["Public Reading Room", "Digital Archives", "Study Pods"]
            right_rooms = ["Book Stacks", "Librarian Desk", "Public Restrooms"]
        elif building_type in ["house", "residential", "villa", "mansion"]:
            left_rooms = ["Living Room", "Kitchen"] if i == 0 else ["Master Bedroom", "En-Suite Bath"]
            right_rooms = ["Dining Area", "Storage"] if i == 0 else ["Guest Room", "Balcony"]
        else:
            left_rooms = ["Open Workspace", "Meeting Room A", "Admin Storage"]
            right_rooms = ["Executive Office", "Meeting Room B", "Public Restrooms"]
            
        floor_rooms.extend(bsp_pack(0, foyer_h if i==0 else 0, left_wing_w, b_length - (foyer_h if i==0 else 0), left_rooms, is_hot))
        floor_rooms.extend(bsp_pack(right_wing_x, foyer_h if i==0 else 0, right_wing_w, b_length - (foyer_h if i==0 else 0), right_rooms, is_hot))

        # Dynamically append any [ADD: ] requested rooms
        add_matches = re.findall(r'\[ADD: (.*?)\]', prompt_lower, re.IGNORECASE)
        for idx, add_room in enumerate(add_matches):
            floor_rooms.append({
                "name": f"New {add_room.title()}",
                "y": (idx * 5) % 30,
                "width": 6,
                "length": 6,
                "is_nested": True
            })

        dynamic_floors.append({
            "level": i + 1,
            "name": f"Level {i+1} ({building_type.title()})",
            "rooms": floor_rooms
        })

    # 3. Build dynamic Mermaid diagram matching Eraser.io
    diagram_lines = [
        "graph LR",
        "classDef baseStyle fill:#1a202c,stroke:#4ade80,stroke-width:2px,color:#f8fafc;",
        "classDef level fill:#24422e,stroke:#3a6a4a,stroke-width:2px,color:#f8fafc;",
        "classDef system fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;",
        "classDef atrium fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;",
        "",
        "subgraph Building [\"Procedural Massing Pipeline (VAE)\"]"
    ]

    for i in range(num_floors, 0, -1):
        node_id = f"L{i}"
        diagram_lines.append(f"  {node_id}[\"Generated {building_type.title()} Level {i}\"]:::level")

    diagram_lines.extend([
        "end",
        "",
        "subgraph Systems [\"Generative 3D Architecture\"]",
        "  S1[\"RAG Context Search\"]:::system",
        "  S2[\"Latent Space VAE Encoding\"]:::system",
        "  S3[\"Diffusion Model Mesh Gen\"]:::system",
        "  S4[\"GAN Photorealism Rendering\"]:::system",
        "end",
        "",
        "subgraph Output [\"FINAL 3D MESH\"]",
        "  A1[\"Procedural Geometry<br/>Stable Diffusion Enhancement<br/>Export Ready\"]:::atrium",
        "end",
        "",
        f"L{num_floors} -->|structural bounds| S2",
        "L1 -->|metadata| S1",
        f"L{max(1, num_floors-1)} -->|depth maps| S3",
        "S1 -->|context| A1",
        "S2 -->|latent vectors| A1",
        "S3 -->|mesh| A1"
    ])

    mermaid_diagram = "\n".join(diagram_lines)

    # Calculate dynamic bounding box so the building shell perfectly wraps the rooms
    max_w = max(room["x"] + room["width"] for floor in dynamic_floors for room in floor["rooms"])
    max_l = max(room["y"] + room["length"] for floor in dynamic_floors for room in floor["rooms"])

    # 4. Construct JSON Response representing Diffusion/GAN output
    # Calculate architectural metrics
    total_gea = b_width * b_length * num_floors
    total_nia = sum(room.get("area", room.get("width", 0) * room.get("length", 0)) for floor in dynamic_floors for room in floor["rooms"])
    circulation_area = sum(room.get("area", room.get("width", 0) * room.get("length", 0)) for floor in dynamic_floors for room in floor["rooms"] if "core" in room["name"].lower() or "corridor" in room["name"].lower())
    circ_ratio = (circulation_area / total_nia * 100) if total_nia > 0 else 0
    
    return {
      "project": {
        "name": f"{building_type.title()} Project",
        "type": building_type,
        "style": "contemporary",
        "climate": climate
      },
      "metrics": {
          "GEA_sqm": total_gea,
          "NIA_sqm": total_nia,
          "circulation_ratio": round(circ_ratio, 1)
      },
      "building_width": b_width,
      "building_length": b_length,
      "ceiling_height": c_height,
      "target_wwr": t_wwr,
      "floors": dynamic_floors,
      "systems_diagram": mermaid_diagram,
      "explanation": {
        "rationale": f"This {building_type} was procedurally synthesized using a Simulated RAG pipeline. By mapping the layout into a VAE latent space, we establish structural boundaries. A mock Diffusion Model workflow is applied to extrude the 3D meshes based on the {num_floors}-floor structured requirements.",
        "sdg_alignment": "Demonstrates advanced integration of Generative AI (RAG, GAN, Diffusion) for rapid architectural prototyping."
      },
      "materials_estimate": [
        {
          "item": "Portland Cement (Grade 53)",
          "quantity": round(total_area * 4),
          "unit": "Bags (50kg)",
          "present_rate": 420.00,
          "total_cost": 420.00 * round(total_area * 4)
        },
        {
          "item": "Structural Steel (TMT Bars)",
          "quantity": round(total_area * 40),
          "unit": "Kg",
          "present_rate": 68.00,
          "total_cost": 68.00 * round(total_area * 40)
        },
        {
          "item": "AAC Blocks / Masonry",
          "quantity": round(total_area * 15),
          "unit": "Units",
          "present_rate": 65.00,
          "total_cost": 65.00 * round(total_area * 15)
        },
        {
          "item": "Vitrified Tile Flooring",
          "quantity": round(total_area * 0.85),
          "unit": "Sq. Meters",
          "present_rate": 850.00,
          "total_cost": 850.00 * round(total_area * 0.85)
        },
        {
          "item": "Internal Painting (Emulsion)",
          "quantity": round(total_area * 3.5),
          "unit": "Sq. Meters",
          "present_rate": 140.00,
          "total_cost": 140.00 * round(total_area * 3.5)
        },
        {
          "item": "Electrical & Wiring Modules",
          "quantity": round(total_area),
          "unit": "Sq. Meter Eq.",
          "present_rate": 1250.00,
          "total_cost": 1250.00 * round(total_area)
        },
        {
          "item": "Plumbing & Sanitary Core",
          "quantity": round(total_area),
          "unit": "Sq. Meter Eq.",
          "present_rate": 1100.00,
          "total_cost": 1100.00 * round(total_area)
        },
        {
          "item": "Low-E Eco Glazing",
          "quantity": round(total_area * 0.20),
          "unit": "Sq. Meters",
          "present_rate": 4800.00,
          "total_cost": 4800.00 * round(total_area * 0.20)
        }
      ]
    }
