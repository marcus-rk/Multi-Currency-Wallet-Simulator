from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.enums import Currency, TransactionStatus, TransactionType
from app.repository.transactions_repo import get_transactions_for_wallet
from app.repository.wallets_repo import get_wallet
from tests.integration.helpers import create_wallet, deposit, exchange, withdraw


# --- Wallet endpoints ---


@pytest.mark.integration
def test_create_wallet_persists_row(client, app_instance):
    wallet_id = create_wallet(client, "DKK")

    with app_instance.app_context():
        wallet = get_wallet(wallet_id)
        assert wallet.id == wallet_id
        assert wallet.currency.value == "DKK"
        assert wallet.balance == Decimal("0.00")


@pytest.mark.integration
def test_list_wallets_includes_created_wallet(client):
    created_wallet_id = create_wallet(client, "EUR")

    response = client.get("/api/wallets")
    assert response.status_code == 200
    wallets = response.get_json()
    assert isinstance(wallets, list)

    returned_ids = {wallet["id"] for wallet in wallets}
    assert created_wallet_id in returned_ids


# --- Deposit / Withdraw ---


@pytest.mark.integration
def test_deposit_success_persists_wallet_and_transaction(client, app_instance):
    wallet_id = create_wallet(client, "DKK")

    response = deposit(client, wallet_id, "10.00", "DKK")
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["wallet"]["id"] == wallet_id
    assert body["wallet"]["balance"] == "10.00"
    assert body["transaction"]["type"] == TransactionType.DEPOSIT.value
    assert body["transaction"]["status"] == TransactionStatus.COMPLETED.value
    assert body["transaction"]["error_code"] is None

    with app_instance.app_context():
        persisted_wallet = get_wallet(wallet_id)
        assert persisted_wallet.balance == Decimal("10.00")

        transactions = get_transactions_for_wallet(wallet_id)
        assert len(transactions) == 1
        assert transactions[0].status == TransactionStatus.COMPLETED


@pytest.mark.integration
def test_withdraw_insufficient_funds_records_failed_transaction(client, app_instance):
    wallet_id = create_wallet(client, "DKK")

    response = withdraw(client, wallet_id, "1.00", "DKK")
    assert response.status_code == 422
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["transaction"]["status"] == TransactionStatus.FAILED.value
    assert body["transaction"]["error_code"] == "INSUFFICIENT_FUNDS"

    with app_instance.app_context():
        persisted_wallet = get_wallet(wallet_id)
        assert persisted_wallet.balance == Decimal("0.00")

        transactions = get_transactions_for_wallet(wallet_id)
        assert len(transactions) == 1
        assert transactions[0].status == TransactionStatus.FAILED
        assert transactions[0].error_code.value == "INSUFFICIENT_FUNDS"


# --- Exchange ---


@pytest.mark.integration
def test_exchange_success_updates_both_wallets(client, app_instance, fx_rate_stub):
    """Verify end-to-end exchange wiring updates balances and records an exchange tx."""

    source_wallet_id = create_wallet(client, "DKK")
    target_wallet_id = create_wallet(client, "USD")

    deposit(client, source_wallet_id, "100.00", "DKK")

    response = exchange(client, source_wallet_id, target_wallet_id, "10.00")
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["source_wallet"]["balance"] == "90.00"
    assert Decimal(body["target_wallet"]["balance"]) == Decimal("20.00")
    assert body["transaction"]["type"] == TransactionType.EXCHANGE.value
    assert body["transaction"]["status"] == TransactionStatus.COMPLETED.value

    with app_instance.app_context():
        persisted_source = get_wallet(source_wallet_id)
        persisted_target = get_wallet(target_wallet_id)
        assert persisted_source.balance == Decimal("90.00")
        assert persisted_target.balance == Decimal("20.00")

        source_transactions = get_transactions_for_wallet(source_wallet_id)
        assert len(source_transactions) == 2  # deposit + exchange

        exchange_transactions = [
            tx for tx in source_transactions if tx.type == TransactionType.EXCHANGE
        ]
        assert len(exchange_transactions) == 1


@pytest.mark.integration
def test_exchange_success_persists_expected_transaction_fields(
    client, app_instance, fx_rate_stub
):
    """Verify persisted exchange tx contains core accounting fields."""

    source_wallet_id = create_wallet(client, "DKK")
    target_wallet_id = create_wallet(client, "USD")

    deposit(client, source_wallet_id, "100.00", "DKK")

    response = exchange(client, source_wallet_id, target_wallet_id, "10.00")
    assert response.status_code == 200

    with app_instance.app_context():
        source_transactions = get_transactions_for_wallet(source_wallet_id)
        assert len(source_transactions) == 2  # deposit + exchange
        exchange_transactions = [
            tx for tx in source_transactions if tx.type == TransactionType.EXCHANGE
        ]
        assert len(exchange_transactions) == 1

        exchange_tx = exchange_transactions[0]
        assert exchange_tx.status == TransactionStatus.COMPLETED
        assert exchange_tx.error_code is None
        assert exchange_tx.source_wallet_id == source_wallet_id
        assert exchange_tx.target_wallet_id == target_wallet_id
        assert exchange_tx.amount == Decimal("10.00")
        assert exchange_tx.currency == Currency.DKK
        assert exchange_tx.credited_amount == Decimal("20.00")
        assert exchange_tx.credited_currency == Currency.USD
        assert exchange_tx.source_balance_after == Decimal("90.00")
        assert exchange_tx.target_balance_after == Decimal("20.00")


@pytest.mark.integration
def test_exchange_fx_failure_returns_502_and_does_not_change_wallets(
    client, app_instance, fx_rate_fail_stub
):
    """External FX failure returns 502 and must not mutate balances."""
    
    source_wallet_id = create_wallet(client, "DKK")
    target_wallet_id = create_wallet(client, "USD")

    deposit(client, source_wallet_id, "10.00", "DKK")

    response = exchange(client, source_wallet_id, target_wallet_id, "5.00")
    assert response.status_code == 502
    body = response.get_json()
    assert isinstance(body, dict)
    assert "error" in body

    with app_instance.app_context():
        persisted_source = get_wallet(source_wallet_id)
        persisted_target = get_wallet(target_wallet_id)
        assert persisted_source.balance == Decimal("10.00")
        assert persisted_target.balance == Decimal("0.00")

        # Current behavior: exchange fails before apply_exchange(), so only deposit tx exists
        source_transactions = get_transactions_for_wallet(source_wallet_id)
        assert len(source_transactions) == 1


# --- Transactions ---


@pytest.mark.integration
def test_list_transactions_returns_expected_items(client, app_instance):
    wallet_id = create_wallet(client, "DKK")

    deposit(client, wallet_id, "10.00", "DKK")
    withdraw(client, wallet_id, "2.00", "DKK")

    response = client.get(f"/api/wallets/{wallet_id}/transactions")
    assert response.status_code == 200
    transactions_payload = response.get_json()

    assert isinstance(transactions_payload, list)
    assert len(transactions_payload) == 2
    assert all(
        isinstance(tx, dict) and "id" in tx and "status" in tx
        for tx in transactions_payload
    )
    assert {tx["type"] for tx in transactions_payload} == {
        TransactionType.DEPOSIT.value,
        TransactionType.WITHDRAWAL.value,
    }
