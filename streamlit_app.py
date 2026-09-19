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
    /* Import modern Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Space+Grotesk:wght@400;700&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }
    
    .stApp {
        background-color: #0d1117;
        background-image: radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.08), rgba(13, 17, 23, 1) 70%);
    }

    /* Style the Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        font-weight: 700;
        letter-spacing: 1px;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 6px;
        padding: 0.8rem 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(14, 165, 233, 0.6);
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    .stButton > button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.5);
        color: #cbd5e1;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px;
        font-size: 0.85rem;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #0ea5e9;
        color: white;
    }

    /* Text Inputs and Text Areas */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        color: #f1f5f9 !important;
        border-radius: 6px !important;
        font-family: 'Space Grotesk', monospace !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 1px #0ea5e9 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: rgba(15, 23, 42, 0.5);
        border-radius: 8px 8px 0 0;
        padding: 5px 5px 0 5px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        padding: 10px 20px;
        color: #64748b;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(30, 41, 59, 0.8) !important;
        color: #0ea5e9 !important;
        border-top: 2px solid #0ea5e9;
        border-radius: 6px 6px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# Modern Header & Branding (CAD Style)
st.markdown("""
<div style="display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 25px; padding: 20px 30px; background: rgba(30, 41, 59, 0.3); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; backdrop-filter: blur(12px); background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 20px 20px;">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.5); padding: 12px; border-radius: 8px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(14, 165, 233, 0.2);">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="1.5" stroke-linecap="square" stroke-linejoin="miter">
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
            <h1 style="font-size: 2.2rem; font-weight: 700; letter-spacing: 0.02em; margin: 0; line-height: 1.1; color: #f1f5f9; text-transform: uppercase; font-family: 'Space Grotesk', sans-serif;">
                R D <span style="color: #0ea5e9;">Homes</span>
            </h1>
            <p style="font-size: 0.9rem; color: #94a3b8; margin: 0; font-weight: 400; letter-spacing: 0.15em; text-transform: uppercase;">AI Architectural CAD Studio</p>
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
        {"role": "assistant", "content": "Welcome to the Studio! Configure parameters in the left panel or ask me to modify your design directly via this chat."}
    ]
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = "design a 4 story eco friendly public library"

def render_model_viewer(glb_base64):
    html_code = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
    <div style="width: 100%; height: 600px; background-color: #0f172a; border-radius: 0 0 8px 8px; overflow: hidden; display: flex; justify-content: center; align-items: center; border: 1px solid rgba(255,255,255,0.05); border-top: none;">
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
    components.html(html_code, height=620)

@st.dialog("🤖 AI Consultant Intervention")
def ai_intervention_popup(err_msg):
    st.markdown(f"**{err_msg}**")
    user_clarification = st.text_area("Describe the required rooms and layout:")
    if st.button("Submit Program", type="primary"):
        st.session_state.messages.append({"role": "user", "content": f"The building requires: {user_clarification}"})
        new_prompt, bot_reply = process_simulated_chat(user_clarification, st.session_state.current_prompt)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        if new_prompt != st.session_state.current_prompt:
            st.session_state.current_prompt = new_prompt
        st.rerun()

def generate_assets(prompt_text, p_width=30, p_length=30, p_height=3.0, p_wwr=40):
    with st.spinner("Synthesizing geometry & calculating structural grid..."):
        time.sleep(0.5)
        try:
            json_spec = extract_requirements(prompt_text, width=p_width, length=p_length, height=p_height, wwr=p_wwr)
        except ValueError as e:
            if "Unknown Typology:" in str(e):
                err_msg = str(e).replace("Unknown Typology: ", "")
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
                ai_intervention_popup(err_msg)
            else:
                st.error(str(e))
            st.session_state.report_data = None
            st.session_state.gen3d_data = None
            return False
            
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
            status_text.text(f"Extruding BIM Level: Floor {idx+1}/{len(floors)}...")
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
            
        status_text.text("Merging multi-story CAD meshes...")
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
        return True

# --- LAYOUT DEFINITION ---
app_mode = st.sidebar.radio("Navigation", ["Generative 3D Design", "PDF Blueprint Analysis"])

# Sidebar AI Chat
st.sidebar.divider()
st.sidebar.subheader("💬 AI Consultant Chat")
chat_container = st.sidebar.container(height=400)
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
        success = generate_assets(st.session_state.current_prompt)
        if success:
            st.rerun()
    else:
        st.rerun()

if app_mode == "Generative 3D Design":
    # SPLIT SCREEN LAYOUT
    col_left, col_right = st.columns([1.2, 2.0], gap="large")
    
    with col_left:
        st.markdown("### 🏛️ Program Requirements")
        
        # Interactive Quick-Start Tags
        st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 5px; font-weight: 600;'>QUICK-START PRESETS</p>", unsafe_allow_html=True)
        row1_col1, row1_col2 = st.columns(2)
        if row1_col1.button("🏢 4-Story Eco Library", use_container_width=True):
            st.session_state.current_prompt = "design a 4 story eco friendly public library"
            st.rerun()
        if row1_col2.button("🏡 Minimalist Villa", use_container_width=True):
            st.session_state.current_prompt = "design a 2 story minimalist cantilever villa"
            st.rerun()
            
        row2_col1, row2_col2 = st.columns(2)
        if row2_col1.button("🏙️ Parametric Office", use_container_width=True):
            st.session_state.current_prompt = "design a 10 story parametric office tower"
            st.rerun()
        if row2_col2.button("🌿 Courtyard Pavilion", use_container_width=True):
            st.session_state.current_prompt = "design a 1 story courtyard pavilion museum"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        prompt = st.text_area("Custom Architectural Prompt", value=st.session_state.current_prompt, height=120)
        
        st.markdown("### 📐 Structural Parameters")
        b_width_override = st.slider("Building Width (m)", min_value=10, max_value=60, value=30, step=5)
        b_length_override = st.slider("Building Depth (m)", min_value=10, max_value=60, value=30, step=5)
        ceiling_height = st.slider("Ceiling Height (m)", min_value=2.5, max_value=6.0, value=3.0, step=0.5)
        target_wwr = st.slider("Target WWR (%)", min_value=10, max_value=90, value=40, step=5)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ GENERATE CAD MODEL", type="primary", use_container_width=True):
            st.session_state.current_prompt = prompt
            success = generate_assets(st.session_state.current_prompt, b_width_override, b_length_override, ceiling_height, target_wwr)
            if success:
                st.rerun()

    with col_right:
        st.markdown("### 🖥️ Viewport Canvas")
        
        if st.session_state.gen3d_data and st.session_state.report_data:
            ai_arch = st.session_state.report_data.get("ai_architecture", {})
            if ai_arch:
                with st.expander("🪄 View AI Generation Pipeline (VAE / GAN / Diffusion)"):
                    st.markdown(f"**🧠 VAE (Latent Boundary Setup):** {ai_arch.get('vae', '')}")
                    st.markdown(f"**⚖️ GAN (Spatial Packing):** {ai_arch.get('gan', '')}")
                    st.markdown(f"**☁️ Diffusion (3D Extrusion):** {ai_arch.get('diffusion', '')}")
                    
            tabs = st.tabs(["3D BIM Viewer", "2D Blueprints", "Analytics & Schedule", "Export"])
            
            floors_data = st.session_state.gen3d_data["floors"]
            floor_names = [f["name"] for f in floors_data]
            
            with tabs[0]:
                st.radio("Render Scope", ["Entire Project", "Single Level"], horizontal=True, key="view_mode")
                if st.session_state.view_mode == "Entire Project":
                    render_model_viewer(st.session_state.gen3d_data["combined_glb"])
                else:
                    selected_3d_floor = st.selectbox("Select Level", floor_names, key="sel_3d")
                    floor_idx = floor_names.index(selected_3d_floor)
                    render_model_viewer(floors_data[floor_idx]['glb_base64'])
                    
            with tabs[1]:
                selected_2d_floor = st.selectbox("Select Blueprint Level", floor_names, key="sel_2d")
                floor_idx = floor_names.index(selected_2d_floor)
                st.markdown("<div style='background: white; padding: 20px; border-radius: 0 0 8px 8px; border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
                st.markdown(floors_data[floor_idx]['svg_content'], unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with tabs[2]:
                st.markdown("<div style='padding: 20px; background: rgba(30,41,59,0.3); border-radius: 0 0 8px 8px; border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
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
                st.markdown("</div>", unsafe_allow_html=True)
                
            with tabs[3]:
                st.markdown("<div style='padding: 20px; background: rgba(30,41,59,0.3); border-radius: 0 0 8px 8px; border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
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
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Placeholder State - Awaiting Generation
            st.markdown("""
            <div style="width: 100%; height: 600px; border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; background: rgba(15, 23, 42, 0.4); display: flex; flex-direction: column; justify-content: center; align-items: center; backdrop-filter: blur(12px); background-image: radial-gradient(rgba(14, 165, 233, 0.1) 1px, transparent 1px); background-size: 30px 30px;">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="rgba(14, 165, 233, 0.5)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 20px;">
                    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                    <polyline points="2 17 12 22 22 17"></polyline>
                    <polyline points="2 12 12 17 22 12"></polyline>
                </svg>
                <h2 style="color: rgba(255,255,255,0.8); margin: 0; font-weight: 600; font-family: 'Space Grotesk', sans-serif;">Studio Canvas Ready</h2>
                <p style="color: rgba(255,255,255,0.4); text-align: center; max-width: 350px; margin-top: 10px; font-size: 0.95rem;">Configure your program requirements in the left panel and click <b>GENERATE CAD MODEL</b> to synthesize the BIM assets.</p>
            </div>
            """, unsafe_allow_html=True)
            
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
