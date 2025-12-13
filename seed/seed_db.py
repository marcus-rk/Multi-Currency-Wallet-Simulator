
"""Database seeding script.

Goal
  Populate the default SQLite database with a small, meaningful dataset so the
  UI isn't empty on first run.

Characteristics
  - Simple, dependency-free (no external FX API calls)
  - Seeds 5–10 wallets across ACTIVE/FROZEN/CLOSED
  - Seeds a mix of DEPOSIT/WITHDRAWAL/EXCHANGE/STATUS_CHANGE transactions
  - Includes a few FAILED transactions to showcase error states

Usage
  python seed/seed_db.py
  python seed/seed_db.py --reset
  python seed/seed_db.py --force
  python seed/seed_db.py --db /path/to/wallet.db --reset
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

# Allow running as a script: `python seed/seed_db.py`
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

from app import create_app
from app.database import get_db, init_schema
from app.domain.enums import Currency, WalletStatus
from app.domain.models.Wallet import Wallet
from app.domain.rules import apply_deposit, apply_withdraw, apply_exchange, apply_status_change
from app.repository.wallets_repo import create_wallet as repo_create_wallet, update_wallet
from app.repository.transactions_repo import create_transaction


@dataclass(frozen=True)
class SeedWallet:
	name: str
	wallet_id: str
	currency: Currency


def _db_path_from_args(db_path: str | None) -> str | None:
	if db_path:
		return os.path.abspath(db_path)
	return None


def _default_project_db_path() -> str:
	return os.path.join(REPO_ROOT, "instance", "wallet.db")


def _choose_db_path(arg_db: str | None) -> str:
	"""Choose a usable DB path.

	- If --db is provided, always use it.
	- Else, prefer $DATABASE only if its parent dir exists (avoids committed
	  placeholder values like /absolute/path/to/instance/wallet.db).
	- Else, fall back to ./instance/wallet.db.
	"""
	if arg_db:
		return arg_db

	env_db = os.getenv("DATABASE")
	if env_db:
		env_db_abs = os.path.abspath(env_db)
		parent = os.path.dirname(env_db_abs)
		if os.path.isdir(parent):
			return env_db_abs

	return _default_project_db_path()


def _reset_db_file(db_path: str) -> None:
	os.makedirs(os.path.dirname(db_path), exist_ok=True)
	if os.path.exists(db_path):
		os.remove(db_path)


def _table_count(table_name: str) -> int:
	db = get_db()
	cur = db.execute(f"SELECT COUNT(*) AS c FROM {table_name}")
	row = cur.fetchone()
	return int(row["c"]) if row else 0


def _clear_tables() -> None:
	db = get_db()
	db.execute("DELETE FROM transactions")
	db.execute("DELETE FROM wallets")
	db.commit()


def _create_wallet(currency: Currency, now: datetime) -> Wallet:
	return Wallet(
		id=str(uuid4()),
		currency=currency,
		balance=Decimal("0.00"),
		status=WalletStatus.ACTIVE,
		created_at=now,
		updated_at=now,
	)


def _persist_wallet_and_tx(updated_wallet: Wallet, tx) -> None:
	update_wallet(updated_wallet)
	create_transaction(tx)


def _seed_dataset() -> tuple[int, int]:
	"""Seed wallets + transactions. Returns (wallet_count, tx_count)."""
	now = datetime.now(timezone.utc) - timedelta(days=2)
	tx_count = 0
	wallets: dict[str, SeedWallet] = {}

	def add_wallet(name: str, currency: Currency) -> SeedWallet:
		nonlocal now
		w = _create_wallet(currency, now)
		repo_create_wallet(w)
		wallets[name] = SeedWallet(name=name, wallet_id=w.id, currency=currency)
		return wallets[name]

	def deposit(name: str, amount: str) -> None:
		nonlocal now, tx_count
		seed = wallets[name]
		wallet_row = _get_wallet(seed.wallet_id)
		updated, tx = apply_deposit(
			wallet=wallet_row,
			amount=Decimal(amount),
			currency=seed.currency,
			transaction_id=str(uuid4()),
			now=now,
		)
		_persist_wallet_and_tx(updated, tx)
		tx_count += 1
		now += timedelta(minutes=7)

	def withdraw(name: str, amount: str) -> None:
		nonlocal now, tx_count
		seed = wallets[name]
		wallet_row = _get_wallet(seed.wallet_id)
		updated, tx = apply_withdraw(
			wallet=wallet_row,
			amount=Decimal(amount),
			currency=seed.currency,
			transaction_id=str(uuid4()),
			now=now,
		)
		_persist_wallet_and_tx(updated, tx)
		tx_count += 1
		now += timedelta(minutes=9)

	def exchange(source_name: str, target_name: str, amount: str, fx_rate: str) -> None:
		nonlocal now, tx_count
		source_seed = wallets[source_name]
		target_seed = wallets[target_name]
		source_wallet = _get_wallet(source_seed.wallet_id)
		target_wallet = _get_wallet(target_seed.wallet_id)

		updated_source, updated_target, tx = apply_exchange(
			source_wallet=source_wallet,
			target_wallet=target_wallet,
			amount=Decimal(amount),
			fx_rate=Decimal(fx_rate),
			transaction_id=str(uuid4()),
			now=now,
		)
		update_wallet(updated_source)
		update_wallet(updated_target)
		create_transaction(tx)
		tx_count += 1
		now += timedelta(minutes=11)

	def change_status(name: str, new_status: WalletStatus) -> None:
		nonlocal now, tx_count
		seed = wallets[name]
		wallet_row = _get_wallet(seed.wallet_id)
		updated_wallet, tx = apply_status_change(
			wallet=wallet_row,
			new_status=new_status,
			transaction_id=str(uuid4()),
			now=now,
		)
		_persist_wallet_and_tx(updated_wallet, tx)
		tx_count += 1
		now += timedelta(minutes=5)

	# --- Helper to reload wallet after updates ---
	def _get_wallet(wallet_id: str) -> Wallet:
		db = get_db()
		cur = db.execute(
			"SELECT id, currency, balance, status, created_at, updated_at FROM wallets WHERE id = ?",
			(wallet_id,),
		)
		row = cur.fetchone()
		if not row:
			raise RuntimeError(f"Seed error: wallet {wallet_id} not found")
		return Wallet(
			id=row["id"],
			currency=Currency(row["currency"]),
			balance=Decimal(row["balance"]),
			status=WalletStatus(row["status"]),
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)

	# --- Wallets (8 total) ---
	add_wallet("dk_main", Currency.DKK)
	add_wallet("dk_savings", Currency.DKK)
	add_wallet("eur_main", Currency.EUR)
	add_wallet("eur_travel", Currency.EUR)
	add_wallet("usd_main", Currency.USD)
	add_wallet("usd_spare", Currency.USD)
	add_wallet("eur_history", Currency.EUR)
	add_wallet("dk_history", Currency.DKK)
	now += timedelta(minutes=3)

	# --- Fund wallets (completed) ---
	deposit("dk_main", "1537.42")
	deposit("eur_main", "687.33")
	deposit("usd_main", "418.79")
	deposit("dk_savings", "3470.89")
	deposit("eur_travel", "237.58")

	# --- Withdrawals (completed) ---
	withdraw("dk_main", "128.17")
	withdraw("eur_travel", "43.21")

	# --- Exchanges (completed, deterministic FX rates) ---
	# DKK -> EUR
	exchange("dk_main", "eur_main", "312.83", fx_rate="0.1317")
	# EUR -> USD
	exchange("eur_main", "usd_main", "123.45", fx_rate="1.0834")

	# --- Wallet lifecycle history ---
	# Frozen wallet with a failed operation
	change_status("dk_history", WalletStatus.FROZEN)
	deposit("dk_history", "52.19")  # will be FAILED (invalid state)

	# Freeze -> unfreeze -> keep ACTIVE (shows both transitions)
	deposit("eur_history", "186.67")
	change_status("eur_history", WalletStatus.FROZEN)
	change_status("eur_history", WalletStatus.ACTIVE)
	withdraw("eur_history", "15.84")

	# Close a wallet after some activity (final CLOSED)
	deposit("usd_spare", "94.13")
	change_status("usd_spare", WalletStatus.CLOSED)
	withdraw("usd_spare", "10.07")  # FAILED (invalid state)

	# Another closed wallet (final CLOSED)
	deposit("dk_savings", "12.83")
	change_status("dk_savings", WalletStatus.CLOSED)

	# Failed exchange due to invalid wallet state (source is CLOSED)
	exchange("dk_savings", "eur_main", "7.77", fx_rate="0.1321")

	wallet_count = len(wallets)
	return wallet_count, tx_count


def main() -> int:
	parser = argparse.ArgumentParser(description="Seed the Multi-Currency Wallet Simulator database")
	parser.add_argument("--reset", action="store_true", help="Delete the DB file before seeding")
	parser.add_argument("--force", action="store_true", help="Overwrite existing data (clears tables)")
	parser.add_argument("--db", type=str, default=None, help="Override DB path (defaults to app config)")
	args = parser.parse_args()

	db_path = _choose_db_path(_db_path_from_args(args.db))

	if args.reset:
		_reset_db_file(db_path)

	# Always pass DATABASE explicitly so local runs are not affected by
	# placeholder values in a committed .env.
	app = create_app(test_config={"DATABASE": db_path})

	with app.app_context():
		init_schema()

		existing_wallets = _table_count("wallets")
		if existing_wallets > 0 and not args.force:
			print(f"Seed skipped: database already has {existing_wallets} wallets. Use --force or --reset.")
			return 0

		if args.force and existing_wallets > 0:
			_clear_tables()

		wallet_count, tx_count = _seed_dataset()
		print(f"Seed completed: {wallet_count} wallets, {tx_count} transactions")
		print(f"Database: {app.config['DATABASE']}")

	return 0


if __name__ == "__main__":
	raise SystemExit(main())

