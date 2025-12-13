from __future__ import annotations
"""Integration tests for the Flask API (vertical slice).

These tests exercise the HTTP layer (Flask test client) and verify persistence via the
repository layer against a real SQLite database created per test by integration fixtures.
The external FX boundary is stubbed (e.g., `fx_rate_stub`) so exchange tests are deterministic.

Scope / intent
- Validate routing + request parsing (status codes and JSON shapes).
- Validate orchestration across routes -> services -> domain rules -> repositories.
- Validate persisted state (wallet balances and transaction records).
- Validate boundary behavior (e.g., FX failure -> 502 and no mutation).

Note: exhaustive input partitioning and boundary cases are covered by unit tests derived
from the black-box test design. Integration tests focus on system wiring and persistence.

Reading the tests
Each test may use short phase comments:
- Arrange: scenario preconditions
- Act: the API call under test
- Assert (API): HTTP status + JSON contract/fields/codes
- Assert (DB): persisted state within `with app_instance.app_context():`
Unused phases are omitted.

Run:
    python -m pytest -m integration
"""

from decimal import Decimal

import pytest

from app.domain.enums import Currency, TransactionStatus, TransactionType
from app.repository.transactions_repo import get_transactions_for_wallet
from app.repository.wallets_repo import get_wallet
from tests.integration.helpers import create_wallet, deposit, exchange, withdraw


# --- Wallet endpoints ---


@pytest.mark.integration
def test_create_wallet_persists_row(client, app_instance):
    # Act: create wallet via API
    wallet_id = create_wallet(client, "DKK")

    # Assert (DB): wallet row persisted
    with app_instance.app_context():
        wallet = get_wallet(wallet_id)
        assert wallet.id == wallet_id
        assert wallet.currency.value == "DKK"
        assert wallet.balance == Decimal("0.00")


@pytest.mark.integration
def test_list_wallets_includes_created_wallet(client):
    # Arrange: create wallet
    created_wallet_id = create_wallet(client, "EUR")

    # Act: list wallets via API
    response = client.get("/api/wallets")

    # Assert (API): 200 + created wallet appears
    assert response.status_code == 200
    wallets = response.get_json()
    assert isinstance(wallets, list)

    returned_ids = {wallet["id"] for wallet in wallets}
    assert created_wallet_id in returned_ids


# --- Deposit / Withdraw ---


@pytest.mark.integration
def test_deposit_success_persists_wallet_and_transaction(client, app_instance):
    # Arrange: create wallet
    wallet_id = create_wallet(client, "DKK")

    # Act: deposit via API
    response = deposit(client, wallet_id, "10.00", "DKK")

    # Assert (API): 200 + payload fields
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["wallet"]["id"] == wallet_id
    assert body["wallet"]["balance"] == "10.00"
    assert body["transaction"]["type"] == TransactionType.DEPOSIT.value
    assert body["transaction"]["status"] == TransactionStatus.COMPLETED.value
    assert body["transaction"]["error_code"] is None

    # Assert (DB): wallet updated + tx persisted
    with app_instance.app_context():
        persisted_wallet = get_wallet(wallet_id)
        assert persisted_wallet.balance == Decimal("10.00")

        transactions = get_transactions_for_wallet(wallet_id)
        assert len(transactions) == 1
        assert transactions[0].status == TransactionStatus.COMPLETED


@pytest.mark.integration
def test_withdraw_insufficient_funds_records_failed_transaction(client, app_instance):
    # Arrange: create wallet with zero balance
    wallet_id = create_wallet(client, "DKK")

    # Act: withdraw via API
    response = withdraw(client, wallet_id, "1.00", "DKK")

    # Assert (API): 422 + error code
    assert response.status_code == 422
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["transaction"]["status"] == TransactionStatus.FAILED.value
    assert body["transaction"]["error_code"] == "INSUFFICIENT_FUNDS"

    # Assert (DB): balance unchanged + failed tx persisted
    with app_instance.app_context():
        persisted_wallet = get_wallet(wallet_id)
        assert persisted_wallet.balance == Decimal("0.00")

        transactions = get_transactions_for_wallet(wallet_id)
        assert len(transactions) == 1
        assert transactions[0].status == TransactionStatus.FAILED
        assert transactions[0].error_code.value == "INSUFFICIENT_FUNDS"


@pytest.mark.integration
@pytest.mark.parametrize(
    "endpoint, payload",
    [
        ("deposit", {"amount": "abc", "currency": "DKK"}),
        ("withdraw", {"amount": "abc", "currency": "DKK"}),
    ],
)
def test_deposit_withdraw_invalid_amount_returns_400_json(client, endpoint, payload):
    wallet_id = create_wallet(client, "DKK")

    response = client.post(f"/api/wallets/{wallet_id}/{endpoint}", json=payload)

    assert response.status_code == 400
    body = response.get_json()
    assert isinstance(body, dict)
    assert "error" in body
    assert body["error"] == "Invalid amount"


@pytest.mark.integration
def test_exchange_invalid_amount_returns_400_json(client):
    source_wallet_id = create_wallet(client, "DKK")
    target_wallet_id = create_wallet(client, "USD")

    response = exchange(client, source_wallet_id, target_wallet_id, "abc")

    assert response.status_code == 400
    body = response.get_json()
    assert isinstance(body, dict)
    assert "error" in body
    assert body["error"] == "Invalid amount"


# --- Exchange ---


@pytest.mark.integration
def test_exchange_success_updates_both_wallets(client, app_instance, fx_rate_stub):
    """Verify end-to-end exchange wiring updates balances and records an exchange tx."""

    # Arrange: create wallets + seed source balance
    source_wallet_id = create_wallet(client, "DKK")
    target_wallet_id = create_wallet(client, "USD")

    deposit(client, source_wallet_id, "100.00", "DKK")

    # Act: exchange via API
    response = exchange(client, source_wallet_id, target_wallet_id, "10.00")

    # Assert (API): 200 + balances + tx fields
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, dict)

    assert body["source_wallet"]["balance"] == "90.00"
    assert Decimal(body["target_wallet"]["balance"]) == Decimal("20.00")
    assert body["transaction"]["type"] == TransactionType.EXCHANGE.value
    assert body["transaction"]["status"] == TransactionStatus.COMPLETED.value

    # Assert (DB): both wallets updated + exchange tx persisted
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

    # Arrange: create wallets + seed source balance
    source_wallet_id = create_wallet(client, "DKK")
    target_wallet_id = create_wallet(client, "USD")

    deposit(client, source_wallet_id, "100.00", "DKK")

    # Act: exchange via API
    response = exchange(client, source_wallet_id, target_wallet_id, "10.00")

    # Assert (API): 200
    assert response.status_code == 200

    # Assert (DB): exchange tx fields persisted
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

    # Arrange: create wallets + seed source balance
    source_wallet_id = create_wallet(client, "DKK")
    target_wallet_id = create_wallet(client, "USD")

    deposit(client, source_wallet_id, "10.00", "DKK")

    # Act: exchange via API
    response = exchange(client, source_wallet_id, target_wallet_id, "5.00")

    # Assert (API): 502 + error payload
    assert response.status_code == 502
    body = response.get_json()
    assert isinstance(body, dict)
    assert "error" in body

    # Assert (DB): balances unchanged + no exchange tx
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
    # Arrange: create wallet + create transactions
    wallet_id = create_wallet(client, "DKK")

    deposit(client, wallet_id, "10.00", "DKK")
    withdraw(client, wallet_id, "2.00", "DKK")

    # Act: list transactions via API
    response = client.get(f"/api/wallets/{wallet_id}/transactions")

    # Assert (API): 200 + list contract
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
