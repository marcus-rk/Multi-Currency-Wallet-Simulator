from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from ..models.Transaction import Transaction
from ..models.Wallet import Wallet
from ..enums import TransactionErrorCode, TransactionStatus


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
    - Returns (updated_source, updated_target, transaction).
    """
    error_code = _validate_exchange(source_wallet, target_wallet, amount, fx_rate)

    if error_code is None:
        # SRS v2.1: Round half up to 2 decimal places for credited amounts.
        credited_amount = (amount * fx_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        source_balance_after = source_wallet.balance - amount
        target_balance_after = target_wallet.balance + credited_amount

        updated_source = Wallet(
            id=source_wallet.id,
            currency=source_wallet.currency,
            balance=source_balance_after,
            status=source_wallet.status,
            created_at=source_wallet.created_at,
            updated_at=now,
        )

        updated_target = Wallet(
            id=target_wallet.id,
            currency=target_wallet.currency,
            balance=target_balance_after,
            status=target_wallet.status,
            created_at=target_wallet.created_at,
            updated_at=now,
        )

        status = TransactionStatus.COMPLETED
        credited_currency = target_wallet.currency
    else:
        updated_source = source_wallet
        updated_target = target_wallet
        credited_amount = None
        credited_currency = None
        source_balance_after = None
        target_balance_after = None
        status = TransactionStatus.FAILED

    transaction = Transaction.exchange(
        transaction_id=transaction_id,
        source_wallet_id=source_wallet.id,
        target_wallet_id=target_wallet.id,
        amount=amount,
        source_currency=source_wallet.currency,
        credited_amount=credited_amount,
        credited_currency=credited_currency,
        source_balance_after=source_balance_after,
        target_balance_after=target_balance_after,
        status=status,
        error_code=error_code,
        created_at=now,
    )

    return updated_source, updated_target, transaction


def _validate_exchange(
    source_wallet: Wallet,
    target_wallet: Wallet,
    amount: Decimal,
    fx_rate: Optional[Decimal],
) -> Optional[TransactionErrorCode]:
    """
    Returns an error code if the exchange is invalid, otherwise None.
    """
    error_code: Optional[TransactionErrorCode] = None

    if not source_wallet.is_active() or not target_wallet.is_active():
        error_code = TransactionErrorCode.INVALID_WALLET_STATE
    elif source_wallet.id == target_wallet.id:
        error_code = TransactionErrorCode.INVALID_WALLET_STATE
    elif amount <= Decimal("0"):
        error_code = TransactionErrorCode.INVALID_AMOUNT
    elif source_wallet.currency == target_wallet.currency:
        error_code = TransactionErrorCode.UNSUPPORTED_CURRENCY
    elif amount > source_wallet.balance:
        error_code = TransactionErrorCode.INSUFFICIENT_FUNDS
    elif fx_rate is None or fx_rate <= Decimal("0"):
        error_code = TransactionErrorCode.EXCHANGE_RATE_UNAVAILABLE

    return error_code
