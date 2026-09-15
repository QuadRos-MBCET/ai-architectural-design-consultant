from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import requirements, design

app = FastAPI(title="AI Architectural Design Consultant")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(requirements.router)
app.include_router(design.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Architectural Design Consultant API. Visit /docs for the interactive API documentation."}
