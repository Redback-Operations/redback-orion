#!/usr/bin/env python3
"""Fixture Risk Matrix for Hawthorn Hawks 2026 Season"""

import json

# Hawthorn's 2026 fixtures (from R0 to R22)
fixtures = [
    {"round": 0, "opponent": "GWS", "location": "away", "ground": "Giants Stadium"},
    {"round": 1, "opponent": "Essendon", "location": "home", "ground": "MCG"},
    {"round": 2, "opponent": "Sydney", "location": "home", "ground": "MCG"},
    {"round": 3, "opponent": "Geelong", "location": "home", "ground": "MCG"},
    {"round": 4, "opponent": "Bulldogs", "location": "neutral", "ground": "UTAS Stadium"},
    {"round": 5, "opponent": "Port Adelaide", "location": "home", "ground": "MCG"},
    {"round": 6, "opponent": "Gold Coast", "location": "neutral", "ground": "TIO Stadium"},
    {"round": 7, "opponent": "Collingwood", "location": "away", "ground": "MCG"},
    {"round": 8, "opponent": "Fremantle", "location": "away", "ground": "Optus Stadium"},
    {"round": 9, "opponent": "Melbourne", "location": "away", "ground": "MCG"},
    {"round": 10, "opponent": "Adelaide", "location": "home", "ground": "MCG"},
    {"round": 11, "opponent": "St Kilda", "location": "away", "ground": "Marvel Stadium"},
    {"round": 12, "opponent": "Bulldogs", "location": "home", "ground": "MCG"},
    {"round": 13, "opponent": "Gold Coast", "location": "away", "ground": "People First Stadium"},
    {"round": 14, "opponent": "GWS", "location": "home", "ground": "MCG"},
    {"round": 15, "opponent": "Melbourne", "location": "neutral", "ground": "UTAS Stadium"},
    {"round": 16, "opponent": "Carlton", "location": "away", "ground": "MCG"},
    {"round": 17, "opponent": "Richmond", "location": "away", "ground": "MCG"},
    {"round": 18, "opponent": "Essendon", "location": "home", "ground": "MCG"},
    {"round": 19, "opponent": "North Melbourne", "location": "neutral", "ground": "UTAS Stadium"},
    {"round": 20, "opponent": "Brisbane", "location": "away", "ground": "Gabba"},
    {"round": 21, "opponent": "Collingwood", "location": "home", "ground": "MCG"},
    {"round": 22, "opponent": "West Coast", "location": "away", "ground": "Optus Stadium"},
]

# Rivalry teams (historical rivals of Hawthorn)
historical_rivals = ["Geelong", "Essendon", "Collingwood"]
melbourne_teams = ["Collingwood", "Essendon", "Carlton", "Richmond", "Melbourne", "Bulldogs", "St Kilda", "North Melbourne", "Geelong"]

# Opponent fan base risk (1-3 scale)
fan_base_risk = {
    "Collingwood": 3,
    "Essendon": 2,
    "Carlton": 2,
    "Richmond": 2,
    "Geelong": 2,
    "Bulldogs": 1,
    "Melbourne": 1,
    "Sydney": 1,
    "GWS": 1,
    "Port Adelaide": 1,
    "Adelaide": 1,
    "Fremantle": 1,
    "West Coast": 1,
    "Brisbane": 1,
    "Gold Coast": 1,
    "St Kilda": 1,
    "North Melbourne": 1,
}

def calculate_risk_score(fixture):
    """Calculate risk score from 1-5 for a fixture"""
    score = 1  # Base minimum score
    
    # Rivalry factor (0-3)
    if fixture["opponent"] in historical_rivals:
        score += 3
    
    # Location factor (0-2)
    if fixture["location"] == "away":
        score += 2
    elif fixture["location"] == "neutral":
        score += 0
    
    # Melbourne derby factor (0-4)
    if fixture["opponent"] in melbourne_teams and fixture["location"] in ["home", "away"]:
        score += 2
    
    # Finals implication (late season rounds 15-22)
    if fixture["round"] >= 15:
        score += 1
    
    # Fan base factor (0-3)
    score += fan_base_risk.get(fixture["opponent"], 1)
    
    # Normalize to 1-5 scale
    normalized = min(5, max(1, round(score / 3)))
    
    return normalized

def get_risk_level(score):
    """Convert numeric score to risk level and emoji"""
    if score >= 4:
        return "🔴 HIGH"
    elif score == 3:
        return "🟡 MEDIUM"
    else:
        return "🟢 LOW"

def generate_risk_matrix():
    """Generate the full risk matrix for Hawthorn"""
    matrix = []
    
    for fixture in fixtures:
        risk_score = calculate_risk_score(fixture)
        
        matrix.append({
            "round": fixture["round"],
            "opponent": fixture["opponent"],
            "location": fixture["location"].upper(),
            "ground": fixture["ground"],
            "risk_score": risk_score,
            "risk_level": get_risk_level(risk_score)
        })
    
    return matrix

def print_visual_matrix(matrix):
    """Print a beautiful visual matrix to the console"""
    print("\n" + "="*80)
    print("🏉 HAWTHORN 2026 FIXTURE RISK MATRIX")
    print("="*80)
    print(f"{'Round':<6} {'Opponent':<15} {'Loc':<4} {'Ground':<20} {'Risk':<8} {'Level'}")
    print("-"*80)
    
    for game in matrix:
        print(f"R{game['round']:<3}  {game['opponent']:<15} {game['location']:<4} {game['ground']:<20}   {game['risk_score']}     {game['risk_level']}")
    
    print("-"*80)
    
    # Summary statistics
    high_risk = [g for g in matrix if g["risk_score"] >= 4]
    medium_risk = [g for g in matrix if g["risk_score"] == 3]
    low_risk = [g for g in matrix if g["risk_score"] <= 2]
    
    print(f"\n Hawthorn 2026 Season Fxiture Risk Summary:")
    print(f"   🔴 High risk games: {len(high_risk)}")
    for game in high_risk:
        print(f"      - R{game['round']}: vs {game['opponent']} ({game['location']})")
    print(f"   🟡 Medium risk games: {len(medium_risk)}")
    print(f"   🟢 Low risk games: {len(low_risk)}")
    print(f"\n   Average risk score: {sum(g['risk_score'] for g in matrix)/len(matrix):.1f}/5.0")

def save_as_json(matrix):
    """Save the matrix as JSON for API use"""
    output = {
        "team": "Hawthorn Hawks",
        "season": 2025,
        "risk_matrix": matrix,
        "summary": {
            "high_risk_games": len([g for g in matrix if g["risk_score"] >= 4]),
            "medium_risk_games": len([g for g in matrix if g["risk_score"] == 3]),
            "low_risk_games": len([g for g in matrix if g["risk_score"] <= 2]),
            "average_risk": sum(g["risk_score"] for g in matrix) / len(matrix)
        }
    }
    
    with open("hawthorn_risk_matrix.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n Saved to hawthorn_risk_matrix.json")

if __name__ == "__main__":
    # Generate and display the matrix
    matrix = generate_risk_matrix()
    print_visual_matrix(matrix)
    save_as_json(matrix)