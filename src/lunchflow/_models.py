from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import TypeAlias

JsonValue: TypeAlias = (
    str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
)
JsonObject: TypeAlias = dict[str, JsonValue]
AccountId: TypeAlias = str | int


@dataclass(frozen=True, slots=True)
class Account:
    id: AccountId
    name: str
    institution_name: str
    institution_logo: str | None
    provider: str
    currency: str
    status: str
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> Account:
        return cls(
            id=_id(data, "id"),
            name=_str(data, "name"),
            institution_name=_str(data, "institution_name"),
            institution_logo=_optional_str(data, "institution_logo"),
            provider=_str(data, "provider"),
            currency=_str(data, "currency"),
            status=_str(data, "status"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class AccountsResponse:
    accounts: list[Account]
    total: int
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> AccountsResponse:
        accounts = _object_list(data, "accounts")
        return cls(
            accounts=[Account.from_dict(account) for account in accounts],
            total=_int(data, "total"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class Transaction:
    id: str
    account_id: AccountId
    amount: float
    currency: str
    date: date
    merchant: str | None
    description: str | None
    is_pending: bool
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> Transaction:
        return cls(
            id=_str(data, "id"),
            account_id=_id(data, "accountId"),
            amount=_float(data, "amount"),
            currency=_str(data, "currency"),
            date=_date(data, "date"),
            merchant=_optional_str(data, "merchant"),
            description=_optional_str(data, "description"),
            is_pending=_bool(data, "isPending"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class TransactionsResponse:
    transactions: list[Transaction]
    total: int
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> TransactionsResponse:
        transactions = _object_list(data, "transactions")
        return cls(
            transactions=[Transaction.from_dict(transaction) for transaction in transactions],
            total=_int(data, "total"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class Balance:
    amount: float
    currency: str
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> Balance:
        return cls(amount=_float(data, "amount"), currency=_str(data, "currency"), raw=dict(data))


@dataclass(frozen=True, slots=True)
class BalanceResponse:
    balance: Balance
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> BalanceResponse:
        return cls(balance=Balance.from_dict(_object(data, "balance")), raw=dict(data))


@dataclass(frozen=True, slots=True)
class Security:
    name: str | None
    currency: str | None
    ticker_symbol: str | None
    figi: str | None
    cusip: str | None
    isin: str | None
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> Security:
        return cls(
            name=_optional_str(data, "name"),
            currency=_optional_str(data, "currency"),
            ticker_symbol=_optional_str(data, "tickerSymbol"),
            figi=_optional_str(data, "figi"),
            cusip=_optional_str(data, "cusp"),
            isin=_optional_str(data, "isin"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class Holding:
    security: Security
    quantity: float
    price: float
    value: float
    cost_basis: float | None
    currency: str
    raw_provider_data: JsonObject
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> Holding:
        return cls(
            security=Security.from_dict(_object(data, "security")),
            quantity=_float(data, "quantity"),
            price=_float(data, "price"),
            value=_float(data, "value"),
            cost_basis=_optional_float(data, "costBasis"),
            currency=_str(data, "currency"),
            raw_provider_data=_optional_object(data, "raw"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class HoldingsResponse:
    holdings: list[Holding]
    total_value: float
    currency: str
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> HoldingsResponse:
        holdings = _object_list(data, "holdings")
        return cls(
            holdings=[Holding.from_dict(holding) for holding in holdings],
            total_value=_float(data, "totalValue"),
            currency=_str(data, "currency"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class TokenResponse:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_id: str | None
    external_user_id: str | None
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> TokenResponse:
        return cls(
            access_token=_str(data, "access_token"),
            refresh_token=_str(data, "refresh_token"),
            token_type=_str(data, "token_type"),
            expires_in=_int(data, "expires_in"),
            user_id=_optional_str(data, "user_id"),
            external_user_id=_optional_str(data, "external_user_id"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class User:
    user_id: str
    external_user_id: str | None
    email: str
    limits: JsonObject
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> User:
        return cls(
            user_id=_str(data, "user_id"),
            external_user_id=_optional_str(data, "external_user_id"),
            email=_str(data, "email"),
            limits=_optional_object(data, "limits"),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True)
class UserResponse:
    user: User
    raw: JsonObject

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> UserResponse:
        return cls(user=User.from_dict(_object(data, "user")), raw=dict(data))


def _str(data: Mapping[str, JsonValue], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"Expected '{key}' to be a string")
    return value


def _optional_str(data: Mapping[str, JsonValue], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Expected '{key}' to be a string or null")
    return value


def _id(data: Mapping[str, JsonValue], key: str) -> AccountId:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, str | int):
        raise ValueError(f"Expected '{key}' to be a string or integer")
    return value


def _int(data: Mapping[str, JsonValue], key: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Expected '{key}' to be an integer")
    return value


def _float(data: Mapping[str, JsonValue], key: str) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"Expected '{key}' to be a number")
    return float(value)


def _optional_float(data: Mapping[str, JsonValue], key: str) -> float | None:
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"Expected '{key}' to be a number or null")
    return float(value)


def _bool(data: Mapping[str, JsonValue], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"Expected '{key}' to be a boolean")
    return value


def _date(data: Mapping[str, JsonValue], key: str) -> date:
    return date.fromisoformat(_str(data, key))


def _object(data: Mapping[str, JsonValue], key: str) -> JsonObject:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Expected '{key}' to be an object")
    return value


def _optional_object(data: Mapping[str, JsonValue], key: str) -> JsonObject:
    value = data.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected '{key}' to be an object or null")
    return value


def _object_list(data: Mapping[str, JsonValue], key: str) -> list[JsonObject]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"Expected '{key}' to be a list")

    objects: list[JsonObject] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"Expected every item in '{key}' to be an object")
        objects.append(item)
    return objects
