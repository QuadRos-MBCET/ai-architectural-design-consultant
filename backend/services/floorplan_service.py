import os
from typing import Dict, Any

def generate_svg_floorplan(b_width: int, b_length: int, floor: Dict[str, Any], output_path: str, project_name: str) -> bool:
    """
    Generates a traditional 2D architectural floor plan SVG with doors and windows for a specific floor.
    """
    try:
        rooms = floor.get("rooms", [])
        level_name = floor.get("name", "Floor").upper()

        scale = 15 # Larger scale for more detail
        svg_width = b_width * scale + 150
        svg_height = b_length * scale + 150

        svg_content = [
            f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{svg_width}" height="{svg_height}" fill="#f0f4f8"/>',
            # Building outline
            f'<rect x="75" y="75" width="{b_width * scale}" height="{b_length * scale}" fill="#ffffff" stroke="#1f2937" stroke-width="4"/>'
        ]

        # Draw rooms (Thick Walls)
        for idx, room in enumerate(rooms):
            name = room.get("name", "Room")
            rx = 75 + room.get("x", 0) * scale
            ry = 75 + room.get("y", 0) * scale
            rw = room.get("width", 5) * scale
            rh = room.get("length", 5) * scale
            
            # Thick interior walls
            svg_content.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="none" stroke="#374151" stroke-width="6"/>')
            
            # Procedural Window (Exterior wall)
            # Just put a window on the bottom wall for demonstration
            wx = rx + (rw / 2) - 15
            wy = ry + rh - 3
            svg_content.append(f'<rect x="{wx}" y="{wy}" width="30" height="6" fill="#60a5fa" stroke="#2563eb" stroke-width="1"/>')
            
            # Procedural Door (Interior wall)
            # Put a door on the right wall, near the top corner to avoid overlapping text
            dx = rx + rw - 3
            dy = ry + 15
            # Door gap (white cutout)
            svg_content.append(f'<rect x="{dx-1}" y="{dy}" width="8" height="30" fill="#ffffff"/>')
            # Door swing arc
            svg_content.append(f'<path d="M {dx+3} {dy} A 30 30 0 0 1 {dx+33} {dy+30} L {dx+3} {dy+30} Z" fill="none" stroke="#9ca3af" stroke-width="1"/>')
            
            # Room Label
            svg_content.append(f'<text x="{rx + rw/2}" y="{ry + rh/2}" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1f2937" text-anchor="middle" dominant-baseline="middle">{name.upper()}</text>')
            # Dimensions
            svg_content.append(f'<text x="{rx + rw/2}" y="{ry + rh/2 + 20}" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle" dominant-baseline="middle">{room.get("width")}m x {room.get("length")}m</text>')

        # Title
        project_type = project_name.replace("_", " ").upper()
        svg_content.append(f'<text x="75" y="45" font-family="sans-serif" font-weight="bold" font-size="20" fill="#111827">{project_type} - {level_name}</text>')

        svg_content.append('</svg>')

        with open(output_path, 'w') as f:
            f.write('\n'.join(svg_content))
            
        return True
    except Exception as e:
        print(f"Error generating SVG: {e}")
        return False
