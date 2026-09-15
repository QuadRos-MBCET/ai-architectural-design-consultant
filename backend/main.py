from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import requirements, design
import os

app = FastAPI(title="AI Architectural Design Consultant")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory to serve images/models over the internet
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routers
app.include_router(requirements.router)
app.include_router(design.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Architectural Design Consultant API. Visit /docs for the interactive API documentation."}
