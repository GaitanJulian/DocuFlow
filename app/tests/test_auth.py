import uuid


def test_register_and_login(client):
    # Unique email to avoid conflicts with previous data
    email = f"test_{uuid.uuid4().hex}@example.com"

    # 1. Register a user
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strongpassword",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email

    # 2. Login
    response = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": "strongpassword",
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token
