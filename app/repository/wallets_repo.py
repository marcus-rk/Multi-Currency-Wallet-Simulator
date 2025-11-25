from typing import Optional
from datetime import datetime
from decimal import Decimal

from ..database import get_db
from app.domain.models.Wallet import Wallet
from app.domain.enums import Currency, WalletStatus


def create_wallet(wallet: Wallet) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO wallets (id, currency, balance, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            wallet.id,
            wallet.currency.value,
            str(wallet.balance),
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


def insert_wallet(wallet: Wallet) -> None:
    """Insert a new wallet row based on a Wallet domain object."""
    db = get_db()
    db.execute(
        """
        INSERT INTO wallets (id, currency, balance, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            wallet.id,
            wallet.currency.value,
            str(wallet.balance),
            wallet.status.value,
            wallet.created_at.isoformat(),
            wallet.updated_at.isoformat(),
        ),
    )
    db.commit()


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
            str(wallet.balance),
            wallet.status.value,
            wallet.updated_at.isoformat(),
            wallet.id,
        ),
    )
    db.commit()


def _row_to_wallet(row) -> Wallet:
    """Map a DB row to a Wallet domain object."""
    return Wallet(
        id=row["id"],
        currency=Currency(row["currency"]),
        balance=Decimal(row["balance"]),
        status=WalletStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
