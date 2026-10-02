import sys
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from backend.services.consultant_service import run_rag_consultant_pipeline, compare_standard_vs_rag
except Exception:
    from services.consultant_service import run_rag_consultant_pipeline, compare_standard_vs_rag

router = APIRouter(prefix="/api/consultant", tags=["consultant"])

class ConsultantRequest(BaseModel):
    prompt: str
    width: Optional[float] = 30.0
    length: Optional[float] = 20.0

@router.post("/analyze")
async def analyze_prompt(request: ConsultantRequest):
    """
    RAG Architectural Design Consultant:
    Retrieves real-world architectural knowledge, extracts climate & spatial rules, and generates context-aware layout.
    """
    try:
        res = run_rag_consultant_pipeline(request.prompt, width=request.width or 30.0, length=request.length or 20.0)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_frameworks(request: ConsultantRequest):
    """
    Experimental Comparison:
    Compares Standard Prompt-Only Baseline vs. Our Proposed RAG-Backed AI Architectural Consultant Framework.
    """
    try:
        res = compare_standard_vs_rag(request.prompt, width=request.width or 30.0, length=request.length or 20.0)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
