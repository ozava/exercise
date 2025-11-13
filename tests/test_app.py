from fastapi.testclient import TestClient
from src import app as appmod

client = TestClient(appmod.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity keys
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure email not already in participants
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    if email in data[activity]["participants"]:
        # remove for test precondition
        client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant appears
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify participant removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    activity = "Chess Club"
    email = "doesnotexist@example.com"

    # Ensure participant is not present
    resp = client.get("/activities")
    data = resp.json()
    if email in data[activity]["participants"]:
        client.delete(f"/activities/{activity}/participants", params={"email": email})

    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404

