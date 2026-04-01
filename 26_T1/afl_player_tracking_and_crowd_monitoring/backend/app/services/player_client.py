def get_player_data():
    return {
        "status": "success",
        "message": "Players data retrieved successfully",
        "data": [
            {
                "player_id": 1,
                "team": "Team A",
                "x": 120,
                "y": 340,
                "speed": 6.4
            },
            {
                "player_id": 2,
                "team": "Team B",
                "x": 210,
                "y": 280,
                "speed": 5.8
            }
        ]
    }