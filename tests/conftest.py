# tests/conftest.py

from datetime import datetime
from decimal import Decimal
from typing import Callable, Optional

import pytest

from app.domain.models.Wallet import Wallet
from app.domain.enums import Currency, WalletStatus


@pytest.fixture
def get_fixed_timestamp() -> datetime:
    """
    Shared fixed datetime so tests are deterministic when asserting
    on created_at/updated_at.

    Value: 2025-01-01 12:00:00 (YYYY-MM-DD HH:MM:SS)
    """
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def wallet_factory(get_fixed_timestamp: datetime) -> Callable[..., Wallet]:
    """
    Factory fixture for creating Wallet test instances.

    Example usage:
        wallet = wallet_factory(
            balance=Decimal("100.00"),
            currency=Currency.DKK,
            status=WalletStatus.ACTIVE,
        )
    """
    def _create(
        *, # Enforce keyword arguments
        wallet_id: str = "wallet-1",
        balance: Decimal = Decimal("100.00"),
        currency: Currency = Currency.DKK,
        status: WalletStatus = WalletStatus.ACTIVE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> Wallet:
        created = created_at or get_fixed_timestamp
        updated = updated_at or created

        return Wallet(
            id=wallet_id,
            currency=currency,
            balance=balance,
            status=status,
            created_at=created,
            updated_at=updated,
        )

    return _create
