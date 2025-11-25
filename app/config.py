# app/config.py
import os

# Project root (one level above app/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    """
    Default configuration for the wallet application.
    """
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    DATABASE = os.environ.get(
        "DATABASE",
        os.path.join(BASE_DIR, "instance", "wallet.db"),
    )


class TestConfig(Config):
    """
    Configuration used in tests.
    (Can be overridden passing test_config dict to create_app.)
    """
    TESTING = True
    DATABASE = os.environ.get(
        "TEST_DATABASE",
        os.path.join(BASE_DIR, "instance", "test_wallet.db"),
    )
