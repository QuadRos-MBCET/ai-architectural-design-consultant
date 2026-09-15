import streamlit as st
import sys
import os
import json
import base64
import time

# Ensure backend imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from services.llm_service import extract_requirements_from_prompt
from services.floorplan_service import generate_svg_floorplan
from services.extrusion_service import generate_floor_extrusion, export_combined_meshes
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Architectural Consultant", layout="wide")

st.title("🏛️ AI Architectural Design Consultant")
st.markdown("Generative Retrieval-Augmented 3D Design Pipeline")

# Initialize session state
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "gen3d_data" not in st.session_state:
    st.session_state.gen3d_data = None

def render_mermaid(mermaid_code):
    html_code = f"""
    <div style="background-color: #1a202c; padding: 20px; border-radius: 8px;">
        <div class="mermaid" style="display: flex; justify-content: center; color: white;">
            {mermaid_code}
        </div>
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    </script>
    """
    components.html(html_code, height=500, scrolling=True)

def render_model_viewer(glb_base64):
    html_code = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
    <div style="width: 100%; height: 500px; background-color: #1a202c; border-radius: 8px; overflow: hidden; display: flex; justify-content: center; align-items: center;">
        <model-viewer 
            src="data:model/gltf-binary;base64,{glb_base64}" 
            camera-controls 
            auto-rotate 
            shadow-intensity="1"
            style="width: 100%; height: 100%;"
            exposure="1.2">
        </model-viewer>
    </div>
    """
    components.html(html_code, height=520)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Project Requirements")
    prompt = st.text_area("Describe the architectural project...", value="design a 4 floor eco friendly public library for a hot climate", height=200)
    
    if st.button("Generate Multi-Story Design", type="primary", use_container_width=True):
        with st.spinner("Analyzing geometry & generating blueprints..."):
            json_spec = extract_requirements_from_prompt(prompt)
            st.session_state.report_data = json_spec
            
            # Setup output directories for rendering
            public_dir = os.path.join(os.path.dirname(__file__), "static")
            os.makedirs(public_dir, exist_ok=True)
            
            b_width = json_spec.get("building_width", 30)
            b_length = json_spec.get("building_length", 30)
            project_name = json_spec.get("project", {}).get("type", "Floor Plan")
            floors = json_spec.get("floors", [])
            
            all_floor_meshes = []
            floor_responses = []
            
            st.session_state.gen3d_data = None
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, floor in enumerate(floors):
                status_text.text(f"Extruding Multi-Story Massing Model: Floor {idx+1}/{len(floors)}...")
                level = floor.get("level", idx + 1)
                name = floor.get("name", f"Floor {level}")
                
                # Generate SVG
                svg_filename = f"floorplan_{level}.svg"
                svg_path = os.path.join(public_dir, svg_filename)
                generate_svg_floorplan(b_width, b_length, floor, svg_path, project_name)
                
                # Generate GLB
                glb_filename = f"concept_floor_{level}.glb"
                glb_path = os.path.join(public_dir, glb_filename)
                elevation = idx * 4.0
                
                meshes = generate_floor_extrusion(b_width, b_length, floor, elevation, glb_path)
                if meshes:
                    all_floor_meshes.extend(meshes)
                    
                # Read base64
                with open(svg_path, "r", encoding="utf-8") as f:
                    svg_content = f.read()
                
                with open(glb_path, "rb") as f:
                    glb_base64 = base64.b64encode(f.read()).decode('utf-8')
                    
                floor_responses.append({
                    "name": name,
                    "svg_content": svg_content,
                    "glb_base64": glb_base64
                })
                
                progress_bar.progress((idx + 1) / len(floors))
                
            status_text.text("Merging combined 3D models...")
            combined_filename = "concept_combined.glb"
            combined_path = os.path.join(public_dir, combined_filename)
            export_combined_meshes(all_floor_meshes, combined_path)
            
            with open(combined_path, "rb") as f:
                combined_glb_base64 = base64.b64encode(f.read()).decode('utf-8')
                
            st.session_state.gen3d_data = {
                "combined_glb": combined_glb_base64,
                "floors": floor_responses
            }
            
            progress_bar.empty()
            status_text.empty()
            st.success("Generation Complete!")

    if st.session_state.report_data and "materials_estimate" in st.session_state.report_data:
        st.subheader("Bill of Materials (INR)")
        materials = st.session_state.report_data["materials_estimate"]
        # Format materials into a list of dicts for dataframe
        df_data = []
        for m in materials:
            df_data.append({
                "Item": m["item"],
                "Qty": f"{m['quantity']} {m['unit']}",
                "Rate": f"₹{m['present_rate']:,.2f}",
                "Total Cost": f"₹{m['total_cost']:,.0f}"
            })
        st.dataframe(df_data, hide_index=True, use_container_width=True)

with col2:
    if st.session_state.gen3d_data and st.session_state.report_data:
        # Create tabs dynamically based on floors + systems + combined
        tab_names = ["Systems Diagram", "Entire Building"] + [f["name"] for f in st.session_state.gen3d_data["floors"]]
        tabs = st.tabs(tab_names)
        
        with tabs[0]:
            st.subheader("Climate & Systems Architecture")
            render_mermaid(st.session_state.report_data["systems_diagram"])
            
        with tabs[1]:
            st.subheader("Multi-Story Building View")
            render_model_viewer(st.session_state.gen3d_data["combined_glb"])
            
        for idx, floor in enumerate(st.session_state.gen3d_data["floors"]):
            with tabs[idx + 2]:
                st.subheader(f"2D Blueprint - {floor['name']}")
                st.markdown(floor['svg_content'], unsafe_allow_html=True)
                
                st.subheader("3D CAD Rendering")
                render_model_viewer(floor['glb_base64'])
    else:
        st.info("Enter a prompt and click Generate to see visualizations here.")
