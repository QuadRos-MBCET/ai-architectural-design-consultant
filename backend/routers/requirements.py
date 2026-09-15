from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from services.llm_service import extract_requirements
from typing import Dict, Any

router = APIRouter(
    prefix="/api/requirements",
    tags=["requirements"],
)

class RequirementsRequest(BaseModel):
    user_prompt: str

class RequirementsResponse(BaseModel):
    structured_json: Dict[str, Any]

@router.post("/extract", response_model=RequirementsResponse)
async def extract_requirements_endpoint(request: RequirementsRequest):
    try:
        # Call the LLM service to extract structured requirements
        json_data = extract_requirements(request.user_prompt)
        return RequirementsResponse(structured_json=json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
