import os
from typing import Dict, Any

def render_floorplan_svg(floorplan: Dict[str, Any], output_path: str = None) -> str:
    """
    Renders a standardized floor plan JSON representation into a high-precision 2D CAD SVG architectural blueprint.
    Inspired by top AI architectural tools (Maket.ai, Finch 3D, PlanFinder, Edraw.AI, Hypar):
    - Color-coded functional zoning (Primary, Administrative, Wet/Restroom, Storage)
    - Structural column axis grid markers (A, B, C / 1, 2, 3)
    - Architectural furniture block schematics (Study tables, computer desks, office desks, toilet fixtures)
    - Door swing arcs, glass window openings, and m² area badges
    """
    try:
        b_width = float(floorplan.get("building_width", 30.0))
        b_length = float(floorplan.get("building_length", 20.0))
        b_type = floorplan.get("building_type", "Floor Plan").replace("_", " ").upper()
        rooms = floorplan.get("rooms", [])

        scale = 16  # Scale factor: 16px per meter
        margin = 110  # Generous top/left margin to prevent header text & grid bubble overlaps
        svg_width = b_width * scale + (margin * 2)
        svg_height = b_length * scale + (margin * 2)

        svg_content = [
            f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
            # Background
            f'<rect width="{svg_width}" height="{svg_height}" fill="#f8fafc"/>',
            # Definitions for patterns & markers
            f'<defs>',
            f'  <pattern id="grid" width="{scale}" height="{scale}" patternUnits="userSpaceOnUse">',
            f'    <path d="M {scale} 0 L 0 0 0 {scale}" fill="none" stroke="#e2e8f0" stroke-width="0.5"/>',
            f'  </pattern>',
            f'</defs>',
            f'<rect x="{margin}" y="{margin}" width="{b_width * scale}" height="{b_length * scale}" fill="url(#grid)"/>'
        ]

        # 1. Structural Axis Grid Lines & Axis Bubbles (Finch 3D / Hypar style)
        grid_cols = max(3, int(b_width / 6.0))
        grid_rows = max(2, int(b_length / 6.0))

        col_letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
        for c in range(grid_cols + 1):
            cx = margin + (c * (b_width * scale / grid_cols))
            # Grid Line
            svg_content.append(f'<line x1="{cx}" y1="{margin - 30}" x2="{cx}" y2="{margin + b_length * scale + 15}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="4,3"/>')
            # Top Grid Bubble (positioned cleanly at cy = margin - 20)
            c_label = col_letters[c % len(col_letters)]
            svg_content.append(f'<circle cx="{cx}" cy="{margin - 20}" r="10" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>')
            svg_content.append(f'<text x="{cx}" y="{margin - 16}" font-family="Space Grotesk, sans-serif" font-size="10" font-weight="700" fill="#334155" text-anchor="middle">{c_label}</text>')

        for r in range(grid_rows + 1):
            ry = margin + (r * (b_length * scale / grid_rows))
            # Grid Line
            svg_content.append(f'<line x1="{margin - 30}" y1="{ry}" x2="{margin + b_width * scale + 15}" y2="{ry}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="4,3"/>')
            # Left Grid Bubble (positioned cleanly at cx = margin - 20)
            svg_content.append(f'<circle cx="{margin - 20}" cy="{ry}" r="10" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>')
            svg_content.append(f'<text x="{margin - 20}" y="{ry + 4}" font-family="Space Grotesk, sans-serif" font-size="10" font-weight="700" fill="#334155" text-anchor="middle">{r+1}</text>')

        # 2. Outer Load-Bearing Boundary Wall Envelope
        svg_content.append(f'<rect x="{margin}" y="{margin}" width="{b_width * scale}" height="{b_length * scale}" fill="none" stroke="#0f172a" stroke-width="10"/>')

        # 3. Render Individual Rooms & Functional Zoning
        for idx, room in enumerate(rooms):
            r_type = room.get("type", "").lower()
            name = room.get("name", room.get("type", f"Room {idx+1}")).replace("_", " ").title()
            
            rx = margin + float(room.get("x", 0.0)) * scale
            ry = margin + float(room.get("y", 0.0)) * scale
            rw = max(1.5, float(room.get("width", 5.0))) * scale
            rh = max(1.5, float(room.get("height", room.get("length", 5.0)))) * scale

            m_w = room.get("width", rw / scale)
            m_h = room.get("height", room.get("length", rh / scale))
            area_sqm = m_w * m_h

            # Functional Color Zoning (Maket.ai & Finch 3D style)
            if "toilet" in r_type or "restroom" in r_type or "washroom" in r_type:
                bg_color = "#e0f2fe"  # Light sky blue (Wet Zone)
                stroke_color = "#0284c7"
            elif "reading" in r_type or "hall" in r_type or "exhibition" in r_type:
                bg_color = "#f0f9ff"  # Soft ice blue (Primary Public Zone)
                stroke_color = "#0369a1"
            elif "office" in r_type or "discussion" in r_type or "conference" in r_type:
                bg_color = "#fef3c7"  # Warm amber tint (Administrative/Focus Zone)
                stroke_color = "#d97706"
            elif "computer" in r_type or "lab" in r_type:
                bg_color = "#f0fdf4"  # Light mint green (Tech Zone)
                stroke_color = "#15803d"
            else:
                bg_color = "#f8fafc"  # Neutral slate (Storage/Support Zone)
                stroke_color = "#475569"

            # Room Envelope & Interior Partition Wall
            svg_content.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{bg_color}" stroke="{stroke_color}" stroke-width="4"/>')

            # Architectural Furniture Schematics (PlanFinder & Edraw.AI style)
            center_x = rx + (rw / 2)
            center_y = ry + (rh / 2)

            if "reading" in r_type or "discussion" in r_type:
                # Study Table with Chairs Schematic
                tbl_w, tbl_h = min(rw * 0.4, 40), min(rh * 0.3, 20)
                svg_content.append(f'<rect x="{center_x - tbl_w/2}" y="{center_y - tbl_h/2}" width="{tbl_w}" height="{tbl_h}" rx="2" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>')
                # Chair dots
                svg_content.append(f'<circle cx="{center_x - tbl_w/4}" cy="{center_y - tbl_h/2 - 4}" r="3" fill="#cbd5e1"/>')
                svg_content.append(f'<circle cx="{center_x + tbl_w/4}" cy="{center_y - tbl_h/2 - 4}" r="3" fill="#cbd5e1"/>')
                svg_content.append(f'<circle cx="{center_x - tbl_w/4}" cy="{center_y + tbl_h/2 + 4}" r="3" fill="#cbd5e1"/>')
                svg_content.append(f'<circle cx="{center_x + tbl_w/4}" cy="{center_y + tbl_h/2 + 4}" r="3" fill="#cbd5e1"/>')

            elif "computer" in r_type or "lab" in r_type:
                # PC Workstation Array Schematic
                ws_w, ws_h = min(rw * 0.5, 50), min(rh * 0.25, 15)
                svg_content.append(f'<rect x="{center_x - ws_w/2}" y="{center_y - ws_h/2}" width="{ws_w}" height="{ws_h}" fill="#ffffff" stroke="#64748b" stroke-width="1.5"/>')
                svg_content.append(f'<rect x="{center_x - ws_w/4 - 4}" y="{center_y - ws_h/2 + 2}" width="8" height="4" fill="#38bdf8"/>')
                svg_content.append(f'<rect x="{center_x + ws_w/4 - 4}" y="{center_y - ws_h/2 + 2}" width="8" height="4" fill="#38bdf8"/>')

            elif "toilet" in r_type or "restroom" in r_type:
                # Sanitary Fixture Schematic
                fix_w, fix_h = min(rw * 0.25, 16), min(rh * 0.25, 16)
                svg_content.append(f'<rect x="{rx + 8}" y="{ry + 8}" width="{fix_w}" height="{fix_h}" rx="4" fill="#ffffff" stroke="#0284c7" stroke-width="1.5"/>')
                svg_content.append(f'<circle cx="{rx + 8 + fix_w/2}" cy="{ry + 8 + fix_h/2}" r="4" fill="#bae6fd"/>')

            elif "office" in r_type:
                # Executive Desk Schematic
                desk_w, desk_h = min(rw * 0.35, 35), min(rh * 0.25, 18)
                svg_content.append(f'<rect x="{center_x - desk_w/2}" y="{center_y - desk_h/2}" width="{desk_w}" height="{desk_h}" fill="#ffffff" stroke="#d97706" stroke-width="1.5"/>')
                svg_content.append(f'<circle cx="{center_x}" cy="{center_y - desk_h/2 - 5}" r="4" fill="#fcd34d"/>')

            # Glass Window Openings (Exterior Edge)
            wx = rx + (rw / 2) - 16
            wy = ry + rh - 3
            svg_content.append(f'<rect x="{wx}" y="{wy}" width="32" height="6" fill="#38bdf8" stroke="#0284c7" stroke-width="1"/>')

            # Door Arc Placement
            dx = rx + rw - 3
            dy = ry + 12
            svg_content.append(f'<rect x="{dx-1}" y="{dy}" width="8" height="24" fill="#ffffff"/>')
            svg_content.append(f'<path d="M {dx+3} {dy} A 24 24 0 0 1 {dx+27} {dy+24} L {dx+3} {dy+24} Z" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="2,2"/>')

            # Room Label & m² Area Badges (Maket.ai & Finch style)
            font_size = max(8, min(12, int(rw / (len(name) * 0.65 + 1))))
            svg_content.append(f'<text x="{center_x}" y="{ry + 20}" font-family="Space Grotesk, sans-serif" font-size="{font_size}" font-weight="700" fill="#0f172a" text-anchor="middle">{name.upper()}</text>')
            svg_content.append(f'<text x="{center_x}" y="{ry + 32}" font-family="Inter, sans-serif" font-size="8.5" font-weight="600" fill="#475569" text-anchor="middle">{m_w:.1f}m × {m_h:.1f}m ({area_sqm:.1f} m²)</text>')

            # Entrance Arrow Indicator
            if "FOYER" in name.upper() or "ENTRANCE" in name.upper() or "RECEPTION" in name.upper():
                arrow_x = rx + (rw / 2)
                arrow_y_start = ry + rh + 28
                arrow_y_end = ry + rh + 6
                svg_content.append(f'<path d="M {arrow_x} {arrow_y_start} L {arrow_x} {arrow_y_end} L {arrow_x - 5} {arrow_y_end + 8} M {arrow_x} {arrow_y_end} L {arrow_x + 5} {arrow_y_end + 8}" fill="none" stroke="#ef4444" stroke-width="3"/>')
                svg_content.append(f'<text x="{arrow_x}" y="{arrow_y_start + 12}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#ef4444" text-anchor="middle">MAIN ENTRANCE</text>')

        # 4. Architectural Title Block & Legend (Top Header, cleanly spaced)
        svg_content.append(f'<text x="{margin}" y="32" font-family="Space Grotesk, sans-serif" font-weight="700" font-size="18" fill="#0f172a">2D ARCHITECTURAL BLUEPRINT — {b_type}</text>')
        svg_content.append(f'<text x="{margin}" y="50" font-family="Inter, sans-serif" font-size="11" fill="#475569">Perimeter Bounds: {b_width:.1f}m × {b_length:.1f}m | Total Area: {b_width*b_length:.1f} m² | Scale 1:100</text>')

        # Legend (Right-aligned, top header)
        leg_x = margin + (b_width * scale) - 260
        svg_content.append(f'<g transform="translate({leg_x}, 20)">')
        svg_content.append(f'  <rect width="260" height="30" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
        svg_content.append(f'  <rect x="10" y="9" width="12" height="12" fill="#f0f9ff" stroke="#0369a1"/>')
        svg_content.append(f'  <text x="26" y="19" font-family="sans-serif" font-size="8" fill="#334155">Primary</text>')
        svg_content.append(f'  <rect x="70" y="9" width="12" height="12" fill="#fef3c7" stroke="#d97706"/>')
        svg_content.append(f'  <text x="86" y="19" font-family="sans-serif" font-size="8" fill="#334155">Admin</text>')
        svg_content.append(f'  <rect x="130" y="9" width="12" height="12" fill="#e0f2fe" stroke="#0284c7"/>')
        svg_content.append(f'  <text x="146" y="19" font-family="sans-serif" font-size="8" fill="#334155">Wet Zone</text>')
        svg_content.append(f'  <rect x="195" y="9" width="12" height="12" fill="#38bdf8"/>')
        svg_content.append(f'  <text x="211" y="19" font-family="sans-serif" font-size="8" fill="#334155">Window</text>')
        svg_content.append(f'</g>')

        svg_content.append('</svg>')
        svg_str = '\n'.join(svg_content)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_str)

        return svg_str
    except Exception as e:
        print(f"Error rendering CAD floorplan SVG: {e}")
        return "<svg><text>Error rendering CAD SVG</text></svg>"

def generate_svg_floorplan(b_width: int, b_length: int, floor: Dict[str, Any], output_path: str, project_name: str) -> bool:
    floorplan = {
        "building_type": project_name,
        "building_width": b_width,
        "building_length": b_length,
        "rooms": floor.get("rooms", [])
    }
    render_floorplan_svg(floorplan, output_path)
    return True
