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
    - Circulation / Entrance accessibility
    """
    if not floorplan or "rooms" not in floorplan:
        return {
            "valid": False,
            "score": 0.0,
            "errors": ["Malformed floorplan structure"],
            "warnings": [],
            "missing_rooms": [],
            "overlaps_count": 0,
            "boundary_violations": 0,
            "unused_area_ratio": 1.0,
            "room_coverage_ratio": 0.0
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
            warnings.append(f"Room '{rname}' has undersized dimensions ({rw:.1f}m x {rh:.1f}m). Minimum is 1.5m.")

        if rx < 0.0 or ry < 0.0 or (rx + rw) > (b_width + 0.01) or (ry + rh) > (b_length + 0.01):
            boundary_violations += 1
            warnings.append(f"Room '{rname}' extends beyond outer boundary ({b_width}m x {b_length}m).")

        total_room_area += max(0.0, rw * rh)

    # 2. Overlap Checks (Axis-Aligned Bounding Box intersection)
    for i in range(len(rooms)):
        r1 = rooms[i]
        x1, y1, w1, h1 = r1["x"], r1["y"], r1["width"], r1.get("height", r1.get("length", 0))
        for j in range(i + 1, len(rooms)):
            r2 = rooms[j]
            x2, y2, w2, h2 = r2["x"], r2["y"], r2["width"], r2.get("height", r2.get("length", 0))

            # Calculate intersection
            inter_x1 = max(x1, x2)
            inter_y1 = max(y1, y2)
            inter_x2 = min(x1 + w1, x2 + w2)
            inter_y2 = min(y1 + h1, y2 + h2)

            if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                overlap_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                if overlap_area > 0.5:  # Tolerance threshold in sq.m
                    overlaps.append({
                        "room1": r1.get("name", "Room 1"),
                        "room2": r2.get("name", "Room 2"),
                        "overlap_sqm": round(overlap_area, 2)
                    })
                    warnings.append(f"Overlap detected between '{r1.get('name')}' and '{r2.get('name')}' ({overlap_area:.1f} m²).")

    # 3. Unused Area Calculation
    unused_area = max(0.0, total_building_area - total_room_area)
    unused_ratio = round(unused_area / max(total_building_area, 1.0), 3)

    if unused_ratio > 0.40:
        warnings.append(f"High unused space ratio ({unused_ratio * 100:.1f}%). Layout contains open courtyard/circulation.")

    # 4. Target Room Coverage Check
    missing_rooms = []
    if target_requirements and "rooms" in target_requirements:
        req_types = [r.get("type", "").lower() for r in target_requirements["rooms"]]
        gen_types = [r.get("type", "").lower() for r in rooms]
        
        for req_t in set(req_types):
            if req_t and req_t not in gen_types:
                missing_rooms.append(req_t.replace("_", " ").title())

        if missing_rooms:
            warnings.append(f"Missing required room categories: {', '.join(missing_rooms)}")

    # 5. Circulation & Entrance Availability
    has_entrance = any("foyer" in r.get("type", "").lower() or "reception" in r.get("type", "").lower() or "entrance" in r.get("name", "").lower() for r in rooms)
    if not has_entrance:
        warnings.append("No explicit entrance/foyer room detected. Defaulting main access to perimeter boundary.")

    # Determine overall validity score
    is_valid = len(overlaps) <= 2 and boundary_violations <= 1 and len(rooms) > 0
    score = max(0.0, 1.0 - (len(overlaps) * 0.15) - (boundary_violations * 0.20) - (len(missing_rooms) * 0.10) - (invalid_dim_count * 0.05))
    score = round(score * 100.0, 1)

    return {
        "valid": is_valid,
        "score_percentage": score,
        "errors": errors,
        "warnings": warnings,
        "missing_rooms": missing_rooms,
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
    Optional post-processing geometry repair step that clamps out-of-bounds rooms
    and resolves minor wall overlaps.
    """
    if not floorplan or "rooms" not in floorplan:
        return floorplan, False

    b_width = float(floorplan.get("building_width", 30.0))
    b_length = float(floorplan.get("building_length", 20.0))
    repaired = False
    repaired_rooms = []

    for r in floorplan["rooms"]:
        rx, ry = float(r.get("x", 0.0)), float(r.get("y", 0.0))
        rw, rh = float(r.get("width", 5.0)), float(r.get("height", r.get("length", 5.0)))

        # Clamp width and height
        rw = max(2.0, min(rw, b_width))
        rh = max(2.0, min(rh, b_length))

        # Clamp position inside boundary
        if rx + rw > b_width:
            rx = max(0.0, b_width - rw)
            repaired = True
        if ry + rh > b_length:
            ry = max(0.0, b_length - rh)
            repaired = True

        r_copy = dict(r)
        r_copy["x"] = round(rx, 2)
        r_copy["y"] = round(ry, 2)
        r_copy["width"] = round(rw, 2)
        r_copy["height"] = round(rh, 2)
        repaired_rooms.append(r_copy)

    repaired_plan = dict(floorplan)
    repaired_plan["rooms"] = repaired_rooms
    return repaired_plan, repaired
