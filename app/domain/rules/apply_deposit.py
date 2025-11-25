from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from ..models.Transaction import Transaction
from ..models.Wallet import Wallet
from ..enums import (
    Currency, 
    TransactionStatus, 
    TransactionErrorCode, 
    TransactionType
)


def apply_deposit(
    wallet: Wallet,
    amount: Decimal,
    currency: Currency,
    transaction_id: str,
    now: datetime,
) -> Tuple[Wallet, Transaction]:
    """
    Pure domain rule for deposits.
    - Returns (updated_wallet, transaction).
    """
    error_code = _validate_deposit(wallet, amount, currency)

    if error_code is None:
        updated_wallet = Wallet(
            id=wallet.id,
            currency=wallet.currency,
            balance=wallet.balance + amount,
            status=wallet.status,
            created_at=wallet.created_at,
            updated_at=now,
        )
        status = TransactionStatus.COMPLETED
    else:
        updated_wallet = wallet
        status = TransactionStatus.FAILED

    transaction = Transaction.deposit(
        transaction_id=transaction_id,
        wallet_id=wallet.id,
        amount=amount,
        currency=currency,
        status=status,
        error_code=error_code,
        created_at=now,
    )

    return updated_wallet, transaction


def _validate_deposit(
    wallet: Wallet,
    amount: Decimal,
    currency: Currency,
) -> Optional[TransactionErrorCode]:
    """
    Returns an error code string if the deposit is invalid, otherwise None.
    """
    if not wallet.is_active():
        return TransactionErrorCode.INVALID_WALLET_STATE

    if amount <= Decimal("0"):
        return TransactionErrorCode.INVALID_AMOUNT

    if currency != wallet.currency:
        return TransactionErrorCode.UNSUPPORTED_CURRENCY

    return None
