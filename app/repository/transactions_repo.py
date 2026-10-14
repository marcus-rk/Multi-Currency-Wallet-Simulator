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
from .money import to_minor_units, from_minor_units


def create_transaction(transaction: Transaction) -> None:
    """Insert a new transaction row based on a Transaction domain object."""
    target_currency = _target_currency(transaction.credited_currency, transaction.currency)
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
            to_minor_units(transaction.amount, transaction.currency),
            transaction.currency.value,
            _to_minor_units_or_none(transaction.credited_amount, transaction.credited_currency),
            transaction.credited_currency.value if transaction.credited_currency is not None else None,
            _to_minor_units_or_none(transaction.source_balance_after, transaction.currency),
            _to_minor_units_or_none(transaction.target_balance_after, target_currency),
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
    currency = Currency(row["currency"])
    credited_currency = (
        Currency(row["credited_currency"]) if row["credited_currency"] is not None else None
    )
    target_currency = _target_currency(credited_currency, currency)
    return Transaction(
        id=row["id"],
        type=TransactionType(row["type"]),
        source_wallet_id=row["source_wallet_id"],
        target_wallet_id=row["target_wallet_id"],
        amount=from_minor_units(row["amount"], currency),
        currency=currency,
        credited_amount=_from_minor_units_or_none(row["credited_amount"], credited_currency),
        credited_currency=credited_currency,
        source_balance_after=_from_minor_units_or_none(row["source_balance_after"], currency),
        target_balance_after=_from_minor_units_or_none(row["target_balance_after"], target_currency),
        status=TransactionStatus(row["status"]),
        error_code=TransactionErrorCode(row["error_code"])
        if row["error_code"] is not None
        else None,
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _target_currency(credited_currency: Optional[Currency], currency: Currency) -> Currency:
    """Currency of the target wallet: the credited currency for exchanges, else `currency`."""
    return credited_currency if credited_currency is not None else currency


def _to_minor_units_or_none(amount: Optional[Decimal], currency: Optional[Currency]) -> Optional[int]:
    return to_minor_units(amount, currency) if amount is not None else None


def _from_minor_units_or_none(units: Optional[int], currency: Optional[Currency]) -> Optional[Decimal]:
    return from_minor_units(units, currency) if units is not None else None
