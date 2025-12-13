from __future__ import annotations

from datetime import datetime
from typing import Tuple

from app.domain.enums import WalletStatus
from app.domain.exceptions import WalletStateError
from app.domain.models.Transaction import Transaction
from app.domain.models.Wallet import Wallet


def apply_status_change(
    wallet: Wallet,
    new_status: WalletStatus,
    transaction_id: str,
    now: datetime,
) -> Tuple[Wallet, Transaction]:
    """Pure domain rule for wallet lifecycle transitions.

    Allowed transitions:
      - ACTIVE -> FROZEN
      - FROZEN -> ACTIVE
      - ACTIVE/FROZEN -> CLOSED
      - CLOSED -> (no transitions)

    On invalid transition: raise WalletStateError.
    """

    allowed = {
        (WalletStatus.ACTIVE, WalletStatus.FROZEN),
        (WalletStatus.FROZEN, WalletStatus.ACTIVE),
        (WalletStatus.ACTIVE, WalletStatus.CLOSED),
        (WalletStatus.FROZEN, WalletStatus.CLOSED),
    }

    if (wallet.status, new_status) not in allowed:
        raise WalletStateError("Wallet state transition not allowed")

    updated_wallet = Wallet(
        id=wallet.id,
        currency=wallet.currency,
        balance=wallet.balance,
        status=new_status,
        created_at=wallet.created_at,
        updated_at=now,
    )

    tx = Transaction.status_change(
        transaction_id=transaction_id,
        wallet_id=wallet.id,
        currency=wallet.currency,
        created_at=now,
        balance_after=wallet.balance,
    )

    return updated_wallet, tx
