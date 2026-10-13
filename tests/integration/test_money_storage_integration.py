"""Integration tests for exact money storage (ADR-0004).

Technique: equivalence partitioning on amounts that a binary float cannot
represent exactly (0.10 + 0.20) versus amounts the minor unit cannot hold
(more than two decimal places), run against a real temporary SQLite database.
"""

import sqlite3
from decimal import Decimal

import pytest

from app.domain.enums import Currency, TransactionStatus
from app.domain.models.Transaction import Transaction
from app.repository import transactions_repo, wallets_repo
from tests.integration.helpers import create_wallet, deposit

pytestmark = pytest.mark.integration


def test_wallet_balance_round_trip_is_exact(app_instance, wallet_factory):
    # Arrange: DKK wallet whose balance is 0.10 + 0.20, a sum a float cannot hold
    wallet = wallet_factory(balance=Decimal("0.10") + Decimal("0.20"))

    with app_instance.app_context():
        # Act: save the wallet and load it back
        wallets_repo.create_wallet(wallet)
        reloaded = wallets_repo.get_wallet(wallet.id)

    # Assert: exactly 0.30, with two decimal places
    assert str(reloaded.balance) == "0.30"


def test_wallet_negative_balance_is_refused(app_instance, wallet_factory):
    # Arrange: DKK wallet one øre below zero (boundary: 0.00 is the lowest valid balance)
    wallet = wallet_factory(balance=Decimal("-0.01"))

    with app_instance.app_context():
        # Act + Assert: the database refuses the row through CHECK (balance >= 0)
        with pytest.raises(sqlite3.IntegrityError):
            wallets_repo.create_wallet(wallet)


# Transactions whose amount is 0.10 + 0.20, built at a fixed timestamp
TRANSACTION_CASES = pytest.mark.parametrize(
    "build_transaction",
    [
        # deposit: credited amount, credited currency and source balance stay None
        lambda now: Transaction.deposit(
            transaction_id="tx-deposit",
            wallet_id="wallet-dkk",
            amount=Decimal("0.10") + Decimal("0.20"),
            currency=Currency.DKK,
            status=TransactionStatus.COMPLETED,
            error_code=None,
            created_at=now,
            target_balance_after=Decimal("0.30"),
        ),
        # exchange: every amount column holds a value, in two currencies
        lambda now: Transaction.exchange(
            transaction_id="tx-exchange",
            source_wallet_id="wallet-dkk",
            target_wallet_id="wallet-eur",
            amount=Decimal("0.10") + Decimal("0.20"),
            source_currency=Currency.DKK,
            credited_amount=Decimal("0.04"),
            credited_currency=Currency.EUR,
            source_balance_after=Decimal("10.50"),
            target_balance_after=Decimal("0.04"),
            status=TransactionStatus.COMPLETED,
            error_code=None,
            created_at=now,
        ),
    ],
    ids=["deposit", "exchange"],
)


@TRANSACTION_CASES
def test_transaction_round_trip_keeps_every_field(app_instance, get_fixed_timestamp, build_transaction):
    # Arrange: a transaction whose amount is 0.10 + 0.20
    transaction = build_transaction(get_fixed_timestamp)

    with app_instance.app_context():
        # Act: save the transaction and load it back
        transactions_repo.create_transaction(transaction)
        reloaded = transactions_repo.get_transaction(transaction.id)

    # Assert: every field comes back with the value it was saved with
    assert reloaded == transaction


@TRANSACTION_CASES
def test_transaction_round_trip_amount_is_exact(app_instance, get_fixed_timestamp, build_transaction):
    # Arrange: a transaction whose amount is 0.10 + 0.20
    transaction = build_transaction(get_fixed_timestamp)

    with app_instance.app_context():
        # Act: save the transaction and load it back
        transactions_repo.create_transaction(transaction)
        reloaded = transactions_repo.get_transaction(transaction.id)

    # Assert: exactly 0.30, with two decimal places (equality alone accepts 0.3)
    assert str(reloaded.amount) == "0.30"


def test_wallet_balance_with_three_decimals_is_refused(app_instance, wallet_factory):
    # Arrange: DKK wallet with 1.234, one decimal more than the minor unit holds
    wallet = wallet_factory(balance=Decimal("1.234"))

    with app_instance.app_context():
        # Act + Assert: the repository refuses to store an inexact amount
        with pytest.raises(ValueError):
            wallets_repo.create_wallet(wallet)


def test_deposit_twice_balance_is_exact(client):
    # Arrange: empty DKK wallet
    wallet_id = create_wallet(client, "DKK")

    # Act: deposit 0.10, then 0.20, then read the wallet back
    deposit(client, wallet_id, "0.10", "DKK")
    deposit(client, wallet_id, "0.20", "DKK")
    response = client.get(f"/api/wallets/{wallet_id}")

    # Assert: the stored balance is exactly "0.30"
    assert response.status_code == 200
    assert response.get_json()["balance"] == "0.30"


def test_get_wallet_balance_is_decimal_string(client):
    # Arrange: DKK wallet with one deposit of 10.50
    wallet_id = create_wallet(client, "DKK")
    deposit(client, wallet_id, "10.50", "DKK")

    # Act: read the wallet back from the database
    response = client.get(f"/api/wallets/{wallet_id}")

    # Assert: the balance is a decimal string with two decimals, not minor units
    assert response.get_json()["balance"] == "10.50"


def test_list_transactions_amount_is_decimal_string(client):
    # Arrange: DKK wallet with one deposit of 10.50
    wallet_id = create_wallet(client, "DKK")
    deposit(client, wallet_id, "10.50", "DKK")

    # Act: read the wallet's transactions back from the database
    response = client.get(f"/api/wallets/{wallet_id}/transactions")

    # Assert: the amount is a decimal string with two decimals, not minor units
    assert response.get_json()[0]["amount"] == "10.50"
