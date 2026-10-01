"""Test scenarios for crowd allocation risk zone validation"""

import json
from main import assess_risk

def run_test(test_name, input_data, expected_output):
    """Run a single test and report results"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = assess_risk(input_data)
        
        # Compare results
        matches = True
        issues = []
        
        # Check video_id
        if result.get("video_id") != expected_output.get("video_id"):
            matches = False
            issues.append(f"video_id mismatch: got {result.get('video_id')}, expected {expected_output.get('video_id')}")
        
        # Check zones length
        if len(result.get("zones", [])) != len(expected_output.get("zones", [])):
            matches = False
            issues.append(f"Zone count mismatch: got {len(result.get('zones', []))}, expected {len(expected_output.get('zones', []))}")
        
        # Check each zone
        for i, (result_zone, expected_zone) in enumerate(zip(result.get("zones", []), expected_output.get("zones", []))):
            if result_zone.get("risk_level") != expected_zone.get("risk_level"):
                matches = False
                issues.append(f"Zone {i} risk_level: got {result_zone.get('risk_level')}, expected {expected_zone.get('risk_level')}")
            if result_zone.get("flagged") != expected_zone.get("flagged"):
                matches = False
                issues.append(f"Zone {i} flagged: got {result_zone.get('flagged')}, expected {expected_zone.get('flagged')}")
        
        # Check recommendations
        if result.get("recommendations") != expected_output.get("recommendations"):
            matches = False
            issues.append(f"Recommendations mismatch")
        
        if matches:
            print("✅ PASSED")
            print(f"Output: {json.dumps(result, indent=2)}")
        else:
            print("❌ FAILED")
            for issue in issues:
                print(f"  • {issue}")
            print(f"\nGot: {json.dumps(result, indent=2)}")
            print(f"\nExpected: {json.dumps(expected_output, indent=2)}")
        
        return matches
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# Test Scenario 1: Normal operation (from SCHEMA.md)
def scenario_1():
    input_data = {
        "video_id": "match_01",
        "crowd_state": "increasing_density",
        "zones": [
            {"zone_id": "A1", "person_count": 8, "density": 0.72},
            {"zone_id": "A2", "person_count": 5, "density": 0.45}
        ]
    }
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
    return run_test("Normal operation (SCHEMA.md example)", input_data, expected)

# Test Scenario 2: Critical density zone
def scenario_2():
    input_data = {
        "video_id": "match_02",
        "crowd_state": "stable",
        "zones": [
            {"zone_id": "B1", "person_count": 15, "density": 0.92},
            {"zone_id": "B2", "person_count": 3, "density": 0.25}
        ]
    }
    result = assess_risk(input_data)
    print(f"\n{'='*60}")
    print(f"Test: Critical density zone")
    print(f"{'='*60}")
    
    # Manual checks
    issues = []
    zones = result.get("zones", [])
    
    if zones[0].get("risk_level") != "critical":
        issues.append(f"Zone B1 risk_level: got {zones[0].get('risk_level')}, expected critical")
    if not zones[0].get("flagged"):
        issues.append(f"Zone B1 flagged: expected True")
    if zones[1].get("risk_level") != "very_low":
        issues.append(f"Zone B2 risk_level: got {zones[1].get('risk_level')}, expected very_low")
    
    # Check for critical zone recommendation
    has_critical_rec = any("critical" in rec.lower() for rec in result.get("recommendations", []))
    if not has_critical_rec:
        issues.append("Missing recommendation for critical zone")
    
    # Also check that critical recommendation includes the zone ID
    critical_rec_for_b1 = any("B1" in rec and "critical" in rec.lower() for rec in result.get("recommendations", []))
    if not critical_rec_for_b1:
        issues.append("Critical recommendation should mention zone B1")
    
    if not issues:
        print("✅ PASSED")
        print(f"Output: {json.dumps(result, indent=2)}")
        return True
    else:
        print("❌ FAILED")
        for issue in issues:
            print(f"  • {issue}")
        return False

# Test Scenario 3: Multiple high-risk zones
def scenario_3():
    input_data = {
        "video_id": "match_03",
        "crowd_state": "increasing_density",
        "zones": [
            {"zone_id": "C1", "person_count": 10, "density": 0.75},
            {"zone_id": "C2", "person_count": 9, "density": 0.72},
            {"zone_id": "C3", "person_count": 4, "density": 0.38}
        ]
    }
    result = assess_risk(input_data)
    print(f"\n{'='*60}")
    print(f"Test: Multiple high-risk zones")
    print(f"{'='*60}")
    
    issues = []
    zones = result.get("zones", [])
    
    # Check risk levels
    if zones[0].get("risk_level") != "high":
        issues.append(f"Zone C1: expected high, got {zones[0].get('risk_level')}")
    if zones[1].get("risk_level") != "high":
        issues.append(f"Zone C2: expected high, got {zones[1].get('risk_level')}")
    if zones[2].get("risk_level") != "low":
        issues.append(f"Zone C3: expected low, got {zones[2].get('risk_level')}")
    
    # Check flagged status
    if not zones[0].get("flagged"):
        issues.append("Zone C1 should be flagged")
    if not zones[1].get("flagged"):
        issues.append("Zone C2 should be flagged")
    
    # Check recommendations include high-risk zones
    recommendations = result.get("recommendations", [])
    if not any("C1" in rec for rec in recommendations):
        issues.append("Recommendation missing for C1")
    if not any("C2" in rec for rec in recommendations):
        issues.append("Recommendation missing for C2")
    
    if not issues:
        print("✅ PASSED")
        print(f"Output: {json.dumps(result, indent=2)}")
        return True
    else:
        print("❌ FAILED")
        for issue in issues:
            print(f"  • {issue}")
        return False

# Test Scenario 4: Empty zones list
def scenario_4():
    input_data = {
        "video_id": "match_04",
        "crowd_state": "stable",
        "zones": []
    }
    expected = {
        "video_id": "match_04",
        "zones": [],
        "recommendations": ["All zones within safe thresholds - continue monitoring"]
    }
    return run_test("Empty zones list", input_data, expected)

# Test Scenario 5: Missing crowd_state (should default to stable)
def scenario_5():
    input_data = {
        "video_id": "match_05",
        "zones": [
            {"zone_id": "D1", "person_count": 3, "density": 0.25}
        ]
    }
    result = assess_risk(input_data)
    print(f"\n{'='*60}")
    print(f"Test: Missing crowd_state (should default to stable)")
    print(f"{'='*60}")
    
    # Should not throw error and should work
    if result.get("video_id") == "match_05" and result.get("zones"):
        print("✅ PASSED - Handles missing crowd_state gracefully")
        print(f"Output: {json.dumps(result, indent=2)}")
        return True
    else:
        print("❌ FAILED")
        return False

# Run all tests
def run_all_tests():
    print("\n" + "="*60)
    print("RUNNING CROWD ALLOCATION RISK ZONE VALIDATION TESTS")
    print("="*60)
    
    results = []
    results.append(scenario_1())
    results.append(scenario_2())
    results.append(scenario_3())
    results.append(scenario_4())
    results.append(scenario_5())
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Module is ready for integration.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review and fix.")

if __name__ == "__main__":
    run_all_tests()