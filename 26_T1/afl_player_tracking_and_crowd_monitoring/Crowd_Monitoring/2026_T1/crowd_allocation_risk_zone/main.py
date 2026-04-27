"""Crowd Allocation and Risk Zone Task Implementation

This task receives behaviour analysis data and returns risk zone assessments.
Input and output formats are defined in SCHEMA.md - DO NOT MODIFY THEM.
"""

def assess_risk(input_data):
    """
    Assess zone risk levels and prepare recommendations.
    
    Input format (from SCHEMA.md):
    {
        "video_id": str,
        "crowd_state": str,
        "zones": [
            {"zone_id": str, "person_count": int, "density": float}
        ]
    }
    
    Output format (from SCHEMA.md):
    {
        "video_id": str,
        "zones": [
            {"zone_id": str, "risk_level": str, "flagged": bool}
        ],
        "recommendations": [str]
    }
    """
    
    # Risk thresholds based on density (0.0 to 1.0)
    # Adjusted to match SCHEMA.md example (0.45 = medium)
    RISK_THRESHOLDS = {
        "critical": 0.85,
        "high": 0.70,
        "medium": 0.40,  # Changed from 0.50 to 0.40 so 0.45 = medium
        "low": 0.30
    }
    
    def get_risk_level(density):
        """Determine risk level and flagged status based on density"""
        if density >= RISK_THRESHOLDS["critical"]:
            return "critical", True
        elif density >= RISK_THRESHOLDS["high"]:
            return "high", True
        elif density >= RISK_THRESHOLDS["medium"]:
            return "medium", False
        elif density >= RISK_THRESHOLDS["low"]:
            return "low", False
        else:
            return "very_low", False
    
    # Assess each zone
    assessed_zones = []
    high_risk_zones = []
    
    for zone in input_data["zones"]:
        risk_level, flagged = get_risk_level(zone["density"])
        
        assessed_zones.append({
            "zone_id": zone["zone_id"],
            "risk_level": risk_level,
            "flagged": flagged
        })
        
        if flagged:
            high_risk_zones.append(zone["zone_id"])
    
    # Generate recommendations matching SCHEMA.md exactly
    recommendations = []
    crowd_state = input_data.get("crowd_state", "stable")
    
    # Critical zone recommendations (highest priority)
    for zone in assessed_zones:
        if zone["risk_level"] == "critical":
            recommendations.append(f"🚨 CRITICAL: Zone {zone['zone_id']} at critical density - immediate crowd control required")
    
    # High risk zone recommendations
    for zone in assessed_zones:
        if zone["risk_level"] == "high" and zone["flagged"]:
            recommendations.append(f"Monitor zone {zone['zone_id']} closely")
    
    # Crowd state recommendations
    if crowd_state == "increasing_density":
        recommendations.append("Prepare crowd redirection if density increases further")
    
    # Fallback for other scenarios
    if not recommendations:
        if high_risk_zones:
            zones_str = ", ".join(high_risk_zones)
            recommendations.append(f"Monitor zone(s) {zones_str} closely")
        else:
            recommendations.append("All zones within safe thresholds - continue monitoring")
    
    # Return output matching SCHEMA.md exactly
    return {
        "video_id": input_data["video_id"],
        "zones": assessed_zones,
        "recommendations": recommendations
    }


if __name__ == "__main__":
    # Test with the example from SCHEMA.md
    test_input = {
        "video_id": "match_01",
        "crowd_state": "increasing_density",
        "zones": [
            {"zone_id": "A1", "person_count": 8, "density": 0.72},
            {"zone_id": "A2", "person_count": 5, "density": 0.45}
        ]
    }
    
    print("=== Testing with SCHEMA.md example ===")
    print("Input:")
    print(test_input)
    print("\nOutput:")
    result = assess_risk(test_input)
    print(result)
    
    print("\n--- Expected Output from SCHEMA.md ---")
    expected = {
        "video_id": "match_01",
        "zones": [
            {"zone_id": "A1", "risk_level": "high", "flagged": True},
            {"zone_id": "A2", "risk_level": "medium", "flagged": False}
        ],
        "recommendations": [
            "Monitor zone A1 closely",
            "Prepare crowd redirection if density increases further"
        ]
    }
    print(expected)
    
    print("\n✓ Match!" if result == expected else "\n✗ Still needs adjustment")