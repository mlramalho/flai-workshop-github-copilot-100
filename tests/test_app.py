"""
Tests for the Mergington High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test."""
    original_participants = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, data in activities.items():
        data["participants"] = original_participants[name]


@pytest.fixture
def client():
    return TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_200(client):
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_dict(client):
    response = client.get("/activities")
    data = response.json()
    assert isinstance(data, dict)


def test_get_activities_contains_known_activities(client):
    response = client.get("/activities")
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Basketball Team" in data


def test_get_activities_activity_has_required_fields(client):
    response = client.get("/activities")
    data = response.json()
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success(client):
    response = client.post("/activities/Basketball Team/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]


def test_signup_adds_participant(client):
    email = "teststudent@mergington.edu"
    client.post(f"/activities/Soccer Club/signup?email={email}")
    assert email in activities["Soccer Club"]["participants"]


def test_signup_activity_not_found(client):
    response = client.post("/activities/Nonexistent Activity/signup?email=x@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered(client):
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


# --- DELETE /activities/{activity_name}/unregister ---

def test_unregister_success(client):
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"
    client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found(client):
    response = client.delete("/activities/Nonexistent Activity/unregister?email=x@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Basketball Team/unregister?email=nobody@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


# --- GET / redirect ---

def test_root_redirects_to_static(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307, 308)
    assert "/static/index.html" in response.headers["location"]
