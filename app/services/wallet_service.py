from datetime import datetime
from decimal import Decimal
from app.domain.rules.deposit import apply_deposit
from app.repository.wallets_repo import wallets_repo
from app.repository.transactions_repo import transactions_repo


def deposit_money(
    db,
    wallet_id: str,
    amount: Decimal,
    currency: str,
    now: datetime,
    transaction_id: str,
):
    wallet = wallets_repo.get_wallet(db, wallet_id)
    if wallet is None:
        raise ValueError("Wallet not found")

    result = apply_deposit(wallet, amount, currency, transaction_id, now)
    updated_wallet = result["updated_wallet"]
    transaction = result["transaction"]

    wallets_repo.save_wallet(db, updated_wallet)
    transactions_repo.insert_transaction(db, transaction)

    return transaction
