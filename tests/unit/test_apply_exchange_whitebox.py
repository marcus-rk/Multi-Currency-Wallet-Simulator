from __future__ import annotations
"""
White-box unit tests for the exchange domain rule (apply_exchange).

Goal
----
Improve statement + decision coverage by exercising edge-case branches such as:
- non-positive amount
- self-exchange (same wallet id)
- missing FX rate / invalid inputs
- same-currency scenarios (if applicable)

Layer under test
----------------
Pure domain logic: no DB, no HTTP, no Flask.
Tests assert on returned wallet state and transaction status/error_code.

Philosophy
----------
Classicist:
- No mocks needed (pure function)
- Focus on state changes + transaction outcome
"""
from datetime import datetime
from decimal import Decimal

import pytest

from app.domain.enums import Currency, TransactionErrorCode, TransactionStatus, TransactionType
from app.domain.rules.apply_exchange import apply_exchange


def test_apply_exchange_fails_on_self_exchange(wallet_factory):
    # Arrange: source and target are the same wallet (invalid)
    now = datetime(2025, 1, 1, 12, 0, 0)
    wallet = wallet_factory(wallet_id="wallet-1", balance=Decimal("100.00"), currency=Currency.DKK)

    # Act: attempt exchange into same wallet
    updated_source, updated_target, tx = apply_exchange(
        source_wallet=wallet,
        target_wallet=wallet,
        amount=Decimal("10.00"),
        fx_rate=Decimal("2.0"),
        transaction_id="tx-1",
        now=now,
    )

    # Assert: wallets unchanged and transaction fails with correct error
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
    # Arrange: source and target currencies are the same (unsupported)
    now = datetime(2025, 1, 1, 12, 0, 0)
    source = wallet_factory(wallet_id="source", balance=Decimal("100.00"), currency=Currency.DKK)
    target = wallet_factory(wallet_id="target", balance=Decimal("0.00"), currency=Currency.DKK)

    # Act: attempt exchange between same currencies
    updated_source, updated_target, tx = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=Decimal("10.00"),
        fx_rate=Decimal("1.0"),
        transaction_id="tx-2",
        now=now,
    )

    # Assert: wallets unchanged and transaction fails with correct error
    assert updated_source is source
    assert updated_target is target

    assert tx.status == TransactionStatus.FAILED
    assert tx.error_code == TransactionErrorCode.UNSUPPORTED_CURRENCY


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1")])
def test_apply_exchange_fails_on_non_positive_amount(wallet_factory, amount: Decimal):
    # Arrange: non-positive amount (invalid)
    now = datetime(2025, 1, 1, 12, 0, 0)
    source = wallet_factory(wallet_id="source", balance=Decimal("100.00"), currency=Currency.DKK)
    target = wallet_factory(wallet_id="target", balance=Decimal("0.00"), currency=Currency.USD)

    # Act: attempt exchange with invalid amount
    updated_source, updated_target, tx = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=amount,
        fx_rate=Decimal("2.0"),
        transaction_id="tx-3",
        now=now,
    )

    # Assert: wallets unchanged and transaction fails with correct error
    assert updated_source is source
    assert updated_target is target

    assert tx.status == TransactionStatus.FAILED
    assert tx.error_code == TransactionErrorCode.INVALID_AMOUNT


def test_apply_exchange_fails_on_missing_fx_rate(wallet_factory):
    # Arrange: FX rate is missing (unavailable)
    now = datetime(2025, 1, 1, 12, 0, 0)
    source = wallet_factory(wallet_id="source", balance=Decimal("100.00"), currency=Currency.DKK)
    target = wallet_factory(wallet_id="target", balance=Decimal("0.00"), currency=Currency.USD)

    # Act: attempt exchange with an invalid FX rate (e.g., zero)
    updated_source, updated_target, tx = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=Decimal("10.00"),
        fx_rate=Decimal("0"),
        transaction_id="tx-4",
        now=now,
    )

    # Assert: wallets unchanged and transaction fails with correct error
    assert updated_source is source
    assert updated_target is target

    assert tx.status == TransactionStatus.FAILED
    assert tx.error_code == TransactionErrorCode.EXCHANGE_RATE_UNAVAILABLE
