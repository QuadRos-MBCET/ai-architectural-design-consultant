import numpy as np
import torch
from typing import Dict, Any, List, Tuple

# Standardized Room Categories across typologies
ROOM_CATEGORIES = [
    "unknown",
    "reading_hall",
    "computer_section",
    "discussion_room",
    "librarian_office",
    "storage",
    "toilet",
    "foyer",
    "lobby",
    "corridor",
    "office",
    "meeting_room",
    "restroom",
    "reception",
    "exhibition_hall",
    "cafeteria",
    "classroom",
    "lab",
    "bedroom",
    "living_room",
    "kitchen",
    "dining"
]

ROOM_TO_IDX = {cat: i for i, cat in enumerate(ROOM_CATEGORIES)}
IDX_TO_ROOM = {i: cat for i, cat in enumerate(ROOM_CATEGORIES)}
NUM_ROOM_CLASSES = len(ROOM_CATEGORIES)
MAX_ROOMS = 16  # Maximum room slots per layout tensor

class FloorplanEncoder:
    """
    Encoder/Decoder converting standardized floor plan JSONs to/from PyTorch tensors.
    
    Room Vector Representation (dim = 4 + NUM_ROOM_CLASSES):
      [norm_x, norm_y, norm_w, norm_h, one_hot_room_type...]
    """
    def __init__(self, max_rooms: int = MAX_ROOMS):
        self.max_rooms = max_rooms
        self.feature_dim = 4 + NUM_ROOM_CLASSES

    def encode(self, floorplan_json: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Encodes a floor plan JSON into (layout_tensor, condition_vector).
        layout_tensor shape: (MAX_ROOMS, 4 + NUM_ROOM_CLASSES)
        condition_vector shape: (2 + NUM_ROOM_CLASSES,) -> [norm_width, norm_length, room_counts_per_class...]
        """
        b_width = float(floorplan_json.get("building_width", 30.0))
        b_length = float(floorplan_json.get("building_length", 20.0))
        rooms = floorplan_json.get("rooms", [])

        layout_matrix = np.zeros((self.max_rooms, self.feature_dim), dtype=np.float32)
        room_counts = np.zeros(NUM_ROOM_CLASSES, dtype=np.float32)

        for idx, room in enumerate(rooms[:self.max_rooms]):
            rx = float(room.get("x", 0.0)) / max(b_width, 1.0)
            ry = float(room.get("y", 0.0)) / max(b_length, 1.0)
            rw = float(room.get("width", 5.0)) / max(b_width, 1.0)
            rh = float(room.get("height", room.get("length", 5.0))) / max(b_length, 1.0)

            rtype = room.get("type", "unknown").lower()
            cat_idx = ROOM_TO_IDX.get(rtype, 0)
            room_counts[cat_idx] += 1.0

            layout_matrix[idx, 0] = np.clip(rx, 0.0, 1.0)
            layout_matrix[idx, 1] = np.clip(ry, 0.0, 1.0)
            layout_matrix[idx, 2] = np.clip(rw, 0.0, 1.0)
            layout_matrix[idx, 3] = np.clip(rh, 0.0, 1.0)
            layout_matrix[idx, 4 + cat_idx] = 1.0

        cond_vector = np.concatenate([
            [b_width / 100.0, b_length / 100.0],
            room_counts / float(self.max_rooms)
        ], axis=0).astype(np.float32)

        return layout_matrix, cond_vector

    def decode(self, layout_tensor: np.ndarray, b_width: float, b_length: float, building_type: str = "custom", target_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Decodes a (MAX_ROOMS, 4 + NUM_ROOM_CLASSES) tensor back into a standardized JSON floor plan.
        Maps target requirements to ensure generated spatial boxes represent the user's prompt rooms.
        """
        if isinstance(layout_tensor, torch.Tensor):
            layout_tensor = layout_tensor.detach().cpu().numpy()

        target_rooms = target_requirements.get("rooms", []) if target_requirements else []

        raw_boxes = []
        for idx in range(layout_tensor.shape[0]):
            vec = layout_tensor[idx]
            rx_norm, ry_norm, rw_norm, rh_norm = vec[0:4]

            rw = max(2.5, float(rw_norm * b_width))
            rh = max(2.5, float(rh_norm * b_length))
            rx = float(rx_norm * b_width)
            ry = float(ry_norm * b_length)

            rx = min(max(0.0, rx), max(0.0, b_width - rw))
            ry = min(max(0.0, ry), max(0.0, b_length - rh))

            class_probs = vec[4:]
            cat_idx = int(np.argmax(class_probs))
            room_type = IDX_TO_ROOM.get(cat_idx, "room")
            if room_type == "unknown":
                room_type = "office"

            raw_boxes.append({
                "x": round(rx, 2),
                "y": round(ry, 2),
                "width": round(rw, 2),
                "height": round(rh, 2),
                "type": room_type,
                "area": rw * rh
            })

        rooms = []
        if target_rooms:
            count = len(target_rooms)
            cols = int(np.ceil(np.sqrt(count)))
            rows = int(np.ceil(count / float(cols)))

            cell_w = b_width / max(1, cols)
            cell_h = b_length / max(1, rows)

            for idx, tr in enumerate(target_rooms):
                r_name = tr.get("name", f"Room {idx+1}")
                r_type = tr.get("type", "room")

                if idx < len(raw_boxes) and raw_boxes[idx]["width"] >= 2.0:
                    box = raw_boxes[idx]
                    rx, ry, rw, rh = box["x"], box["y"], box["width"], box["height"]
                else:
                    c = idx % cols
                    r = idx // cols
                    rx = round(c * cell_w, 2)
                    ry = round(r * cell_h, 2)
                    rw = round(min(cell_w - 0.2, b_width - rx), 2)
                    rh = round(min(cell_h - 0.2, b_length - ry), 2)

                rooms.append({
                    "id": idx + 1,
                    "type": r_type,
                    "name": r_name,
                    "x": max(0.0, rx),
                    "y": max(0.0, ry),
                    "width": max(2.5, rw),
                    "height": max(2.5, rh),
                    "is_nested": "toilet" in r_type or "storage" in r_type
                })
        else:
            for idx, box in enumerate(raw_boxes[:8]):
                r_type = box["type"]
                rooms.append({
                    "id": idx + 1,
                    "type": r_type,
                    "name": r_type.replace("_", " ").title(),
                    "x": box["x"],
                    "y": box["y"],
                    "width": box["width"],
                    "height": box["height"],
                    "is_nested": "toilet" in r_type or "storage" in r_type
                })

        return {
            "building_type": building_type,
            "building_width": b_width,
            "building_length": b_length,
            "floors_count": 1,
            "rooms": rooms
        }
