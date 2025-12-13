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
    # Arrange: ACTIVE wallet with sufficient funds
    initial_balance = Decimal("100000000000")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act: withdraw a valid amount in the wallet currency
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-valid-withdraw",
        now=get_fixed_timestamp,
    )

    # Assert: transaction succeeds without an error code
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
    (Decimal("100.00"), Decimal("99.99"), Decimal("0.01")),  # Boundary: just below balance (valid)
    (Decimal("100.00"), Decimal("100.00"), Decimal("0.00")), # Boundary: exact balance (valid)
    (Decimal("0.01"), Decimal("0.01"), Decimal("0.00")),     # Boundary: exact balance (small)
])
def test_withdraw_deducts_correctly_from_balance(wallet_factory, get_fixed_timestamp, initial_balance, amount, expected_remaining):
    # Arrange: ACTIVE wallet with known balance and a valid withdraw amount
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act: withdraw and capture updated wallet
    updated_wallet, _ = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-deduct-balance",
        now=get_fixed_timestamp,
    )

    # Assert: balance decreases by the withdrawn amount
    assert updated_wallet.balance == expected_remaining


@pytest.mark.parametrize("currency", [
    Currency.DKK,
    Currency.EUR,
    Currency.USD,
])
def test_withdraw_supported_currencies_pass(wallet_factory, get_fixed_timestamp, currency):
    # Arrange: ACTIVE wallet with a supported currency
    initial_balance = Decimal("100.00")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=currency,
        status=WalletStatus.ACTIVE,
    )

    # Act: withdraw a valid amount in the same currency
    updated_wallet, transaction = apply_withdraw(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=currency,
        transaction_id=f"tx-{currency.value.lower()}-withdraw",
        now=get_fixed_timestamp,
    )

    # Assert: wallet balance decreases and transaction succeeds
    expected = (
        initial_balance - Decimal("10.00"),
        TransactionStatus.COMPLETED,
        None,
    )
    actual = (
        updated_wallet.balance,
        transaction.status,
        transaction.error_code,
    )
    assert actual == expected


# ------------------------------------------------
# Negative testing (EP + 3-V BVA)
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    Decimal("-9999999999"), # extreme negative EP
    Decimal("-10.00"),      # negative
    Decimal("-0.02"),       # just below boundary -0.01
    Decimal("-0.01"),       # boundary negative
    Decimal("0.00"),        # boundary invalid
])
def test_withdraw_invalid_amount_fails(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange: ACTIVE wallet and an invalid (non-positive) withdraw amount
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act: attempt the withdrawal
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-invalid-amount",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with INVALID_AMOUNT
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
    Decimal("-9999999999"), # extreme negative EP
    Decimal("-10.00"),      # negative
    Decimal("-0.02"),       # just below boundary -0.01
    Decimal("-0.01"),       # boundary negative
    Decimal("0.00"),        # boundary invalid
])
def test_withdraw_negative_amount_keeps_balance(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange: ACTIVE wallet with known starting balance
    initial_balance = Decimal("100.00")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act: attempt an invalid withdrawal
    updated_wallet, _ = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-balance-unchanged",
        now=get_fixed_timestamp,
    )

    # Assert: balance stays unchanged on failed withdrawal
    assert updated_wallet.balance == initial_balance


@pytest.mark.parametrize("amount", [
    Decimal("100.01"),      # Just above balance (Boundary)
    Decimal("1000.00"),     # Way above balance
])
def test_withdraw_insufficient_funds_fails(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange: ACTIVE wallet where amount exceeds available balance
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act: attempt the withdrawal
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-insufficient",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with INSUFFICIENT_FUNDS
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
    # Arrange: wallet is not ACTIVE (withdraw should be blocked)
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=status,
    )

    # Act: attempt withdraw from non-active wallet
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=Currency.DKK,
        transaction_id="tx-status-fail",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with INVALID_WALLET_STATE
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
    # Arrange: ACTIVE DKK wallet but withdraw currency differs (unsupported)
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act: attempt withdraw with mismatching currency
    _, transaction = apply_withdraw(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=withdraw_currency, # Mismatch
        transaction_id="tx-currency-fail",
        now=get_fixed_timestamp,
    )

    # Assert: transaction fails with UNSUPPORTED_CURRENCY
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
    Decimal("0.01"),
    Decimal("0.02"),
    Decimal("1000000.00"),
])
def test_withdraw_returns_decimal_balance_and_amount(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange: ACTIVE wallet and a valid withdraw amount
    initial_balance = Decimal("10000000.00")
    wallet = wallet_factory(
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act: withdraw and capture returned wallet/transaction objects
    updated_wallet, transaction = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-datatype",
        now=get_fixed_timestamp,
    )

    # Assert: decimals remain Decimal (no float conversion)
    expected = (Decimal, Decimal)
    actual = (type(updated_wallet.balance), type(transaction.amount))
    assert actual == expected


@pytest.mark.parametrize("amount", [
    "10",      # string instead of Decimal
    10.0,      # float instead of Decimal
    None,      # NoneType
])
def test_withdraw_invalid_amount_type_raises_typeerror(wallet_factory, get_fixed_timestamp, amount):
    # Arrange: ACTIVE wallet but amount is the wrong type
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act + Assert: rule enforces Decimal typing
    with pytest.raises(TypeError):
        apply_withdraw(
            wallet=wallet,
            amount=amount,
            currency=Currency.DKK,
            transaction_id="tx-wrong-type",
            now=get_fixed_timestamp,
        )
