import streamlit as st
import sys
import os
import time
import base64

# Ensure backend imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from backend.routers.requirements import parse_requirements_locally
from backend.services.generative_floorplan_service import generate_floorplan
from backend.services.floorplan_service import render_floorplan_svg

st.set_page_config(
    page_title="Prompt-Based 2D Floor Plan Generator",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Grotesk:wght@700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: #f0f6fc !important; }
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .stButton > button[kind="primary"] { background: #238636; color: white; font-weight: 700; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

st.title("📐 Prompt-Based 2D Floor Plan Generator")
st.caption("Generative Architectural Layout Synthesis using PyTorch Conditional GAN and VAE Models")

# Sidebar Controls
st.sidebar.header("Configuration & Parameters")

building_type = st.sidebar.selectbox(
    "Building Typology",
    ["library", "hospital", "mall", "office", "school", "house", "museum", "warehouse"]
)

col_w, col_l = st.sidebar.columns(2)
with col_w:
    width = st.number_input("Width (m)", min_value=10, max_value=100, value=30)
with col_l:
    length = st.number_input("Length (m)", min_value=10, max_value=100, value=20)

model_choice = st.sidebar.selectbox(
    "Generative AI Model",
    ["gan", "vae", "bsp_baseline"],
    format_func=lambda x: "Conditional GAN (PyTorch)" if x == "gan" else ("Conditional VAE (PyTorch)" if x == "vae" else "BSP Baseline (Procedural)")
)

# Main Prompt Input
prompt_text = st.text_area(
    "Describe your desired 2D floor plan:",
    value="Create a modern college library of 30m × 20m with a large reading hall, computer section, two discussion rooms, librarian office, storage and toilets.",
    height=120
)

# Workflow Modal Dialog
@st.dialog("⚙️ Generative AI Synthesis Workflow: RAG + GAN Pipeline", width="large")
def show_workflow_dialog(reqs_dict, gen_result):
    btype_display = reqs_dict.get('building_type', 'building').replace('_', ' ').title()
    rooms_list = [r.get('name', 'Room') for r in reqs_dict.get('rooms', [])]
    rooms_preview = ", ".join(rooms_list[:6]) + (f" (+{len(rooms_list)-6} more)" if len(rooms_list) > 6 else "")
    
    html_dialog = f"""
<div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(0, 210, 255, 0.25); border-radius: 10px; padding: 18px; margin-bottom: 16px;">
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
<span style="font-size: 1.4rem;">🏛️</span>
<h4 style="margin: 0; color: #00D2FF; font-family: 'Space Grotesk', sans-serif;">SURJ Homes Architectural Synthesis Engine</h4>
</div>
<p style="color: #94a3b8; font-size: 0.88rem; margin: 0;">
Real-time execution trace: How your natural language prompt transforms through <b>RAG</b> and <b>cGAN</b> into a collision-free 2D CAD floor plan.
</p>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px;">
<div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 14px;">
<div style="color: #38bdf8; font-weight: 700; font-size: 0.95rem; margin-bottom: 6px;">
1️⃣ STAGE 1: RAG & Typology Extraction
</div>
<p style="color: #cbd5e1; font-size: 0.82rem; line-height: 1.4; margin-bottom: 6px;">
<b>Detected Typology:</b> <span style="color: #00D2FF;">{btype_display}</span><br>
<b>Footprint Bounds:</b> {reqs_dict.get('building_width')}m × {reqs_dict.get('building_length')}m<br>
<b>Extracted Program:</b> {len(rooms_list)} functional zones
</p>
<div style="background: rgba(15, 23, 42, 0.7); border-radius: 4px; padding: 6px 10px; font-size: 0.78rem; color: #94a3b8;">
<b>Active Spaces:</b> {rooms_preview}
</div>
</div>

<div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 14px;">
<div style="color: #34d399; font-weight: 700; font-size: 0.95rem; margin-bottom: 6px;">
2️⃣ STAGE 2: Conditional GAN Spatial Packing
</div>
<p style="color: #cbd5e1; font-size: 0.82rem; line-height: 1.4; margin-bottom: 6px;">
<b>Model:</b> <span style="color: #34d399;">{gen_result.get('actual_model_used', 'cGAN').upper()}</span><br>
<b>Spatial Solver:</b> Non-overlapping AABB partitioning<br>
<b>Validation Score:</b> {gen_result.get('validation', {}).get('score_percentage', 100)}% Compliance
</p>
<div style="background: rgba(15, 23, 42, 0.7); border-radius: 4px; padding: 6px 10px; font-size: 0.78rem; color: #94a3b8;">
<b>Circulation:</b> Central corridor alignment & zero-overlap guarantee
</div>
</div>
</div>
"""
    st.markdown(html_dialog, unsafe_allow_html=True)
    
    if st.button("Close Workflow & View 2D Blueprint", type="primary", use_container_width=True):
        st.rerun()

col_btn1, col_btn2 = st.columns([1.5, 3.5])
with col_btn1:
    generate_clicked = st.button("Generate 2D Floor Plan", type="primary", use_container_width=True)
with col_btn2:
    if "last_res" in st.session_state:
        if st.button("ℹ️ View Generation Workflow", use_container_width=False):
            show_workflow_dialog(st.session_state.get("last_reqs", {}), st.session_state["last_res"])

# Check if prompt or parameters changed
current_prompt_key = f"{prompt_text}_{building_type}_{width}_{length}_{model_choice}"
is_new_prompt = st.session_state.get("active_key") != current_prompt_key

if generate_clicked or is_new_prompt or "last_svg" not in st.session_state:
    with st.spinner("Executing generative layout model & layout validator..."):
        # 1. Parse prompt
        reqs = parse_requirements_locally(prompt_text)
        
        # 2. Only override with sidebar if prompt did not explicitly define them
        if not any(alias in prompt_text.lower() for aliases in [["library"], ["hospital"], ["school"], ["hotel"], ["house"], ["office"], ["mall"], ["police"], ["restaurant"]] for alias in aliases):
            reqs["building_type"] = building_type
            
        dim_in_prompt = any(x in prompt_text.lower() for x in ["x", "×", "by"])
        if not dim_in_prompt:
            reqs["building_width"] = float(width)
            reqs["building_length"] = float(length)

        # 3. Generate floorplan
        gen_res = generate_floorplan(reqs, model_type=model_choice)
        svg_content = render_floorplan_svg(gen_res["floorplan"])

        # 4. Save to session state
        st.session_state["last_res"] = gen_res
        st.session_state["last_svg"] = svg_content
        st.session_state["last_reqs"] = reqs
        st.session_state["active_key"] = current_prompt_key

        # 5. Show popup on click
        if generate_clicked:
            show_workflow_dialog(reqs, gen_res)

if "last_res" in st.session_state:
    res = st.session_state["last_res"]
    svg_data = st.session_state["last_svg"]

    col_view, col_info = st.columns([3, 2])

    with col_view:
        st.subheader("2D Architectural Blueprint SVG")
        # Display SVG
        svg_b64 = base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')
        html_str = f'<div style="text-align: center; background: #161b22; padding: 1rem; border-radius: 8px; border: 1px solid #30363d;"><img src="data:image/svg+xml;base64,{svg_b64}" style="max-width: 100%; height: auto;" /></div>'
        st.markdown(html_str, unsafe_allow_html=True)

        st.download_button(
            label="Download Blueprint SVG",
            data=svg_data,
            file_name=f"floorplan_{res['actual_model_used']}.svg",
            mime="image/svg+xml"
        )

    with col_info:
        st.subheader("Model & Validation Metrics")
        
        status_color = "green" if res["is_trained_checkpoint"] else "orange"
        st.markdown(f"**Model Used:** `{res['actual_model_used'].upper()}`")
        st.markdown(f"**Status:** :{status_color}[{res['status']}]")

        val = res["validation"]
        m1, m2 = st.columns(2)
        m1.metric("Validation Score", f"{val['score_percentage']}%")
        m2.metric("Room Density", f"{val['room_count']} Rooms")

        m3, m4 = st.columns(2)
        m3.metric("Boundary", f"{res['floorplan']['building_width']}m × {res['floorplan']['building_length']}m")
        m4.metric("Unused Area", f"{val['unused_area_ratio']*100:.1f}%")

        if val.get("warnings"):
            st.warning("**Validation Audit & Warnings:**\n" + "\n".join([f"- {w}" for w in val["warnings"]]))
