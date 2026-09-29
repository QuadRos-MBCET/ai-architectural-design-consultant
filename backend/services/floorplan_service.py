import os
from typing import Dict, Any

def render_floorplan_svg(floorplan: Dict[str, Any], output_path: str = None) -> str:
    """
    Renders a standardized floor plan JSON representation into a clean 2D SVG architectural blueprint.
    Independent of generation method (GAN, VAE, or BSP Baseline).
    """
    try:
        b_width = float(floorplan.get("building_width", 30.0))
        b_length = float(floorplan.get("building_length", 20.0))
        b_type = floorplan.get("building_type", "Floor Plan").replace("_", " ").upper()
        rooms = floorplan.get("rooms", [])

        scale = 15  # Scale factor: 15px per meter
        margin = 75
        svg_width = b_width * scale + (margin * 2)
        svg_height = b_length * scale + (margin * 2)

        svg_content = [
            f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
            # Background Grid
            f'<defs>',
            f'  <pattern id="grid" width="{scale}" height="{scale}" patternUnits="userSpaceOnUse">',
            f'    <path d="M {scale} 0 L 0 0 0 {scale}" fill="none" stroke="#e2e8f0" stroke-width="0.5"/>',
            f'  </pattern>',
            f'</defs>',
            f'<rect width="{svg_width}" height="{svg_height}" fill="#f8fafc"/>',
            f'<rect x="{margin}" y="{margin}" width="{b_width * scale}" height="{b_length * scale}" fill="url(#grid)"/>',
            # Outer Boundary Walls
            f'<rect x="{margin}" y="{margin}" width="{b_width * scale}" height="{b_length * scale}" fill="none" stroke="#0f172a" stroke-width="8"/>'
        ]

        # Render Individual Rooms
        for idx, room in enumerate(rooms):
            name = room.get("name", room.get("type", f"Room {idx+1}")).replace("_", " ").title()
            rx = margin + float(room.get("x", 0.0)) * scale
            ry = margin + float(room.get("y", 0.0)) * scale
            rw = max(1.0, float(room.get("width", 5.0))) * scale
            rh = max(1.0, float(room.get("height", room.get("length", 5.0)))) * scale

            # Room Background & Interior Walls
            is_wet = "toilet" in room.get("type", "").lower() or "restroom" in room.get("type", "").lower()
            bg_color = "#eff6ff" if is_wet else "#ffffff"
            
            svg_content.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{bg_color}" stroke="#334155" stroke-width="4"/>')

            # Window Placement (Exterior Walls)
            wx = rx + (rw / 2) - 15
            wy = ry + rh - 3
            svg_content.append(f'<rect x="{wx}" y="{wy}" width="30" height="6" fill="#38bdf8" stroke="#0284c7" stroke-width="1"/>')

            # Door Arc Placement
            dx = rx + rw - 3
            dy = ry + 10
            svg_content.append(f'<rect x="{dx-1}" y="{dy}" width="8" height="24" fill="#ffffff"/>')
            svg_content.append(f'<path d="M {dx+3} {dy} A 24 24 0 0 1 {dx+27} {dy+24} L {dx+3} {dy+24} Z" fill="none" stroke="#94a3b8" stroke-width="1"/>')

            # Room Label & Dimensions
            m_w = room.get("width", rw / scale)
            m_h = room.get("height", room.get("length", rh / scale))
            dim_str = f"{m_w:.1f}m x {m_h:.1f}m"

            font_size = max(7, min(12, int(rw / (len(name) * 0.7 + 1))))
            svg_content.append(f'<text x="{rx + rw/2}" y="{ry + rh/2 - 4}" font-family="Space Grotesk, sans-serif" font-size="{font_size}" font-weight="700" fill="#0f172a" text-anchor="middle">{name.upper()}</text>')
            svg_content.append(f'<text x="{rx + rw/2}" y="{ry + rh/2 + font_size}" font-family="Inter, sans-serif" font-size="8" fill="#64748b" text-anchor="middle">{dim_str}</text>')

            # Entrance Indicator
            if "FOYER" in name.upper() or "ENTRANCE" in name.upper() or "RECEPTION" in name.upper():
                arrow_x = rx + (rw / 2)
                arrow_y_start = ry + rh + 25
                arrow_y_end = ry + rh + 5
                svg_content.append(f'<path d="M {arrow_x} {arrow_y_start} L {arrow_x} {arrow_y_end} L {arrow_x - 5} {arrow_y_end + 8} M {arrow_x} {arrow_y_end} L {arrow_x + 5} {arrow_y_end + 8}" fill="none" stroke="#ef4444" stroke-width="3"/>')
                svg_content.append(f'<text x="{arrow_x}" y="{arrow_y_start + 12}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#ef4444" text-anchor="middle">MAIN ENTRANCE</text>')

        # Title Block
        svg_content.append(f'<text x="{margin}" y="45" font-family="Space Grotesk, sans-serif" font-weight="700" font-size="18" fill="#0f172a">2D ARCHITECTURAL BLUEPRINT - {b_type}</text>')
        svg_content.append(f'<text x="{margin}" y="62" font-family="Inter, sans-serif" font-size="11" fill="#64748b">Boundary Dimensions: {b_width:.1f}m × {b_length:.1f}m | Scale: 1:100</text>')

        svg_content.append('</svg>')
        svg_str = '\n'.join(svg_content)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_str)

        return svg_str
    except Exception as e:
        print(f"Error rendering floorplan SVG: {e}")
        return "<svg><text>Error rendering SVG</text></svg>"

def generate_svg_floorplan(b_width: int, b_length: int, floor: Dict[str, Any], output_path: str, project_name: str) -> bool:
    """
    Backwards-compatible wrapper function for existing backend routers.
    """
    floorplan = {
        "building_type": project_name,
        "building_width": b_width,
        "building_length": b_length,
        "rooms": floor.get("rooms", [])
    }
    render_floorplan_svg(floorplan, output_path)
    return True
