from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import requirements

app = FastAPI(
    title="AI Architectural Design Consultant API",
    description="Backend API for the AI Architectural Design Consultant research prototype.",
    version="0.1.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Architectural Design Consultant API. Visit /docs for the interactive API documentation."}
