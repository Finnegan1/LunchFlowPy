from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import httpx

from lunchflow._errors import LunchFlowAPIError
from lunchflow._models import JsonObject, JsonValue


class BaseClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> BaseClient:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path_or_url: str,
        *,
        headers: Mapping[str, str] | None = None,
        auth: httpx.Auth | None = None,
        json: Mapping[str, JsonValue] | None = None,
        params: Mapping[str, str] | None = None,
    ) -> JsonObject:
        request_path = path_or_url if path_or_url.startswith("http") else path_or_url.lstrip("/")
        response = self._client.request(
            method,
            request_path,
            headers=headers,
            auth=auth,
            json=json,
            params=params,
        )

        if response.status_code == 204:
            return {}

        if response.status_code < 200 or response.status_code >= 300:
            raise self._api_error(response)

        return _json_object(response)

    @staticmethod
    def _api_error(response: httpx.Response) -> LunchFlowAPIError:
        error: str | None = None
        message: str | None = None

        try:
            body = _json_object(response)
        except ValueError:
            body = {}

        raw_error = body.get("error")
        raw_message = body.get("message")
        if isinstance(raw_error, str):
            error = raw_error
        if isinstance(raw_message, str):
            message = raw_message

        return LunchFlowAPIError(
            status_code=response.status_code,
            error=error,
            message=message,
            response=response,
        )


def _json_object(response: httpx.Response) -> JsonObject:
    value = cast(Any, response.json())
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object response")
    return cast(JsonObject, value)
