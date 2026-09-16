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
from services.pdf_service import analyze_pdf_blueprint
import streamlit.components.v1 as components

st.set_page_config(page_title="R D Homes | AI Architecture", layout="wide", initial_sidebar_state="expanded")

# Inject Custom Premium CSS Styling
st.markdown("""
<style>
    /* Import modern Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stApp {
        background-color: #0b0f19;
        background-image: radial-gradient(circle at 15% 50%, rgba(20, 30, 48, 1), rgba(11, 15, 25, 1));
    }

    /* Primary Headers */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }

    /* Style the Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.39);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        color: white;
    }

    /* Text Inputs and Text Areas */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 1px #8b5cf6 !important;
    }

    /* Expanders and Chat Bubbles */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stChatMessage"] {
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.1) !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 40px; margin-top: 10px;">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 16px; border-radius: 16px; box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4); display: flex; align-items: center; justify-content: center;">
            <svg width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 21h18"></path>
                <path d="M9 8h1"></path>
                <path d="M9 12h1"></path>
                <path d="M9 16h1"></path>
                <path d="M14 8h1"></path>
                <path d="M14 12h1"></path>
                <path d="M14 16h1"></path>
                <path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16"></path>
            </svg>
        </div>
        <div>
            <h1 style="font-size: 3.8rem; font-weight: 900; letter-spacing: -0.04em; margin: 0; line-height: 1.1; background: -webkit-linear-gradient(45deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                R D <span style="background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Homes</span>
            </h1>
            <p style="font-size: 1.2rem; color: #94a3b8; margin: 0; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase;">AI Architectural Studio</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "gen3d_data" not in st.session_state:
    st.session_state.gen3d_data = None
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to R D Homes! Describe a building you want our AI to design, or click Generate. Once it's built, you can ask me to **add a floor**, **remove a floor**, or **change the building type**!"}
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

def generate_assets(prompt_text, p_width=30, p_length=30, p_height=3.0, p_wwr=40):
    with st.spinner("Analyzing geometry & generating blueprints..."):
        try:
            json_spec = extract_requirements(prompt_text, width=p_width, length=p_length, height=p_height, wwr=p_wwr)
        except ValueError as e:
            if "Unknown Typology:" in str(e):
                err_msg = str(e).replace("Unknown Typology: ", "")
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
                st.warning("⚠️ Unknown Building Type detected! I have sent you a message in the AI Consultant Chat in the sidebar.")
            else:
                st.error(str(e))
            st.session_state.report_data = None
            st.session_state.gen3d_data = None
            return
            
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

app_mode = st.sidebar.radio("Navigation", ["Generative 3D Design", "PDF Blueprint Analysis"])

if app_mode == "Generative 3D Design":
    # 1. Left Panel (Sidebar Controls)
    b_width_override = st.sidebar.slider("Building Width (m)", min_value=10, max_value=60, value=30, step=5)
    b_length_override = st.sidebar.slider("Building Depth (m)", min_value=10, max_value=60, value=30, step=5)
    ceiling_height = st.sidebar.slider("Ceiling Height (m)", min_value=2.5, max_value=6.0, value=3.0, step=0.5)
    target_wwr = st.sidebar.slider("Target WWR (%)", min_value=10, max_value=90, value=40, step=5)
        
    st.sidebar.divider()
    st.sidebar.subheader("💬 AI Consultant Chat")
    chat_container = st.sidebar.container(height=300)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    if chat_input := st.sidebar.chat_input("Ask me to add a floor..."):
        st.session_state.messages.append({"role": "user", "content": chat_input})
        new_prompt, bot_reply = process_simulated_chat(chat_input, st.session_state.current_prompt)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        if new_prompt != st.session_state.current_prompt:
            st.session_state.current_prompt = new_prompt
            generate_assets(st.session_state.current_prompt)
        st.rerun()

    # 2. Main Panel Workspace
    st.markdown("### 🏛️ Project Requirements")
    prompt = st.text_area("", value=st.session_state.current_prompt, height=100, placeholder="Describe the architectural project... (e.g. A 4 story modern office building)")
    
    if st.button("✨ Generate Multi-Story Design", type="primary", use_container_width=True):
        st.session_state.current_prompt = prompt
        generate_assets(st.session_state.current_prompt, b_width_override, b_length_override, ceiling_height, target_wwr)
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.gen3d_data and st.session_state.report_data:
        tabs = st.tabs(["2D Floor Plans", "3D BIM Viewport", "Spatial Analytics & Schedule", "Export/Download"])
        
        floors_data = st.session_state.gen3d_data["floors"]
        floor_names = [f["name"] for f in floors_data]
        
        # TAB 1: 2D Floor Plans
        with tabs[0]:
            colA, colB = st.columns([1, 4])
            with colA:
                selected_2d_floor = st.selectbox("Select Level (2D)", floor_names, key="sel_2d")
            with colB:
                floor_idx = floor_names.index(selected_2d_floor)
                st.markdown(floors_data[floor_idx]['svg_content'], unsafe_allow_html=True)
                
        # TAB 2: 3D BIM Viewport
        with tabs[1]:
            st.radio("View Mode", ["Entire Building", "Single Floor"], horizontal=True, key="view_mode")
            legend_html = """
            <div style='display: flex; justify-content: center; gap: 20px; margin-bottom: 10px; background-color: #1e293b; padding: 10px; border-radius: 6px; border: 1px solid #334155;'>
                <div style='display: flex; align-items: center;'><div style='width: 16px; height: 16px; background-color: #ADD8E6; margin-right: 8px; border-radius: 4px; border: 1px solid #fff;'></div> <span style='color: #f1f5f9; font-size: 14px;'>Window Glass</span></div>
                <div style='display: flex; align-items: center;'><div style='width: 16px; height: 16px; background-color: #8B4513; margin-right: 8px; border-radius: 4px; border: 1px solid #fff;'></div> <span style='color: #f1f5f9; font-size: 14px;'>Solid Door</span></div>
            </div>
            """
            st.markdown(legend_html, unsafe_allow_html=True)
            
            if st.session_state.view_mode == "Entire Building":
                render_model_viewer(st.session_state.gen3d_data["combined_glb"])
            else:
                colA, colB = st.columns([1, 4])
                with colA:
                    selected_3d_floor = st.selectbox("Select Level (3D)", floor_names, key="sel_3d")
                with colB:
                    floor_idx = floor_names.index(selected_3d_floor)
                    render_model_viewer(floors_data[floor_idx]['glb_base64'])
                    
        # TAB 3: Spatial Analytics & Schedule
        with tabs[2]:
            st.subheader("Architectural Metrics")
            metrics = st.session_state.report_data.get("metrics", {})
            m1, m2, m3 = st.columns(3)
            m1.metric("Gross External Area (GEA)", f"{metrics.get('GEA_sqm', 0):,} sqm")
            m2.metric("Net Internal Area (NIA)", f"{metrics.get('NIA_sqm', 0):,} sqm")
            m3.metric("Circulation Ratio", f"{metrics.get('circulation_ratio', 0)}%")
            
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
            
        # TAB 4: Export/Download
        with tabs[3]:
            st.subheader("BIM Exports")
            colX, colY = st.columns(2)
            with colX:
                st.markdown("##### Full Project")
                glb_bytes = base64.b64decode(st.session_state.gen3d_data["combined_glb"])
                st.download_button("📥 Download Combined 3D Model (.glb)", data=glb_bytes, file_name="concept_combined.glb", mime="model/gltf-binary", use_container_width=True)
            
            with colY:
                st.markdown("##### Individual Floors")
                selected_dl_floor = st.selectbox("Select Level to Export", floor_names, key="sel_dl")
                dl_idx = floor_names.index(selected_dl_floor)
                st.download_button(f"📥 Download {selected_dl_floor} SVG Blueprint", data=floors_data[dl_idx]['svg_content'], file_name=f"floor_{dl_idx+1}.svg", mime="image/svg+xml", use_container_width=True)
                dl_glb_bytes = base64.b64decode(floors_data[dl_idx]['glb_base64'])
                st.download_button(f"📥 Download {selected_dl_floor} 3D Mesh (.glb)", data=dl_glb_bytes, file_name=f"floor_{dl_idx+1}.glb", mime="model/gltf-binary", use_container_width=True)
    else:
        st.info("👈 Use the parameters in the sidebar, enter your prompt above, and click Generate to build the architectural model!")
            
elif app_mode == "PDF Blueprint Analysis":
    st.header("📄 PDF Blueprint Analysis & Code Compliance")
    st.markdown("Upload a 2D PDF architectural floor plan to automatically extract programmatic area schedules, verify code compliance, and analyze structural typology.")
    
    uploaded_file = st.file_uploader("Upload Blueprint PDF", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Ingesting vector lines, detecting scales, and running BIM analysis..."):
            analysis = analyze_pdf_blueprint(uploaded_file.name)
            
        st.success(f"Successfully analyzed **{analysis['filename']}**")
        st.markdown(f"**Detected Typology:** {analysis['typology']} | **Detected Scale:** {analysis['scale_detected']}")
        
        st.subheader("📊 Programmatic Area Schedule")
        st.dataframe(analysis['schedule'], hide_index=True, use_container_width=True)
        
        st.subheader("⚖️ Circulation & Code Compliance")
        for item in analysis['compliance']:
            if item['type'] == 'success':
                st.success(item['message'])
            elif item['type'] == 'warning':
                st.warning(item['message'])
            elif item['type'] == 'error':
                st.error(item['message'])
                
        st.subheader("💡 Redesign & 3D Extrusion Recommendations")
        st.info(analysis['recommendations'])
