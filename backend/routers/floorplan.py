import os
import time
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List

try:
    from backend.routers.requirements import parse_requirements_locally
    from backend.services.generative_floorplan_service import generate_floorplan
    from backend.services.layout_validator import validate_floorplan
    from backend.services.floorplan_service import render_floorplan_svg
except ImportError:
    from routers.requirements import parse_requirements_locally
    from services.generative_floorplan_service import generate_floorplan
    from services.layout_validator import validate_floorplan
    from services.floorplan_service import render_floorplan_svg
from models.vae.inference import load_vae_model
from models.gan.inference import load_cgan_model
from models.diffusion.inference import load_diffusion_model

router = APIRouter(prefix="/api/floorplan", tags=["floorplan"])

class FloorplanGenerateRequest(BaseModel):
    prompt: Optional[str] = None
    model: Optional[str] = "gan"
    building_type: Optional[str] = None
    width: Optional[float] = None
    length: Optional[float] = None

class FloorplanValidateRequest(BaseModel):
    floorplan: Dict[str, Any]
    requirements: Optional[Dict[str, Any]] = None

class FloorplanRenderRequest(BaseModel):
    floorplan: Dict[str, Any]

@router.get("/models")
async def get_available_models():
    _, vae_loaded = load_vae_model()
    _, gan_loaded = load_cgan_model()
    _, diff_loaded = load_diffusion_model()
    return {
        "models": [
            {
                "id": "gan",
                "name": "Conditional GAN",
                "description": "Adversarial network conditioned on space requirements.",
                "available": gan_loaded,
                "status": "Trained Checkpoint Available" if gan_loaded else "Checkpoint Unavailable — Uses Procedural Fallback"
            },
            {
                "id": "vae",
                "name": "Conditional VAE",
                "description": "Variational autoencoder sampling layout latent space.",
                "available": vae_loaded,
                "status": "Trained Checkpoint Available" if vae_loaded else "Checkpoint Unavailable — Uses Procedural Fallback"
            },
            {
                "id": "diffusion",
                "name": "Conditional DDPM Diffusion",
                "description": "Iterative denoising diffusion probabilistic model.",
                "available": diff_loaded,
                "status": "Trained Checkpoint Available" if diff_loaded else "Checkpoint Unavailable — Uses Procedural Fallback"
            },
            {
                "id": "bsp_baseline",
                "name": "BSP Baseline",
                "description": "Procedural Binary Space Partitioning benchmark.",
                "available": True,
                "status": "Operational Baseline"
            }
        ]
    }

@router.post("/generate")
async def generate_floorplan_endpoint(request: FloorplanGenerateRequest):
    try:
        # Step 1: Requirements Extraction
        if request.prompt:
            requirements = parse_requirements_locally(request.prompt)
        else:
            requirements = {
                "building_type": request.building_type or "library",
                "building_width": request.width or 30.0,
                "building_length": request.length or 20.0,
                "rooms": []
            }

        if request.building_type: requirements["building_type"] = request.building_type
        if request.width: requirements["building_width"] = request.width
        if request.length: requirements["building_length"] = request.length

        selected_model = (request.model or "gan").lower()

        # Step 2: Generative Floor Plan Generation (VAE / GAN / BSP Baseline)
        gen_result = generate_floorplan(requirements, model_type=selected_model)

        # Step 3: Render 2D Architectural Blueprint SVG
        timestamp = int(time.time())
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_dir = os.path.join(base_dir, "static")
        os.makedirs(static_dir, exist_ok=True)

        filename = f"floorplan_{selected_model}_{timestamp}.svg"
        output_path = os.path.join(static_dir, filename)

        svg_content = render_floorplan_svg(gen_result["floorplan"], output_path=output_path)

        return {
            "success": True,
            "model_requested": selected_model,
            "actual_model_used": gen_result["actual_model_used"],
            "is_trained_checkpoint": gen_result["is_trained_checkpoint"],
            "status": gen_result["status"],
            "requirements": requirements,
            "floorplan": gen_result["floorplan"],
            "validation": gen_result["validation"],
            "svg_url": f"/static/{filename}?t={timestamp}",
            "svg_content": svg_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_floorplan_models(request: FloorplanGenerateRequest):
    """
    Generates and returns floor plans for VAE, GAN, and BSP Baseline side-by-side for model comparison.
    """
    try:
        if request.prompt:
            requirements = parse_requirements_locally(request.prompt)
        else:
            requirements = {
                "building_type": request.building_type or "library",
                "building_width": request.width or 30.0,
                "building_length": request.length or 20.0,
                "rooms": []
            }

        if request.building_type: requirements["building_type"] = request.building_type
        if request.width: requirements["building_width"] = request.width
        if request.length: requirements["building_length"] = request.length

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_dir = os.path.join(base_dir, "static")
        os.makedirs(static_dir, exist_ok=True)
        timestamp = int(time.time())

        results = {}
        for m in ["gan", "vae", "diffusion", "bsp_baseline"]:
            start_time = time.time()
            gen_res = generate_floorplan(requirements, model_type=m)
            elapsed_ms = round((time.time() - start_time) * 1000, 1)

            filename = f"floorplan_compare_{m}_{timestamp}.svg"
            output_path = os.path.join(static_dir, filename)
            svg_content = render_floorplan_svg(gen_res["floorplan"], output_path=output_path)

            model_name_map = {
                "gan": "Conditional GAN",
                "vae": "Conditional VAE",
                "diffusion": "DDPM Diffusion",
                "bsp_baseline": "BSP Baseline"
            }

            results[m] = {
                "model_name": model_name_map.get(m, m.upper()),
                "actual_model_used": gen_res["actual_model_used"],
                "is_trained_checkpoint": gen_res["is_trained_checkpoint"],
                "status": gen_res["status"],
                "generation_time_ms": elapsed_ms,
                "floorplan": gen_res["floorplan"],
                "validation": gen_res["validation"],
                "svg_url": f"/static/{filename}?t={timestamp}",
                "svg_content": svg_content
            }

        return {
            "success": True,
            "requirements": requirements,
            "comparison": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_endpoint(request: FloorplanValidateRequest):
    val_info = validate_floorplan(request.floorplan, target_requirements=request.requirements)
    return {"success": True, "validation": val_info}

@router.post("/render")
async def render_endpoint(request: FloorplanRenderRequest):
    svg_str = render_floorplan_svg(request.floorplan)
    return {"success": True, "svg_content": svg_str}
