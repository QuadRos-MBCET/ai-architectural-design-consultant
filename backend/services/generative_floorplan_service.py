from typing import Dict, Any, Tuple
import os
import sys
import numpy as np

# Import VAE and CGAN inference
from models.vae.inference import generate_with_vae
from models.gan.inference import generate_with_gan
try:
    from backend.services.llm_service import extract_requirements
    from backend.services.layout_validator import validate_floorplan, repair_geometry_if_needed
except ImportError:
    from services.llm_service import extract_requirements
    from services.layout_validator import validate_floorplan, repair_geometry_if_needed

def generate_bsp_baseline_floorplan(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procedural BSP layout generator used as a baseline benchmark and development fallback.
    Generates non-overlapping spatial partitions directly matching the user's prompt rooms.
    """
    b_width = float(requirements.get("building_width", requirements.get("width", 30.0)))
    b_length = float(requirements.get("building_length", requirements.get("length", 20.0)))
    b_type = requirements.get("building_type", "library")
    rooms = requirements.get("rooms", [])

    if not rooms:
        rooms = [
            {"type": "reading_hall", "name": "Main Reading Hall"},
            {"type": "librarian_office", "name": "Librarian Office"},
            {"type": "storage", "name": "Storage Room"},
            {"type": "toilet", "name": "Restroom"}
        ]

    count = len(rooms)
    cols = int(np.ceil(np.sqrt(count)))
    rows = int(np.ceil(count / float(cols)))

    cell_w = b_width / max(1, cols)
    cell_h = b_length / max(1, rows)

    formatted_rooms = []
    for idx, r in enumerate(rooms):
        c = idx % cols
        row_idx = idx // cols
        rx = round(c * cell_w, 2)
        ry = round(row_idx * cell_h, 2)
        rw = round(min(cell_w - 0.2, b_width - rx), 2)
        rh = round(min(cell_h - 0.2, b_length - ry), 2)

        r_name = r.get("name", f"Room {idx+1}")
        r_type = r.get("type", "room")

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
      - 'bsp_baseline': Procedural BSP Baseline Algorithm
    """
    model_type = model_type.lower()
    floorplan = None
    is_real_checkpoint = False
    status_msg = ""
    actual_model_used = model_type

    if model_type == "vae":
        floorplan, is_real_checkpoint, status_msg = generate_with_vae(requirements)
        if not floorplan:
            actual_model_used = "bsp_baseline"
            floorplan = generate_bsp_baseline_floorplan(requirements)
            status_msg = "VAE Checkpoint unavailable — executed BSP procedural fallback."

    elif model_type == "gan":
        floorplan, is_real_checkpoint, status_msg = generate_with_gan(requirements)
        if not floorplan:
            actual_model_used = "bsp_baseline"
            floorplan = generate_bsp_baseline_floorplan(requirements)
            status_msg = "GAN Checkpoint unavailable — executed BSP procedural fallback."

    else:
        actual_model_used = "bsp_baseline"
        is_real_checkpoint = True
        floorplan = generate_bsp_baseline_floorplan(requirements)
        status_msg = "Generated using Procedural BSP Baseline Generator."

    # Validate generated geometry
    validation_info = validate_floorplan(floorplan, target_requirements=requirements)

    # Apply minor geometry repair if overlaps / out of bounds exist
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
