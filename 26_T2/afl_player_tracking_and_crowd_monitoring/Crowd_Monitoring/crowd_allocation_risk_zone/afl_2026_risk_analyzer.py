#!/usr/bin/env python3
"""AFL 2026 Season Fixture Risk Analyzer - Multi-Team Support"""

import json
import csv
from afl_teams_config import *

# Sample 2026 fixtures for the 10 teams (Rounds 1-24)
# Format: (round, home_team, away_team, time_slot, is_public_holiday)
FIXTURES_2026 = [
    # Round 1
    (1, "Collingwood", "Sydney", "Friday Night", False),
    (1, "Essendon", "Carlton", "Saturday Night", False),
    (1, "Richmond", "Geelong", "Saturday Afternoon", False),
    (1, "Melbourne", "Western Bulldogs", "Sunday Afternoon", False),
    (1, "Brisbane", "Hawthorn", "Saturday Night", False),
    
    # Round 2
    (2, "Carlton", "Richmond", "Thursday Night", False),
    (2, "Collingwood", "Essendon", "Friday Night", False),  # Early season rivalry
    (2, "Geelong", "Melbourne", "Saturday Afternoon", False),
    (2, "Sydney", "Brisbane", "Saturday Night", False),
    (2, "Western Bulldogs", "Hawthorn", "Sunday Afternoon", False),
    
    # Round 3
    (3, "Essendon", "Collingwood", "Friday Night", False),
    (3, "Richmond", "Carlton", "Saturday Night", False),
    (3, "Hawthorn", "Geelong", "Saturday Afternoon", False),
    (3, "Brisbane", "Melbourne", "Sunday Afternoon", False),
    (3, "Sydney", "Western Bulldogs", "Saturday Night", False),
    
    # Round 4 - Easter Monday
    (4, "Geelong", "Hawthorn", "Monday Afternoon", True),  # Easter Monday special match
    
    # Round 5
    (5, "Collingwood", "Richmond", "Friday Night", False),
    (5, "Carlton", "Essendon", "Saturday Night", False),
    (5, "Melbourne", "Sydney", "Saturday Afternoon", False),
    (5, "Western Bulldogs", "Brisbane", "Sunday Afternoon", False),
    
    # Round 6 - ANZAC Day
    (6, "Collingwood", "Essendon", "Friday Night", True),  # ANZAC Day special match
    
    # Round 7
    (7, "Richmond", "Collingwood", "Saturday Night", False),
    (7, "Carlton", "Geelong", "Thursday Night", False),
    (7, "Hawthorn", "Melbourne", "Saturday Afternoon", False),
    
    # Round 8
    (8, "Essendon", "Richmond", "Friday Night", False),
    (8, "Collingwood", "Carlton", "Saturday Night", False),
    (8, "Brisbane", "Sydney", "Saturday Night", False),
    
    # Round 9
    (9, "Geelong", "Collingwood", "Friday Night", False),
    (9, "Hawthorn", "Essendon", "Saturday Afternoon", False),
    
    # Round 10 - Dreamtime
    (10, "Essendon", "Richmond", "Saturday Night", True),  # Dreamtime special match
    
    # Round 11
    (11, "Carlton", "Collingwood", "Friday Night", False),
    (11, "Sydney", "Geelong", "Saturday Night", False),
    
    # Round 12 - Queen's Birthday
    (12, "Melbourne", "Collingwood", "Monday Afternoon", True),  # Queen's Birthday special match
    
    # Rounds 13-24 (additional fixtures to complete season)
    (13, "Richmond", "Essendon", "Saturday Night", False),
    (14, "Collingwood", "Geelong", "Friday Night", False),
    (15, "Carlton", "Hawthorn", "Sunday Afternoon", False),
    (16, "Essendon", "Collingwood", "Friday Night", False),
    (17, "Richmond", "Carlton", "Thursday Night", False),
    (18, "Hawthorn", "Collingwood", "Saturday Afternoon", False),
    (19, "Geelong", "Essendon", "Saturday Night", False),
    (20, "Melbourne", "Richmond", "Sunday Afternoon", False),
    (21, "Collingwood", "Carlton", "Friday Night", False),
    (22, "Essendon", "Geelong", "Saturday Night", False),
    (23, "Richmond", "Hawthorn", "Saturday Afternoon", False),
    (24, "Collingwood", "Melbourne", "Friday Night", False),
]

def calculate_risk_score(round_num, home_team, away_team, time_slot, is_public_holiday):
    """Calculate risk score (1-5) for a fixture"""
    score = 1  # Base minimum score
    
    # Time slot weight (Thursday/Friday night highest)
    score += TIME_SLOT_WEIGHTS.get(time_slot, 0)
    
    # Public holiday
    if is_public_holiday:
        score += 2
    
    # Rivalry weight
    score += get_rivalry_weight(home_team, away_team)
    
    # Special match weight
    special_weight, special_name = get_special_match_weight(home_team, away_team, round_num)
    score += special_weight
    
    # Away game (for crowd risk analysis - away fans increase risk)
    # For neutral games, both teams' fans travel
    score += 1  # Default away game risk
    
    # Fan base risk (average of both teams)
    fan_risk = (FAN_BASE_RISK.get(home_team, 1) + FAN_BASE_RISK.get(away_team, 1)) / 2
    score += fan_risk
    
    # Normalize to 1-5 scale
    normalized = min(5, max(1, round(score / 3)))
    
    return normalized

def get_risk_level(score):
    """Convert numeric score to risk level and emoji"""
    if score >= 4:
        return f"🔴 HIGH ({score})"
    elif score == 3:
        return f"🟡 MEDIUM ({score})"
    else:
        return f"🟢 LOW ({score})"

def analyze_all_fixtures():
    """Analyze all fixtures and return results"""
    results = []
    
    for fixture in FIXTURES_2026:
        round_num, home_team, away_team, time_slot, is_public_holiday = fixture
        
        risk_score = calculate_risk_score(round_num, home_team, away_team, time_slot, is_public_holiday)
        
        # Get special match name if applicable
        _, special_name = get_special_match_weight(home_team, away_team, round_num)
        
        results.append({
            "round": round_num,
            "home_team": home_team,
            "away_team": away_team,
            "time_slot": time_slot,
            "is_public_holiday": is_public_holiday,
            "special_match": special_name,
            "risk_score": risk_score,
            "risk_level": get_risk_level(risk_score)
        })
    
    return results

def print_summary(results):
    """Print console summary of risk analysis"""
    print("\n" + "="*80)
    print("🏉 AFL 2026 SEASON FIXTURE RISK ANALYSIS")
    print("="*80)
    
    # Sort by risk score (highest first)
    sorted_results = sorted(results, key=lambda x: x["risk_score"], reverse=True)
    
    print("\n🔴 HIGHEST RISK FIXTURES (Top 10):")
    print("-"*80)
    for i, fixture in enumerate(sorted_results[:10], 1):
        special = f" - {fixture['special_match']}" if fixture['special_match'] else ""
        print(f"{i:2}. R{fixture['round']}: {fixture['home_team']} vs {fixture['away_team']} ({fixture['time_slot']}){special} → Score: {fixture['risk_score']}/5")
    
    # Team risk summary
    print("\n📊 TEAM RISK SUMMARY:")
    print("-"*80)
    
    team_high_risk = {}
    for fixture in results:
        if fixture["risk_score"] >= 4:
            for team in [fixture["home_team"], fixture["away_team"]]:
                team_high_risk[team] = team_high_risk.get(team, 0) + 1
    
    sorted_teams = sorted(team_high_risk.items(), key=lambda x: x[1], reverse=True)
    for team, count in sorted_teams[:10]:
        bar = "█" * min(count, 10)
        print(f"   {team:20} : {count} high risk games {bar}")
    
    # Overall statistics
    high_risk = [f for f in results if f["risk_score"] >= 4]
    medium_risk = [f for f in results if f["risk_score"] == 3]
    low_risk = [f for f in results if f["risk_score"] <= 2]
    
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   Total fixtures analyzed: {len(results)}")
    print(f"   🔴 High risk (4-5): {len(high_risk)}")
    print(f"   🟡 Medium risk (3): {len(medium_risk)}")
    print(f"   🟢 Low risk (1-2): {len(low_risk)}")
    print(f"   📊 Average risk score: {sum(f['risk_score'] for f in results)/len(results):.2f}/5.0")
    
    print("\n💾 Output saved to:")
    print("   - afl_2026_risk_matrix.json")
    print("   - afl_2026_risk_matrix.csv")

def save_to_json(results, filename="afl_2026_risk_matrix.json"):
    """Save results to JSON file"""
    output = {
        "season": 2026,
        "total_fixtures": len(results),
        "fixtures": results,
        "summary": {
            "high_risk": len([f for f in results if f["risk_score"] >= 4]),
            "medium_risk": len([f for f in results if f["risk_score"] == 3]),
            "low_risk": len([f for f in results if f["risk_score"] <= 2]),
            "average_risk": sum(f["risk_score"] for f in results) / len(results)
        }
    }
    
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    print(f"   - {filename}")

def save_to_csv(results, filename="afl_2026_risk_matrix.csv"):
    """Save results to CSV file"""
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["round", "home_team", "away_team", "time_slot", "special_match", "risk_score", "risk_level"])
        writer.writeheader()
        for fixture in results:
            writer.writerow({
                "round": fixture["round"],
                "home_team": fixture["home_team"],
                "away_team": fixture["away_team"],
                "time_slot": fixture["time_slot"],
                "special_match": fixture["special_match"] or "",
                "risk_score": fixture["risk_score"],
                "risk_level": fixture["risk_level"]
            })
    print(f"   - {filename}")

if __name__ == "__main__":
    results = analyze_all_fixtures()
    print_summary(results)
    save_to_json(results)
    save_to_csv(results)