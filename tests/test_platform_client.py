from __future__ import annotations

from base64 import b64encode

import httpx

from lunchflow import LunchFlowPlatformClient


def test_register_user_uses_basic_auth_and_returns_tokens() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(
            200,
            json={
                "user_id": "user_123",
                "external_user_id": "ext_123",
                "access_token": "access",
                "refresh_token": "refresh",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

    client = LunchFlowPlatformClient(
        client_id="client-id",
        client_secret="client-secret",
        base_url="https://platform.test/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.register_user(
        email="user@example.com",
        external_user_id="ext_123",
        limits={"us_ca_connections_limit": 2},
    )

    expected_auth = "Basic " + b64encode(b"client-id:client-secret").decode()
    assert seen_request is not None
    assert seen_request.method == "POST"
    assert str(seen_request.url) == "https://platform.test/v1/users"
    assert seen_request.headers["authorization"] == expected_auth
    assert seen_request.read() == (
        b'{"email":"user@example.com","external_user_id":"ext_123",'
        b'"limits":{"us_ca_connections_limit":2}}'
    )
    assert response.user_id == "user_123"
    assert response.access_token == "access"


def test_authorization_url_builds_oauth_redirect_url() -> None:
    client = LunchFlowPlatformClient(
        client_id="client-id",
        client_secret="client-secret",
        base_url="https://platform.test/v1",
        oauth_base_url="https://platform.test/oauth",
        transport=httpx.MockTransport(lambda request: httpx.Response(500)),
    )

    url = client.authorization_url(
        redirect_uri="https://app.example/callback",
        state="opaque-state",
        email="user@example.com",
    )

    assert url == (
        "https://platform.test/oauth/authorize?client_id=client-id&"
        "redirect_uri=https%3A%2F%2Fapp.example%2Fcallback&"
        "state=opaque-state&email=user%40example.com"
    )


def test_platform_data_methods_use_bearer_token() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(200, json={"accounts": [], "total": 0})

    client = LunchFlowPlatformClient(
        access_token="access-token",
        base_url="https://platform.test/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_accounts()

    assert seen_request is not None
    assert str(seen_request.url) == "https://platform.test/v1/accounts"
    assert seen_request.headers["authorization"] == "Bearer access-token"
    assert response.accounts == []
    assert response.total == 0


def test_exchange_code_posts_to_oauth_token_endpoint() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(
            200,
            json={
                "access_token": "new-access",
                "refresh_token": "new-refresh",
                "token_type": "Bearer",
                "expires_in": 3600,
                "user_id": "user_123",
            },
        )

    client = LunchFlowPlatformClient(
        client_id="client-id",
        client_secret="client-secret",
        base_url="https://platform.test/v1",
        oauth_base_url="https://platform.test/oauth",
        transport=httpx.MockTransport(handler),
    )

    response = client.exchange_code(
        code="code-123",
        redirect_uri="https://app.example/callback",
    )

    assert seen_request is not None
    assert str(seen_request.url) == "https://platform.test/oauth/token"
    assert seen_request.read() == (
        b'{"grant_type":"authorization_code","client_id":"client-id",'
        b'"client_secret":"client-secret","code":"code-123",'
        b'"redirect_uri":"https://app.example/callback"}'
    )
    assert response.access_token == "new-access"
    assert response.user_id == "user_123"
