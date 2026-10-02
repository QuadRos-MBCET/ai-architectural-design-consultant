import os
from typing import Dict, Any

def render_floorplan_svg(floorplan: Dict[str, Any], output_path: str = None) -> str:
    """
    Renders a standardized floor plan JSON representation into a high-precision 2D CAD SVG architectural blueprint.
    Generous vertical stacking eliminates any title, subtitle, legend, or grid bubble overlaps.
    """
    try:
        b_width = float(floorplan.get("building_width", 30.0))
        b_length = float(floorplan.get("building_length", 20.0))
        b_type = floorplan.get("building_type", "Floor Plan").replace("_", " ").upper()
        rooms = floorplan.get("rooms", [])

        scale = 16  # Scale factor: 16px per meter
        margin_x = 85
        margin_top = 145  # Spacious top margin for clean 4-tier vertical header stacking
        margin_bottom = 75

        svg_width = b_width * scale + (margin_x * 2)
        svg_height = b_length * scale + margin_top + margin_bottom

        svg_content = [
            f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
            # Warm Classic Architectural Vellum Drafting Paper Background
            f'<rect width="{svg_width}" height="{svg_height}" fill="#faf8f2"/>',
            # SVG Definitions: Pencil Sketch Filter & Drafting Grid Pattern
            f'<defs>',
            f'  <filter id="pencil-sketch" x="-5%" y="-5%" width="110%" height="110%">',
            f'    <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" result="noise"/>',
            f'    <feDisplacementMap in="SourceGraphic" in2="noise" scale="1.4" xChannelSelector="R" yChannelSelector="G"/>',
            f'  </filter>',
            f'  <pattern id="grid" width="{scale}" height="{scale}" patternUnits="userSpaceOnUse">',
            f'    <path d="M {scale} 0 L 0 0 0 {scale}" fill="none" stroke="#e2ded4" stroke-width="0.5"/>',
            f'  </pattern>',
            f'</defs>',
            # Main Drafting Grid
            f'<rect x="{margin_x}" y="{margin_top}" width="{b_width * scale}" height="{b_length * scale}" fill="url(#grid)"/>'
        ]

        floor_name = floorplan.get("floor_name", "")
        title_suffix = f" — {floor_name.upper()}" if floor_name else ""
        # Tier 1: Hand-Drafted Title Text (y = 35)
        svg_content.append(f'<text x="{margin_x}" y="35" font-family="Space Grotesk, Architects Daughter, sans-serif" font-weight="700" font-size="18" fill="#1e293b" letter-spacing="1">CLASSIC ARCHITECTURAL PENCIL DRAFT — {b_type}{title_suffix}</text>')

        # Tier 2: Subtitle & Scale Metadata (y = 56)
        svg_content.append(f'<text x="{margin_x}" y="56" font-family="Inter, sans-serif" font-size="11" font-weight="600" fill="#475569">Human Pencil Scale 1:100 | Perimeter: {b_width:.1f}m × {b_length:.1f}m | Total Area: {b_width*b_length:.1f} m²</text>')

        # Tier 3: Classic Drafting Legend Bar (y = 72..90)
        svg_content.append(f'<g transform="translate({margin_x}, 72)">')
        svg_content.append(f'  <rect width="360" height="24" rx="3" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
        svg_content.append(f'  <rect x="10" y="6" width="12" height="12" fill="#f4efe6" stroke="#475569" stroke-width="1.2"/>')
        svg_content.append(f'  <text x="26" y="15" font-family="sans-serif" font-size="9" font-weight="600" fill="#334155">Primary Zone</text>')
        svg_content.append(f'  <rect x="95" y="6" width="12" height="12" fill="#fdf6e2" stroke="#d97706" stroke-width="1.2"/>')
        svg_content.append(f'  <text x="111" y="15" font-family="sans-serif" font-size="9" font-weight="600" fill="#334155">Admin Zone</text>')
        svg_content.append(f'  <rect x="180" y="6" width="12" height="12" fill="#e8f4f8" stroke="#0284c7" stroke-width="1.2"/>')
        svg_content.append(f'  <text x="196" y="15" font-family="sans-serif" font-size="9" font-weight="600" fill="#334155">Wet Zone</text>')
        svg_content.append(f'  <rect x="260" y="6" width="12" height="12" fill="#7dd3fc" stroke="#0284c7" stroke-width="1.2"/>')
        svg_content.append(f'  <text x="276" y="15" font-family="sans-serif" font-size="9" font-weight="600" fill="#334155">Window</text>')
        svg_content.append(f'</g>')

        # Tier 4: Structural Axis Grid Lines & Pencil Axis Bubbles
        grid_cols = max(3, int(b_width / 6.0))
        grid_rows = max(2, int(b_length / 6.0))

        col_letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
        for c in range(grid_cols + 1):
            cx = margin_x + (c * (b_width * scale / grid_cols))
            # Pencil Grid Line
            svg_content.append(f'<line x1="{cx}" y1="{margin_top - 32}" x2="{cx}" y2="{margin_top + b_length * scale + 15}" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="5,4"/>')
            # Top Grid Bubble
            c_label = col_letters[c % len(col_letters)]
            svg_content.append(f'<circle cx="{cx}" cy="{margin_top - 24}" r="10" fill="#ffffff" stroke="#334155" stroke-width="1.5"/>')
            svg_content.append(f'<text x="{cx}" y="{margin_top - 20}" font-family="Space Grotesk, sans-serif" font-size="10" font-weight="700" fill="#1e293b" text-anchor="middle">{c_label}</text>')

        for r in range(grid_rows + 1):
            ry = margin_top + (r * (b_length * scale / grid_rows))
            # Pencil Grid Line
            svg_content.append(f'<line x1="{margin_x - 32}" y1="{ry}" x2="{margin_x + b_width * scale + 15}" y2="{ry}" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="5,4"/>')
            # Left Grid Bubble
            svg_content.append(f'<circle cx="{margin_x - 24}" cy="{ry}" r="10" fill="#ffffff" stroke="#334155" stroke-width="1.5"/>')
            svg_content.append(f'<text x="{margin_x - 24}" y="{ry + 4}" font-family="Space Grotesk, sans-serif" font-size="10" font-weight="700" fill="#1e293b" text-anchor="middle">{r+1}</text>')

        # Outer Double-Line Graphite Boundary Wall Envelope (starts at margin_top = 145)
        svg_content.append(f'<rect x="{margin_x}" y="{margin_top}" width="{b_width * scale}" height="{b_length * scale}" fill="none" stroke="#1e293b" stroke-width="8"/>')
        svg_content.append(f'<rect x="{margin_x + 3}" y="{margin_top + 3}" width="{b_width * scale - 6}" height="{b_length * scale - 6}" fill="none" stroke="#475569" stroke-width="1"/>')

        # Render Individual Rooms with Classic Hand-Pencil Fills & Corner Ticks
        for idx, room in enumerate(rooms):
            r_type = room.get("type", "").lower()
            name = room.get("name", room.get("type", f"Room {idx+1}")).replace("_", " ").title()
            
            rx = margin_x + float(room.get("x", 0.0)) * scale
            ry = margin_top + float(room.get("y", 0.0)) * scale
            rw = max(1.5, float(room.get("width", 5.0))) * scale
            rh = max(1.5, float(room.get("height", room.get("length", 5.0)))) * scale

            m_w = room.get("width", rw / scale)
            m_h = room.get("height", room.get("length", rh / scale))
            area_sqm = m_w * m_h

            # Hand-Pencil Tone Zoning
            if "toilet" in r_type or "restroom" in r_type or "washroom" in r_type:
                bg_color = "#e8f4f8"  # Soft blue-graphite wash (Wet Zone)
                stroke_color = "#0284c7"
            elif "reading" in r_type or "hall" in r_type or "exhibition" in r_type:
                bg_color = "#f4efe6"  # Warm vellum wash (Primary Zone)
                stroke_color = "#475569"
            elif "office" in r_type or "discussion" in r_type or "conference" in r_type:
                bg_color = "#fdf6e2"  # Soft ivory pencil wash (Admin Zone)
                stroke_color = "#d97706"
            elif "computer" in r_type or "lab" in r_type:
                bg_color = "#ebf6ed"  # Soft sage pencil wash (Tech Zone)
                stroke_color = "#15803d"
            else:
                bg_color = "#faf6ed"  # Parchment neutral slate
                stroke_color = "#475569"

            # Room Partition Envelope (Graphite Double-Line Pencil Effect)
            svg_content.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{bg_color}" stroke="{stroke_color}" stroke-width="3"/>')

            # Classic Hand-Drafting Corner Extension Ticks (Architectural Pencil Ticks)
            tick_len = 6
            svg_content.append(f'<line x1="{rx - tick_len}" y1="{ry}" x2="{rx + tick_len}" y2="{ry}" stroke="{stroke_color}" stroke-width="1.2"/>')
            svg_content.append(f'<line x1="{rx}" y1="{ry - tick_len}" x2="{rx}" y2="{ry + tick_len}" stroke="{stroke_color}" stroke-width="1.2"/>')
            svg_content.append(f'<line x1="{rx + rw - tick_len}" y1="{ry}" x2="{rx + rw + tick_len}" y2="{ry}" stroke="{stroke_color}" stroke-width="1.2"/>')
            svg_content.append(f'<line x1="{rx + rw}" y1="{ry - tick_len}" x2="{rx + rw}" y2="{ry + tick_len}" stroke="{stroke_color}" stroke-width="1.2"/>')

            # Architectural Furniture Schematics
            center_x = rx + (rw / 2)
            center_y = ry + (rh / 2)

            # Architectural Furniture Schematics (Positioned at bottom-left corner, completely clear of center text)
            furn_x = rx + 10
            furn_y = ry + rh - 20

            if "reading" in r_type or "discussion" in r_type:
                # Study Table with Chairs Schematic
                tbl_w, tbl_h = min(rw * 0.2, 22), min(rh * 0.12, 10)
                svg_content.append(f'<rect x="{furn_x}" y="{furn_y}" width="{tbl_w}" height="{tbl_h}" rx="2" fill="#ffffff" stroke="#94a3b8" stroke-width="1.0"/>')

            elif "computer" in r_type or "lab" in r_type:
                # PC Workstation Array Schematic
                ws_w, ws_h = min(rw * 0.2, 22), min(rh * 0.12, 10)
                svg_content.append(f'<rect x="{furn_x}" y="{furn_y}" width="{ws_w}" height="{ws_h}" fill="#ffffff" stroke="#64748b" stroke-width="1.0"/>')

            elif "toilet" in r_type or "restroom" in r_type or "washroom" in r_type:
                # Sanitary Fixture Schematic
                fix_w, fix_h = min(rw * 0.18, 12), min(rh * 0.18, 12)
                svg_content.append(f'<rect x="{furn_x}" y="{ry + rh - fix_h - 8}" width="{fix_w}" height="{fix_h}" rx="3" fill="#ffffff" stroke="#0284c7" stroke-width="1.2"/>')

            elif "office" in r_type:
                # Executive Desk Schematic
                desk_w, desk_h = min(rw * 0.2, 22), min(rh * 0.12, 10)
                svg_content.append(f'<rect x="{furn_x}" y="{ry + rh - desk_h - 8}" width="{desk_w}" height="{desk_h}" fill="#ffffff" stroke="#d97706" stroke-width="1.0"/>')

            # Glass Window Openings
            win_w = min(32, rw * 0.4)
            wx = rx + (rw / 2) - (win_w / 2)
            wy = ry + rh - 3
            svg_content.append(f'<rect x="{wx}" y="{wy}" width="{win_w}" height="6" fill="#38bdf8" stroke="#0284c7" stroke-width="1"/>')

            # Door Arc Placement
            door_w = min(20, rh * 0.3)
            dx = rx + rw - 3
            dy = ry + 8
            svg_content.append(f'<rect x="{dx-1}" y="{dy}" width="6" height="{door_w}" fill="#ffffff"/>')
            svg_content.append(f'<path d="M {dx+3} {dy} A {door_w} {door_w} 0 0 1 {dx+door_w+3} {dy+door_w} L {dx+3} {dy+door_w} Z" fill="none" stroke="#64748b" stroke-width="1.2" stroke-dasharray="2,2"/>')

            # Room Label & m² Area Badges (With Multi-Line Text Wrapping & Collision Avoidance)
            words = name.upper().split()
            lines = []
            curr_line = ""
            for w in words:
                if len(curr_line + " " + w) > 13 and curr_line:
                    lines.append(curr_line.strip())
                    curr_line = w
                else:
                    curr_line += " " + w
            if curr_line:
                lines.append(curr_line.strip())

            max_line_len = max(len(l) for l in lines) if lines else 10
            font_size = max(7.5, min(10.5, float((rw - 12) / (max_line_len * 0.65))))

            start_y = center_y - (len(lines) * 6)
            for l_idx, line_text in enumerate(lines):
                svg_content.append(f'<text x="{center_x}" y="{start_y + (l_idx * (font_size + 3))}" font-family="Space Grotesk, sans-serif" font-size="{font_size:.1f}" font-weight="700" fill="#0f172a" text-anchor="middle">{line_text}</text>')

            dim_y = start_y + (len(lines) * (font_size + 3)) + 4
            dim_font_size = max(6.5, font_size - 1.5)
            svg_content.append(f'<text x="{center_x}" y="{dim_y}" font-family="Inter, sans-serif" font-size="{dim_font_size:.1f}" font-weight="600" fill="#475569" text-anchor="middle">{m_w:.1f}m × {m_h:.1f}m ({area_sqm:.1f} m²)</text>')

            # Entrance Arrow Indicator
            if "FOYER" in name.upper() or "ENTRANCE" in name.upper() or "RECEPTION" in name.upper():
                arrow_x = rx + (rw / 2)
                arrow_y_start = ry + rh + 28
                arrow_y_end = ry + rh + 6
                svg_content.append(f'<path d="M {arrow_x} {arrow_y_start} L {arrow_x} {arrow_y_end} L {arrow_x - 5} {arrow_y_end + 8} M {arrow_x} {arrow_y_end} L {arrow_x + 5} {arrow_y_end + 8}" fill="none" stroke="#ef4444" stroke-width="3"/>')
                svg_content.append(f'<text x="{arrow_x}" y="{arrow_y_start + 12}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#ef4444" text-anchor="middle">MAIN ENTRANCE</text>')

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
