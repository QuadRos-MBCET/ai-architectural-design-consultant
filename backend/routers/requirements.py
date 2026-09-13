from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from services.llm_service import extract_requirements

router = APIRouter(
    prefix="/api/requirements",
    tags=["requirements"],
)

class RequirementInput(BaseModel):
    user_prompt: str

class ExtractedRequirements(BaseModel):
    building_type: str
    climate: str
    key_features: list[str]
    sustainability_goals: list[str]
    user_capacity: str
    raw_extraction: str

@router.post("/extract", response_model=ExtractedRequirements)
async def process_requirements(req: RequirementInput):
    try:
        extracted = extract_requirements(req.user_prompt)
        return extracted
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
