# app/database.py
import sqlite3
from typing import Optional

from flask import current_app, g
from flask import Flask


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS wallets (
    id TEXT PRIMARY KEY,
    currency TEXT NOT NULL,
    balance NUMERIC NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    source_wallet_id TEXT,
    target_wallet_id TEXT,
    amount NUMERIC NOT NULL,
    currency TEXT NOT NULL,
    credited_amount NUMERIC,
    credited_currency TEXT,
    source_balance_after NUMERIC,
    target_balance_after NUMERIC,
    status TEXT NOT NULL,
    error_code TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(source_wallet_id) REFERENCES wallets(id),
    FOREIGN KEY(target_wallet_id) REFERENCES wallets(id)
);
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_e: Optional[BaseException] = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_schema() -> None:
    db = get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()


def init_db(app: Flask) -> None:
    app.teardown_appcontext(close_db)
