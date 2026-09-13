# AI Architectural Design Consultant

A research-oriented Generative AI system for architectural concept design.

## Project Structure
- `/backend`: FastAPI Python backend
- `/frontend`: React frontend
- `/rag`, `/embeddings`, `/data`: Data and AI pipelines
- `/prompts`: LLM prompts
- `/docs`: Documentation

## Phase 1: Setup

### Backend
1. Navigate to `backend`
2. Run `pip install -r requirements.txt` (recommend doing this in a virtual environment)
3. Run `uvicorn main:app --reload` to start the backend on port 8000.

### Frontend
1. Navigate to `frontend`
2. Run `npm install`
3. Run `npm run dev` to start the Vite frontend.
