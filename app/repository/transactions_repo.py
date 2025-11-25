from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from ..database import get_db
from app.domain.models.Transaction import Transaction
from app.domain.enums import (
    TransactionType,
    TransactionStatus,
    TransactionErrorCode,
    Currency,
)


def create_transaction(transaction: Transaction) -> None:
    """Insert a new transaction row based on a Transaction domain object."""
    db = get_db()
    db.execute(
        """
        INSERT INTO transactions (
            id,
            type,
            source_wallet_id,
            target_wallet_id,
            amount,
            currency,
            credited_amount,
            credited_currency,
            source_balance_after,
            target_balance_after,
            status,
            error_code,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction.id,
            transaction.type.value,
            transaction.source_wallet_id,
            transaction.target_wallet_id,
            str(transaction.amount),
            transaction.currency.value,
            str(transaction.credited_amount) if transaction.credited_amount is not None else None,
            transaction.credited_currency.value if transaction.credited_currency is not None else None,
            str(transaction.source_balance_after) if transaction.source_balance_after is not None else None,
            str(transaction.target_balance_after) if transaction.target_balance_after is not None else None,
            transaction.status.value,
            transaction.error_code.value if transaction.error_code is not None else None,
            transaction.created_at.isoformat(),
        ),
    )
    db.commit()


def get_transaction(transaction_id: str) -> Optional[Transaction]:
    """Fetch a transaction by id, or None if not found."""
    db = get_db()
    cur = db.execute(
        """
        SELECT
            id,
            type,
            source_wallet_id,
            target_wallet_id,
            amount,
            currency,
            credited_amount,
            credited_currency,
            source_balance_after,
            target_balance_after,
            status,
            error_code,
            created_at
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    )
    row = cur.fetchone()
    return _row_to_transaction(row) if row else None


def get_transactions_for_wallet(wallet_id: str) -> List[Transaction]:
    """
    Returns all transactions where the wallet is either source or target,
    ordered by creation time.
    """
    db = get_db()
    cur = db.execute(
        """
        SELECT
            id,
            type,
            source_wallet_id,
            target_wallet_id,
            amount,
            currency,
            credited_amount,
            credited_currency,
            source_balance_after,
            target_balance_after,
            status,
            error_code,
            created_at
        FROM transactions
        WHERE source_wallet_id = ?
           OR target_wallet_id = ?
        ORDER BY created_at DESC
        """,
        (wallet_id, wallet_id),
    )
    rows = cur.fetchall()
    return [_row_to_transaction(row) for row in rows]


def _row_to_transaction(row) -> Transaction:
    """Map a DB row to a Transaction domain object."""
    return Transaction(
        id=row["id"],
        type=TransactionType(row["type"]),
        source_wallet_id=row["source_wallet_id"],
        target_wallet_id=row["target_wallet_id"],
        amount=Decimal(row["amount"]),
        currency=Currency(row["currency"]),
        credited_amount=Decimal(row["credited_amount"]) if row["credited_amount"] is not None else None,
        credited_currency=Currency(row["credited_currency"]) if row["credited_currency"] is not None else None,
        source_balance_after=Decimal(row["source_balance_after"]) if row["source_balance_after"] is not None else None,
        target_balance_after=Decimal(row["target_balance_after"]) if row["target_balance_after"] is not None else None,
        status=TransactionStatus(row["status"]),
        error_code=TransactionErrorCode(row["error_code"])
        if row["error_code"] is not None
        else None,
        created_at=datetime.fromisoformat(row["created_at"]),
    )
