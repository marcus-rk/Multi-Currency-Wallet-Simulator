"""
Unit tests for exchange behaviour, derived from Black-Box Test Design PDF:
- Section 2.1: Amount equivalence partitions
- Section 3.3: Exchange decision table

Run with pytest:
    python -m pytest tests/unit/test_wallet_exchange_blackbox.py
Run with coverage:
    python -m pytest --cov=app --cov-report=term-missing tests/unit/test_wallet_exchange_blackbox.py
"""
from decimal import Decimal

import pytest

from app.domain.enums import (
    Currency,
    WalletStatus,
    TransactionStatus,
    TransactionErrorCode,
)
from app.domain.rules.apply_exchange import apply_exchange


# ------------------------------------------------
# Positive testing (EP + 3-V BVA)
# ------------------------------------------------

@pytest.mark.parametrize("amount, fx_rate, expected_target_credit", [
    (Decimal("0.01"), Decimal("1.0"), Decimal("0.01")),     # lower boundary of valid amount
    (Decimal("0.02"), Decimal("1.0"), Decimal("0.02")),     # just above lower boundary
    (Decimal("10.00"), Decimal("0.01"), Decimal("0.10")),   # lower boundary of valid fx_rate
    (Decimal("1000000"), Decimal("1.5"), Decimal("1500000")), # typical valid large value
    (Decimal("9999999999"), Decimal("0.5"), Decimal("4999999999.5")), # large value within valid partition
])
def test_exchange_valid_amount_passes(wallet_factory, get_fixed_timestamp, amount, fx_rate, expected_target_credit):
    # Arrange: ACTIVE source/target wallets with different currencies
    source_wallet = wallet_factory(
        balance=Decimal("100000000000"),
        currency=Currency.EUR,
        status=WalletStatus.ACTIVE,
    )
    target_wallet = wallet_factory(
        balance=Decimal("0.00"),
        currency=Currency.USD,
        status=WalletStatus.ACTIVE,
    )

    # Act: exchange a valid amount using the provided FX rate
    _, _, transaction = apply_exchange(
        source_wallet=source_wallet,
        target_wallet=target_wallet,
        amount=amount,
        fx_rate=fx_rate,
        transaction_id="tx-valid-exchange",
        now=get_fixed_timestamp,
    )

    # Assert: transaction completes and credited amount matches expectation
    expected = (
        TransactionStatus.COMPLETED,
        None,
        expected_target_credit,
    )
    actual = (
        transaction.status,
        transaction.error_code,
        transaction.credited_amount,
    )
    assert actual == expected


@pytest.mark.parametrize("initial_source, initial_target, amount, fx_rate, expected_source, expected_target", [
    (Decimal("100.00"), Decimal("50.00"), Decimal("99.99"), Decimal("1.0"), Decimal("0.01"), Decimal("149.99")), # Boundary: just below balance
    (Decimal("100.00"), Decimal("50.00"), Decimal("100.00"), Decimal("1.0"), Decimal("0.00"), Decimal("150.00")), # Boundary: exact balance
    (Decimal("0.01"), Decimal("0.00"), Decimal("0.01"), Decimal("1.0"), Decimal("0.00"), Decimal("0.01")), # Boundary: exact balance (small)
])
def test_exchange_updates_balances_correctly(wallet_factory, get_fixed_timestamp, initial_source, initial_target, amount, fx_rate, expected_source, expected_target):
    # Arrange: wallets with known balances for a balance-update check
    source_wallet = wallet_factory(
        balance=initial_source,
        currency=Currency.EUR,
    )
    target_wallet = wallet_factory(
        balance=initial_target,
        currency=Currency.USD,
    )

    # Act: perform exchange
    updated_source, updated_target, _ = apply_exchange(
        source_wallet=source_wallet,
        target_wallet=target_wallet,
        amount=amount,
        fx_rate=fx_rate,
        transaction_id="tx-balance-check",
        now=get_fixed_timestamp,
    )

    # Assert: balances are updated correctly
    assert (updated_source.balance, updated_target.balance) == (expected_source, expected_target)


@pytest.mark.parametrize("source_currency, target_currency", [
    (Currency.DKK, Currency.EUR),
    (Currency.USD, Currency.DKK),
    (Currency.EUR, Currency.USD),
])
def test_exchange_supported_currency_pairs_pass(wallet_factory, get_fixed_timestamp, source_currency, target_currency):
    # Arrange: ACTIVE wallets using a supported currency pair
    source_wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=source_currency,
        status=WalletStatus.ACTIVE,
    )
    target_wallet = wallet_factory(
        balance=Decimal("0.00"),
        currency=target_currency,
        status=WalletStatus.ACTIVE,
    )

    # Act: exchange a fixed valid amount
    updated_source, updated_target, transaction = apply_exchange(
        source_wallet=source_wallet,
        target_wallet=target_wallet,
        amount=Decimal("10.00"),
        fx_rate=Decimal("1.0"),
        transaction_id="tx-currency-pair",
        now=get_fixed_timestamp,
    )

    # Assert: balances and transaction outcome match expectations
    expected = (
        Decimal("90.00"),
        Decimal("10.00"),
        TransactionStatus.COMPLETED,
        None,
    )
    actual = (
        updated_source.balance,
        updated_target.balance,
        transaction.status,
        transaction.error_code,
    )
    assert actual == expected


# ------------------------------------------------
# Negative testing (EP + 3-V BVA)
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    Decimal("-9999999999"), # extreme negative EP
    Decimal("-1000000"),    # large negative
    Decimal("-0.02"),       # just below boundary -0.01
    Decimal("-0.01"),       # boundary to zero
    Decimal("0.00"),        # boundary between invalid and valid
])
def test_exchange_invalid_amount_fails(wallet_factory, get_fixed_timestamp, amount):
    # Arrange: valid wallets but an invalid (non-positive) amount
    source = wallet_factory(balance=Decimal("100.00"), currency=Currency.EUR)
    target = wallet_factory(balance=Decimal("0.00"), currency=Currency.USD)

    # Act: attempt exchange
    _, _, transaction = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=amount,
        fx_rate=Decimal("1.0"),
        transaction_id="tx-invalid-amount",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with INVALID_AMOUNT
    assert transaction.error_code == TransactionErrorCode.INVALID_AMOUNT


@pytest.mark.parametrize("amount", [
    Decimal("-9999999999"), # extreme negative EP
    Decimal("-1000000"),    # large negative
    Decimal("-0.02"),       # just below boundary -0.01
    Decimal("-0.01"),       # boundary to zero
    Decimal("0.00"),        # boundary between invalid and valid
])
def test_exchange_failure_keeps_both_balances_unchanged(wallet_factory, get_fixed_timestamp, amount):
    # Arrange: wallets with known starting balances
    initial_source = Decimal("100.00")
    initial_target = Decimal("50.00")
    source = wallet_factory(balance=initial_source, currency=Currency.EUR)
    target = wallet_factory(balance=initial_target, currency=Currency.USD)

    # Act: attempt exchange with invalid amount
    updated_source, updated_target, _ = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=amount,
        fx_rate=Decimal("1.0"),
        transaction_id="tx-balance-unchanged",
        now=get_fixed_timestamp,
    )

    # Assert: balances remain unchanged when exchange fails
    assert (updated_source.balance, updated_target.balance) == (initial_source, initial_target)


@pytest.mark.parametrize("amount", [
    Decimal("100.01"),  # Just above balance
    Decimal("1000.00"), # Way above
])
def test_exchange_insufficient_funds_fails(wallet_factory, get_fixed_timestamp, amount):
    # Arrange: source wallet does not have enough funds for the requested amount
    source = wallet_factory(balance=Decimal("100.00"), currency=Currency.EUR)
    target = wallet_factory(balance=Decimal("0.00"), currency=Currency.USD)

    # Act: attempt exchange
    _, _, transaction = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=amount,
        fx_rate=Decimal("1.0"),
        transaction_id="tx-insufficient",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with INSUFFICIENT_FUNDS
    assert transaction.error_code == TransactionErrorCode.INSUFFICIENT_FUNDS


@pytest.mark.parametrize("source_status, target_status", [
    (WalletStatus.FROZEN, WalletStatus.ACTIVE),
    (WalletStatus.CLOSED, WalletStatus.ACTIVE),
    (WalletStatus.ACTIVE, WalletStatus.FROZEN),
    (WalletStatus.ACTIVE, WalletStatus.CLOSED),
])
def test_exchange_with_non_active_wallets_fails(wallet_factory, get_fixed_timestamp, source_status, target_status):
    # Arrange: one or both wallets are not ACTIVE (exchange should be blocked)
    source = wallet_factory(status=source_status, currency=Currency.EUR, balance=Decimal("100.00"))
    target = wallet_factory(status=target_status, currency=Currency.USD)

    # Act: attempt exchange
    _, _, transaction = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=Decimal("10.00"),
        fx_rate=Decimal("1.0"),
        transaction_id="tx-status-fail",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with INVALID_WALLET_STATE
    assert transaction.error_code == TransactionErrorCode.INVALID_WALLET_STATE


def test_exchange_same_currency_fails(wallet_factory, get_fixed_timestamp):
    # Arrange: source and target wallets use the same currency (unsupported)
    source = wallet_factory(currency=Currency.EUR, balance=Decimal("100.00"))
    target = wallet_factory(currency=Currency.EUR) # Same currency

    # Act: attempt exchange
    _, _, transaction = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=Decimal("10.00"),
        fx_rate=Decimal("1.0"),
        transaction_id="tx-same-currency",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with UNSUPPORTED_CURRENCY
    assert transaction.error_code == TransactionErrorCode.UNSUPPORTED_CURRENCY


@pytest.mark.parametrize("fx_rate", [
    None,
    Decimal("0.00"),        # Boundary: Zero (Invalid)
    Decimal("-0.01"),       # Boundary: Just below zero (Invalid)
    Decimal("-1.5"),        # Negative EP
])
def test_exchange_invalid_fx_rate_fails(wallet_factory, get_fixed_timestamp, fx_rate):
    # Arrange: FX rate is missing/invalid (unavailable)
    source = wallet_factory(currency=Currency.EUR, balance=Decimal("100.00"))
    target = wallet_factory(currency=Currency.USD)

    # Act: attempt exchange
    _, _, transaction = apply_exchange(
        source_wallet=source,
        target_wallet=target,
        amount=Decimal("10.00"),
        fx_rate=fx_rate,
        transaction_id="tx-bad-rate",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with EXCHANGE_RATE_UNAVAILABLE
    assert transaction.error_code == TransactionErrorCode.EXCHANGE_RATE_UNAVAILABLE


# ------------------------------------------------
# Data type testing
# ------------------------------------------------

def test_exchange_invalid_amount_type_raises_typeerror(wallet_factory, get_fixed_timestamp):
    # Arrange: wallets are valid but amount is the wrong type
    source = wallet_factory(currency=Currency.EUR, balance=Decimal("100.00"))
    target = wallet_factory(currency=Currency.USD)

    # Act + Assert: rule enforces Decimal typing
    with pytest.raises(TypeError):
        apply_exchange(
            source_wallet=source,
            target_wallet=target,
            amount="10.00", # String
            fx_rate=Decimal("1.0"),
            transaction_id="tx-type-error",
            now=get_fixed_timestamp,
        )
