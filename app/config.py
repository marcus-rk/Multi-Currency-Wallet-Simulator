"""Application configuration.

Reads runtime settings from environment variables and provides defaults for local
development and testing.
"""

import os

# Project root (one level above app/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    DATABASE = os.getenv(
        "DATABASE",
        os.path.join(BASE_DIR, "instance", "wallet.db"),
    )
    EXCHANGE_API_URL = os.getenv(
        "EXCHANGE_API_URL",
        "https://api.frankfurter.dev/v1", # Documentation: https://frankfurter.dev
    )


class TestConfig(Config):
    TESTING = True
    DATABASE = os.getenv(
        "TEST_DATABASE",
        os.path.join(BASE_DIR, "instance", "test_wallet.db"),
    )
