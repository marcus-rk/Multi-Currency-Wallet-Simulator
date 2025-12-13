"""White-box unit tests for wallet lifecycle status change rule.

These tests validate the explicit branch outcomes of apply_status_change:
- allowed transitions produce updated wallet + STATUS_CHANGE transaction
- invalid transitions raise WalletStateError
"""

from decimal import Decimal

import pytest

from app.domain.enums import Currency, TransactionStatus, TransactionType, WalletStatus
from app.domain.exceptions import WalletStateError
from app.domain.rules.apply_status_change import apply_status_change


def test_active_to_frozen_creates_status_change_tx(wallet_factory, get_fixed_timestamp):
    # Arrange: ACTIVE wallet (DKK) with any balance
    wallet = wallet_factory(status=WalletStatus.ACTIVE, currency=Currency.DKK)

    # Act: apply the lifecycle transition ACTIVE -> FROZEN
    updated_wallet, tx = apply_status_change(
        wallet=wallet,
        new_status=WalletStatus.FROZEN,
        transaction_id="tx-1",
        now=get_fixed_timestamp,
    )

    # Assert: wallet updates + a STATUS_CHANGE transaction is produced
    assert updated_wallet.status == WalletStatus.FROZEN
    assert updated_wallet.updated_at == get_fixed_timestamp

    assert tx.type == TransactionType.STATUS_CHANGE
    assert tx.status == TransactionStatus.COMPLETED
    assert tx.source_wallet_id == wallet.id
    assert tx.target_wallet_id == wallet.id
    assert tx.amount == Decimal("0.00")
    assert tx.currency == Currency.DKK


@pytest.mark.parametrize(
    "from_status,to_status",
    [
        (WalletStatus.FROZEN, WalletStatus.ACTIVE),
        (WalletStatus.ACTIVE, WalletStatus.CLOSED),
        (WalletStatus.FROZEN, WalletStatus.CLOSED),
    ],
)
def test_allowed_transitions_succeed(wallet_factory, get_fixed_timestamp, from_status, to_status):
    # Arrange: wallet in the "from" lifecycle state
    wallet = wallet_factory(status=from_status)

    # Act: apply lifecycle transition
    updated_wallet, tx = apply_status_change(
        wallet=wallet,
        new_status=to_status,
        transaction_id="tx-2",
        now=get_fixed_timestamp,
    )

    # Assert: wallet transitions and tx is STATUS_CHANGE
    assert updated_wallet.status == to_status
    assert tx.type == TransactionType.STATUS_CHANGE


@pytest.mark.parametrize(
    "from_status,to_status",
    [
        (WalletStatus.CLOSED, WalletStatus.ACTIVE),
        (WalletStatus.CLOSED, WalletStatus.FROZEN),
        (WalletStatus.CLOSED, WalletStatus.CLOSED),
        (WalletStatus.ACTIVE, WalletStatus.ACTIVE),
        (WalletStatus.FROZEN, WalletStatus.FROZEN),
    ],
)
def test_invalid_transition_raises(wallet_factory, get_fixed_timestamp, from_status, to_status):
    # Arrange: wallet in the "from" lifecycle state
    wallet = wallet_factory(status=from_status)

    # Act + Assert: invalid transition raises
    with pytest.raises(WalletStateError):
        apply_status_change(
            wallet=wallet,
            new_status=to_status,
            transaction_id="tx-3",
            now=get_fixed_timestamp,
        )
