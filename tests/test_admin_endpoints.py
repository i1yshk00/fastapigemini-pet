def test_admin_requires_admin_role(client, create_user, make_token):
    user = create_user("user@example.com", "StrongP@ssw0rd", is_admin=False)
    token = make_token(user)

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_admin_can_list_users(client, create_user, make_token):
    admin = create_user("admin@example.com", "StrongP@ssw0rd", is_admin=True)
    create_user("u1@example.com", "StrongP@ssw0rd")
    token = make_token(admin)

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_admin_update_user_access(client, create_user, make_token):
    admin = create_user("admin2@example.com", "StrongP@ssw0rd", is_admin=True)
    user = create_user("target@example.com", "StrongP@ssw0rd", is_admin=False)
    token = make_token(admin)

    response = client.patch(
        f"/admin/users/{user.id}/access",
        headers={"Authorization": f"Bearer {token}"},
        json={"is_admin": True, "is_active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_admin"] is True
    assert data["is_active"] is False


def test_admin_can_list_all_gemini_requests(
        client,
        create_user,
        create_gemini_request,
        make_token,
):
    admin = create_user("admin3@example.com", "StrongP@ssw0rd", is_admin=True)
    user = create_user("requser@example.com", "StrongP@ssw0rd")
    create_gemini_request(user.id, prompt="p1", response="r1")
    token = make_token(admin)

    response = client.get(
        "/admin/gemini/requests",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["prompt"] == "p1"
