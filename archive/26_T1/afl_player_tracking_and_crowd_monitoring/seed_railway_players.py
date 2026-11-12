import requests

LOCAL_URL = "http://localhost:8000/api/players"
RAILWAY_URL = "https://project-orion-production-8239.up.railway.app/api/player"

print("Reading players from local database...")

response = requests.get(
    LOCAL_URL,
    timeout=30,
)

response.raise_for_status()

players = response.json()

print(f"Found {len(players)} local players.")

for player in players:
    # The production database will generate its own ID.
    player_payload = {
        key: value
        for key, value in player.items()
        if key != "id"
    }

    print(
        f"Uploading: {player.get('name', 'Unknown')}"
    )

    upload_response = requests.post(
        RAILWAY_URL,
        json=player_payload,
        timeout=60,
    )

    if upload_response.ok:
        result = upload_response.json()

        print(
            f"  SUCCESS -> production ID: "
            f"{result.get('id')}"
        )
    else:
        print(
            f"  FAILED -> "
            f"{upload_response.status_code}"
        )

        print(
            upload_response.text
        )

print("\nFinished.")