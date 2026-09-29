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

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    generate_clicked = st.button("Generate 2D Floor Plan", type="primary")

if generate_clicked or "last_svg" not in st.session_state:
    with st.spinner("Executing generative layout model & layout validator..."):
        reqs = parse_requirements_locally(prompt_text)
        reqs["building_type"] = building_type
        reqs["building_width"] = float(width)
        reqs["building_length"] = float(length)

        gen_res = generate_floorplan(reqs, model_type=model_choice)
        svg_content = render_floorplan_svg(gen_res["floorplan"])

        st.session_state["last_res"] = gen_res
        st.session_state["last_svg"] = svg_content

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
