"""AFL Teams Configuration for Risk Matrix - Sprint 4"""

# Top 10 teams for Sprint 4
TEAMS = [
    "Collingwood",
    "Essendon",
    "Carlton",
    "Richmond",
    "Geelong",
    "Hawthorn",
    "Melbourne",
    "Western Bulldogs",
    "Sydney",
    "Brisbane"
]

# Fan base risk (size and intensity) - 1 to 3 scale
FAN_BASE_RISK = {
    "Collingwood": 3,
    "Essendon": 2,
    "Carlton": 2,
    "Richmond": 2,
    "Geelong": 2,
    "Hawthorn": 2,
    "Melbourne": 1,
    "Western Bulldogs": 1,
    "Sydney": 1,
    "Brisbane": 1,
}

# Historical rivalries (significant high-risk matchups)
HISTORICAL_RIVALRIES = [
    ("Collingwood", "Essendon"),
    ("Collingwood", "Carlton"),
    ("Collingwood", "Richmond"),
    ("Essendon", "Carlton"),
    ("Essendon", "Richmond"),
    ("Geelong", "Hawthorn"),
    ("Geelong", "Collingwood"),
    ("Carlton", "Richmond"),
]

# Special matches with extra weight
SPECIAL_MATCHES = {
    ("Collingwood", "Essendon"): {"name": "ANZAC Day", "weight": 4, "round": 6},
    ("Essendon", "Richmond"): {"name": "Dreamtime at the 'G", "weight": 4, "round": 10},
    ("Geelong", "Hawthorn"): {"name": "Easter Monday", "weight": 3, "round": 4},
    ("Melbourne", "Collingwood"): {"name": "Queen's Birthday", "weight": 3, "round": 12},
}

# Time slot risk weights (Thursday/Friday night highest)
TIME_SLOT_WEIGHTS = {
    "Thursday Night": 2,
    "Friday Night": 2,
    "Saturday Night": 1,
    "Saturday Afternoon": 0,
    "Saturday Twilight": 0,
    "Sunday Afternoon": 0,
    "Sunday Twilight": 0,
}

def get_rivalry_weight(team1, team2):
    """Get rivalry weight between two teams"""
    if (team1, team2) in HISTORICAL_RIVALRIES or (team2, team1) in HISTORICAL_RIVALRIES:
        return 2
    return 0

def get_special_match_weight(team1, team2, round_num):
    """Get special match weight if applicable"""
    # Check both orders
    for (t1, t2), match_info in SPECIAL_MATCHES.items():
        if ((team1 == t1 and team2 == t2) or (team1 == t2 and team2 == t1)) and match_info["round"] == round_num:
            return match_info["weight"], match_info["name"]
    return 0, None