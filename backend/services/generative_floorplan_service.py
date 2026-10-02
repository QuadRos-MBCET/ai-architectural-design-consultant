from typing import Dict, Any, Tuple
import os
import sys
import numpy as np

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.vae.inference import generate_with_vae
from models.gan.inference import generate_with_gan
from models.diffusion.inference import generate_with_diffusion
try:
    from backend.services.llm_service import extract_requirements
    from backend.services.layout_validator import validate_floorplan, repair_geometry_if_needed
except Exception:
    from services.llm_service import extract_requirements
    from services.layout_validator import validate_floorplan, repair_geometry_if_needed

def generate_bsp_baseline_floorplan(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procedural layout generator that respects prompt-specific room geometries,
    room ordering, dimensions, and positioning.
    """
    b_width = float(requirements.get("building_width", requirements.get("width", 30.0)))
    b_length = float(requirements.get("building_length", requirements.get("length", 20.0)))
    b_type = requirements.get("building_type", "library")
    rooms = requirements.get("rooms", [])

    is_top = requirements.get("is_top_floor", False)
    
    if is_top:
        # Generate architectural top-floor specialized room programs with spacious spatial proportions
        typology_upper_programs = {
            "police_station": [
                {"type": "storage", "name": "High-Security Holding Cells", "width": b_width * 0.5, "height": b_length * 0.5, "x": 0.0, "y": 0.0},
                {"type": "discussion_room", "name": "Interrogation & Briefing Room", "width": b_width * 0.5, "height": b_length * 0.5, "x": b_width * 0.5, "y": 0.0},
                {"type": "librarian_office", "name": "Station Chief Suite", "width": b_width * 0.4, "height": b_length * 0.5, "x": 0.0, "y": b_length * 0.5},
                {"type": "toilet", "name": "Upper Staff Restrooms", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.4, "y": b_length * 0.5},
                {"type": "foyer", "name": "Stairwell Riser Core", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.7, "y": b_length * 0.5}
            ],
            "hospital": [
                {"type": "lab", "name": "Intensive Care Unit (ICU)", "width": b_width * 0.5, "height": b_length * 0.5, "x": 0.0, "y": 0.0},
                {"type": "bedroom", "name": "Private Patient Wards", "width": b_width * 0.5, "height": b_length * 0.5, "x": b_width * 0.5, "y": 0.0},
                {"type": "librarian_office", "name": "Doctor Consultation Suite", "width": b_width * 0.4, "height": b_length * 0.5, "x": 0.0, "y": b_length * 0.5},
                {"type": "toilet", "name": "Sanitary Restroom Core", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.4, "y": b_length * 0.5},
                {"type": "foyer", "name": "Stair & Elevator Core", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.7, "y": b_length * 0.5}
            ],
            "hotel": [
                {"type": "bedroom", "name": "Executive Guest Suite 1", "width": b_width * 0.5, "height": b_length * 0.5, "x": 0.0, "y": 0.0},
                {"type": "bedroom", "name": "Executive Guest Suite 2", "width": b_width * 0.5, "height": b_length * 0.5, "x": b_width * 0.5, "y": 0.0},
                {"type": "bedroom", "name": "Deluxe Guest Suite 3", "width": b_width * 0.4, "height": b_length * 0.5, "x": 0.0, "y": b_length * 0.5},
                {"type": "toilet", "name": "En-Suite Bathrooms", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.4, "y": b_length * 0.5},
                {"type": "foyer", "name": "Elevator & Stair Riser", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.7, "y": b_length * 0.5}
            ],
            "library": [
                {"type": "reading_hall", "name": "Upper Quiet Special Collections", "width": b_width * 0.5, "height": b_length * 0.5, "x": 0.0, "y": 0.0},
                {"type": "discussion_room", "name": "Seminar & Discussion Suite", "width": b_width * 0.5, "height": b_length * 0.5, "x": b_width * 0.5, "y": 0.0},
                {"type": "librarian_office", "name": "Chief Librarian Suite", "width": b_width * 0.4, "height": b_length * 0.5, "x": 0.0, "y": b_length * 0.5},
                {"type": "toilet", "name": "Upper Facility Restrooms", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.4, "y": b_length * 0.5},
                {"type": "foyer", "name": "Stairwell Riser Core", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.7, "y": b_length * 0.5}
            ],
            "house": [
                {"type": "bedroom", "name": "Master Bedroom Suite", "width": b_width * 0.5, "height": b_length * 0.5, "x": 0.0, "y": 0.0},
                {"type": "bedroom", "name": "Bedroom 2", "width": b_width * 0.5, "height": b_length * 0.5, "x": b_width * 0.5, "y": 0.0},
                {"type": "living_room", "name": "Upper Family Lounge & Terrace", "width": b_width * 0.4, "height": b_length * 0.5, "x": 0.0, "y": b_length * 0.5},
                {"type": "toilet", "name": "Master Bath", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.4, "y": b_length * 0.5},
                {"type": "foyer", "name": "Staircase Core", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.7, "y": b_length * 0.5}
            ]
        }
        
        default_upper = [
            {"type": "librarian_office", "name": "Executive Suite 1", "width": b_width * 0.5, "height": b_length * 0.5, "x": 0.0, "y": 0.0},
            {"type": "discussion_room", "name": "Executive Suite 2", "width": b_width * 0.5, "height": b_length * 0.5, "x": b_width * 0.5, "y": 0.0},
            {"type": "storage", "name": "Upper Archive Vault", "width": b_width * 0.4, "height": b_length * 0.5, "x": 0.0, "y": b_length * 0.5},
            {"type": "toilet", "name": "Upper Level Washrooms", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.4, "y": b_length * 0.5},
            {"type": "foyer", "name": "Stairwell Riser Core", "width": b_width * 0.3, "height": b_length * 0.5, "x": b_width * 0.7, "y": b_length * 0.5}
        ]
        
        rooms = typology_upper_programs.get(b_type, default_upper)
    elif not rooms:
        rooms = [
            {"type": "reading_hall", "name": "Main Reading Hall", "x": 0.0, "y": 0.0, "width": 15.0, "height": 10.0},
            {"type": "computer_section", "name": "Computer Lab", "x": 15.0, "y": 0.0, "width": 15.0, "height": 10.0},
            {"type": "librarian_office", "name": "Staff Office", "x": 0.0, "y": 10.0, "width": 15.0, "height": 10.0},
            {"type": "toilet", "name": "Restroom", "x": 15.0, "y": 10.0, "width": 15.0, "height": 10.0}
        ]

    count = len(rooms)
    cols = int(np.ceil(np.sqrt(count)))
    rows = int(np.ceil(count / float(cols)))

    cell_w = b_width / max(1, cols)
    cell_h = b_length / max(1, rows)

    formatted_rooms = []
    for idx, r in enumerate(rooms):
        r_name = r.get("name", f"Room {idx+1}")
        r_type = r.get("type", "room")

        # Use prompt-sensitive coordinates if present, otherwise compute grid position
        rx = float(r.get("x", (idx % cols) * cell_w))
        ry = float(r.get("y", (idx // cols) * cell_h))
        rw = float(r.get("width", cell_w - 0.2))
        rh = float(r.get("height", r.get("length", cell_h - 0.2)))

        formatted_rooms.append({
            "id": idx + 1,
            "type": r_type,
            "name": r_name,
            "x": max(0.0, rx),
            "y": max(0.0, ry),
            "width": max(2.5, rw),
            "height": max(2.5, rh),
            "is_nested": "toilet" in r_type or "storage" in r_type
        })

    return {
        "building_type": b_type,
        "building_width": b_width,
        "building_length": b_length,
        "floors_count": 1,
        "rooms": formatted_rooms
    }

def generate_floorplan(requirements: Dict[str, Any], model_type: str = "gan") -> Dict[str, Any]:
    """
    Unified Generative Floor Plan Generation Interface.
    Modes supported:
      - 'vae': PyTorch Conditional VAE
      - 'gan': PyTorch Conditional GAN
      - 'diffusion': PyTorch Conditional DDPM Diffusion
      - 'bsp_baseline': Procedural Baseline Algorithm
    """
    model_type = model_type.lower()
    floorplan = None
    is_real_checkpoint = False
    status_msg = ""
    actual_model_used = model_type

    if requirements.get("is_top_floor", False):
        actual_model_used = "procedural_top_floor"
        is_real_checkpoint = True
        floorplan = generate_bsp_baseline_floorplan(requirements)
        status_msg = "Generated Top Floor architectural plan using procedural floor alignment."
    elif model_type == "vae":
        floorplan, is_real_checkpoint, status_msg = generate_with_vae(requirements)
        if not floorplan:
            actual_model_used = "bsp_baseline"
            floorplan = generate_bsp_baseline_floorplan(requirements)
            status_msg = "VAE Checkpoint unavailable — executed procedural fallback."

    elif model_type == "gan":
        floorplan, is_real_checkpoint, status_msg = generate_with_gan(requirements)
        if not floorplan:
            actual_model_used = "bsp_baseline"
            floorplan = generate_bsp_baseline_floorplan(requirements)
            status_msg = "GAN Checkpoint unavailable — executed procedural fallback."

    elif model_type in ["diffusion", "ddpm"]:
        floorplan, is_real_checkpoint, status_msg = generate_with_diffusion(requirements)
        if not floorplan:
            actual_model_used = "bsp_baseline"
            floorplan = generate_bsp_baseline_floorplan(requirements)
            status_msg = "Diffusion Checkpoint unavailable — executed procedural fallback."

    else:
        actual_model_used = "bsp_baseline"
        is_real_checkpoint = True
        floorplan = generate_bsp_baseline_floorplan(requirements)
        status_msg = "Generated using Procedural Baseline Generator."

    # Validate generated geometry
    validation_info = validate_floorplan(floorplan, target_requirements=requirements)

    # Apply geometry solver if overlaps / out of bounds exist
    repaired_plan, was_repaired = repair_geometry_if_needed(floorplan)
    if was_repaired:
        validation_info = validate_floorplan(repaired_plan, target_requirements=requirements)
        validation_info["repaired"] = True

    return {
        "requested_model": model_type,
        "actual_model_used": actual_model_used,
        "is_trained_checkpoint": is_real_checkpoint,
        "status": status_msg,
        "floorplan": repaired_plan,
        "validation": validation_info
    }
