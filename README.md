# Prompt-Based 2D Floor Plan Generation Using GAN and VAE

A Generative AI system for synthesizing architectural 2D floor plans from natural language prompts using **Conditional GAN** and **Conditional VAE** PyTorch models, complete with geometric validation and 2D SVG blueprint rendering.

---

## 🌟 Key Features

- **Natural Language Prompt Processing**: Converts prompts (*e.g., "Create a modern college library of 30m × 20m with a reading hall, computer section, librarian office, storage and toilets"*) into structured requirements.
- **Deep Generative AI Models (PyTorch)**:
  - **Conditional GAN (`models/gan/`)**: Adversarial layout generator conditioned on spatial dimensions and room programs.
  - **Conditional VAE (`models/vae/`)**: Variational autoencoder mapping architectural layouts into continuous latent space.
  - **BSP Baseline Engine**: Procedural Binary Space Partitioning benchmark and offline fallback.
- **Automated Geometry Validation (`backend/services/layout_validator.py`)**: Audits room overlap ($m^2$), boundary compliance, minimum dimensions, unused space ratio, and room coverage.
- **SVG Architectural Blueprint Renderer (`backend/services/floorplan_service.py`)**: Renders clean 2D blueprint drawings featuring background grid lines, thick interior/exterior walls, door swing arcs, glass window openings, title blocks, and entrance indicators.
- **Dual User Interfaces**:
  - **React + Vite Studio (`frontend/`)**: Modern web UI featuring model selection, interactive blueprint rendering, metric dashboards, SVG/PNG download options, and a side-by-side **Model Comparison Mode**.
  - **Streamlit Studio (`streamlit_app.py`)**: Standalone dashboard alternative.
- **Zero Cloud API Lock-in**: Fully functional locally without requiring cloud LLM dependencies (e.g., Gemini / OpenAI).

---

## 📐 System Architecture

```
NATURAL LANGUAGE PROMPT
        ↓
REQUIREMENT PARSER (Local / Deterministic)
        ↓
STRUCTURED REQUIREMENTS JSON
        ↓
CONDITIONAL VAE / GAN (PyTorch Models)
        ↓
STRUCTURED 2D FLOOR-PLAN LAYOUT
        ↓
GEOMETRY VALIDATION & REPAIR
        ↓
2D SVG BLUEPRINT RENDERER
        ↓
INTERACTIVE REACT & STREAMLIT UI
```

---

## 🛠️ Project Structure

```
.
├── backend/                  # FastAPI Python backend
│   ├── main.py               # Application entry point & router mounting
│   ├── routers/              # API endpoints (/api/floorplan, /api/requirements)
│   └── services/             # Generative floorplan service, validator, SVG renderer
├── frontend/                 # React + Vite frontend single-page application
│   ├── src/App.jsx           # Main 2D Floor Plan Generator studio UI
│   └── src/App.css           # Styling rules
├── models/                   # PyTorch deep learning models
│   ├── gan/                  # Conditional GAN (generator, discriminator, cgan)
│   └── vae/                  # Conditional VAE (encoder, decoder, vae)
├── preprocessing/            # Dataset parsing, encoding, and tensor builder
├── data/                     # Ground-truth typologies & processed dataset tensors
├── docs/                     # Comprehensive documentation & architectural specs
├── streamlit_app.py          # Streamlit Studio dashboard
├── requirements.txt          # Python dependencies
└── run_project.bat           # Startup batch script for Windows
```

---

## 🚀 Quick Start Guide

### 1. Installation & Environment Setup
Clone the repository and install the Python dependencies:

```bash
pip install -r requirements.txt
```

To set up the React frontend:

```bash
cd frontend
npm install
```

### 2. Preprocess Dataset & Train PyTorch Models

Build processed dataset tensors from architectural seed data:

```bash
python -m preprocessing.dataset_builder
```

Train the **Conditional VAE** and **Conditional GAN** models:

```bash
# Train Conditional VAE (50 epochs)
python -m models.vae.train

# Train Conditional GAN (50 epochs)
python -m models.gan.train
```

Checkpoints will be saved automatically to `models/vae/checkpoints/` and `models/gan/checkpoints/`.

---

## 💻 Running the Application

### Option A: Launch Both Servers (FastAPI + React Vite)
Run the startup script:

```cmd
run_project.bat
```
- **Backend API**: `http://localhost:8000` (Interactive API Docs: `http://localhost:8000/docs`)
- **React Frontend**: `http://localhost:5173`

### Option B: Run Streamlit Studio Dashboard
```bash
streamlit run streamlit_app.py
```

---

## 🔌 API Reference

### `POST /api/floorplan/generate`
Generates a 2D floor plan using the requested model (`gan`, `vae`, or `bsp_baseline`).

#### Request Body
```json
{
  "prompt": "Create a modern college library of 30m x 20m with reading hall, computer section, librarian office, storage and toilets.",
  "model": "gan",
  "building_type": "library",
  "width": 30.0,
  "length": 20.0
}
```

#### Response
```json
{
  "success": true,
  "model_requested": "gan",
  "actual_model_used": "gan",
  "is_trained_checkpoint": true,
  "status": "Generated using PyTorch Conditional GAN",
  "floorplan": { ... },
  "validation": {
    "valid": true,
    "score_percentage": 82.5,
    "overlaps_count": 0,
    "unused_area_ratio": 0.18
  },
  "svg_url": "/static/floorplan_gan_1727606000.svg",
  "svg_content": "<svg ...></svg>"
}
```

### `POST /api/floorplan/compare`
Executes VAE, GAN, and BSP Baseline concurrently for side-by-side comparative benchmarking.

---

## 📚 Documentation Links
- [Architectural Overview](docs/architecture.md)
- [Standard Floor-Plan Representation Spec](docs/floorplan_representation.md)
- [Model Training Guide](docs/model_training.md)
- [Evaluation & Benchmarks](docs/evaluation.md)

---

## 📜 Research Integrity & Transparency
- **Explicit Model Reporting**: The application explicitly reports the model used (`gan`, `vae`, or `bsp_baseline`) and whether a trained checkpoint was loaded (`is_trained_checkpoint`).
- **No Faked Weights**: If a model checkpoint is unpopulated or missing, the system gracefully falls back to the procedural BSP generator while clearly informing the user: `"Model checkpoint not available — using development fallback."`
