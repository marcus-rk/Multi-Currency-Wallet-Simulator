from datetime import datetime
from decimal import Decimal

from ..models.Transaction import Transaction
from ..models.Wallet import Wallet

def apply_deposit(
    wallet: Wallet,
    amount: Decimal,
    currency: str,
    transaction_id: str,
    now: datetime,
) -> dict:
    """
    Pure domain rule for deposits.

    - Does not talk to DB or external services.
    - Does not mutate the input wallet.
    - Returns (updated_wallet, transaction).
    """
    # Common transaction fields
    base_tx = {
        "id": transaction_id,
        "type": "deposit",              # TxType
        "source_wallet_id": None,       # deposit has only a target
        "target_wallet_id": wallet.id,
        "amount": amount,
        "credited_amount": amount,      # same as amount for deposit
        "currency": currency,
        "created_at": now,
    }

    # 1) Check wallet status (must be ACTIVE)
    if wallet.status != "ACTIVE":
        transaction = Transaction(
            status="failed",
            error_code="INVALID_WALLET_STATE",
            **base_tx,
        )
        # No state change
        return {"updated_wallet": wallet, "transaction": transaction}

    # 2) Check amount (must be > 0)
    if amount <= Decimal("0"):
        transaction = Transaction(
            status="failed",
            error_code="INVALID_AMOUNT",
            **base_tx,
        )
        return {"updated_wallet": wallet, "transaction": transaction}

    # 3) Check currency (must match wallet currency)
    if currency != wallet.currency:
        transaction = Transaction(
            status="failed",
            error_code="UNSUPPORTED_CURRENCY",
            **base_tx,
        )
        return {"updated_wallet": wallet, "transaction": transaction}

    # 4) All good → apply deposit
    updated_wallet = Wallet(
        id=wallet.id,
        currency=wallet.currency,
        balance=wallet.balance + amount,
        status=wallet.status,
        created_at=wallet.created_at,
        updated_at=now,
    )

    transaction = Transaction(
        status="completed",
        error_code=None,
        **base_tx,
    )

    return {"updated_wallet": updated_wallet, "transaction": transaction}