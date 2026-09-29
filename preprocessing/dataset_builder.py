import os
import json
import numpy as np
import torch
from preprocessing.floorplan_encoder import FloorplanEncoder
from preprocessing.dataset_parser import DatasetParser

def generate_seed_dataset_from_typologies(db_path: str, count_per_typology: int = 50) -> list:
    """
    Generates synthetic ground-truth dataset samples using spatial variations across standard typologies.
    This enables model training even when external datasets (e.g. RPLAN) are not yet downloaded.
    """
    if not os.path.exists(db_path):
        return []

    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    samples = []
    np.random.seed(42)

    for b_type, data in db.items():
        left_rooms = list(data.get("left_rooms", {}).keys()) if isinstance(data.get("left_rooms"), dict) else data.get("left_rooms", [])
        right_rooms = list(data.get("right_rooms", {}).keys()) if isinstance(data.get("right_rooms"), dict) else data.get("right_rooms", [])
        all_rooms = left_rooms + right_rooms

        if not all_rooms:
            continue

        for i in range(count_per_typology):
            # Introduce stochastic width/length variations
            w = float(np.random.randint(15, 45))
            h = float(np.random.randint(15, 35))

            rooms = []
            cur_x, cur_y = 0.0, 0.0
            col_width = w / 2.0
            row_height = h / (len(all_rooms) / 2.0 if len(all_rooms) >= 2 else 1.0)

            for idx, rname in enumerate(all_rooms):
                r_type = rname.lower().replace(" ", "_")
                if "restroom" in r_type or "toilet" in r_type:
                    r_type = "toilet"
                elif "reading" in r_type or "hall" in r_type:
                    r_type = "reading_hall"
                elif "computer" in r_type:
                    r_type = "computer_section"
                elif "discussion" in r_type:
                    r_type = "discussion_room"
                elif "office" in r_type or "librarian" in r_type:
                    r_type = "librarian_office"

                rx = (idx % 2) * col_width + float(np.random.uniform(0, 1.0))
                ry = (idx // 2) * row_height + float(np.random.uniform(0, 1.0))
                rw = max(3.0, col_width - float(np.random.uniform(0.5, 2.0)))
                rh = max(3.0, row_height - float(np.random.uniform(0.5, 2.0)))

                rx = min(rx, w - rw)
                ry = min(ry, h - rh)

                rooms.append({
                    "id": idx + 1,
                    "type": r_type,
                    "name": rname,
                    "x": round(rx, 2),
                    "y": round(ry, 2),
                    "width": round(rw, 2),
                    "height": round(rh, 2),
                    "is_nested": "toilet" in r_type or "storage" in r_type
                })

            samples.append({
                "building_type": b_type,
                "building_width": w,
                "building_length": h,
                "floors_count": 1,
                "rooms": rooms
            })

    return samples

def build_dataset(data_dir: str = "data"):
    raw_dir = os.path.join(data_dir, "raw")
    processed_dir = os.path.join(data_dir, "processed")
    db_path = os.path.join(data_dir, "typology_database.json")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    parser = DatasetParser(raw_dir=raw_dir)
    plans = parser.load_raw_files()

    if not plans:
        print("No raw floor plan files found in data/raw. Generating seed dataset from typology_database.json...")
        plans = generate_seed_dataset_from_typologies(db_path, count_per_typology=50)

    print(f"Processing {len(plans)} floor plan samples...")

    encoder = FloorplanEncoder()
    layout_list = []
    cond_list = []

    for plan in plans:
        norm_plan = parser.normalize_floorplan(plan)
        layout_tensor, cond_vector = encoder.encode(norm_plan)
        layout_list.append(layout_tensor)
        cond_list.append(cond_vector)

    layout_arr = np.array(layout_list, dtype=np.float32)
    cond_arr = np.array(cond_list, dtype=np.float32)

    output_path = os.path.join(processed_dir, "floorplans_dataset.pt")
    torch.save({
        "layouts": torch.tensor(layout_arr),
        "conditions": torch.tensor(cond_arr),
        "num_samples": len(plans)
    }, output_path)

    print(f"Successfully saved processed dataset tensor ({len(plans)} samples) to {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_dataset(os.path.join(base_dir, "data"))
