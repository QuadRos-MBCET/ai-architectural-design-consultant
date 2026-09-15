from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import os
import time
from services.floorplan_service import generate_svg_floorplan
from services.extrusion_service import generate_floor_extrusion, export_combined_meshes

router = APIRouter(prefix="/api/design", tags=["design"])

class Generate3DRequest(BaseModel):
    structured_json: Dict[str, Any]

class FloorResponse(BaseModel):
    level: int
    name: str
    blueprint_url: str
    model_url: str
    
class Generate3DResponse(BaseModel):
    combined_model_url: str
    floors: List[FloorResponse]

@router.post("/generate-3d", response_model=Generate3DResponse)
async def generate_3d(request: Generate3DRequest):
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        public_dir = os.path.join(base_dir, "static")
        os.makedirs(public_dir, exist_ok=True)
        
        json_data = request.structured_json
        b_width = json_data.get("building_width", 30)
        b_length = json_data.get("building_length", 30)
        project_name = json_data.get("project", {}).get("type", "Floor Plan")
        floors = json_data.get("floors", [])
        
        timestamp = int(time.time())
        all_floor_meshes = []
        floor_responses = []
        
        for idx, floor in enumerate(floors):
            level = floor.get("level", idx + 1)
            name = floor.get("name", f"Floor {level}")
            
            # SVG
            svg_filename = f"floorplan_{level}.svg"
            svg_path = os.path.join(public_dir, svg_filename)
            generate_svg_floorplan(b_width, b_length, floor, svg_path, project_name)
            
            # GLB
            glb_filename = f"concept_floor_{level}.glb"
            glb_path = os.path.join(public_dir, glb_filename)
            elevation = idx * 4.0 # 4 meters per floor
            
            meshes = generate_floor_extrusion(b_width, b_length, floor, elevation, glb_path)
            if meshes:
                all_floor_meshes.extend(meshes)
                
            floor_responses.append(FloorResponse(
                level=level,
                name=name,
                blueprint_url=f"/static/{svg_filename}?t={timestamp}",
                model_url=f"/static/{glb_filename}?t={timestamp}"
            ))
            
        # Combine
        combined_filename = "concept_combined.glb"
        combined_path = os.path.join(public_dir, combined_filename)
        export_combined_meshes(all_floor_meshes, combined_path)
        
        return Generate3DResponse(
            combined_model_url=f"/static/{combined_filename}?t={timestamp}",
            floors=floor_responses
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
