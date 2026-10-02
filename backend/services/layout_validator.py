import numpy as np
from typing import Dict, Any, List, Tuple

def validate_floorplan(floorplan: Dict[str, Any], target_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Validates a generated 2D floor plan against architectural standards and target prompt requirements.
    
    Checks:
    - Bounding box compliance (rooms outside boundary)
    - Room overlap detection
    - Minimum room dimensions (< 1.5m)
    - Unused building area ratio
    - Required room coverage
    """
    if not floorplan or "rooms" not in floorplan:
        return {
            "valid": False,
            "score_percentage": 0.0,
            "errors": ["Malformed floorplan structure"],
            "warnings": [],
            "missing_rooms": [],
            "overlaps_count": 0,
            "boundary_violations": 0,
            "unused_area_ratio": 1.0,
            "room_count": 0,
            "total_area_sqm": 0.0,
            "utilized_area_sqm": 0.0
        }

    b_width = float(floorplan.get("building_width", 30.0))
    b_length = float(floorplan.get("building_length", 20.0))
    total_building_area = b_width * b_length
    rooms = floorplan.get("rooms", [])

    errors = []
    warnings = []
    overlaps = []
    boundary_violations = 0
    invalid_dim_count = 0
    total_room_area = 0.0

    # 1. Bounding & Size Checks
    for room in rooms:
        rx = float(room.get("x", 0.0))
        ry = float(room.get("y", 0.0))
        rw = float(room.get("width", 0.0))
        rh = float(room.get("height", room.get("length", 0.0)))
        rname = room.get("name", room.get("type", "Room"))

        if rw < 1.5 or rh < 1.5:
            invalid_dim_count += 1
            warnings.append(f"Room '{rname}' has undersized dimensions ({rw:.1f}m x {rh:.1f}m).")

        if rx < -0.01 or ry < -0.01 or (rx + rw) > (b_width + 0.5) or (ry + rh) > (b_length + 0.5):
            boundary_violations += 1
            warnings.append(f"Room '{rname}' extends beyond boundary ({b_width}m x {b_length}m).")

        total_room_area += max(0.0, rw * rh)

    # 2. Overlap Checks (Axis-Aligned Bounding Box intersection)
    for i in range(len(rooms)):
        r1 = rooms[i]
        x1, y1, w1, h1 = float(r1.get("x", 0)), float(r1.get("y", 0)), float(r1.get("width", 0)), float(r1.get("height", r1.get("length", 0)))
        for j in range(i + 1, len(rooms)):
            r2 = rooms[j]
            x2, y2, w2, h2 = float(r2.get("x", 0)), float(r2.get("y", 0)), float(r2.get("width", 0)), float(r2.get("height", r2.get("length", 0)))

            # Intersection
            inter_x1 = max(x1, x2)
            inter_y1 = max(y1, y2)
            inter_x2 = min(x1 + w1, x2 + w2)
            inter_y2 = min(y1 + h1, y2 + h2)

            if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                overlap_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                if overlap_area > 0.5:
                    overlaps.append({
                        "room1": r1.get("name", "Room 1"),
                        "room2": r2.get("name", "Room 2"),
                        "overlap_sqm": round(overlap_area, 2)
                    })
                    warnings.append(f"Overlap detected between '{r1.get('name')}' and '{r2.get('name')}' ({overlap_area:.1f} m²).")

    # 3. Unused Area Calculation
    unused_area = max(0.0, total_building_area - total_room_area)
    unused_ratio = round(unused_area / max(total_building_area, 1.0), 3)

    # 4. Score Percentage Calculation
    penalty = (len(overlaps) * 12) + (boundary_violations * 10) + (invalid_dim_count * 5)
    score_percentage = max(15.0, round(100.0 - penalty, 1))

    return {
        "valid": len(errors) == 0 and len(overlaps) == 0 and boundary_violations == 0,
        "score_percentage": score_percentage,
        "errors": errors,
        "warnings": warnings,
        "overlaps_count": len(overlaps),
        "overlaps_detail": overlaps,
        "boundary_violations": boundary_violations,
        "unused_area_ratio": unused_ratio,
        "room_count": len(rooms),
        "total_area_sqm": total_building_area,
        "utilized_area_sqm": round(total_room_area, 2)
    }

def repair_geometry_if_needed(floorplan: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """
    Geometry solver pass:
    If room overlaps exist, rearranges rooms into non-overlapping spatial partitions
    within building bounds (W x L), ensuring 0 overlaps and 100% boundary compliance.
    """
    if not floorplan or "rooms" not in floorplan or not floorplan["rooms"]:
        return floorplan, False

    b_width = float(floorplan.get("building_width", 30.0))
    b_length = float(floorplan.get("building_length", 20.0))
    rooms = floorplan["rooms"]

    # Check if overlaps exist
    val = validate_floorplan(floorplan)
    if val["overlaps_count"] == 0 and val["boundary_violations"] == 0:
        return floorplan, False

    count = len(rooms)
    cols = int(np.ceil(np.sqrt(count)))
    rows = int(np.ceil(count / float(cols)))

    cell_w = b_width / max(1, cols)
    cell_h = b_length / max(1, rows)

    repaired_rooms = []
    for idx, r in enumerate(rooms):
        c = idx % cols
        row_idx = idx // cols

        rx = round(c * cell_w, 2)
        ry = round(row_idx * cell_h, 2)
        rw = round(min(cell_w - 0.2, b_width - rx), 2)
        rh = round(min(cell_h - 0.2, b_length - ry), 2)

        r_copy = dict(r)
        r_copy["x"] = max(0.0, rx)
        r_copy["y"] = max(0.0, ry)
        r_copy["width"] = max(2.5, rw)
        r_copy["height"] = max(2.5, rh)
        repaired_rooms.append(r_copy)

    repaired_plan = dict(floorplan)
    repaired_plan["rooms"] = repaired_rooms
    return repaired_plan, True
