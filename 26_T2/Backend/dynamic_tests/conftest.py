import os   #Read environment variables

import pytest
import requests #Let's us communicate with the HTTP backend directly instead of testing TestClient.


BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:8000").rstrip("/") #No need to hard-code backend address permanently


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def live_session():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    try:
        response = session.get(f"{BASE_URL}/", timeout=5)   #Check if docker is running
        response.raise_for_status() #200 OK response is expected, otherwise raise an error

    except requests.RequestException as e:
        pytest.skip(    #Important to use skip instead of fail because we can't test if a live API if the API itself isn't running
            f"Orion backend is not reachable at {BASE_URL}. "
            f"Start the T2 Compose stack first. Cause: {e}"
        )

    return session