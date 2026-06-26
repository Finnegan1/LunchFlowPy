from __future__ import annotations

from datetime import date

import httpx

from lunchflow._base import BaseClient
from lunchflow._models import (
    AccountsResponse,
    BalanceResponse,
    HoldingsResponse,
    TransactionsResponse,
)


class LunchFlowClient(BaseClient):
    """Client for the Lunch Flow Personal API."""

    DEFAULT_BASE_URL = "https://www.lunchflow.app/api/v1"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        super().__init__(base_url=base_url, timeout=timeout, transport=transport)
        self._api_key = api_key

    def list_accounts(self) -> AccountsResponse:
        data = self._request("GET", "accounts", headers=self._headers())
        return AccountsResponse.from_dict(data)

    def get_transactions(
        self,
        account_id: str | int,
        *,
        include_pending: bool = False,
        from_date: date | str | None = None,
        to_date: date | str | None = None,
    ) -> TransactionsResponse:
        data = self._request(
            "GET",
            f"accounts/{account_id}/transactions",
            headers=self._headers(),
            params=_transaction_params(
                include_pending=include_pending,
                from_date=from_date,
                to_date=to_date,
            ),
        )
        return TransactionsResponse.from_dict(data)

    def get_balance(self, account_id: str | int) -> BalanceResponse:
        data = self._request(
            "GET",
            f"accounts/{account_id}/balance",
            headers=self._headers(),
        )
        return BalanceResponse.from_dict(data)

    def get_holdings(self, account_id: str | int) -> HoldingsResponse:
        data = self._request(
            "GET",
            f"accounts/{account_id}/holdings",
            headers=self._headers(),
        )
        return HoldingsResponse.from_dict(data)

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self._api_key}


def _transaction_params(
    *,
    include_pending: bool,
    from_date: date | str | None,
    to_date: date | str | None,
) -> dict[str, str]:
    params: dict[str, str] = {}
    if include_pending:
        params["include_pending"] = "true"
    if from_date is not None:
        params["from"] = _date_param(from_date)
    if to_date is not None:
        params["to"] = _date_param(to_date)
    return params


def _date_param(value: date | str) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return value
