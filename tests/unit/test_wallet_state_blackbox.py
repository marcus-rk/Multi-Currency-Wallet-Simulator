"""
Unit tests for wallet state transitions, derived from Black-Box Test Design PDF:
- Section 4: State Transition Diagram

Run with pytest:
    python -m pytest tests/unit/test_wallet_state_blackbox.py
Run with coverage:
    python -m pytest --cov=app --cov-report=term-missing tests/unit/test_wallet_state_blackbox.py
"""
from app.domain.enums import WalletStatus
from app.domain.rules.wallet_state import (
    freeze_wallet,
    unfreeze_wallet,
    close_wallet,
)


# ------------------------------------------------
# Positive testing (Valid Transitions)
# ------------------------------------------------

def test_transition_active_to_frozen(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.ACTIVE)

    # Act
    updated_wallet = freeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    assert updated_wallet.status == WalletStatus.FROZEN


def test_transition_frozen_to_active(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.FROZEN)

    # Act
    updated_wallet = unfreeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    assert updated_wallet.status == WalletStatus.ACTIVE


def test_transition_active_to_closed(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.ACTIVE)

    # Act
    updated_wallet = close_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    assert updated_wallet.status == WalletStatus.CLOSED


def test_transition_frozen_to_closed(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.FROZEN)

    # Act
    updated_wallet = close_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    assert updated_wallet.status == WalletStatus.CLOSED


# ------------------------------------------------
# Negative testing (Invalid Transitions)
# ------------------------------------------------

def test_transition_closed_to_active_fails(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.CLOSED)

    # Act
    updated_wallet = unfreeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    # Should remain CLOSED (transition ignored)
    assert updated_wallet.status == WalletStatus.CLOSED


def test_transition_closed_to_frozen_fails(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.CLOSED)

    # Act
    updated_wallet = freeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    # Should remain CLOSED (transition ignored)
    assert updated_wallet.status == WalletStatus.CLOSED


# ------------------------------------------------
# Idempotency / No-op Transitions
# ------------------------------------------------

def test_freeze_on_already_frozen_wallet(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.FROZEN)

    # Act
    updated_wallet = freeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    assert updated_wallet.status == WalletStatus.FROZEN


def test_unfreeze_on_already_active_wallet(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.ACTIVE)

    # Act
    updated_wallet = unfreeze_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    assert updated_wallet.status == WalletStatus.ACTIVE


def test_close_on_already_closed_wallet(wallet_factory, get_fixed_timestamp):
    # Arrange
    wallet = wallet_factory(status=WalletStatus.CLOSED)

    # Act
    updated_wallet = close_wallet(wallet, now=get_fixed_timestamp)

    # Assert
    assert updated_wallet.status == WalletStatus.CLOSED
