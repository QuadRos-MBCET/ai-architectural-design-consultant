import os
import json
import glob
from typing import List, Dict, Any

class DatasetParser:
    """
    Parses raw floor plan JSON files or structured datasets (e.g., RPLAN format, custom layout JSONs)
    and converts them into standardized floor plan format.
    """
    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = raw_dir

    def load_raw_files(self) -> List[Dict[str, Any]]:
        raw_plans = []
        if not os.path.exists(self.raw_dir):
            return raw_plans

        json_paths = glob.glob(os.path.join(self.raw_dir, "**/*.json"), recursive=True)
        for path in json_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        raw_plans.extend(data)
                    elif isinstance(data, dict):
                        raw_plans.append(data)
            except Exception as e:
                print(f"Warning: Failed to parse raw floor plan file {path}: {e}")
        return raw_plans

    def normalize_floorplan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes arbitrary raw floor plan schema into standardized format.
        """
        b_width = float(plan.get("building_width", plan.get("width", 30.0)))
        b_length = float(plan.get("building_length", plan.get("length", 20.0)))
        b_type = plan.get("building_type", plan.get("type", "library"))

        rooms = []
        raw_rooms = plan.get("rooms", [])

        for idx, r in enumerate(raw_rooms):
            rtype = r.get("type", r.get("name", "room")).lower().replace(" ", "_")
            x = float(r.get("x", 0.0))
            y = float(r.get("y", 0.0))
            w = float(r.get("width", r.get("w", 5.0)))
            h = float(r.get("height", r.get("length", r.get("h", 5.0))))

            rooms.append({
                "id": idx + 1,
                "type": rtype,
                "name": r.get("name", rtype.replace("_", " ").title()),
                "x": round(x, 2),
                "y": round(y, 2),
                "width": round(w, 2),
                "height": round(h, 2),
                "is_nested": r.get("is_nested", False)
            })

        return {
            "building_type": b_type,
            "building_width": b_width,
            "building_length": b_length,
            "floors_count": 1,
            "rooms": rooms
        }
