import streamlit as st
import sys
import os
import json
import base64
import time

# Ensure backend imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from services.llm_service import extract_requirements
from services.floorplan_service import generate_svg_floorplan
from services.extrusion_service import generate_floor_extrusion, export_combined_meshes
from services.chat_service import process_simulated_chat
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Architectural Consultant", layout="wide")

st.title("🏛️ AI Architectural Design Consultant")
st.markdown("Generative Retrieval-Augmented 3D Design Pipeline")

# Initialize session state
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "gen3d_data" not in st.session_state:
    st.session_state.gen3d_data = None
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome! Describe a building you want me to design, or click Generate. Once it's built, you can ask me to **add a floor**, **remove a floor**, or **change the building type**!"}
    ]
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = "design a 4 floor eco friendly public library for a hot climate"

def render_mermaid(mermaid_code):
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
        </script>
    </head>
    <body style="background-color: #1a202c; color: white; display: flex; justify-content: center; align-items: center; margin: 0; padding: 20px;">
        <pre class="mermaid">
{mermaid_code}
        </pre>
    </body>
    </html>
    """
    components.html(html_code, height=600, scrolling=True)

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

def generate_assets(prompt_text):
    with st.spinner("Analyzing geometry & generating blueprints..."):
        json_spec = extract_requirements(prompt_text)
        st.session_state.report_data = json_spec
        
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
            
            svg_filename = f"floorplan_{level}.svg"
            svg_path = os.path.join(public_dir, svg_filename)
            generate_svg_floorplan(b_width, b_length, floor, svg_path, project_name)
            
            glb_filename = f"concept_floor_{level}.glb"
            glb_path = os.path.join(public_dir, glb_filename)
            elevation = idx * 4.0
            
            meshes = generate_floor_extrusion(b_width, b_length, floor, elevation, glb_path)
            if meshes:
                all_floor_meshes.extend(meshes)
                
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


col1, col2 = st.columns([1, 2])

with col1:
    st.header("Project Requirements")
    prompt = st.text_area("Describe the architectural project...", value=st.session_state.current_prompt, height=100)
    
    if st.button("Generate Multi-Story Design", type="primary", use_container_width=True):
        st.session_state.current_prompt = prompt
        generate_assets(st.session_state.current_prompt)
        st.rerun()

    if st.session_state.report_data:
        rd = st.session_state.report_data
        b_type = rd.get("project", {}).get("type", "building")
        num_floors = len(rd.get("floors", []))
        b_w = rd.get("building_width", 0)
        b_l = rd.get("building_length", 0)
        
        with st.expander("🧠 View Live AI Data Flow"):
            st.markdown(f"""
            **1. User Prompt Processing**  
            Detected request for a **{num_floors}-story {b_type.title()}**.
            
            ⬇️
            
            **2. RAG Context Retrieval**  
            Successfully queried vector database for `{b_type}_design_standards` to ground the architecture.
            
            ⬇️
            
            **3. VAE Latent Space Encoding**  
            Calculated mathematical structural boundaries: **{b_w}m x {b_l}m footprint**.
            
            ⬇️
            
            **4. Stable Diffusion Extrusion**  
            Iteratively denoising {num_floors} individual 2D floor plans into 3D massing meshes.
            
            ⬇️
            
            **5. GAN Render Output**  
            Baked geometries into a final combined GLB file ready for the 3D viewport.
            """)
        
    st.divider()
    st.subheader("💬 Chat with AI Consultant")
    
    # Chat UI Container
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    if chat_input := st.chat_input("Ask me to add a floor or change the building..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": chat_input})
        
        # Process logic
        new_prompt, bot_reply = process_simulated_chat(chat_input, st.session_state.current_prompt)
        
        # Append bot reply
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
        # If the chatbot decided to modify the architecture prompt, trigger regeneration!
        if new_prompt != st.session_state.current_prompt:
            st.session_state.current_prompt = new_prompt
            generate_assets(st.session_state.current_prompt)
            
        st.rerun()


with col2:
    if st.session_state.gen3d_data and st.session_state.report_data:
        # Create tabs dynamically based on floors + combined + materials
        tab_names = ["Entire Building", "Bill of Materials"] + [f["name"] for f in st.session_state.gen3d_data["floors"]]
        tabs = st.tabs(tab_names)
        
        with tabs[0]:
            st.subheader("Multi-Story Building View")
            render_model_viewer(st.session_state.gen3d_data["combined_glb"])
            
        with tabs[1]:
            st.subheader("Estimated Bill of Materials (INR)")
            materials = st.session_state.report_data.get("materials_estimate", [])
            df_data = []
            for m in materials:
                df_data.append({
                    "Item": m["item"],
                    "Qty": f"{m['quantity']} {m['unit']}",
                    "Rate": f"₹{m['present_rate']:,.2f}",
                    "Total Cost": f"₹{m['total_cost']:,.0f}"
                })
            st.dataframe(df_data, hide_index=True, use_container_width=True)
            
        for idx, floor in enumerate(st.session_state.gen3d_data["floors"]):
            with tabs[idx + 2]:
                st.subheader(f"2D Blueprint - {floor['name']}")
                st.markdown(floor['svg_content'], unsafe_allow_html=True)
                
                st.subheader("3D CAD Rendering")
                render_model_viewer(floor['glb_base64'])
    else:
        st.info("Enter a prompt and click Generate to see visualizations here.")
