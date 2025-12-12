from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.enums import TransactionStatus, TransactionType, Currency
from app.repository.wallets_repo import get_wallet
from app.repository.transactions_repo import get_transactions_for_wallet


def _create_wallet(client, currency: str = "DKK") -> str:
    response = client.post("/api/wallets", json={"currency": currency})
    assert response.status_code == 201
    wallet_payload = response.get_json()
    assert isinstance(wallet_payload, dict)
    assert "id" in wallet_payload
    return wallet_payload["id"]


def _deposit(client, wallet_id: str, amount: str, currency: str):
    return client.post(
        f"/api/wallets/{wallet_id}/deposit",
        json={"amount": amount, "currency": currency},
    )


def _withdraw(client, wallet_id: str, amount: str, currency: str):
    return client.post(
        f"/api/wallets/{wallet_id}/withdraw",
        json={"amount": amount, "currency": currency},
    )


@pytest.mark.integration
def test_create_wallet_persists_row(client, app_instance):
    wallet_id = _create_wallet(client, "DKK")

    with app_instance.app_context():
        wallet = get_wallet(wallet_id)
        assert wallet.id == wallet_id
        assert wallet.currency.value == "DKK"
        assert wallet.balance == Decimal("0.00")


@pytest.mark.integration
def test_list_wallets_includes_created_wallet(client):
    created_wallet_id = _create_wallet(client, "EUR")

    response = client.get("/api/wallets")
    assert response.status_code == 200
    wallets = response.get_json()
    assert isinstance(wallets, list)

    returned_ids = {wallet["id"] for wallet in wallets}
    assert created_wallet_id in returned_ids


@pytest.mark.integration
def test_deposit_success_persists_wallet_and_transaction(client, app_instance):
    wallet_id = _create_wallet(client, "DKK")

    response = _deposit(client, wallet_id, "10.00", "DKK")
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["wallet"]["id"] == wallet_id
    assert body["wallet"]["balance"] == "10.00"
    assert body["transaction"]["type"] == "DEPOSIT"
    assert body["transaction"]["status"] == "COMPLETED"
    assert body["transaction"]["error_code"] is None

    with app_instance.app_context():
        persisted_wallet = get_wallet(wallet_id)
        assert persisted_wallet.balance == Decimal("10.00")

        transactions = get_transactions_for_wallet(wallet_id)
        assert len(transactions) == 1
        assert transactions[0].status == TransactionStatus.COMPLETED


@pytest.mark.integration
def test_withdraw_insufficient_funds_records_failed_transaction(client, app_instance):
    wallet_id = _create_wallet(client, "DKK")

    response = _withdraw(client, wallet_id, "1.00", "DKK")
    assert response.status_code == 422
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["transaction"]["status"] == "FAILED"
    assert body["transaction"]["error_code"] == "INSUFFICIENT_FUNDS"

    with app_instance.app_context():
        persisted_wallet = get_wallet(wallet_id)
        assert persisted_wallet.balance == Decimal("0.00")

        transactions = get_transactions_for_wallet(wallet_id)
        assert len(transactions) == 1
        assert transactions[0].status == TransactionStatus.FAILED
        assert transactions[0].error_code.value == "INSUFFICIENT_FUNDS"


@pytest.mark.integration
def test_exchange_success_updates_both_wallets(client, app_instance, fx_rate_stub):
    source_wallet_id = _create_wallet(client, "DKK")
    target_wallet_id = _create_wallet(client, "USD")

    _deposit(client, source_wallet_id, "100.00", "DKK")

    response = client.post(
        "/api/wallets/exchange",
        json={
            "source_wallet_id": source_wallet_id,
            "target_wallet_id": target_wallet_id,
            "amount": "10.00",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["source_wallet"]["balance"] == "90.00"
    assert Decimal(body["target_wallet"]["balance"]) == Decimal("20.00")
    assert body["transaction"]["type"] == "EXCHANGE"
    assert body["transaction"]["status"] == "COMPLETED"

    with app_instance.app_context():
        persisted_source = get_wallet(source_wallet_id)
        persisted_target = get_wallet(target_wallet_id)
        assert persisted_source.balance == Decimal("90.00")
        assert persisted_target.balance == Decimal("20.00")

        source_transactions = get_transactions_for_wallet(source_wallet_id)
        assert len(source_transactions) == 2  # deposit + exchange

        latest_transaction = source_transactions[0]
        assert latest_transaction.type == TransactionType.EXCHANGE
        assert latest_transaction.status == TransactionStatus.COMPLETED
        assert latest_transaction.error_code is None
        assert latest_transaction.source_wallet_id == source_wallet_id
        assert latest_transaction.target_wallet_id == target_wallet_id
        assert latest_transaction.amount == Decimal("10.00")
        assert latest_transaction.currency == Currency.DKK
        assert latest_transaction.credited_amount == Decimal("20.00")
        assert latest_transaction.credited_currency == Currency.USD
        assert latest_transaction.source_balance_after == Decimal("90.00")
        assert latest_transaction.target_balance_after == Decimal("20.00")


@pytest.mark.integration
def test_exchange_fx_failure_returns_502_and_does_not_change_wallets(
    client, app_instance, fx_rate_fail_stub
):
    source_wallet_id = _create_wallet(client, "DKK")
    target_wallet_id = _create_wallet(client, "USD")

    _deposit(client, source_wallet_id, "10.00", "DKK")

    response = client.post(
        "/api/wallets/exchange",
        json={
            "source_wallet_id": source_wallet_id,
            "target_wallet_id": target_wallet_id,
            "amount": "5.00",
        },
    )
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


@pytest.mark.integration
def test_list_transactions_returns_expected_items(client, app_instance):
    wallet_id = _create_wallet(client, "DKK")

    _deposit(client, wallet_id, "10.00", "DKK")
    _withdraw(client, wallet_id, "2.00", "DKK")

    response = client.get(f"/api/wallets/{wallet_id}/transactions")
    assert response.status_code == 200
    transactions_payload = response.get_json()

    assert isinstance(transactions_payload, list)
    assert len(transactions_payload) == 2
    assert {tx["type"] for tx in transactions_payload} == {"DEPOSIT", "WITHDRAWAL"}
