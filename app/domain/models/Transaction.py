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
    '''
    Transaction domain model representing a financial transaction.
    - **id**: str, identifier of the transaction
    - **type**: TransactionType, type of the transaction (DEPOSIT, WITHDRAWAL, EXCHANGE)
    - **source_wallet_id**: Optional[str], ID of the source wallet (if applicable)
    - **target_wallet_id**: Optional[str], ID of the target wallet (if applicable)
    - **amount**: Decimal, amount involved in the transaction
    - **currency**: Currency, currency of the transaction amount
    - **credited_amount**: Optional[Decimal], amount credited to target wallet in exchange transactions
    - **credited_currency**: Optional[Currency], currency of the credited amount in exchange transactions
    - **source_balance_after**: Optional[Decimal], balance of source wallet after transaction
    - **target_balance_after**: Optional[Decimal], balance of target wallet after transaction
    - **status**: TransactionStatus, status of the transaction (COMPLETED, FAILED)
    - **error_code**: Optional[TransactionErrorCode], error code if the transaction failed
    - **created_at**: datetime, timestamp when the transaction was created
    '''
    id: str
    type: TransactionType
    source_wallet_id: Optional[str]
    target_wallet_id: Optional[str]
    amount: Decimal
    currency: Currency
    credited_amount: Optional[Decimal] = None       # Amount credited to target wallet in exchange transactions
    credited_currency: Optional[Currency] = None    # Currency of the credited amount in exchange transactions
    source_balance_after: Optional[Decimal] = None  # Balance of source wallet after transaction
    target_balance_after: Optional[Decimal] = None
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
        target_balance_after: Optional[Decimal] = None,
    ) -> "Transaction":
        return Transaction(
            id=transaction_id,
            type=TransactionType.DEPOSIT,
            source_wallet_id=None,
            target_wallet_id=wallet_id,
            amount=amount,
            currency=currency,
            credited_amount=None,
            credited_currency=None,
            source_balance_after=None,
            target_balance_after=target_balance_after,
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
        source_balance_after: Optional[Decimal] = None,
    ) -> "Transaction":
        return Transaction(
            id=transaction_id,
            type=TransactionType.WITHDRAWAL,
            source_wallet_id=wallet_id,
            target_wallet_id=None,
            amount=amount,
            currency=currency,
            credited_amount=None,
            credited_currency=None,
            source_balance_after=source_balance_after,
            target_balance_after=None,
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
        credited_amount: Optional[Decimal],
        credited_currency: Optional[Currency],
        source_balance_after: Optional[Decimal],
        target_balance_after: Optional[Decimal],
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
            credited_amount=credited_amount,
            credited_currency=credited_currency,
            source_balance_after=source_balance_after,
            target_balance_after=target_balance_after,
            status=status,
            error_code=error_code,
            created_at=created_at,
        )
