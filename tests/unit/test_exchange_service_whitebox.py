from __future__ import annotations
"""
White-box unit tests for the external FX boundary (exchange_service).

Goal
----
Exercise decision/exception paths that depend on external API behavior:
- same-currency shortcut
- explicit_rate shortcut
- HTTP failures (requests exceptions)
- malformed JSON payloads
- non-numeric rates (Decimal parsing -> InvalidOperation)

Layer under test
----------------
Boundary adapter: "convert external API responses into a safe internal rate"
or raise ExchangeRateServiceError.

Why mocking is required here
----------------------------
Network calls are nondeterministic and outside our control. We stub requests.get
so tests are fast, stable, and CI-friendly.

Philosophy
----------
Classic boundary testing:
- Mock only the external dependency (requests)
- Assert observable outcomes (Decimal rate returned or ExchangeRateServiceError)
"""
from decimal import Decimal

import pytest
from flask import Flask
import requests

from app.domain.enums import Currency
from app.domain.exceptions import ExchangeRateServiceError
from app.services import exchange_service


def test_get_exchange_rate_returns_explicit_rate():
    # Arrange: explicit_rate shortcut
    # Act: request rate with explicit override
    result = exchange_service.get_exchange_rate(
        Currency.DKK,
        Currency.USD,
        explicit_rate=Decimal("9.99"),
    )

    # Assert: returns explicit rate without network
    assert result == Decimal("9.99")


def test_get_exchange_rate_same_currency_is_one():
    # Arrange: same-currency shortcut
    # Act: request rate for same currency
    result = exchange_service.get_exchange_rate(Currency.DKK, Currency.DKK)

    # Assert: returns 1.0 without network
    assert result == Decimal("1.0")


def test_get_exchange_rate_success_parses_decimal(monkeypatch):
    # Arrange: stub external response with numeric rate
    app = Flask(__name__)
    app.config["EXCHANGE_API_URL"] = "https://example.invalid"

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"rates": {"USD": 7.5}}

    monkeypatch.setattr(exchange_service.requests, "get", lambda *args, **kwargs: FakeResponse())

    with app.app_context():
        # Act: request rate (uses stubbed requests.get)
        rate = exchange_service.get_exchange_rate(Currency.DKK, Currency.USD)

    # Assert: parses into Decimal
    assert rate == Decimal("7.5")


def test_get_exchange_rate_bad_payload_raises(monkeypatch):
    # Arrange: stub external response with unexpected payload shape
    app = Flask(__name__)
    app.config["EXCHANGE_API_URL"] = "https://example.invalid"

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"unexpected": "shape"}

    monkeypatch.setattr(exchange_service.requests, "get", lambda *args, **kwargs: FakeResponse())

    with app.app_context():
        # Act + Assert: malformed payload is rejected
        with pytest.raises(ExchangeRateServiceError):
            exchange_service.get_exchange_rate(Currency.DKK, Currency.USD)


def test_get_exchange_rate_non_numeric_rate_raises(monkeypatch):
    # Arrange: stub external response with non-numeric rate
    app = Flask(__name__)
    app.config["EXCHANGE_API_URL"] = "https://example.invalid"

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"rates": {"USD": "not-a-number"}}

    monkeypatch.setattr(exchange_service.requests, "get", lambda *args, **kwargs: FakeResponse())

    with app.app_context():
        # Act + Assert: non-numeric rate is rejected
        with pytest.raises(ExchangeRateServiceError):
            exchange_service.get_exchange_rate(Currency.DKK, Currency.USD)


def test_get_exchange_rate_requests_error_raises(monkeypatch):
    # Arrange: requests.get fails
    app = Flask(__name__)
    app.config["EXCHANGE_API_URL"] = "https://example.invalid"

    def boom(*_args, **_kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr(exchange_service.requests, "get", boom)

    with app.app_context():
        # Act + Assert: request error is mapped to ExchangeRateServiceError
        with pytest.raises(ExchangeRateServiceError):
            exchange_service.get_exchange_rate(Currency.DKK, Currency.USD)
