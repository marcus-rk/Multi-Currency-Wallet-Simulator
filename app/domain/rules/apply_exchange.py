import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from ..models.Transaction import Transaction
from ..models.Wallet import Wallet
from ..models.enums import Currency, TransactionStatus, TransactionErrorCode, TransactionType


def apply_exchange(
    source_wallet: Wallet,
    target_wallet: Wallet,
    amount: Decimal,
    fx_rate: Decimal,
    transaction_id: str,
    now: datetime,
) -> Tuple[Wallet, Wallet, Transaction]:
    """
    Pure domain rule for exchanges between two wallets.
    - Returns (updated_source_wallet, updated_target_wallet, transaction).
    """
    error_code = validate_exchange(source_wallet, target_wallet, amount, fx_rate)

    if error_code is None:
        # Money leaves the source wallet in its own currency
        new_source = Wallet(
            id=source_wallet.id,
            currency=source_wallet.currency,
            balance=source_wallet.balance - amount,
            status=source_wallet.status,
            created_at=source_wallet.created_at,
            updated_at=now,
        )

        # Money enters the target wallet in its currency
        credited_amount = amount * fx_rate  # rounding rules can be applied here later
        new_target = Wallet(
            id=target_wallet.id,
            currency=target_wallet.currency,
            balance=target_wallet.balance + credited_amount,
            status=target_wallet.status,
            created_at=target_wallet.created_at,
            updated_at=now,
        )

        status: TransactionStatus = TransactionStatus.COMPLETED
    else:
        new_source = source_wallet
        new_target = target_wallet
        status = TransactionStatus.FAILED

    transaction = Transaction(
        id=transaction_id,
        type=TransactionType.EXCHANGE,
        source_wallet_id=source_wallet.id,
        target_wallet_id=target_wallet.id,
        amount=amount,                 # in source currency
        currency=source_wallet.currency,
        status=status,
        error_code=error_code,
        created_at=now,
    )

    return new_source, new_target, transaction


def validate_exchange(
    source_wallet: Wallet,
    target_wallet: Wallet,
    amount: Decimal,
    fx_rate: Optional[Decimal],
) -> Optional[TransactionErrorCode]:
    """
    Returns an error code string if the exchange is invalid, otherwise None.
    """
    if not source_wallet.is_active() or not target_wallet.is_active():
        return TransactionErrorCode.INVALID_WALLET_STATE

    if amount <= Decimal("0"):
        return TransactionErrorCode.INVALID_AMOUNT

    if source_wallet.currency == target_wallet.currency:
        return TransactionErrorCode.UNSUPPORTED_CURRENCY

    if amount > source_wallet.balance:
        return TransactionErrorCode.INSUFFICIENT_FUNDS

    # FX_UNAVAILABLE is not in the Enum, so return None for now
    if fx_rate is None or fx_rate <= Decimal("0"):
        return None

    return None