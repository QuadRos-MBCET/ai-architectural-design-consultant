import trimesh
import numpy as np
from typing import Dict, Any, List
import sys
import os

# Optional PyTorch Diffusion Model (Requires Trained Weights)
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from models import MeshDiffusionUnet3D
    DIFFUSION_LOADED = True
except ImportError:
    DIFFUSION_LOADED = False

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
        
        level = floor.get("level", 1)
        floor_color = colors[(level - 1) % len(colors)]
        
        for idx, room in enumerate(rooms):
            # Epsilon shrinkage to prevent z-fighting on shared party walls
            rx = room.get("x", 0) + 0.05
            ry = room.get("y", 0) + 0.05
            rw = room.get("width", 10) - 0.1
            rl = room.get("length", 10) - 0.1
            
            color = floor_color
            
            def create_wall(w, d, x, z, h=wall_height, elevation_offset=0, custom_color=None):
                box = trimesh.creation.box(extents=(w, h, d))
                box.visual.face_colors = custom_color if custom_color else color
                transform = np.eye(4)
                transform[0, 3] = x + (w / 2)
                transform[1, 3] = (h / 2) + elevation + elevation_offset
                transform[2, 3] = z + (d / 2)
                box.apply_transform(transform)
                meshes.append(box)

            is_nested = room.get("is_nested", False)
            
            # Back Wall (North Facade - Passive Diffuse Light / High WWR)
            if not is_nested and ry == 0:
                create_wall(rw, wall_thick, rx, ry, h=0.5) # Low Sill
                create_wall(rw, wall_thick, rx, ry, h=0.5, elevation_offset=3.5) # Header
                create_wall(rw, wall_thick * 0.2, rx, ry + (wall_thick*0.4), h=3.0, elevation_offset=0.5, custom_color=[173, 216, 230, 150]) # Large Curtain Glass
            else:
                create_wall(rw, wall_thick, rx, ry)
            
            # Front Wall
            if not is_nested:
                window_width = 3.0
                create_wall((rw - window_width)/2, wall_thick, rx, ry + rl - wall_thick)
                create_wall((rw - window_width)/2, wall_thick, rx + (rw + window_width)/2, ry + rl - wall_thick)
                # Sill, Header, Glass
                window_x = rx + (rw - window_width)/2
                window_z = ry + rl - wall_thick
                create_wall(window_width, wall_thick, window_x, window_z, h=1.0, elevation_offset=0)
                create_wall(window_width, wall_thick, window_x, window_z, h=1.0, elevation_offset=3.0)
                create_wall(window_width, wall_thick * 0.2, window_x, window_z + (wall_thick*0.4), h=2.0, elevation_offset=1.0, custom_color=[173, 216, 230, 200])
            else:
                # High ventilation window for nested rooms (bathrooms/closets)
                window_width = 1.5
                create_wall((rw - window_width)/2, wall_thick, rx, ry + rl - wall_thick)
                create_wall((rw - window_width)/2, wall_thick, rx + (rw + window_width)/2, ry + rl - wall_thick)
                window_x = rx + (rw - window_width)/2
                window_z = ry + rl - wall_thick
                create_wall(window_width, wall_thick, window_x, window_z, h=2.0, elevation_offset=0) # High Sill
                create_wall(window_width, wall_thick, window_x, window_z, h=0.5, elevation_offset=3.5) # Header
                create_wall(window_width, wall_thick * 0.2, window_x, window_z + (wall_thick*0.4), h=1.5, elevation_offset=2.0, custom_color=[173, 216, 230, 200]) # Glass
                
            # Left Wall
            if is_nested:
                # Door on the left wall connecting to the Master Bedroom
                door_z_start = ry + wall_thick + ((rl - (wall_thick * 2) - door_width) / 2)
                create_wall(wall_thick, (rl - (wall_thick * 2) - door_width) / 2, rx, ry + wall_thick)
                create_wall(wall_thick, (rl - (wall_thick * 2) - door_width) / 2, rx, door_z_start + door_width)
                create_wall(wall_thick, door_width, rx, door_z_start, h=1.0, elevation_offset=3.0) # Header
                create_wall(wall_thick * 0.3, door_width, rx + (wall_thick*0.35), door_z_start, h=3.0, elevation_offset=0, custom_color=[139, 69, 19, 255]) # Wooden Door
            else:
                create_wall(wall_thick, rl - (wall_thick * 2), rx, ry + wall_thick)
                
            # Right Wall
            if not is_nested:
                # Standard door on the right wall
                door_z_start = ry + wall_thick + ((rl - (wall_thick * 2) - door_width) / 2)
                create_wall(wall_thick, (rl - (wall_thick * 2) - door_width) / 2, rx + rw - wall_thick, ry + wall_thick)
                create_wall(wall_thick, (rl - (wall_thick * 2) - door_width) / 2, rx + rw - wall_thick, door_z_start + door_width)
                door_x = rx + rw - wall_thick
                create_wall(wall_thick, door_width, door_x, door_z_start, h=1.0, elevation_offset=3.0) # Header
                create_wall(wall_thick * 0.3, door_width, door_x + (wall_thick*0.35), door_z_start, h=3.0, elevation_offset=0, custom_color=[139, 69, 19, 255]) # Wooden Door
            else:
                create_wall(wall_thick, rl - (wall_thick * 2), rx + rw - wall_thick, ry + wall_thick)
            
        # Floor plate (Climate Responsive Deep Overhangs/Louvers)
        if rooms:
            floor_mesh = trimesh.creation.box(extents=(b_width + 8, 0.4, b_length + 8))
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
