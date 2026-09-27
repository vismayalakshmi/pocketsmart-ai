import os

os.environ["DEMO_MODE"] = "true"
os.environ["DATABASE_PATH"] = "test_pocketsmart.db"
os.environ["SESSION_SECRET"] = "test-secret"


from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app


init_db()


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert (
        data["app"]
        == "PocketSmart AI"
    )


def test_register_login_and_home_plan():

    username = "testuser123"

    response = client.post(
        "/register",
        data={
            "username": username,
            "email":
                "testuser123@example.com",
            "password": "password123",
        },
        follow_redirects=False,
    )

    assert response.status_code in (
        303,
        400,
    )


    response = client.post(
        "/login",
        data={
            "username": username,
            "password": "password123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303


    response = client.post(
        "/api/home-planner",
        json={
            "budget": 50000,
            "lights": 4,
            "fans": 2,
            "furniture": 3,
            "rooms": [
                "Living room"
            ],
            "preferences":
                "Modern",
        },
    )


    assert response.status_code == 200


    data = response.json()


    assert (
        data["total_budget"]
        == 50000
    )


    assert (
        "categories"
        in data
    )


def test_unauthorized_api():

    test_client = TestClient(app)

    response = test_client.post(
        "/api/party-planner",
        json={
            "budget": 10000,
            "guests": 10,
        },
    )

    assert response.status_code == 401