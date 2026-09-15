import trimesh
import numpy as np
from typing import Dict, Any, List

def generate_floor_extrusion(b_width: int, b_length: int, floor: Dict[str, Any], elevation: float, output_path: str) -> List[Any]:
    """
    Procedurally generates a 3D GLB model for a single floor.
    Returns the list of generated Trimesh objects for later combination.
    """
    try:
        rooms = floor.get("rooms", [])
        
        meshes = []
        wall_height = 4.0   
        wall_thick = 0.4    
        door_width = 2.0    
        
        colors = [
            [255, 99, 71, 255],     # Tomato Red
            [64, 224, 208, 255],    # Turquoise
            [255, 215, 0, 255],     # Bright Gold
            [138, 43, 226, 255],    # Blue Violet
            [50, 205, 50, 255],     # Lime Green
            [255, 105, 180, 255],   # Hot Pink
        ]
        
        for idx, room in enumerate(rooms):
            rw = room.get("width", 5)
            rl = room.get("length", 5)
            rx = room.get("x", 0)
            ry = room.get("y", 0)
            
            color = colors[idx % len(colors)]
            
            def create_wall(w, d, x, z, h=wall_height, elevation_offset=0, custom_color=None):
                box = trimesh.creation.box(extents=(w, h, d))
                box.visual.face_colors = custom_color if custom_color else color
                transform = np.eye(4)
                transform[0, 3] = x + (w / 2)
                transform[1, 3] = (h / 2) + elevation + elevation_offset
                transform[2, 3] = z + (d / 2)
                box.apply_transform(transform)
                meshes.append(box)

            # Back Wall
            create_wall(rw, wall_thick, rx, ry)
            
            window_width = 3.0
            # Front Wall (with Window)
            create_wall((rw - window_width)/2, wall_thick, rx, ry + rl - wall_thick)
            create_wall((rw - window_width)/2, wall_thick, rx + (rw + window_width)/2, ry + rl - wall_thick)
            
            # Window Sill, Header, and Glass
            window_x = rx + (rw - window_width)/2
            window_z = ry + rl - wall_thick
            create_wall(window_width, wall_thick, window_x, window_z, h=1.0, elevation_offset=0) # Sill
            create_wall(window_width, wall_thick, window_x, window_z, h=1.0, elevation_offset=3.0) # Header
            create_wall(window_width, wall_thick * 0.2, window_x, window_z + (wall_thick*0.4), h=2.0, elevation_offset=1.0, custom_color=[173, 216, 230, 200]) # Glass (Light Blue)
            
            # Left Wall
            create_wall(wall_thick, rl - (wall_thick * 2), rx, ry + wall_thick)
            
            # Right Wall (with Door)
            door_z_start = ry + wall_thick + ((rl - (wall_thick * 2) - door_width) / 2)
            create_wall(wall_thick, (rl - (wall_thick * 2) - door_width) / 2, rx + rw - wall_thick, ry + wall_thick)
            create_wall(wall_thick, (rl - (wall_thick * 2) - door_width) / 2, rx + rw - wall_thick, door_z_start + door_width)
            
            # Door Header and Wooden Slab
            door_x = rx + rw - wall_thick
            create_wall(wall_thick, door_width, door_x, door_z_start, h=1.0, elevation_offset=3.0) # Header
            create_wall(wall_thick * 0.3, door_width, door_x + (wall_thick*0.35), door_z_start, h=3.0, elevation_offset=0, custom_color=[139, 69, 19, 255]) # Wooden Door
            
        # Floor plate
        if rooms:
            floor_mesh = trimesh.creation.box(extents=(b_width + 2, 0.2, b_length + 2))
            floor_mesh.visual.face_colors = [45, 45, 50, 255] # Sleek Charcoal Base
            tf = np.eye(4)
            tf[0, 3] = b_width / 2
            tf[1, 3] = -0.1 + elevation
            tf[2, 3] = b_length / 2
            floor_mesh.apply_transform(tf)
            meshes.append(floor_mesh)

        if meshes:
            combined = trimesh.util.concatenate(meshes)
            combined.export(output_path)
            return meshes
        else:
            return []
            
    except Exception as e:
        print(f"Error extruding floor model: {e}")
        return []

def export_combined_meshes(all_meshes: List[Any], output_path: str) -> bool:
    try:
        if all_meshes:
            combined = trimesh.util.concatenate(all_meshes)
            combined.export(output_path)
            return True
        return False
    except Exception as e:
        print(f"Error combining multi-story model: {e}")
        return False
