from __future__ import annotations

import httpx


class LunchFlowError(Exception):
    """Base exception raised by the Lunch Flow SDK."""


class LunchFlowAPIError(LunchFlowError):
    """Raised when the Lunch Flow API returns a non-success response."""

    def __init__(
        self,
        *,
        status_code: int,
        error: str | None = None,
        message: str | None = None,
        response: httpx.Response | None = None,
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.message = message
        self.response = response
        detail = message or error or "Lunch Flow API request failed"
        super().__init__(f"{status_code}: {detail}")
