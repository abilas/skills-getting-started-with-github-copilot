from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


ACTIVITY_NAME = "Chess Club"


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        yield TestClient(app)
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_participants = activities[ACTIVITY_NAME]["participants"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[ACTIVITY_NAME]["participants"] == expected_participants


def test_signup_adds_participant(client):
    # Arrange
    email = "new-student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {ACTIVITY_NAME}"
    }
    assert email in activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_without_adding_participant_again(client):
    # Arrange
    email = "existing-student@mergington.edu"
    participants = activities[ACTIVITY_NAME]["participants"]
    participants.append(email)
    original_count = participants.count(email)

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert participants.count(email) == original_count


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = "registered-student@mergington.edu"
    activities[ACTIVITY_NAME]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {ACTIVITY_NAME}"
    }
    assert email not in activities[ACTIVITY_NAME]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_unregistered_participant(client):
    # Arrange
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert email not in activities[ACTIVITY_NAME]["participants"]