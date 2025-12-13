from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def e2e_base_url() -> str:
    """Base URL for the running app under test."""
    return os.getenv("E2E_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
