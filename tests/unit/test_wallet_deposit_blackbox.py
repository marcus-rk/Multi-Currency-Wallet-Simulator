"""
Unit tests for deposit behaviour, derived from Black-Box Test Design PDF:
- Section 2.1: Amount equivalence partitions
- Section 2.2: 3-value boundary value analysis
- Section 3.1: Deposit decision table (R1-R5)
"""
from decimal import Decimal
from datetime import datetime

import pytest

from app.domain.enums import (
    Currency,
    WalletStatus,
    TransactionStatus,
    TransactionErrorCode,
)
from app.domain.rules import apply_deposit

# ------------------------------------------------
# Positive tests (EP + 3-V BVA)
# ------------------------------------------------

# Valid amount partition: [0.01, MAX DOUBLE[
@pytest.mark.parametrize("amount", [
    Decimal("0.01"),        # lower boundary of valid
    Decimal("1000000.0"),     # representative large value from EP
    Decimal("9999999999.0"),  # upper boundary just below MAX DOUBLE
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
    updated_wallet, tx = apply_deposit(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-valid-amount",
        now=get_fixed_timestamp,
    )

    # Assert
    assert updated_wallet.balance == initial_balance + amount
    assert tx.status is TransactionStatus.COMPLETED
    assert tx.error_code is None

# ------------------------------------------------
# Negative tests (EP + 3-V BVA)
# ------------------------------------------------

@pytest.mark.parametrize("amount", [
    Decimal("-1000000"),   # EP: representative large negative amount
    Decimal("-0.02"),      # BVA: just below -0.01
    Decimal("-0.01"),      # BVA: boundary between invalid negatives and 0.00
    Decimal("0.00"),       # EP/BVA: zero is invalid for deposit
])
def test_deposit_invalid_amount_fails(wallet_factory, get_fixed_timestamp, amount: Decimal):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    updated_wallet, transaction = apply_deposit(
        wallet=wallet,
        amount=amount,
        currency=Currency.DKK,
        transaction_id="tx-invalid-amount",
        now=get_fixed_timestamp,
    )

    # Assert
    assert updated_wallet.balance == wallet.balance
    assert transaction.status is TransactionStatus.FAILED
    assert transaction.error_code is TransactionErrorCode.INVALID_AMOUNT

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
    updated_wallet, transaction = apply_deposit(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=Currency.DKK,
        transaction_id="tx-non-active-wallet",
        now=get_fixed_timestamp,
    )

    # Assert
    assert updated_wallet.balance == wallet.balance
    assert transaction.status is TransactionStatus.FAILED
    assert transaction.error_code is TransactionErrorCode.INVALID_WALLET_STATE

# ------------------------------------------------
# Negative tests: currency mismatch (Currency EP + decision rule)
# ----------------------------------------------------------------

@pytest.mark.parametrize("deposit_currency", [
    Currency.EUR,   # supported but does not match wallet DKK
    Currency.USD,   # supported but does not match wallet DKK
    'GBP',          # unsupported currency
    'JPY',          # unsupported currency
])
def test_deposit_currency_mismatch_fails(wallet_factory, get_fixed_timestamp, deposit_currency: Currency):
    # Arrange
    wallet = wallet_factory(
        balance=Decimal("100.00"),
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE,
    )

    # Act
    updated_wallet, transaction = apply_deposit(
        wallet=wallet,
        amount=Decimal("10.00"),
        currency=deposit_currency,
        transaction_id="tx-currency-mismatch",
        now=get_fixed_timestamp,
    )

    # Assert
    assert updated_wallet.balance == wallet.balance
    assert transaction.status is TransactionStatus.FAILED
    assert transaction.error_code is TransactionErrorCode.UNSUPPORTED_CURRENCY
