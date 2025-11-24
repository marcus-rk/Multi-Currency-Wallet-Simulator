import sqlite3
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.domain.models.Transaction import Transaction


def insert_transaction(db, transaction: Transaction) -> None:
    db.execute(
        """
        INSERT INTO transactions (
            id, type, source_wallet_id, target_wallet_id,
            amount, credited_amount, currency,
            status, error_code, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction.id,
            transaction.type,
            transaction.source_wallet_id,
            transaction.target_wallet_id,
            str(transaction.amount),
            str(transaction.credited_amount) if transaction.credited_amount is not None else None,
            transaction.currency,
            transaction.status,
            transaction.error_code,
            transaction.created_at.isoformat(),
        ),
    )
    db.commit()


def get_transaction(db, transaction_id: str) -> Optional[Transaction]:
    cur = db.execute(
        "SELECT id, type, source_wallet_id, target_wallet_id, "
        "amount, credited_amount, currency, status, error_code, created_at "
        "FROM transactions WHERE id = ?",
        (transaction_id,),
    )
    row = cur.fetchone()
    return _row_to_transaction(row) if row else None


def _row_to_transaction(row) -> Transaction:
    return Transaction(
        id=row["id"],
        type=row["type"],
        source_wallet_id=row["source_wallet_id"],
        target_wallet_id=row["target_wallet_id"],
        amount=Decimal(row["amount"]),
        credited_amount=Decimal(row["credited_amount"]) if row["credited_amount"] is not None else None,
        currency=row["currency"],
        status=row["status"],
        error_code=row["error_code"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )
