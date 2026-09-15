import time

def analyze_pdf_blueprint(filename: str) -> dict:
    """
    Simulates the ingestion, vector extraction, and typology detection of a PDF blueprint.
    """
    time.sleep(1.5)  # Simulate processing time
    
    is_residential = any(word in filename.lower() for word in ["house", "home", "villa", "residential"])
    
    if is_residential:
        typology = "Residential Villa"
        schedule = [
            {"Space": "Master Bedroom", "Function": "Private Sleeping", "Dimensions": "20' x 18'", "Area": "360 sqft", "En-Suite": "Attached Bath & Walk-in"},
            {"Space": "Guest Bedroom", "Function": "Private Sleeping", "Dimensions": "15' x 14'", "Area": "210 sqft", "En-Suite": "Shared Bath"},
            {"Space": "Living Area", "Function": "Public Zone", "Dimensions": "30' x 20'", "Area": "600 sqft", "En-Suite": "Powder Room Access"},
            {"Space": "Open Kitchen", "Function": "Service/Public", "Dimensions": "15' x 15'", "Area": "225 sqft", "En-Suite": "None"}
        ]
        compliance = [
            {"type": "success", "message": "Daylight Access: Window-to-floor area exceeds 15% across all primary living zones."},
            {"type": "warning", "message": "Plumbing Stack Efficiency: Guest bathroom wet-wall does not align vertically with ground floor kitchen. Consider relocating chase."},
            {"type": "error", "message": "Circulation Check: Dead-end corridor detected near Guest Bedroom exceeding 20 ft egress limit."}
        ]
        recommendations = "Shift the structural column grid at Grid B-3 to open up the Living Area. Reallocate the Guest Bath to align with the Kitchen plumbing stack."
    else:
        typology = "Hospitality / Commercial"
        schedule = [
            {"Space": "Standard Guest Key (x20)", "Function": "Private Room", "Dimensions": "12' x 24'", "Area": "288 sqft", "En-Suite": "Attached 3-Fixture Bath"},
            {"Space": "Lobby Vestibule", "Function": "Public Entry", "Dimensions": "40' x 30'", "Area": "1200 sqft", "En-Suite": "Common Restrooms"},
            {"Space": "Housekeeping Core", "Function": "Service", "Dimensions": "10' x 15'", "Area": "150 sqft", "En-Suite": "None"},
            {"Space": "Fire Egress Stair A", "Function": "Circulation", "Dimensions": "10' x 20'", "Area": "200 sqft", "En-Suite": "None"}
        ]
        compliance = [
            {"type": "success", "message": "Egress Compliance: Distance between Fire Stair A and B meets maximum travel distance codes."},
            {"type": "warning", "message": "Acoustic Buffer: Standard Guest Key walls adjacent to Housekeeping Core may require additional STC 50 sound insulation."},
            {"type": "success", "message": "En-Suite Logic: All guest rooms utilize efficient back-to-back plumbing chases."}
        ]
        recommendations = "Expand Lobby Vestibule ceiling to double-height for visual impact. Add acoustic buffers around the housekeeping vertical core."

    return {
        "filename": filename,
        "typology": typology,
        "scale_detected": "1/4\" = 1'-0\"",
        "schedule": schedule,
        "compliance": compliance,
        "recommendations": recommendations
    }
