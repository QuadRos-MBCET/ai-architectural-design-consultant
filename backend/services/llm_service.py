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

def extract_requirements(user_prompt: str) -> dict:
    """
    Simulated VAE/Diffusion RAG Pipeline for Mini Project Presentation.
    Bypasses heavy PyTorch FAISS and external LLMs.
    """
    # 1. RAG Retrieval Phase
    prompt_lower = user_prompt.lower()
    
    # Active blocking of error messages and tracebacks
    if "file " in prompt_lower and "line " in prompt_lower and (".py" in prompt_lower or "traceback" in prompt_lower):
        raise ValueError("Invalid Prompt: The AI Consultant detected a Python error traceback in your request. Please provide a valid architectural description.")
    
    # Prompt Validation: Ensure it's an architectural request, not an error message or gibberish
    valid_keywords = ["building", "floor", "story", "hospital", "mall", "house", "villa", "home", "museum", "office", "library", "school", "residential", "commercial", "architecture", "mansion", "clinic", "retail"]
    
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
    floor_match = re.search(r'(\d+)\s*floor', prompt_lower)
    num_floors = int(floor_match.group(1)) if floor_match else 3
    
    dynamic_floors = []
    
    # Generate completely dynamic generic layouts based on ANY building type!
    for i in range(num_floors):
        # We handle the specific ones we already made for high quality
        if building_type == "mall":
            if i == 0:
                name = "Mall Ground Level (Main Atrium)"
                rooms = [{"name": "Anchor Store A", "x": 0, "y": 0, "width": 15, "length": 25}, {"name": "Boutique Retail", "x": 15, "y": 0, "width": 10, "length": 10}, {"name": "Food Court", "x": 15, "y": 10, "width": 10, "length": 15}, {"name": "Anchor Store B", "x": 25, "y": 0, "width": 15, "length": 25}]
            elif i == 1:
                name = f"Mall Level {i+1} (Entertainment)"
                rooms = [{"name": "Multiplex Cinema", "x": 0, "y": 0, "width": 25, "length": 25}, {"name": "Arcade", "x": 25, "y": 0, "width": 15, "length": 15}, {"name": "Dining Terrace", "x": 25, "y": 15, "width": 15, "length": 10}]
            elif i == 2:
                name = f"Mall Level {i+1} (Fashion and Apparel)"
                rooms = [{"name": "Designer Brands", "x": 0, "y": 0, "width": 20, "length": 15}, {"name": "Shoe Stores", "x": 20, "y": 0, "width": 15, "length": 15}, {"name": "Jewelry", "x": 15, "y": 15, "width": 20, "length": 10}]
            elif i == 3:
                name = f"Mall Level {i+1} (Tech and Lifestyle)"
                rooms = [{"name": "Electronics Hub", "x": 0, "y": 0, "width": 20, "length": 20}, {"name": "Home Goods", "x": 20, "y": 0, "width": 15, "length": 20}, {"name": "Cafes", "x": 10, "y": 20, "width": 15, "length": 5}]
            else:
                name = f"Mall Level {i+1} (Mixed Expansion)"
                rooms = [{"name": f"Retail Wing {i}A", "x": 0, "y": 0, "width": 15 + (i%3)*2, "length": 20}, {"name": f"Retail Wing {i}B", "x": 15 + (i%3)*2, "y": 0, "width": 15, "length": 15}, {"name": f"Kiosks {i}", "x": 15 + (i%3)*2, "y": 15, "width": 15, "length": 5}]
        elif building_type == "hospital":
            if i == 0:
                name = "Hospital Ground (Emergency)"
                rooms = [{"name": "ER Triage", "x": 0, "y": 0, "width": 15, "length": 15}, {"name": "Trauma Bays", "x": 15, "y": 0, "width": 15, "length": 15}, {"name": "Imaging", "x": 0, "y": 15, "width": 20, "length": 10}, {"name": "Pharmacy", "x": 20, "y": 15, "width": 10, "length": 10}]
            elif i == 1:
                name = f"Hospital Level {i+1} (Patient Wards)"
                rooms = [{"name": "Patient Wards", "x": 0, "y": 0, "width": 20, "length": 10}, {"name": "Surgical ICU", "x": 0, "y": 10, "width": 20, "length": 10}, {"name": "Sterile Corridors", "x": 20, "y": 0, "width": 5, "length": 20}, {"name": "Staff", "x": 25, "y": 0, "width": 10, "length": 20}]
            elif i == 2:
                name = f"Hospital Level {i+1} (Maternity and Peds)"
                rooms = [{"name": "Labor and Delivery", "x": 0, "y": 0, "width": 15, "length": 20}, {"name": "NICU", "x": 15, "y": 0, "width": 15, "length": 10}, {"name": "Pediatric Wards", "x": 15, "y": 10, "width": 15, "length": 10}]
            elif i == 3:
                name = f"Hospital Level {i+1} (Specialty Clinics)"
                rooms = [{"name": "Cardiology", "x": 0, "y": 0, "width": 15, "length": 15}, {"name": "Neurology", "x": 15, "y": 0, "width": 15, "length": 15}, {"name": "Therapy", "x": 0, "y": 15, "width": 30, "length": 10}]
            else:
                name = f"Hospital Level {i+1} (Advanced Care)"
                rooms = [{"name": f"Research Lab {i}", "x": 0, "y": 0, "width": 20 - (i%4), "length": 15}, {"name": f"Testing Unit {i}", "x": 20 - (i%4), "y": 0, "width": 15, "length": 10}, {"name": "Observation", "x": 20 - (i%4), "y": 10, "width": 15, "length": 5}]
        elif building_type == "museum":
            if i == 0:
                name = "Museum Ground (Grand Foyer)"
                rooms = [{"name": "Grand Foyer", "x": 0, "y": 0, "width": 20, "length": 15}, {"name": "Ticketing", "x": 20, "y": 0, "width": 10, "length": 15}, {"name": "Exhibits", "x": 0, "y": 15, "width": 20, "length": 15}, {"name": "Gift Shop", "x": 20, "y": 15, "width": 10, "length": 15}]
            elif i == 1:
                name = f"Museum Level {i+1} (Collections)"
                rooms = [{"name": "Permanent Galleries", "x": 0, "y": 0, "width": 20, "length": 20}, {"name": "Interactive", "x": 20, "y": 0, "width": 15, "length": 10}, {"name": "Restoration", "x": 20, "y": 10, "width": 15, "length": 10}, {"name": "Offices", "x": 20, "y": 20, "width": 15, "length": 10}]
            elif i == 2:
                name = f"Museum Level {i+1} (Modern Art)"
                rooms = [{"name": "Sculpture Garden", "x": 0, "y": 0, "width": 15, "length": 25}, {"name": "Abstract Exhibits", "x": 15, "y": 0, "width": 20, "length": 15}, {"name": "Audio Visual Room", "x": 15, "y": 15, "width": 20, "length": 10}]
            elif i == 3:
                name = f"Museum Level {i+1} (Natural History)"
                rooms = [{"name": "Dinosaur Fossils", "x": 0, "y": 0, "width": 25, "length": 20}, {"name": "Gems and Minerals", "x": 25, "y": 0, "width": 10, "length": 20}, {"name": "Theater", "x": 0, "y": 20, "width": 35, "length": 10}]
            else:
                name = f"Museum Level {i+1} (Private Collections)"
                rooms = [{"name": f"Exhibition Hall {i}", "x": 0, "y": 0, "width": 15 + (i%5), "length": 25}, {"name": "Curator Study", "x": 15 + (i%5), "y": 0, "width": 15, "length": 15}, {"name": "Storage", "x": 15 + (i%5), "y": 15, "width": 15, "length": 10}]
        elif any(word in prompt_lower for word in ["house", "home", "villa", "residential", "mansion"]):
            if i == 0:
                name = "Ground Floor (Living and Services)"
                rooms = [
                    {"name": "Foyer and Living Room", "x": 0, "y": 0, "width": 15, "length": 30},
                    {"name": "Open Kitchen", "x": 15, "y": 0, "width": 15, "length": 15},
                    {"name": "Dining Area", "x": 15, "y": 15, "width": 15, "length": 15}
                ]
            elif i == 1:
                name = "First Floor (Master Suite)"
                rooms = [
                    {"name": "Master Bedroom", "x": 0, "y": 0, "width": 20, "length": 20},
                    {"name": "En-suite Bathroom", "x": 20, "y": 0, "width": 10, "length": 15},
                    {"name": "Walk-in Closet", "x": 20, "y": 15, "width": 10, "length": 15},
                    {"name": "Balcony Lounge", "x": 0, "y": 20, "width": 20, "length": 10}
                ]
            elif i == 2:
                name = "Second Floor (Family & Bedrooms)"
                rooms = [
                    {"name": "Bedroom 2", "x": 0, "y": 0, "width": 15, "length": 15},
                    {"name": "Bedroom 3", "x": 15, "y": 0, "width": 15, "length": 15},
                    {"name": "Shared Bathroom", "x": 15, "y": 15, "width": 15, "length": 15},
                    {"name": "Family Room", "x": 0, "y": 15, "width": 15, "length": 15}
                ]
            else:
                name = f"Level {i+1} (Terrace & Amenities)"
                rooms = [
                    {"name": "Home Office", "x": 0, "y": 0, "width": 15, "length": 15},
                    {"name": "Home Gym", "x": 15, "y": 0, "width": 15, "length": 15},
                    {"name": "Roof Garden", "x": 0, "y": 15, "width": 30, "length": 15}
                ]
        else:
            # TRUE DYNAMIC FALLBACK: Perfectly balanced 30x30 procedural grids
            bt_title = building_type.title()
            if i == 0:
                name = f"{bt_title} Ground (Lobby and Reception)"
                rooms = [
                    {"name": f"Main Reception", "x": 0, "y": 0, "width": 15, "length": 15},
                    {"name": f"Public Waiting Area", "x": 15, "y": 0, "width": 15, "length": 15},
                    {"name": f"Security and Control", "x": 0, "y": 15, "width": 15, "length": 15},
                    {"name": f"{bt_title} Facilities", "x": 15, "y": 15, "width": 15, "length": 15}
                ]
            elif i == 1:
                name = f"{bt_title} Level {i+1} (Operations)"
                rooms = [
                    {"name": f"Core {bt_title} Space", "x": 0, "y": 0, "width": 20, "length": 30},
                    {"name": f"Secondary Zones", "x": 20, "y": 0, "width": 10, "length": 15},
                    {"name": "Admin Offices", "x": 20, "y": 15, "width": 10, "length": 15}
                ]
            elif i == 2:
                name = f"{bt_title} Level {i+1} (Specialty Space)"
                rooms = [
                    {"name": f"Specialty Area A", "x": 0, "y": 0, "width": 15, "length": 20},
                    {"name": f"Specialty Area B", "x": 15, "y": 0, "width": 15, "length": 20},
                    {"name": "Shared Lounge", "x": 0, "y": 20, "width": 30, "length": 10}
                ]
            elif i == 3:
                name = f"{bt_title} Level {i+1} (Executive Hub)"
                rooms = [
                    {"name": "Executive Offices", "x": 0, "y": 0, "width": 15, "length": 15},
                    {"name": "Boardroom", "x": 15, "y": 0, "width": 15, "length": 15},
                    {"name": "Archive Room", "x": 0, "y": 15, "width": 15, "length": 15},
                    {"name": "R and D Space", "x": 15, "y": 15, "width": 15, "length": 15}
                ]
            else:
                name = f"{bt_title} Level {i+1} (Extended Wing)"
                rooms = [
                    {"name": f"Expansion Zone {i}", "x": 0, "y": 0, "width": 15, "length": 15},
                    {"name": f"Flex Space {i}", "x": 15, "y": 0, "width": 15, "length": 15},
                    {"name": "Utilities", "x": 0, "y": 15, "width": 30, "length": 15}
                ]
        
        dynamic_floors.append({
            "level": i + 1,
            "name": name,
            "rooms": rooms
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
    return {
      "project": {
        "type": building_type,
        "location": "Generative Space",
        "climate": "optimized"
      },
      "building_width": max_w,
      "building_length": max_l,
      "floors": dynamic_floors,
      "systems_diagram": mermaid_diagram,
      "explanation": {
        "rationale": f"This {building_type} was procedurally synthesized using a Simulated RAG pipeline. By mapping the layout into a VAE latent space, we establish structural boundaries. A mock Diffusion Model workflow is applied to extrude the 3D meshes based on the {num_floors}-floor structured requirements.",
        "sdg_alignment": "Demonstrates advanced integration of Generative AI (RAG, GAN, Diffusion) for rapid architectural prototyping."
      },
      "materials_estimate": [
        {
          "item": "Portland Cement (Grade 53)",
          "quantity": 120 * num_floors,
          "unit": "Tons",
          "present_rate": 7500.00,
          "total_cost": 7500.00 * (120 * num_floors)
        },
        {
          "item": "Structural Steel (TMT Bars)",
          "quantity": 45 * num_floors,
          "unit": "Tons",
          "present_rate": 65000.00,
          "total_cost": 65000.00 * (45 * num_floors)
        },
        {
          "item": "Electrical Equipment & Wiring",
          "quantity": 1500 * num_floors,
          "unit": "Meters",
          "present_rate": 150.00,
          "total_cost": 150.00 * (1500 * num_floors)
        },
        {
          "item": "Low-E Eco Glazing",
          "quantity": 300 * num_floors,
          "unit": "Sq. Meters",
          "present_rate": 4500.00,
          "total_cost": 4500.00 * (300 * num_floors)
        }
      ]
    }
