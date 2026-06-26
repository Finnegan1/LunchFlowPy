from __future__ import annotations

from datetime import date

import httpx
import pytest

from lunchflow import LunchFlowAPIError, LunchFlowClient


def test_list_accounts_sends_api_key_and_returns_typed_accounts() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(
            200,
            json={
                "accounts": [
                    {
                        "id": 123,
                        "name": "Checking",
                        "institution_name": "Demo Bank",
                        "institution_logo": "https://example.com/logo.png",
                        "provider": "gocardless",
                        "currency": "EUR",
                        "status": "ACTIVE",
                    }
                ],
                "total": 1,
            },
        )

    client = LunchFlowClient(
        api_key="test-key",
        base_url="https://api.test/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_accounts()

    assert seen_request is not None
    assert seen_request.method == "GET"
    assert str(seen_request.url) == "https://api.test/v1/accounts"
    assert seen_request.headers["x-api-key"] == "test-key"
    assert response.total == 1
    assert response.accounts[0].id == 123
    assert response.accounts[0].name == "Checking"


def test_default_base_url_uses_canonical_www_host() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(200, json={"accounts": [], "total": 0})

    client = LunchFlowClient(
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    )

    client.list_accounts()

    assert seen_request is not None
    assert str(seen_request.url) == "https://www.lunchflow.app/api/v1/accounts"


def test_list_accounts_allows_missing_currency() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "accounts": [
                    {
                        "id": 123,
                        "name": "Checking",
                        "institution_name": "Demo Bank",
                        "institution_logo": "https://example.com/logo.png",
                        "provider": "gocardless",
                        "status": "ACTIVE",
                    }
                ],
                "total": 1,
            },
        )

    client = LunchFlowClient(
        api_key="test-key",
        base_url="https://api.test/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_accounts()

    assert response.accounts[0].currency is None
    assert "currency" not in response.accounts[0].raw


def test_get_transactions_serializes_filters_and_parses_dates() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(
            200,
            json={
                "transactions": [
                    {
                        "id": "txn_1",
                        "accountId": 123,
                        "amount": -12.5,
                        "currency": "EUR",
                        "date": "2026-06-26",
                        "merchant": "Cafe",
                        "description": "Lunch",
                        "isPending": False,
                    }
                ],
                "total": 1,
            },
        )

    client = LunchFlowClient(
        api_key="test-key",
        base_url="https://api.test/v1/",
        transport=httpx.MockTransport(handler),
    )

    response = client.get_transactions(
        "123",
        include_pending=True,
        from_date=date(2026, 6, 1),
        to_date="2026-06-30",
    )

    assert seen_request is not None
    assert str(seen_request.url) == (
        "https://api.test/v1/accounts/123/transactions?"
        "include_pending=true&from=2026-06-01&to=2026-06-30"
    )
    assert response.total == 1
    assert response.transactions[0].date == date(2026, 6, 26)
    assert response.transactions[0].is_pending is False


def test_non_success_response_raises_api_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            json={"error": "Forbidden", "message": "Invalid API key"},
            request=request,
        )

    client = LunchFlowClient(
        api_key="bad-key",
        base_url="https://api.test/v1",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(LunchFlowAPIError) as exc_info:
        client.list_accounts()

    assert exc_info.value.status_code == 403
    assert exc_info.value.error == "Forbidden"
    assert exc_info.value.message == "Invalid API key"
