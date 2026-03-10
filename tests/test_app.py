import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Reset activities before each test
    for activity in activities.values():
        activity["participants"] = []


def test_get_activities():
    # Arrange: Add a participant to Chess Club
    activities["Chess Club"]["participants"] = ["alice@mergington.edu"]
    # Act: Get activities
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["participants"] == ["alice@mergington.edu"]


def test_signup_for_activity():
    # Arrange: Ensure no participants
    activities["Chess Club"]["participants"] = []
    # Act: Sign up
    response = client.post("/activities/Chess Club/signup?email=bob@mergington.edu")
    # Assert
    assert response.status_code == 200
    assert "Signed up bob@mergington.edu for Chess Club" in response.json()["message"]
    assert "bob@mergington.edu" in activities["Chess Club"]["participants"]


def test_prevent_duplicate_signup():
    # Arrange: Add participant
    activities["Chess Club"]["participants"] = ["bob@mergington.edu"]
    # Act: Try to sign up again
    response = client.post("/activities/Chess Club/signup?email=bob@mergington.edu")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant():
    # Arrange: Add participant
    activities["Chess Club"]["participants"] = ["bob@mergington.edu"]
    # Act: Unregister
    response = client.delete("/activities/Chess Club/unregister?email=bob@mergington.edu")
    # Assert
    assert response.status_code == 200
    assert "Unregistered bob@mergington.edu from Chess Club" in response.json()["message"]
    assert "bob@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_not_registered():
    # Arrange: No participants
    activities["Chess Club"]["participants"] = []
    # Act: Try to unregister
    response = client.delete("/activities/Chess Club/unregister?email=bob@mergington.edu")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not registered"


def test_signup_activity_not_found():
    # Arrange: No such activity
    # Act: Try to sign up for non-existent activity
    response = client.post("/activities/Nonexistent/signup?email=bob@mergington.edu")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_activity_not_found():
    # Arrange: No such activity
    # Act: Try to unregister from non-existent activity
    response = client.delete("/activities/Nonexistent/unregister?email=bob@mergington.edu")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
