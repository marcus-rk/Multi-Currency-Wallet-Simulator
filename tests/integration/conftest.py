from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from app import create_app
from app.domain.exceptions import ExchangeRateServiceError


@pytest.fixture
def app_instance(tmp_path: Path):
    """Create a fresh Flask app + SQLite DB per test.

    WHY:
    - Isolation: each test gets its own DB file.
    - Stability: schema is initialized eagerly so tests don't depend on request order.
    """
    db_path = tmp_path / "test_wallet.db"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(db_path),
        }
    )

    # Defensive: ensure schema exists even if app init changes later.
    with app.app_context():
        from app.database import init_schema

        init_schema()

    yield app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


@pytest.fixture
def fx_rate_stub(monkeypatch):
    """Deterministic FX stub.

    WHY:
    - Integration tests should not hit the network.
    - Patch target is wallet_service's imported symbol.
    """
    def _stubbed_get_exchange_rate(source_currency, target_currency, explicit_rate=None):
        # Match the real signature: get_exchange_rate(source, target, explicit_rate=None)
        if explicit_rate is not None:
            return explicit_rate
        return Decimal("2.00")

    monkeypatch.setattr(
        "app.services.wallet_service.get_exchange_rate",
        _stubbed_get_exchange_rate,
    )


@pytest.fixture
def fx_rate_fail_stub(monkeypatch):
    """FX stub that simulates an upstream outage (useful for 502 assertions)."""

    def _fail(source_currency, target_currency, explicit_rate=None):
        raise ExchangeRateServiceError("FX service down")

    monkeypatch.setattr("app.services.wallet_service.get_exchange_rate", _fail)
