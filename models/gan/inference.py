import os
import torch
from typing import Dict, Any, Tuple
from models.gan.cgan import FloorplanCGAN
from preprocessing.floorplan_encoder import FloorplanEncoder

def load_cgan_model() -> Tuple[FloorplanCGAN, bool]:
    ckpt_path = os.path.join(os.path.dirname(__file__), "checkpoints", "cgan_latest.pt")
    if not os.path.exists(ckpt_path):
        return None, False

    try:
        ckpt = torch.load(ckpt_path, map_location="cpu")
        cgan = FloorplanCGAN(
            noise_dim=ckpt.get("noise_dim", 64),
            cond_dim=ckpt.get("cond_dim", 24),
            max_rooms=ckpt.get("max_rooms", 16),
            feature_dim=ckpt.get("feature_dim", 26)
        )
        cgan.generator.load_state_dict(ckpt["generator_state_dict"])
        cgan.generator.eval()
        return cgan, True
    except Exception as e:
        print(f"Error loading Conditional GAN checkpoint: {e}")
        return None, False

def generate_with_gan(requirements: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
    """
    Generates a 2D floor plan using the trained Conditional GAN model.
    Returns: (floorplan_json, is_real_model, status_message)
    """
    cgan, is_loaded = load_cgan_model()
    b_width = float(requirements.get("building_width", requirements.get("width", 30.0)))
    b_length = float(requirements.get("building_length", requirements.get("length", 20.0)))
    b_type = requirements.get("building_type", "library")

    encoder = FloorplanEncoder()

    if not is_loaded:
        return None, False, "Model checkpoint not available — using development fallback."

    try:
        dummy_plan = {"building_width": b_width, "building_length": b_length, "rooms": requirements.get("rooms", [])}
        _, cond_vec = encoder.encode(dummy_plan)
        cond_tensor = torch.tensor(cond_vec, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            sampled_tensor = cgan.generate(cond_tensor, num_samples=1)[0]

        floorplan_json = encoder.decode(sampled_tensor, b_width=b_width, b_length=b_length, building_type=b_type, target_requirements=requirements)
        return floorplan_json, True, "Generated using PyTorch Conditional GAN"
    except Exception as e:
        print(f"GAN Inference failure: {e}")
        return None, False, f"GAN Inference Error: {e}"
