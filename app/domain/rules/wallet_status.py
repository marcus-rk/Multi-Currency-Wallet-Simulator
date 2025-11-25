import logging
from datetime import datetime
from decimal import Decimal

from ..models.Wallet import Wallet
from ..models.enums import WalletStatus

def freeze_wallet(wallet: Wallet, now: datetime) -> Wallet:
    """
    Returns a new Wallet in FROZEN state if transition is allowed.
    If the transition is not allowed (e.g., already CLOSED), returns the wallet unchanged.
    """
    if wallet.status == WalletStatus.ACTIVE:
        return Wallet(
            id=wallet.id,
            currency=wallet.currency,
            balance=wallet.balance,
            status=WalletStatus.FROZEN,
            created_at=wallet.created_at,
            updated_at=now,
        )
    return wallet


def unfreeze_wallet(wallet: Wallet, now: datetime) -> Wallet:
    """
    Returns a new Wallet in ACTIVE state if transition is allowed.
    If the transition is not allowed (e.g., CLOSED), returns the wallet unchanged.
    """
    if wallet.status == WalletStatus.FROZEN:
        return Wallet(
            id=wallet.id,
            currency=wallet.currency,
            balance=wallet.balance,
            status=WalletStatus.ACTIVE,
            created_at=wallet.created_at,
            updated_at=now,
        )
    return wallet


def close_wallet(wallet: Wallet, now: datetime) -> Wallet:
    """
    Returns a new Wallet in CLOSED state if transition is allowed.
    CLOSED is terminal: once closed, status never changes again.
    """
    if wallet.status in (WalletStatus.ACTIVE, WalletStatus.FROZEN):
        return Wallet(
            id=wallet.id,
            currency=wallet.currency,
            balance=wallet.balance,
            status=WalletStatus.CLOSED,
            created_at=wallet.created_at,
            updated_at=now,
        )
    return wallet
