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
    """
    Domain model representing a single financial transaction.

    Attributes:
        id:
            Unique identifier of the transaction.
        type:
            Type of transaction (DEPOSIT, WITHDRAWAL, EXCHANGE).
        source_wallet_id:
            ID of the wallet money is taken from (None for deposits).
        target_wallet_id:
            ID of the wallet money is sent to (None for withdrawals).
        amount:
            Input amount of the operation, in `currency`.
            For exchanges, this is the debited amount in the source wallet currency.
        currency:
            Currency of `amount` (source currency for exchanges).
        status:
            Outcome of the transaction (COMPLETED or FAILED).
        error_code:
            Error code explaining why the transaction failed, if any.
        created_at:
            Timestamp when the transaction was created.

        credited_amount:
            For exchanges: amount credited to the target wallet (after FX + rounding),
            in `credited_currency`. None for deposits and withdrawals, or failed exchanges.
        credited_currency:
            Currency of `credited_amount` (target wallet currency for exchanges).
        source_balance_after:
            Balance of the source wallet immediately after the transaction is applied.
            None if the transaction failed or there is no source wallet (deposit).
        target_balance_after:
            Balance of the target wallet immediately after the transaction is applied.
            None if the transaction failed or there is no target wallet (withdrawal).
    """
    id: str
    type: TransactionType
    source_wallet_id: Optional[str]
    target_wallet_id: Optional[str]
    amount: Decimal
    currency: Currency
    status: TransactionStatus
    error_code: Optional[TransactionErrorCode]
    created_at: datetime
    credited_amount: Optional[Decimal] = None       
    credited_currency: Optional[Currency] = None    
    source_balance_after: Optional[Decimal] = None  
    target_balance_after: Optional[Decimal] = None

    # ------------------------------------------------------------------
    # Static factory methods
    #
    # - Marked with @staticmethod → do not utilize `self` because they
    #   create new Transaction instances.
    # - Domain rule functions call these after:
    #       * validating inputs, and
    #       * computing resulting balances and status.
    # - These factories just build consistent Transaction objects from
    #   that data, so creation logic is in one place and the rules stay
    #   focused on business logic instead of wiring fields.
    # ------------------------------------------------------------------

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

    @staticmethod
    def status_change(
        transaction_id: str,
        wallet_id: str,
        currency: Currency,
        created_at: datetime,
        balance_after: Optional[Decimal] = None,
    ) -> "Transaction":
        return Transaction(
            id=transaction_id,
            type=TransactionType.STATUS_CHANGE,
            source_wallet_id=wallet_id,
            target_wallet_id=wallet_id,
            amount=Decimal("0.00"),
            currency=currency,
            credited_amount=None,
            credited_currency=None,
            source_balance_after=balance_after,
            target_balance_after=balance_after,
            status=TransactionStatus.COMPLETED,
            error_code=None,
            created_at=created_at,
        )

