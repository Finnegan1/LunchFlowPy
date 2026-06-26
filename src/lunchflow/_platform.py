from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from urllib.parse import urlencode

import httpx

from lunchflow._base import BaseClient
from lunchflow._client import _transaction_params
from lunchflow._models import (
    AccountsResponse,
    BalanceResponse,
    HoldingsResponse,
    JsonObject,
    JsonValue,
    TokenResponse,
    TransactionsResponse,
    UserResponse,
)


class LunchFlowPlatformClient(BaseClient):
    """Client for the Lunch Flow Platform API."""

    DEFAULT_BASE_URL = "https://lunchflow.app/api/platform/v1"
    DEFAULT_OAUTH_BASE_URL = "https://lunchflow.app/api/platform/oauth"

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        oauth_base_url: str = DEFAULT_OAUTH_BASE_URL,
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        super().__init__(base_url=base_url, timeout=timeout, transport=transport)
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token
        self._oauth_base_url = oauth_base_url.rstrip("/")

    def register_user(
        self,
        *,
        email: str,
        external_user_id: str | None = None,
        limits: Mapping[str, JsonValue] | None = None,
    ) -> TokenResponse:
        body: JsonObject = {"email": email}
        if external_user_id is not None:
            body["external_user_id"] = external_user_id
        if limits is not None:
            body["limits"] = dict(limits)

        data = self._request("POST", "users", auth=self._basic_auth(), json=body)
        return TokenResponse.from_dict(data)

    def update_user(self, user_id: str, *, limits: Mapping[str, JsonValue]) -> UserResponse:
        data = self._request(
            "PUT",
            f"users/{user_id}",
            auth=self._basic_auth(),
            json={"limits": dict(limits)},
        )
        return UserResponse.from_dict(data)

    def delete_user(self, user_id: str) -> None:
        self._request("DELETE", f"users/{user_id}", auth=self._basic_auth())

    def authorization_url(
        self,
        *,
        redirect_uri: str,
        state: str | None = None,
        email: str | None = None,
        client_id: str | None = None,
    ) -> str:
        query: dict[str, str] = {
            "client_id": client_id or self._require_client_id(),
            "redirect_uri": redirect_uri,
        }
        if state is not None:
            query["state"] = state
        if email is not None:
            query["email"] = email
        return f"{self._oauth_base_url}/authorize?{urlencode(query)}"

    def exchange_code(
        self,
        *,
        code: str,
        redirect_uri: str,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> TokenResponse:
        body: JsonObject = {
            "grant_type": "authorization_code",
            "client_id": client_id or self._require_client_id(),
        }
        secret = client_secret if client_secret is not None else self._client_secret
        if secret is not None:
            body["client_secret"] = secret
        body["code"] = code
        body["redirect_uri"] = redirect_uri

        data = self._request("POST", f"{self._oauth_base_url}/token", json=body)
        return TokenResponse.from_dict(data)

    def refresh_access_token(
        self,
        refresh_token: str,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> TokenResponse:
        body: JsonObject = {
            "grant_type": "refresh_token",
            "client_id": client_id or self._require_client_id(),
        }
        secret = client_secret if client_secret is not None else self._client_secret
        if secret is not None:
            body["client_secret"] = secret
        body["refresh_token"] = refresh_token

        data = self._request("POST", f"{self._oauth_base_url}/token", json=body)
        return TokenResponse.from_dict(data)

    def list_accounts(self, *, access_token: str | None = None) -> AccountsResponse:
        data = self._request("GET", "accounts", headers=self._bearer_headers(access_token))
        return AccountsResponse.from_dict(data)

    def get_transactions(
        self,
        account_id: str | int,
        *,
        include_pending: bool = False,
        from_date: date | str | None = None,
        to_date: date | str | None = None,
        access_token: str | None = None,
    ) -> TransactionsResponse:
        data = self._request(
            "GET",
            f"accounts/{account_id}/transactions",
            headers=self._bearer_headers(access_token),
            params=_transaction_params(
                include_pending=include_pending,
                from_date=from_date,
                to_date=to_date,
            ),
        )
        return TransactionsResponse.from_dict(data)

    def get_balance(
        self,
        account_id: str | int,
        *,
        access_token: str | None = None,
    ) -> BalanceResponse:
        data = self._request(
            "GET",
            f"accounts/{account_id}/balance",
            headers=self._bearer_headers(access_token),
        )
        return BalanceResponse.from_dict(data)

    def get_holdings(
        self,
        account_id: str | int,
        *,
        access_token: str | None = None,
    ) -> HoldingsResponse:
        data = self._request(
            "GET",
            f"accounts/{account_id}/holdings",
            headers=self._bearer_headers(access_token),
        )
        return HoldingsResponse.from_dict(data)

    def _basic_auth(self) -> httpx.BasicAuth:
        if self._client_id is None or self._client_secret is None:
            raise ValueError("client_id and client_secret are required for this request")
        return httpx.BasicAuth(self._client_id, self._client_secret)

    def _bearer_headers(self, access_token: str | None) -> dict[str, str]:
        token = access_token or self._access_token
        if token is None:
            raise ValueError("access_token is required for this request")
        return {"Authorization": f"Bearer {token}"}

    def _require_client_id(self) -> str:
        if self._client_id is None:
            raise ValueError("client_id is required for this request")
        return self._client_id
