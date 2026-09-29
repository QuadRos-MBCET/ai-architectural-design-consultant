from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import requirements, design, floorplan
import os

app = FastAPI(
    title="Prompt-Based 2D Floor Plan Generation Using GAN and VAE",
    description="Generative AI system for synthesizing architectural 2D floor plans from natural language prompts using Conditional GAN and VAE models.",
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

@app.get("/")
def read_root():
    return {
        "title": "Prompt-Based 2D Floor Plan Generation Using GAN and VAE",
        "status": "Operational",
        "documentation": "/docs",
        "endpoints": {
            "generate": "/api/floorplan/generate",
            "compare": "/api/floorplan/compare",
            "models": "/api/floorplan/models",
            "validate": "/api/floorplan/validate",
            "render": "/api/floorplan/render"
        }
    }
