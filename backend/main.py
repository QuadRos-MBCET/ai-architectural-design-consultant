from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import requirements, design, floorplan, consultant
import os

app = FastAPI(
    title="AI Architectural Design Consultant: A RAG Framework for Context-Aware Conceptual Architectural Design",
    description="Retrieval-Augmented Generation (RAG) system combining LLMs, FAISS vector databases, and diffusion models for context-aware architectural design.",
    version="2.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Crash-Prevention Exception Handler
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback
import gc

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    tb_str = traceback.format_exc()
    print(f"[CRASH PREVENTED] Exception on {request.url.path}: {error_msg}\n{tb_str}")
    gc.collect()  # Clean up unreferenced objects to avoid memory leaks
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal Server Error", "detail": error_msg}
    )

# Mount static directories to serve SVG blueprints over HTTP
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")
root_static_dir = os.path.join(os.path.dirname(base_dir), "static")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(root_static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routers
app.include_router(requirements.router)
app.include_router(design.router)
app.include_router(floorplan.router)
app.include_router(consultant.router)

@app.get("/")
def read_root():
    return {
        "title": "AI Architectural Design Consultant: RAG Framework",
        "status": "Operational",
        "documentation": "/docs",
        "endpoints": {
            "consultant_analyze": "/api/consultant/analyze",
            "consultant_compare": "/api/consultant/compare",
            "floorplan_generate": "/api/floorplan/generate",
            "floorplan_compare": "/api/floorplan/compare"
        }
    }
