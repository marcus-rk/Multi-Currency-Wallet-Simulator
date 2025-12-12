from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from app.domain.enums import Currency, TransactionErrorCode, TransactionStatus, TransactionType
from app.domain.rules.apply_exchange import apply_exchange


def test_apply_exchange_fails_on_self_exchange(wallet_factory):
    now = datetime(2025, 1, 1, 12, 0, 0)
    wallet = wallet_factory(wallet_id="wallet-1", balance=Decimal("100.00"), currency=Currency.DKK)

    updated_source, updated_target, tx = apply_exchange(
        source_wallet=wallet,
        target_wallet=wallet,
        amount=Decimal("10.00"),
        fx_rate=Decimal("2.0"),
        transaction_id="tx-1",
        now=now,
    )

    assert updated_source is wallet
    assert updated_target is wallet

    assert tx.type == TransactionType.EXCHANGE
    assert tx.status == TransactionStatus.FAILED
    assert tx.error_code == TransactionErrorCode.INVALID_WALLET_STATE
    assert tx.credited_amount is None
    assert tx.credited_currency is None
    assert tx.source_balance_after is None
    assert tx.target_balance_after is None


def test_apply_exchange_fails_on_same_currency(wallet_factory):
    now = datetime(2025, 1, 1, 12, 0, 0)
    source = wallet_factory(wallet_id="source", balance=Decimal("100.00"), currency=Currency.DKK)
    target = wallet_factory(wallet_id="target", balance=Decimal("0.00"), currency=Currency.DKK)

    updated_source, updated_target, tx = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=Decimal("10.00"),
        fx_rate=Decimal("1.0"),
        transaction_id="tx-2",
        now=now,
    )

    assert updated_source is source
    assert updated_target is target

    assert tx.status == TransactionStatus.FAILED
    assert tx.error_code == TransactionErrorCode.UNSUPPORTED_CURRENCY


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1")])
def test_apply_exchange_fails_on_non_positive_amount(wallet_factory, amount: Decimal):
    now = datetime(2025, 1, 1, 12, 0, 0)
    source = wallet_factory(wallet_id="source", balance=Decimal("100.00"), currency=Currency.DKK)
    target = wallet_factory(wallet_id="target", balance=Decimal("0.00"), currency=Currency.USD)

    updated_source, updated_target, tx = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=amount,
        fx_rate=Decimal("2.0"),
        transaction_id="tx-3",
        now=now,
    )

    assert updated_source is source
    assert updated_target is target

    assert tx.status == TransactionStatus.FAILED
    assert tx.error_code == TransactionErrorCode.INVALID_AMOUNT


def test_apply_exchange_fails_on_missing_fx_rate(wallet_factory):
    now = datetime(2025, 1, 1, 12, 0, 0)
    source = wallet_factory(wallet_id="source", balance=Decimal("100.00"), currency=Currency.DKK)
    target = wallet_factory(wallet_id="target", balance=Decimal("0.00"), currency=Currency.USD)

    updated_source, updated_target, tx = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=Decimal("10.00"),
        fx_rate=None,
        transaction_id="tx-4",
        now=now,
    )

    assert updated_source is source
    assert updated_target is target

    assert tx.status == TransactionStatus.FAILED
    assert tx.error_code == TransactionErrorCode.EXCHANGE_RATE_UNAVAILABLE
