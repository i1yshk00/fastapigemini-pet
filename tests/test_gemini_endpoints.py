from unittest.mock import AsyncMock, patch


def test_send_prompt_requires_auth(client):
    response = client.post(
        "/gemini/requests",
        json={"prompt": "Hi Gemini!"},
    )
    assert response.status_code == 401


@patch("app.api.gemini.request_gemini", new_callable=AsyncMock)
def test_send_prompt_with_auth(mock_request, client, create_user, make_token):
    mock_request.return_value = "OK"

    user = create_user("user1@example.com", "StrongP@ssw0rd")
    token = make_token(user)

    response = client.post(
        "/gemini/requests",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "Hi Gemini!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "OK"
    assert data["prompt"] == "Hi Gemini!"
    assert data["request_id"]
    assert data["model_version"] == "gemini-3-flash-preview"

    mock_request.assert_awaited_once_with(
        prompt="Hi Gemini!",
        model_version="gemini-3-flash-preview",
    )


def test_get_my_requests_only_returns_own(
        client,
        create_user,
        create_gemini_request,
        make_token,
):
    user1 = create_user("user2@example.com", "StrongP@ssw0rd")
    user2 = create_user("user3@example.com", "StrongP@ssw0rd")

    create_gemini_request(user1.id, prompt="p1", response="r1")
    create_gemini_request(user2.id, prompt="p2", response="r2")

    token = make_token(user1)
    response = client.get(
        "/gemini/requests",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["prompt"] == "p1"
