from ..database import get_db
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.domain.models.Wallet import Wallet


def row_to_wallet(row) -> Wallet:
    return Wallet(
        id=row["id"],
        currency=row["currency"],
        balance=Decimal(row["balance"]),
        status=row["status"],  # assume DB stores "ACTIVE"/"FROZEN"/"CLOSED"
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def get_wallet(wallet_id: str) -> Optional[Wallet]:
    db = get_db()
    cur = db.execute(
        "SELECT id, currency, balance, status, created_at, updated_at "
        "FROM wallets WHERE id = ?",
        (wallet_id,),
    )
    row = cur.fetchone()
    return row_to_wallet(row) if row else None


def save_wallet(wallet: Wallet) -> None:
    db = get_db()
    db.execute(
        """
        UPDATE wallets
        SET balance = ?, status = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            str(wallet.balance),
            wallet.status,
            wallet.updated_at.isoformat(),
            wallet.id,
        ),
    )
    db.commit()
