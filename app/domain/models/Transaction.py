from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ..enums import (
    TransactionType, 
    TransactionStatus,
    Currency, 
    TransactionErrorCode
)


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
        error_code: Optional[TransactionErrorCode],
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

    @staticmethod
    def withdrawal(
        transaction_id: str,
        wallet_id: str,
        amount: Decimal,
        currency: Currency,
        status: TransactionStatus,
        error_code: Optional[TransactionErrorCode],
        created_at: datetime,
    ) -> "Transaction":
        return Transaction(
            id=transaction_id,
            type=TransactionType.WITHDRAWAL,
            source_wallet_id=wallet_id,
            target_wallet_id=None,
            amount=amount,
            currency=currency,
            status=status,
            error_code=error_code,
            created_at=created_at,
        )

    @staticmethod
    def exchange(
        transaction_id: str,
        source_wallet_id: str,
        target_wallet_id: str,
        amount: Decimal,
        source_currency: Currency,
        status: TransactionStatus,
        error_code: Optional[TransactionErrorCode],
        created_at: datetime,
    ) -> "Transaction":
        return Transaction(
            id=transaction_id,
            type=TransactionType.EXCHANGE,
            source_wallet_id=source_wallet_id,
            target_wallet_id=target_wallet_id,
            amount=amount,
            currency=source_currency,
            status=status,
            error_code=error_code,
            created_at=created_at,
        )
