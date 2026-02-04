def test_register_and_login(client):
    response = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "StrongP@ssw0rd"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

    login = client.post(
        "/auth/login",
        data={"username": "newuser@example.com", "password": "StrongP@ssw0rd"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token_data = login.json()
    assert token_data["access_token"]
    assert token_data["token_type"] == "bearer"
    assert token_data["expires_in"] > 0


def test_login_invalid_password(client, create_user):
    create_user("badpass@example.com", "StrongP@ssw0rd")
    response = client.post(
        "/auth/login",
        data={"username": "badpass@example.com", "password": "WrongPassword1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
