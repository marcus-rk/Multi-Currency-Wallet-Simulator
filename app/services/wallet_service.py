from datetime import datetime
from decimal import Decimal
from typing import Tuple
from uuid import uuid4

from app.domain.enums import Currency, WalletStatus
from app.domain.models.Wallet import Wallet
from app.domain.models.Transaction import Transaction
from app.domain.rules import (
    apply_deposit,
    apply_withdraw,
    apply_exchange,
)
from app.repository.wallets_repo import (
    get_wallet, 
    update_wallet, 
    create_wallet as repo_create_wallet
)
from app.repository.transactions_repo import create_transaction
from .exchange_service import get_exchange_rate


def create_wallet(currency: Currency, initial_balance: Decimal = Decimal("0.00")) -> Wallet:
    now = datetime.utcnow()
    wallet = Wallet(
        id=str(uuid4()), # new UUID for the wallet
        currency=currency,
        balance=initial_balance,
        status=WalletStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    repo_create_wallet(wallet)
    return wallet


def deposit_money(
    wallet_id: str,
    amount: Decimal,
    currency: Currency,
    now: datetime | None = None,
) -> Tuple[Wallet, Transaction]:
    """
    High-level deposit operation:
      - Return (updated_wallet, transaction)
    """
    now = now or datetime.utcnow()
    wallet = _get_wallet_or_fail(wallet_id)

    updated_wallet, transaction = apply_deposit(
        wallet=wallet,
        amount=amount,
        currency=currency,
        transaction_id=str(uuid4()), # new UUID for the transaction
        now=now,
    )

    update_wallet(updated_wallet)
    create_transaction(transaction)

    return updated_wallet, transaction


def withdraw_money(
    wallet_id: str,
    amount: Decimal,
    currency: Currency,
    now: datetime | None = None,
) -> Tuple[Wallet, Transaction]:
    """
    High-level withdrawal operation:
      - Return (updated_wallet, transaction)
    """
    now = now or datetime.utcnow()
    wallet = _get_wallet_or_fail(wallet_id)

    updated_wallet, transaction = apply_withdraw(
        wallet=wallet,
        amount=amount,
        currency=currency,
        transaction_id=str(uuid4()), # new UUID for the transaction
        now=now,
    )

    update_wallet(updated_wallet)
    create_transaction(transaction)

    return updated_wallet, transaction


def exchange_money(
    source_wallet_id: str,
    target_wallet_id: str,
    amount: Decimal,
    now: datetime | None = None,
) -> Tuple[Wallet, Wallet, Transaction]:
    """
    High-level exchange operation:
      - Load source and target wallets
      - Get exchange rate via exchange_service
      - Apply domain rule
      - Persist both wallets + transaction
      - Return (updated_source_wallet, updated_target_wallet, transaction)
    """
    now = now or datetime.utcnow()

    source_wallet = _get_wallet_or_fail(source_wallet_id)
    target_wallet = _get_wallet_or_fail(target_wallet_id)

    # Boundary to external exchange service
    exchange_rate = get_exchange_rate(
        source_wallet.currency,
        target_wallet.currency,
    )

    updated_source, updated_target, transaction = apply_exchange(
        source_wallet=source_wallet,
        target_wallet=target_wallet,
        amount=amount,
        fx_rate=exchange_rate,
        transaction_id=str(uuid4()),  # new UUID for the transaction
        now=now,
    )

    update_wallet(updated_source)
    update_wallet(updated_target)
    create_transaction(transaction)

    return updated_source, updated_target, transaction


def _get_wallet_or_fail(wallet_id: str) -> Wallet:
    """
    Helper to load a wallet or raise a service-level error.
    """
    wallet = get_wallet(wallet_id)
    if wallet is None:
        raise ValueError(f"Wallet {wallet_id} not found")
    return wallet
