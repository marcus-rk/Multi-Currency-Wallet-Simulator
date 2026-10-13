from typing import Optional, List
from datetime import datetime

from ..database import get_db
from app.domain.models.Wallet import Wallet
from app.domain.enums import Currency, WalletStatus
from .money import to_minor_units, from_minor_units


def create_wallet(wallet: Wallet) -> None:
    '''Create a new wallet in the database based on a Wallet domain object.'''
    db = get_db()
    db.execute(
        """
        INSERT INTO wallets (id, currency, balance, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            wallet.id,
            wallet.currency.value,
            to_minor_units(wallet.balance, wallet.currency),
            wallet.status.value,
            wallet.created_at.isoformat(),
            wallet.updated_at.isoformat(),
        ),
    )
    db.commit()


def get_wallet(wallet_id: str) -> Optional[Wallet]:
    """Fetch a single wallet by id, or None if it does not exist."""
    db = get_db()
    cur = db.execute(
        """
        SELECT id, currency, balance, status, created_at, updated_at
        FROM wallets
        WHERE id = ?
        """,
        (wallet_id,),
    )
    row = cur.fetchone()
    return _row_to_wallet(row) if row else None


def get_all_wallets() -> List[Wallet]:
    """Fetch all wallets."""
    db = get_db()
    cur = db.execute(
        """
        SELECT id, currency, balance, status, created_at, updated_at
        FROM wallets
        """
    )
    rows = cur.fetchall()
    return [_row_to_wallet(row) for row in rows]


def update_wallet(wallet: Wallet) -> None:
    """Persist changes to an existing wallet."""
    db = get_db()
    db.execute(
        """
        UPDATE wallets
        SET currency = ?, balance = ?, status = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            wallet.currency.value,
            to_minor_units(wallet.balance, wallet.currency),
            wallet.status.value,
            wallet.updated_at.isoformat(),
            wallet.id,
        ),
    )
    db.commit()


def _row_to_wallet(row) -> Wallet:
    """Map a DB row to a Wallet domain object."""
    currency = Currency(row["currency"])
    return Wallet(
        id=row["id"],
        currency=currency,
        balance=from_minor_units(row["balance"], currency),
        status=WalletStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
