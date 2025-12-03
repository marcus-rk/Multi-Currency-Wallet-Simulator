"""
Unit tests for withdraw behaviour, derived from Black-Box Test Design PDF:
- Section 2.1: Amount equivalence partitions
- Section 2.2: 3-value boundary value analysis
- Section 3.2: Withdraw decision table

Run with pytest:
    python -m pytest tests/unit/test_wallet_withdraw_blackbox.py
Run with coverage:
    python -m pytest --cov=app --cov-report=term-missing tests/unit/test_wallet_withdraw_blackbox.py
"""
from decimal import Decimal

import pytest

from app.domain.enums import (
    Currency,
    WalletStatus,
    TransactionStatus,
    TransactionErrorCode,
)
from app.domain.rules.apply_withdraw import apply_withdraw


# ------------------------------------------------
# Positive testing (EP + 3-V BVA)
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    Decimal("0.01"),        # lower boundary of valid
    Decimal("0.02"),        # just above lower boundary
    Decimal("1000000"),     # typical valid value
    Decimal("9999999999"),  # large value within valid partition
])
def test_withdraw_valid_amount_passes(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    # Ensure balance is sufficient for the largest test case to isolate "valid amount" logic
    initial_balance = Decimal("100000000000")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-valid-withdraw",
        now=get_fixed_timestamp,
    )

    # Assert
    expected = (
        TransactionStatus.COMPLETED,
        None,
    )
    actual = (
        transaction.status,
        transaction.error_code,
    )
    assert actual == expected


@pytest.mark.parametrize("initial_balance, amount, expected_remaining", [
    (Decimal("100.00"), Decimal("0.01"), Decimal("99.99")),
    (Decimal("0.01"), Decimal("0.01"), Decimal("0.00")),     # Boundary: exact balance (small)
    (Decimal("100.00"), Decimal("100.00"), Decimal("0.00")), # Boundary: exact balance (typical)
])
def test_withdraw_deducts_correctly_from_balance(wallet_factory, get_fixed_timestamp, initial_balance, amount, expected_remaining):
    # Arrange
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    updated_wallet, _ = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-deduct-balance",
        now=get_fixed_timestamp,
    )

    # Assert
    assert updated_wallet.balance == expected_remaining


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
def test_withdraw_invalid_amount_fails(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-invalid-amount",
        now=get_fixed_timestamp,
    )

    # Assert
    expected = (
        TransactionStatus.FAILED,
        TransactionErrorCode.INVALID_AMOUNT,
    )
    actual = (
        transaction.status,
        transaction.error_code,
    )
    assert actual == expected


@pytest.mark.parametrize("amount", [
    Decimal("100.01"),      # Just above balance (Boundary)
    Decimal("1000.00"),     # Way above balance
])
def test_withdraw_insufficient_funds_fails(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-insufficient",
        now=get_fixed_timestamp,
    )

    # Assert
    expected = (
        TransactionStatus.FAILED,
        TransactionErrorCode.INSUFFICIENT_FUNDS,
    )
    actual = (
        transaction.status,
        transaction.error_code,
    )
    assert actual == expected


@pytest.mark.parametrize("status", [
    WalletStatus.FROZEN,
    WalletStatus.CLOSED,
])
def test_withdraw_on_non_active_wallet_fails(wallet_factory, get_fixed_timestamp, status: WalletStatus):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=status,
    )

    # Act
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=Currency.DKK,
        transaction_id="tx-status-fail",
        now=get_fixed_timestamp,
    )

    # Assert
    expected = (
        TransactionStatus.FAILED,
        TransactionErrorCode.INVALID_WALLET_STATE,
    )
    actual = (
        transaction.status,
        transaction.error_code,
    )
    assert actual == expected


@pytest.mark.parametrize("withdraw_currency", [
    Currency.EUR,
    Currency.USD,
])
def test_withdraw_currency_mismatch_fails(wallet_factory, get_fixed_timestamp, withdraw_currency):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=withdraw_currency, # Mismatch
        transaction_id="tx-currency-fail",
        now=get_fixed_timestamp,
    )

    # Assert
    expected = (
        TransactionStatus.FAILED,
        TransactionErrorCode.UNSUPPORTED_CURRENCY,
    )
    actual = (
        transaction.status,
        transaction.error_code,
    )
    assert actual == expected


# ------------------------------------------------
# Data type testing
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    "10",      # string instead of Decimal
    10.0,      # float instead of Decimal
    None,      # NoneType
])
def test_withdraw_invalid_amount_type_raises_typeerror(wallet_factory, get_fixed_timestamp, amount):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act / Assert
    with pytest.raises(TypeError):
        apply_withdraw(
            wallet=wallet,
            amount=amount,
            currency=Currency.DKK,
            transaction_id="tx-wrong-type",
            now=get_fixed_timestamp,
        )
