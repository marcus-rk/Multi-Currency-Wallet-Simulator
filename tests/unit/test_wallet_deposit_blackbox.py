"""
Unit tests for deposit behaviour, derived from Black-Box Test Design PDF:
- Section 2.1: Amount equivalence partitions
- Section 2.2: 3-value boundary value analysis
- Section 3.1: Deposit decision table (R1-R5)

Run with pytest:
    python -m pytest tests/unit/test_wallet_deposit_blackbox.py
Run with coverage:
    python -m pytest --cov=app --cov-report=term-missing tests/unit/test_wallet_deposit_blackbox.py
"""
from decimal import Decimal

import pytest

from app.domain.enums import (
    Currency,
    WalletStatus,
    TransactionStatus,
    TransactionErrorCode,
)
from app.domain.rules.apply_deposit import apply_deposit


# ------------------------------------------------
# Positive tests (EP + 3-V BVA)
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    Decimal("0.01"),        # lower boundary of valid
    Decimal("0.02"),
    Decimal("1000000"),     
    Decimal("9999999999"),  # large value within valid partition
])
def test_deposit_valid_amount_passes(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    initial_balance = Decimal("100.00")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    _, transaction = apply_deposit(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-valid-amount",
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


@pytest.mark.parametrize("amount", [
    Decimal("0.01"),        # lower boundary of valid
    Decimal("0.02"),
    Decimal("1000000"),     
    Decimal("9999999999"),  # large value within valid partition
])
def test_deposit_adds_correctly_to_balance(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    initial_balance = Decimal("50.00")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    updated_wallet,_ = apply_deposit(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-correct-balance",
        now=get_fixed_timestamp,
    )

    # Assert
    expected_balance = initial_balance + amount
    assert updated_wallet.balance == expected_balance

# ------------------------------------------------
# Negative tests (EP + 3-V BVA)
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    Decimal("-9999999999"), # NOTE: found error -> forgot minus
    Decimal("-1000000"),    # EP: representative large negative amount
    Decimal("-0.02"),       
    Decimal("-0.01"),
    Decimal("0.00"),        # EP/BVA: zero is invalid for deposit
])
def test_deposit_invalid_amount_fails(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    _, transaction = apply_deposit(
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
    Decimal("-9999999999"),
    Decimal("-1000000"),
    Decimal("-0.02"),
    Decimal("-0.01"), 
    Decimal("0.00"),
])
def test_deposit_negative_amount_keeps_balance(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    initial_balance = Decimal("100")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    updated_wallet, _ = apply_deposit(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-balance-unchanged",
        now=get_fixed_timestamp,
    )

    # Assert
    assert updated_wallet.balance == initial_balance


# ------------------------------------------------
# Negative tests (Decision Table Wallet Status)
# ------------------------------------------------

@pytest.mark.parametrize("status", [
    WalletStatus.FROZEN,
    WalletStatus.CLOSED,
])
def test_deposit_on_non_active_wallet_fails(wallet_factory, get_fixed_timestamp, status: WalletStatus):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=status,
    )

    # Act
    _, transaction = apply_deposit(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=Currency.DKK,
        transaction_id="tx-non-active-wallet",
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

# ------------------------------------------------
# Negative tests: currency mismatch (Currency EP + decision rule)
# ------------------------------------------------

@pytest.mark.parametrize("deposit_currency", [
    Currency.EUR,   # supported but does not match wallet DKK
    Currency.USD,   # supported but does not match wallet DKK
])
def test_deposit_currency_mismatch_fails(wallet_factory, get_fixed_timestamp, deposit_currency):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    _, transaction = apply_deposit(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=deposit_currency,
        transaction_id="tx-currency-mismatch",
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
# Data type tests
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    Decimal("0.01"),
    Decimal("0.02"),
    Decimal("1000000.00"),
])
def test_deposit_returns_decimal_balance_and_amount(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    initial_balance = Decimal("100.00")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    updated_wallet, transaction = apply_deposit(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-datatype",
        now=get_fixed_timestamp,
    )

    # Assert
    expected = (Decimal, Decimal)
    actual = (type(updated_wallet.balance), type(transaction.amount))
    assert actual == expected


# ------------------------------------------------
# Error tests (wrong data type for amount)
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    "10",      # string instead of Decimal
    "10.00",   # string instead of Decimal
    "abc",     # non-numeric string
    None,      # NoneType
    "",        # empty string
])
def test_deposit_invalid_amount_type_raises_typeerror(wallet_factory, get_fixed_timestamp, amount):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act / Assert
    with pytest.raises(TypeError):
        apply_deposit(
            wallet=wallet,
            amount=amount,
            currency=Currency.DKK,
            transaction_id="tx-wrong-type",
            now=get_fixed_timestamp,
        )
