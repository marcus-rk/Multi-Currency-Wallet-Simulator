from __future__ import annotations

"""End-to-end-ish test (API-level) for wallet lifecycle behavior.

Flow:
1) Create wallet
2) Freeze -> deposit blocked
3) Unfreeze -> deposit allowed

This test is intentionally simple and exercises the full stack:
routes -> service -> domain rules -> repositories -> SQLite.
"""

from pathlib import Path

import pytest

from app import create_app
from tests.integration.helpers import create_wallet, deposit


@pytest.mark.e2e
def test_freeze_blocks_deposit_then_unfreeze_allows(tmp_path: Path):
    db_path = tmp_path / "e2e_wallet.db"
    app = create_app({"TESTING": True, "DATABASE": str(db_path)})

    with app.test_client() as client:
        wallet_id = create_wallet(client, "DKK")

        freeze_resp = client.post(f"/api/wallets/{wallet_id}/freeze")
        assert freeze_resp.status_code == 200

        deposit_blocked = deposit(client, wallet_id, "1.00", "DKK")
        assert deposit_blocked.status_code == 422
        blocked_body = deposit_blocked.get_json()
        assert blocked_body["transaction"]["error_code"] == "INVALID_WALLET_STATE"

        unfreeze_resp = client.post(f"/api/wallets/{wallet_id}/unfreeze")
        assert unfreeze_resp.status_code == 200

        deposit_ok = deposit(client, wallet_id, "1.00", "DKK")
        assert deposit_ok.status_code == 200
