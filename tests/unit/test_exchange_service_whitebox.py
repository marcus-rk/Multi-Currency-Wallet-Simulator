from __future__ import annotations

from decimal import Decimal

import pytest
from flask import Flask
import requests

from app.domain.enums import Currency
from app.domain.exceptions import ExchangeRateServiceError
from app.services import exchange_service


def test_get_exchange_rate_returns_explicit_rate():
    assert exchange_service.get_exchange_rate(
        Currency.DKK,
        Currency.USD,
        explicit_rate=Decimal("9.99"),
    ) == Decimal("9.99")


def test_get_exchange_rate_same_currency_is_one():
    assert exchange_service.get_exchange_rate(Currency.DKK, Currency.DKK) == Decimal("1.0")


def test_get_exchange_rate_success_parses_decimal(monkeypatch):
    app = Flask(__name__)
    app.config["EXCHANGE_API_URL"] = "https://example.invalid"

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"rates": {"USD": 7.5}}

    monkeypatch.setattr(exchange_service.requests, "get", lambda *args, **kwargs: FakeResponse())

    with app.app_context():
        rate = exchange_service.get_exchange_rate(Currency.DKK, Currency.USD)

    assert rate == Decimal("7.5")


def test_get_exchange_rate_bad_payload_raises(monkeypatch):
    app = Flask(__name__)
    app.config["EXCHANGE_API_URL"] = "https://example.invalid"

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"unexpected": "shape"}

    monkeypatch.setattr(exchange_service.requests, "get", lambda *args, **kwargs: FakeResponse())

    with app.app_context():
        with pytest.raises(ExchangeRateServiceError):
            exchange_service.get_exchange_rate(Currency.DKK, Currency.USD)


def test_get_exchange_rate_non_numeric_rate_raises(monkeypatch):
    app = Flask(__name__)
    app.config["EXCHANGE_API_URL"] = "https://example.invalid"

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"rates": {"USD": "not-a-number"}}

    monkeypatch.setattr(exchange_service.requests, "get", lambda *args, **kwargs: FakeResponse())

    with app.app_context():
        with pytest.raises(ExchangeRateServiceError):
            exchange_service.get_exchange_rate(Currency.DKK, Currency.USD)


def test_get_exchange_rate_requests_error_raises(monkeypatch):
    app = Flask(__name__)
    app.config["EXCHANGE_API_URL"] = "https://example.invalid"

    def boom(*_args, **_kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr(exchange_service.requests, "get", boom)

    with app.app_context():
        with pytest.raises(ExchangeRateServiceError):
            exchange_service.get_exchange_rate(Currency.DKK, Currency.USD)
