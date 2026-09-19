# Architectural Master Prompts

This document contains generalized, modular architectural master prompts designed to adapt to any building typology (residential, commercial, mixed-use, institutional, or industrial) based on specific project needs. You can copy and paste these into the Streamlit Application during your presentation.

---

## 1. The Modular Master Prompt

**Copy and paste the following into the Streamlit Web App's "Project Requirements" text box, filling in the bracketed information:**

Act as a senior computational design architect. Generate a conceptual design package including schematic floor plans, functional zoning diagrams, structural grid logic, and 3D massing for the following project:

**1. Project Overview & Typology:**
Building Type: [Specify: e.g., Multi-Family Residential / Commercial Office / Mixed-Use Retail + Housing / Boutique Hotel / Healthcare Clinic / Cultural Pavilion]
Site & Footprint: [e.g., 1,500 sq ft (30 ft × 50 ft) urban infill plot / 500 sq m corner lot]
Scale & Height: [e.g., 3-story structure / 12m height limit / FAR requirement]
Context & Climate: [e.g., Dense tropical urban core / Temperate suburban street / Arid climate]

**2. Architectural Language & Performance:**
Style / Movement: [e.g., Contemporary Minimalist, Biophilic, Brutalist, High-Tech, Vernacular-Modern]
Envelope & Materials: Low-maintenance facade, optimized window-to-wall ratio (WWR), passive solar shading (louvers/fins), and a high-performance material palette (e.g., exposed concrete, timber cladding, low-E glazing).
Environmental Strategy: Prioritize passive cross-ventilation, daylight penetration via light wells or atriums, and energy-efficient building orientation.

**3. Program & Spatial Zoning:**
Level 1 (Public / Semi-Public / Service): Main entrance/foyer, vertical circulation core (stairs/elevator), active street-facing functions (reception, retail, or living), and service access (parking, utilities, restrooms).
Intermediate Level(s) (Operational / Semi-Private): Primary functional spaces (open office zones, conference hubs, or bedroom suites) organized around a central circulation spine.
Top Level (Private / Executive / Amenity): Specialized quiet zones (executive suites, master sanctuary, creative studios) opening to an accessible outdoor roof terrace.

**4. Deliverables Required:**
Layered 2D schematic layouts showing circulation cores, structural column grid, egress paths, and spatial dimensions.
Functional adjacency matrix and area programming breakdown.
3D isometric cutaway diagram showing spatial volume relationships and facade articulation.

---

## 2. PDF Document Analysis & Code Compliance Prompt

**Use this prompt when demonstrating the AI's ability to analyze existing blueprints and run structural/plumbing checks:**

You are an expert computational architect and BIM consultant. Analyze the floor plan and drawing details provided in the uploaded PDF document to generate an optimized spatial breakdown and architectural model.

**1. Document & Drawing Ingestion:**
Scale & Vector Extraction: Detect the drawing scale, grid lines, structural columns, load-bearing vs. partition walls, door swings, and window openings.
Typology Detection: Identify the target program based on spatial distribution, whether Residential (single/multi-family, duplex, villa) or Hospitality (boutique hotel, business hotel, guest lodge, resort units).

**2. Typology-Specific & En-Suite Spatial Rules:**
En-Suite & Wet-Area Detection: Explicitly account for internal en-suite bathrooms/toilets integrated directly within bedrooms or guest rooms (water closet, vanity, shower/bath zone, and plumbing chase alignment). Distinguish between private attached en-suites and common/powder rooms.
Residential Logic: Delineate private sleeping zones, public living/dining zones, service access, and utility balconies while checking circulation privacy.
Hospitality Logic: Account for standard guest key rooms (typical bay widths, entry vestibules with en-suite bathrooms, wardrobe closets), service corridors, housekeeping vertical cores, fire egress stairs, and acoustic buffer zones.

**3. Analysis & Output Deliverables:**
Programmatic Area Schedule: Provide a tabular summary listing each detected space, room function, estimated dimensions (L × W), total usable floor area, and en-suite connection.
Circulation & Code Compliance Assessment: Flag bottlenecks, dead-end corridors, daylight access (window-to-floor area adequacy), and plumbing stack efficiency across floors.
Redesign / 3D Extrusion Recommendations: Suggest massing refinements, structural grid optimization, and spatial reallocations based on the detected layout.
