# LunchFlowPy

Typed Python SDK for the [Lunch Flow API](https://www.lunchflow.app/docs/what-is-lunch-flow).

## Installation

This project uses `uv` for development:

```bash
uv sync --dev
```

After publishing, install with:

```bash
pip install lunchflowpy
```

## Personal API

```python
from lunchflow import LunchFlowClient

client = LunchFlowClient(api_key="YOUR_API_KEY")

accounts = client.list_accounts()
for account in accounts.accounts:
    print(account.id, account.name, account.currency)

transactions = client.get_transactions(
    accounts.accounts[0].id,
    include_pending=True,
    from_date="2026-01-01",
    to_date="2026-01-31",
)
```

## Platform API

```python
from lunchflow import LunchFlowPlatformClient

platform = LunchFlowPlatformClient(
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET",
)

tokens = platform.register_user(email="user@example.com")
user_client = LunchFlowPlatformClient(access_token=tokens.access_token)

accounts = user_client.list_accounts()
```

Build an OAuth authorization URL:

```python
url = platform.authorization_url(
    redirect_uri="https://yourapp.example/callback",
    state="opaque-random-state",
    email="user@example.com",
)
```

## Error Handling

```python
from lunchflow import LunchFlowAPIError, LunchFlowClient

client = LunchFlowClient(api_key="YOUR_API_KEY")

try:
    client.list_accounts()
except LunchFlowAPIError as exc:
    print(exc.status_code, exc.error, exc.message)
```

## Development

```bash
uv run pytest -q
uv run mypy
uv run ruff check .
uv build
```
