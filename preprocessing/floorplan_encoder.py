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

    def decode(self, layout_tensor: np.ndarray, b_width: float, b_length: float, building_type: str = "custom") -> Dict[str, Any]:
        """
        Decodes a (MAX_ROOMS, 4 + NUM_ROOM_CLASSES) tensor back into a standardized JSON floor plan.
        """
        rooms = []
        if isinstance(layout_tensor, torch.Tensor):
            layout_tensor = layout_tensor.detach().cpu().numpy()

        for idx in range(layout_tensor.shape[0]):
            vec = layout_tensor[idx]
            rx_norm, ry_norm, rw_norm, rh_norm = vec[0:4]

            # Skip padding / zero rooms
            if rw_norm < 0.02 or rh_norm < 0.02:
                continue

            class_probs = vec[4:]
            cat_idx = int(np.argmax(class_probs))
            room_type = IDX_TO_ROOM.get(cat_idx, "room")

            # De-normalize coordinates
            rx = round(float(rx_norm * b_width), 2)
            ry = round(float(ry_norm * b_length), 2)
            rw = max(1.5, round(float(rw_norm * b_width), 2))
            rh = max(1.5, round(float(rh_norm * b_length), 2))

            # Clamp coordinates to stay within building box
            rx = min(rx, b_width - rw)
            ry = min(ry, b_length - rh)
            rx = max(0.0, rx)
            ry = max(0.0, ry)

            rooms.append({
                "id": len(rooms) + 1,
                "type": room_type,
                "name": room_type.replace("_", " ").title(),
                "x": rx,
                "y": ry,
                "width": rw,
                "height": rh,
                "is_nested": True if "toilet" in room_type or "storage" in room_type else False
            })

        return {
            "building_type": building_type,
            "building_width": b_width,
            "building_length": b_length,
            "floors_count": 1,
            "rooms": rooms
        }
