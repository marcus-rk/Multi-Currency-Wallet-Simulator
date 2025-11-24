from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from .literals import TransactionType, TransactionStatus, Currency, TransactionErrorCode


@dataclass
class Transaction:
    id: str
    type: TransactionType
    source_wallet_id: Optional[str]
    target_wallet_id: Optional[str]
    amount: Decimal
    currency: Currency
    status: TransactionStatus
    error_code: Optional[TransactionErrorCode]
    created_at: datetime

    # Factory method for creating a deposit transaction
    @staticmethod
    def deposit(
        transaction_id: str,
        wallet_id: str,
        amount: Decimal,
        currency: Currency,
        status: TransactionStatus,
        error_code: Optional[str],
        created_at: datetime,
    ) -> "Transaction":
        return Transaction(
            id=transaction_id,
            type=TransactionType.DEPOSIT,
            source_wallet_id=None,
            target_wallet_id=wallet_id,
            amount=amount,
            currency=currency,
            status=status,
            error_code=error_code,
            created_at=created_at,
        )
