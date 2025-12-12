from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from unittest.mock import Mock, call

import pytest

from app.domain.enums import Currency, TransactionStatus
from app.domain.exceptions import WalletNotFoundError
from app.domain.models.Transaction import Transaction
from app.domain.models.Wallet import Wallet
from app.services import wallet_service


def test_create_wallet_persists_via_repo(monkeypatch):
    fixed_uuid = UUID("00000000-0000-0000-0000-000000000001")
    monkeypatch.setattr(wallet_service, "uuid4", lambda: fixed_uuid)

    repo_create_mock = Mock()
    monkeypatch.setattr(wallet_service, "repo_create_wallet", repo_create_mock)

    wallet = wallet_service.create_wallet(Currency.DKK, initial_balance=Decimal("12.34"))

    assert wallet.id == str(fixed_uuid)
    assert wallet.currency == Currency.DKK
    assert wallet.balance == Decimal("12.34")
    assert wallet.created_at.tzinfo is not None
    assert wallet.updated_at == wallet.created_at

    repo_create_mock.assert_called_once()
    created_wallet_arg = repo_create_mock.call_args[0][0]
    assert isinstance(created_wallet_arg, Wallet)
    assert created_wallet_arg.id == wallet.id


def test_get_wallet_raises_when_missing(monkeypatch):
    monkeypatch.setattr(wallet_service, "repo_get_wallet", lambda _wallet_id: None)

    with pytest.raises(WalletNotFoundError):
        wallet_service.get_wallet("missing-wallet")


def test_list_wallets_returns_repo_results(monkeypatch, wallet_factory):
    wallets = [wallet_factory(wallet_id="w1"), wallet_factory(wallet_id="w2")]
    monkeypatch.setattr(wallet_service, "repo_get_all_wallets", lambda: wallets)

    assert wallet_service.list_wallets() == wallets


def test_deposit_money_persists_wallet_and_transaction(monkeypatch, wallet_factory):
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

    apply_deposit_mock = Mock(return_value=(updated_wallet, tx))
    monkeypatch.setattr(wallet_service, "apply_deposit", apply_deposit_mock)

    update_wallet_mock = Mock()
    create_tx_mock = Mock()
    monkeypatch.setattr(wallet_service, "update_wallet", update_wallet_mock)
    monkeypatch.setattr(wallet_service, "create_transaction", create_tx_mock)

    returned_wallet, returned_tx = wallet_service.deposit_money(
        wallet_id="w1",
        amount=Decimal("10.00"),
        currency=Currency.DKK,
        now=now,
    )

    assert returned_wallet == updated_wallet
    assert returned_tx == tx

    apply_deposit_mock.assert_called_once()
    kwargs = apply_deposit_mock.call_args.kwargs
    assert kwargs["wallet"] == wallet
    assert kwargs["amount"] == Decimal("10.00")
    assert kwargs["currency"] == Currency.DKK
    assert kwargs["transaction_id"] == str(fixed_uuid)
    assert kwargs["now"] == now

    update_wallet_mock.assert_called_once_with(updated_wallet)
    create_tx_mock.assert_called_once_with(tx)


def test_withdraw_money_persists_wallet_and_transaction(monkeypatch, wallet_factory):
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

    apply_withdraw_mock = Mock(return_value=(updated_wallet, tx))
    monkeypatch.setattr(wallet_service, "apply_withdraw", apply_withdraw_mock)

    update_wallet_mock = Mock()
    create_tx_mock = Mock()
    monkeypatch.setattr(wallet_service, "update_wallet", update_wallet_mock)
    monkeypatch.setattr(wallet_service, "create_transaction", create_tx_mock)

    returned_wallet, returned_tx = wallet_service.withdraw_money(
        wallet_id="w1",
        amount=Decimal("5.00"),
        currency=Currency.DKK,
        now=now,
    )

    assert returned_wallet == updated_wallet
    assert returned_tx == tx

    apply_withdraw_mock.assert_called_once()
    kwargs = apply_withdraw_mock.call_args.kwargs
    assert kwargs["wallet"] == wallet
    assert kwargs["amount"] == Decimal("5.00")
    assert kwargs["currency"] == Currency.DKK
    assert kwargs["transaction_id"] == str(fixed_uuid)
    assert kwargs["now"] == now

    update_wallet_mock.assert_called_once_with(updated_wallet)
    create_tx_mock.assert_called_once_with(tx)


def test_exchange_money_calls_fx_then_persists(monkeypatch, wallet_factory):
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

    get_rate_mock = Mock(return_value=Decimal("2.0"))
    monkeypatch.setattr(wallet_service, "get_exchange_rate", get_rate_mock)

    apply_exchange_mock = Mock(return_value=(updated_source, updated_target, tx))
    monkeypatch.setattr(wallet_service, "apply_exchange", apply_exchange_mock)

    update_wallet_mock = Mock()
    create_tx_mock = Mock()
    monkeypatch.setattr(wallet_service, "update_wallet", update_wallet_mock)
    monkeypatch.setattr(wallet_service, "create_transaction", create_tx_mock)

    returned_source, returned_target, returned_tx = wallet_service.exchange_money(
        source_wallet_id="source",
        target_wallet_id="target",
        amount=Decimal("10.00"),
        now=now,
    )

    assert returned_source == updated_source
    assert returned_target == updated_target
    assert returned_tx == tx

    get_rate_mock.assert_called_once_with(Currency.DKK, Currency.USD)

    apply_exchange_mock.assert_called_once()
    kwargs = apply_exchange_mock.call_args.kwargs
    assert kwargs["source_wallet"] == source
    assert kwargs["target_wallet"] == target
    assert kwargs["amount"] == Decimal("10.00")
    assert kwargs["fx_rate"] == Decimal("2.0")
    assert kwargs["transaction_id"] == str(fixed_uuid)
    assert kwargs["now"] == now

    update_wallet_mock.assert_has_calls([call(updated_source), call(updated_target)])
    create_tx_mock.assert_called_once_with(tx)


def test_list_transactions_raises_when_wallet_missing(monkeypatch):
    monkeypatch.setattr(wallet_service, "repo_get_wallet", lambda _wallet_id: None)

    with pytest.raises(WalletNotFoundError):
        wallet_service.list_transactions("missing")


def test_list_transactions_returns_repo_results_when_wallet_exists(monkeypatch, wallet_factory):
    # Choice: this targets the single uncovered happy-path line in list_transactions.
    # Approach: stub wallet existence (service gate) and stub repo tx retrieval; no DB/network.
    wallet = wallet_factory(wallet_id="w1")
    expected = [Mock(name="tx1"), Mock(name="tx2")]

    monkeypatch.setattr(wallet_service, "repo_get_wallet", lambda _wallet_id: wallet)
    monkeypatch.setattr(wallet_service, "repo_get_transactions", lambda _wallet_id: expected)

    assert wallet_service.list_transactions("w1") == expected
