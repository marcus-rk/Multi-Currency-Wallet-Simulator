from __future__ import annotations
"""
White-box unit tests for the service layer (wallet_service).

What these tests are
--------------------
Coverage-guided tests: they are derived from code structure (white-box),
aiming to exercise missed statements and decision/branch outcomes.

Layer under test
----------------
Service orchestration:
- loads wallets via repository functions
- delegates business rules to domain rule functions (apply_deposit/withdraw/exchange)
- persists results (update_wallet/create_transaction)
- returns updated objects

Why stubs/captures are used (and why this is NOT "mock-everything")
-------------------------------------------------------------------
The service layer's observable behavior includes *orchestration* and
*persistence intent*. Persistence is not visible via return values alone,
so we use lightweight "capture" stubs to record what would be persisted.

Philosophy
----------
Hybrid:
- Classicist on outcomes (returned wallet/tx objects and raised exceptions)
- Minimal boundary stubbing (repos/FX) to keep tests deterministic and fast
- Avoid brittle call-count expectations; prefer asserting captured values.

How to read each test
---------------------
Arrange: stub repo + rule functions to force a specific branch/path
Act: call exactly one service function
Assert: verify returned objects / exceptions and captured persisted objects
"""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest

from app.domain.enums import Currency, TransactionStatus
from app.domain.exceptions import WalletNotFoundError
from app.domain.models.Transaction import Transaction
from app.domain.models.Wallet import Wallet
from app.services import wallet_service


def test_create_wallet_persists_via_repo(monkeypatch):
    # Arrange: deterministic id and capture persistence intent
    fixed_uuid = UUID("00000000-0000-0000-0000-000000000001")
    monkeypatch.setattr(wallet_service, "uuid4", lambda: fixed_uuid)

    persisted: dict[str, object] = {"wallet": None, "transaction": None, "wallets": []}

    def persist_created_wallet(created_wallet: Wallet) -> None:
        persisted["wallet"] = created_wallet

    monkeypatch.setattr(wallet_service, "repo_create_wallet", persist_created_wallet)

    # Act: create wallet
    wallet = wallet_service.create_wallet(Currency.DKK, initial_balance=Decimal("12.34"))

    # Assert: returned wallet has expected invariants
    assert wallet.id == str(fixed_uuid)
    assert wallet.currency == Currency.DKK
    assert wallet.balance == Decimal("12.34")
    assert wallet.created_at is not None
    assert wallet.updated_at == wallet.created_at

    # Assert (persistence intent): created wallet was persisted
    assert persisted["wallet"] == wallet


def test_get_wallet_raises_when_missing(monkeypatch):
    # Arrange: missing wallet in repository
    monkeypatch.setattr(wallet_service, "repo_get_wallet", lambda _wallet_id: None)

    # Act + Assert: service raises service-level error
    with pytest.raises(WalletNotFoundError):
        wallet_service.get_wallet("missing-wallet")


def test_list_wallets_returns_repo_results(monkeypatch, wallet_factory):
    # Arrange: repo returns wallets
    wallets = [wallet_factory(wallet_id="w1"), wallet_factory(wallet_id="w2")]
    monkeypatch.setattr(wallet_service, "repo_get_all_wallets", lambda: wallets)

    # Act: list wallets
    result = wallet_service.list_wallets()

    # Assert: service returns repo list
    assert result == wallets


def test_deposit_money_persists_wallet_and_transaction(monkeypatch, wallet_factory):
    # Arrange: wallet exists and rule returns an updated wallet + transaction
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    fixed_uuid = UUID("00000000-0000-0000-0000-000000000002")

    wallet = wallet_factory(wallet_id="w1", balance=Decimal("0.00"), currency=Currency.DKK)
    updated_wallet = wallet_factory(wallet_id="w1", balance=Decimal("10.00"), currency=Currency.DKK)
    tx = Transaction.deposit(
        transaction_id="tx-deposit",
        wallet_id="w1",
        amount=Decimal("10.00"),
        currency=Currency.DKK,
        status=TransactionStatus.COMPLETED,
        error_code=None,
        created_at=now,
        target_balance_after=Decimal("10.00"),
    )

    monkeypatch.setattr(wallet_service, "uuid4", lambda: fixed_uuid)
    monkeypatch.setattr(wallet_service, "repo_get_wallet", lambda _wallet_id: wallet)

    monkeypatch.setattr(wallet_service, "apply_deposit", lambda **_kwargs: (updated_wallet, tx))

    persisted: dict[str, object] = {"wallet": None, "transaction": None, "wallets": []}

    def persist_wallet(w: Wallet) -> None:
        persisted["wallet"] = w

    def persist_transaction(t: Transaction) -> None:
        persisted["transaction"] = t

    monkeypatch.setattr(wallet_service, "update_wallet", persist_wallet)
    monkeypatch.setattr(wallet_service, "create_transaction", persist_transaction)

    # Act: deposit money
    returned_wallet, returned_tx = wallet_service.deposit_money(
        wallet_id="w1",
        amount=Decimal("10.00"),
        currency=Currency.DKK,
        now=now,
    )

    # Assert: service returns rule outputs
    assert returned_wallet == updated_wallet
    assert returned_tx == tx

    # Assert (persistence intent): updated wallet + transaction were persisted
    assert persisted["wallet"] == updated_wallet
    assert persisted["transaction"] == tx


def test_withdraw_money_persists_wallet_and_transaction(monkeypatch, wallet_factory):
    # Arrange: wallet exists and rule returns an updated wallet + transaction
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    fixed_uuid = UUID("00000000-0000-0000-0000-000000000003")

    wallet = wallet_factory(wallet_id="w1", balance=Decimal("10.00"), currency=Currency.DKK)
    updated_wallet = wallet_factory(wallet_id="w1", balance=Decimal("5.00"), currency=Currency.DKK)
    tx = Transaction.withdrawal(
        transaction_id="tx-withdraw",
        wallet_id="w1",
        amount=Decimal("5.00"),
        currency=Currency.DKK,
        status=TransactionStatus.COMPLETED,
        error_code=None,
        created_at=now,
        source_balance_after=Decimal("5.00"),
    )

    monkeypatch.setattr(wallet_service, "uuid4", lambda: fixed_uuid)
    monkeypatch.setattr(wallet_service, "repo_get_wallet", lambda _wallet_id: wallet)

    monkeypatch.setattr(wallet_service, "apply_withdraw", lambda **_kwargs: (updated_wallet, tx))

    persisted: dict[str, object] = {"wallet": None, "transaction": None, "wallets": []}

    def persist_wallet(w: Wallet) -> None:
        persisted["wallet"] = w

    def persist_transaction(t: Transaction) -> None:
        persisted["transaction"] = t

    monkeypatch.setattr(wallet_service, "update_wallet", persist_wallet)
    monkeypatch.setattr(wallet_service, "create_transaction", persist_transaction)

    # Act: withdraw money
    returned_wallet, returned_tx = wallet_service.withdraw_money(
        wallet_id="w1",
        amount=Decimal("5.00"),
        currency=Currency.DKK,
        now=now,
    )

    # Assert: service returns rule outputs
    assert returned_wallet == updated_wallet
    assert returned_tx == tx

    # Assert (persistence intent): updated wallet + transaction were persisted
    assert persisted["wallet"] == updated_wallet
    assert persisted["transaction"] == tx


def test_exchange_money_calls_fx_then_persists(monkeypatch, wallet_factory):
    # Arrange: two wallets exist and rule returns updated wallets + transaction
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    fixed_uuid = UUID("00000000-0000-0000-0000-000000000004")

    source = wallet_factory(wallet_id="source", balance=Decimal("100.00"), currency=Currency.DKK)
    target = wallet_factory(wallet_id="target", balance=Decimal("0.00"), currency=Currency.USD)

    updated_source = wallet_factory(wallet_id="source", balance=Decimal("90.00"), currency=Currency.DKK)
    updated_target = wallet_factory(wallet_id="target", balance=Decimal("20.00"), currency=Currency.USD)

    tx = Transaction.exchange(
        transaction_id="tx-exchange",
        source_wallet_id="source",
        target_wallet_id="target",
        amount=Decimal("10.00"),
        source_currency=Currency.DKK,
        credited_amount=Decimal("20.00"),
        credited_currency=Currency.USD,
        source_balance_after=Decimal("90.00"),
        target_balance_after=Decimal("20.00"),
        status=TransactionStatus.COMPLETED,
        error_code=None,
        created_at=now,
    )

    monkeypatch.setattr(wallet_service, "uuid4", lambda: fixed_uuid)

    def fake_repo_get_wallet(wallet_id: str):
        return {"source": source, "target": target}.get(wallet_id)

    monkeypatch.setattr(wallet_service, "repo_get_wallet", fake_repo_get_wallet)

    monkeypatch.setattr(wallet_service, "get_exchange_rate", lambda _src, _dst: Decimal("2.0"))
    monkeypatch.setattr(wallet_service, "apply_exchange", lambda **_kwargs: (updated_source, updated_target, tx))

    persisted: dict[str, object] = {"wallet": None, "transaction": None, "wallets": []}

    def persist_wallet(w: Wallet) -> None:
        persisted["wallets"].append(w)

    def persist_transaction(t: Transaction) -> None:
        persisted["transaction"] = t

    monkeypatch.setattr(wallet_service, "update_wallet", persist_wallet)
    monkeypatch.setattr(wallet_service, "create_transaction", persist_transaction)

    # Act: exchange money
    returned_source, returned_target, returned_tx = wallet_service.exchange_money(
        source_wallet_id="source",
        target_wallet_id="target",
        amount=Decimal("10.00"),
        now=now,
    )

    # Assert: service returns rule outputs
    assert returned_source == updated_source
    assert returned_target == updated_target
    assert returned_tx == tx

    # Assert (persistence intent): both wallets + transaction were persisted
    assert persisted["wallets"] == [updated_source, updated_target]
    assert persisted["transaction"] == tx


def test_list_transactions_raises_when_wallet_missing(monkeypatch):
    # Arrange: missing wallet in repository
    monkeypatch.setattr(wallet_service, "repo_get_wallet", lambda _wallet_id: None)

    # Act + Assert: service raises service-level error
    with pytest.raises(WalletNotFoundError):
        wallet_service.list_transactions("missing")


def test_list_transactions_returns_repo_results_when_wallet_exists(monkeypatch, wallet_factory):
    # Arrange: wallet exists and repo returns transactions
    wallet = wallet_factory(wallet_id="w1")
    expected = [object(), object()]

    monkeypatch.setattr(wallet_service, "repo_get_wallet", lambda _wallet_id: wallet)
    monkeypatch.setattr(wallet_service, "repo_get_transactions", lambda _wallet_id: expected)

    # Act: list transactions
    result = wallet_service.list_transactions("w1")

    # Assert: service returns repo list
    assert result == expected
