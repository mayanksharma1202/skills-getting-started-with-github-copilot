import pytest
from fastapi.testclient import TestClient

from src import app as app_module


ACTIVITY_NAME = "Chess Club"
ACTIVITY_URL = "/activities/Chess%20Club"


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        ACTIVITY_NAME: {
            "description": "Practice chess",
            "schedule": "Fridays at 3:30 PM",
            "max_participants": 2,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_participant_data(client):
    # Arrange
    expected_participants = ["existing@mergington.edu"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[ACTIVITY_NAME]["participants"] == expected_participants


def test_signup_adds_participant(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(f"{ACTIVITY_URL}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {ACTIVITY_NAME}"}
    assert email in app_module.activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Unknown/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_invalid_email(client):
    # Arrange
    email = "invalid-email"

    # Act
    response = client.post(f"{ACTIVITY_URL}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email address"


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.post(f"{ACTIVITY_URL}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_full_activity(client):
    # Arrange
    app_module.activities[ACTIVITY_NAME]["max_participants"] = 1
    email = "new@mergington.edu"

    # Act
    response = client.post(f"{ACTIVITY_URL}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_remove_participant_unregisters_student(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(f"{ACTIVITY_URL}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {ACTIVITY_NAME}"}
    assert email not in app_module.activities[ACTIVITY_NAME]["participants"]


def test_remove_participant_rejects_missing_student(client):
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"{ACTIVITY_URL}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_remove_participant_rejects_unknown_activity(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
