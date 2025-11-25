from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from ..models.Transaction import Transaction
from ..models.Wallet import Wallet
from ..enums import (
    Currency,
    TransactionStatus,
    TransactionErrorCode,
)


def apply_withdraw(
    wallet: Wallet,
    amount: Decimal,
    currency: Currency,
    transaction_id: str,
    now: datetime,
) -> Tuple[Wallet, Transaction]:
    """
    Pure domain rule for withdrawals.
    - Returns (updated_wallet, transaction).
    """
    error_code = _validate_withdraw(wallet, amount, currency)

    if error_code is None:
        new_balance = wallet.balance - amount
        updated_wallet = Wallet(
            id=wallet.id,
            currency=wallet.currency,
            balance=new_balance,
            status=wallet.status,
            created_at=wallet.created_at,
            updated_at=now,
        )
        status = TransactionStatus.COMPLETED
        balance_after = new_balance
    else:
        updated_wallet = wallet
        status = TransactionStatus.FAILED
        balance_after = None

    transaction = Transaction.withdrawal(
        transaction_id=transaction_id,
        wallet_id=wallet.id,
        amount=amount,
        currency=currency,
        status=status,
        error_code=error_code,
        created_at=now,
        source_balance_after=balance_after,
    )

    return updated_wallet, transaction


def _validate_withdraw(
    wallet: Wallet,
    amount: Decimal,
    currency: Currency,
) -> Optional[TransactionErrorCode]:
    """
    Returns an error code if the withdrawal is invalid, otherwise None.
    """
    if not wallet.is_active():
        return TransactionErrorCode.INVALID_WALLET_STATE

    if amount <= Decimal("0"):
        return TransactionErrorCode.INVALID_AMOUNT

    if currency != wallet.currency:
        return TransactionErrorCode.UNSUPPORTED_CURRENCY

    if amount > wallet.balance:
        return TransactionErrorCode.INSUFFICIENT_FUNDS

    return None
