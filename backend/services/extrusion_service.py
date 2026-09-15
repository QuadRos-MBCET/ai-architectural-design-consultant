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
            [230, 240, 250, 255], 
            [250, 240, 230, 255], 
            [240, 250, 230, 255], 
            [245, 235, 245, 255], 
        ]
        
        for idx, room in enumerate(rooms):
            rw = room.get("width", 5)
            rl = room.get("length", 5)
            rx = room.get("x", 0)
            ry = room.get("y", 0)
            
            color = colors[idx % len(colors)]
            
            def create_wall(w, d, x, z):
                box = trimesh.creation.box(extents=(w, wall_height, d))
                box.visual.face_colors = color
                transform = np.eye(4)
                transform[0, 3] = x + (w / 2)
                transform[1, 3] = (wall_height / 2) + elevation
                transform[2, 3] = z + (d / 2)
                box.apply_transform(transform)
                meshes.append(box)

            create_wall(rw, wall_thick, rx, ry)
            
            window_width = 3.0
            create_wall((rw - window_width)/2, wall_thick, rx, ry + rl - wall_thick)
            create_wall((rw - window_width)/2, wall_thick, rx + (rw + window_width)/2, ry + rl - wall_thick)
            
            create_wall(wall_thick, rl - (wall_thick * 2), rx, ry + wall_thick)
            
            create_wall(wall_thick, (rl - (wall_thick * 2) - door_width) / 2, rx + rw - wall_thick, ry + wall_thick)
            create_wall(wall_thick, (rl - (wall_thick * 2) - door_width) / 2, rx + rw - wall_thick, ry + wall_thick + ((rl - (wall_thick * 2) - door_width) / 2) + door_width)
            
        # Floor plate
        if rooms:
            floor_mesh = trimesh.creation.box(extents=(b_width + 2, 0.2, b_length + 2))
            floor_mesh.visual.face_colors = [200, 200, 200, 255]
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
