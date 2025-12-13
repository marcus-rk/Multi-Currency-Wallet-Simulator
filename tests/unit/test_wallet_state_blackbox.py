"""
Unit tests for wallet state transitions, derived from Black-Box Test Design PDF:
- Section 4: State Transition Diagram

Run with pytest:
    python -m pytest tests/unit/test_wallet_state_blackbox.py
Run with coverage:
    python -m pytest --cov=app --cov-report=term-missing tests/unit/test_wallet_state_blackbox.py
"""
from decimal import Decimal

import pytest

from app.domain.enums import WalletStatus, Currency
from app.domain.rules.wallet_state import (
    freeze_wallet,
    unfreeze_wallet,
    close_wallet,
)


# ------------------------------------------------
# Positive testing (Valid Transitions)
# ------------------------------------------------

def test_transition_active_to_frozen(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet starts ACTIVE
    wallet = wallet_factory(status=WalletStatus.ACTIVE)

    # Act: freeze wallet
    updated_wallet = freeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert: wallet becomes FROZEN
    assert updated_wallet.status == WalletStatus.FROZEN


def test_transition_frozen_to_active(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet starts FROZEN
    wallet = wallet_factory(status=WalletStatus.FROZEN)

    # Act: unfreeze wallet
    updated_wallet = unfreeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert: wallet becomes ACTIVE
    assert updated_wallet.status == WalletStatus.ACTIVE


def test_transition_active_to_closed(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet starts ACTIVE
    wallet = wallet_factory(status=WalletStatus.ACTIVE)

    # Act: close wallet
    updated_wallet = close_wallet(wallet, now=get_fixed_timestamp)

    # Assert: wallet becomes CLOSED
    assert updated_wallet.status == WalletStatus.CLOSED


def test_transition_frozen_to_closed(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet starts FROZEN
    wallet = wallet_factory(status=WalletStatus.FROZEN)

    # Act: close wallet
    updated_wallet = close_wallet(wallet, now=get_fixed_timestamp)

    # Assert: wallet becomes CLOSED
    assert updated_wallet.status == WalletStatus.CLOSED


def test_transition_preserves_data_integrity(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet with known id/balance/currency
    initial_balance = Decimal("123.45")
    test_id = "test-uuid-123"
    wallet = wallet_factory(
        wallet_id=test_id,
        balance=initial_balance,
        currency=Currency.DKK,
        status=WalletStatus.ACTIVE
    )

    # Act: freeze wallet
    updated_wallet = freeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert: ONLY status and updated_at changed
    # Verify ONLY status and updated_at changed
    assert updated_wallet.id == wallet.id
    assert updated_wallet.balance == wallet.balance
    assert updated_wallet.currency == wallet.currency
    assert updated_wallet.created_at == wallet.created_at


# ------------------------------------------------
# Negative testing (Invalid Transitions)
# ------------------------------------------------

def test_transition_closed_to_active_fails(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet starts CLOSED (terminal)
    wallet = wallet_factory(status=WalletStatus.CLOSED)

    # Act: attempt invalid transition CLOSED -> ACTIVE
    updated_wallet = unfreeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert: should remain CLOSED (transition ignored)
    # Should remain CLOSED (transition ignored)
    assert updated_wallet.status == WalletStatus.CLOSED


def test_transition_closed_to_frozen_fails(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet starts CLOSED (terminal)
    wallet = wallet_factory(status=WalletStatus.CLOSED)

    # Act: attempt invalid transition CLOSED -> FROZEN
    updated_wallet = freeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert: should remain CLOSED (transition ignored)
    # Should remain CLOSED (transition ignored)
    assert updated_wallet.status == WalletStatus.CLOSED


# ------------------------------------------------
# Idempotency / No-op Transitions
# ------------------------------------------------

def test_freeze_on_already_frozen_wallet(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet is already FROZEN
    wallet = wallet_factory(status=WalletStatus.FROZEN)

    # Act: freeze again (idempotent)
    updated_wallet = freeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert: remains FROZEN
    assert updated_wallet.status == WalletStatus.FROZEN


def test_unfreeze_on_already_active_wallet(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet is already ACTIVE
    wallet = wallet_factory(status=WalletStatus.ACTIVE)

    # Act: unfreeze again (no-op)
    updated_wallet = unfreeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert: remains ACTIVE
    assert updated_wallet.status == WalletStatus.ACTIVE


def test_close_on_already_closed_wallet(wallet_factory, get_fixed_timestamp):
    # Arrange: wallet is already CLOSED
    wallet = wallet_factory(status=WalletStatus.CLOSED)

    # Act: close again (idempotent)
    updated_wallet = close_wallet(wallet, now=get_fixed_timestamp)

    # Assert: remains CLOSED
    assert updated_wallet.status == WalletStatus.CLOSED
