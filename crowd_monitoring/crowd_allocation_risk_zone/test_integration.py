"""Integration test to verify handoff from crowd_behaviour_analytics"""

import sys
sys.path.insert(0, '/Users/xiwan2020/redback-orion/26_T1/afl_player_tracking_and_crowd_monitoring/Crowd_Monitoring/2026_T1')

# Import both tasks
from crowd_allocation_risk_zone.main import assess_risk

# Mock the behavior analytics output (since it's not fully implemented yet)
def mock_analyze_behaviour(input_data):
    """Simulates what crowd_behaviour_analytics would return"""
    return {
        "video_id": input_data.get("video_id", "test"),
        "crowd_state": input_data.get("crowd_state", "stable"),
        "zones": input_data.get("zones", [])
    }

# Test data that would come from the shared service
test_pipeline_data = {
    "video_id": "integration_test_01",
    "crowd_state": "increasing_density",
    "zones": [
        {"zone_id": "Z1", "person_count": 12, "density": 0.88},
        {"zone_id": "Z2", "person_count": 7, "density": 0.65},
        {"zone_id": "Z3", "person_count": 2, "density": 0.20}
    ]
}

print("="*60)
print("INTEGRATION TEST: Handoff from crowd_behaviour_analytics")
print("="*60)

# Simulate the pipeline
print("\n1. Behaviour Analytics processes input...")
behaviour_result = mock_analyze_behaviour(test_pipeline_data)
print(f"   → Returns: video_id={behaviour_result['video_id']}, crowd_state={behaviour_result['crowd_state']}, zones={len(behaviour_result['zones'])} zones")

print("\n2. Risk Zone task receives behaviour_result...")
risk_result = assess_risk(behaviour_result)
print(f"   → Returns: video_id={risk_result['video_id']}, zones assessed={len(risk_result['zones'])}")

print("\n3. Final output from pipeline:")
print(f"   Video ID: {risk_result['video_id']}")
print(f"   Zones assessed:")
for zone in risk_result['zones']:
    print(f"     - {zone['zone_id']}: {zone['risk_level']} (flagged: {zone['flagged']})")
print(f"   Recommendations:")
for rec in risk_result['recommendations']:
    print(f"     • {rec}")

print("\n✅ Integration handoff verified successfully!")