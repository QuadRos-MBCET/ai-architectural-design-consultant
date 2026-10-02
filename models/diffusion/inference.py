import os
import torch
from typing import Dict, Any, Tuple
from models.diffusion.floorplan_ddpm import ConditionalDDPM
from preprocessing.floorplan_encoder import FloorplanEncoder

def load_diffusion_model() -> Tuple[ConditionalDDPM, bool]:
    ckpt_path = os.path.join(os.path.dirname(__file__), "checkpoints", "ddpm_latest.pt")
    if not os.path.exists(ckpt_path):
        return None, False

    try:
        ckpt = torch.load(ckpt_path, map_location="cpu")
        model = ConditionalDDPM(
            max_rooms=ckpt.get("max_rooms", 16),
            feature_dim=ckpt.get("feature_dim", 26),
            cond_dim=ckpt.get("cond_dim", 24),
            timesteps=ckpt.get("timesteps", 100)
        )
        model.load_state_dict(ckpt["model_state_dict"])
        model.eval()
        return model, True
    except Exception as e:
        print(f"Error loading DDPM Diffusion checkpoint: {e}")
        return None, False

def generate_with_diffusion(requirements: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
    """
    Generates a 2D floor plan using the trained Conditional DDPM Diffusion model.
    Returns: (floorplan_json, is_real_model, status_message)
    """
    model, is_loaded = load_diffusion_model()
    b_width = float(requirements.get("building_width", requirements.get("width", 30.0)))
    b_length = float(requirements.get("building_length", requirements.get("length", 20.0)))
    b_type = requirements.get("building_type", "library")

    encoder = FloorplanEncoder()

    if not is_loaded:
        return None, False, "DDPM Diffusion model checkpoint not available."

    try:
        dummy_plan = {"building_width": b_width, "building_length": b_length, "rooms": requirements.get("rooms", [])}
        _, cond_vec = encoder.encode(dummy_plan)
        cond_tensor = torch.tensor(cond_vec, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            sampled_tensor = model.sample(cond_tensor, num_samples=1)[0]

        floorplan_json = encoder.decode(sampled_tensor, b_width=b_width, b_length=b_length, building_type=b_type, target_requirements=requirements)
        return floorplan_json, True, "Generated using PyTorch Conditional DDPM Diffusion Model"
    except Exception as e:
        print(f"Diffusion Inference failure: {e}")
        return None, False, f"Diffusion Inference Error: {e}"
