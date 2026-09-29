from typing import Dict, Any, Tuple
import os
import sys

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
    """
    b_width = float(requirements.get("building_width", requirements.get("width", 30.0)))
    b_length = float(requirements.get("building_length", requirements.get("length", 20.0)))
    b_type = requirements.get("building_type", "library")

    # Run BSP generator from llm_service
    prompt_str = f"design a 1 floor {b_type} of {int(b_width)}m x {int(b_length)}m"
    res = extract_requirements(prompt_str, width=b_width, length=b_length)

    floors = res.get("floors", [])
    rooms = floors[0].get("rooms", []) if floors else []

    formatted_rooms = []
    for idx, r in enumerate(rooms):
        formatted_rooms.append({
            "id": idx + 1,
            "type": r.get("name", "room").lower().replace(" ", "_"),
            "name": r.get("name", f"Room {idx+1}"),
            "x": float(r.get("x", 0.0)),
            "y": float(r.get("y", 0.0)),
            "width": float(r.get("width", 5.0)),
            "height": float(r.get("length", r.get("height", 5.0))),
            "is_nested": r.get("is_nested", False)
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
