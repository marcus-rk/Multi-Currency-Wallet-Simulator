from __future__ import annotations


def create_wallet(client, currency: str = "DKK") -> str:
    response = client.post("/api/wallets", json={"currency": currency})
    assert response.status_code == 201
    wallet_payload = response.get_json()
    assert isinstance(wallet_payload, dict)
    assert "id" in wallet_payload
    return wallet_payload["id"]


def deposit(client, wallet_id: str, amount: str, currency: str):
    return client.post(
        f"/api/wallets/{wallet_id}/deposit",
        json={"amount": amount, "currency": currency},
    )


def withdraw(client, wallet_id: str, amount: str, currency: str):
    return client.post(
        f"/api/wallets/{wallet_id}/withdraw",
        json={"amount": amount, "currency": currency},
    )


def exchange(client, source_wallet_id: str, target_wallet_id: str, amount: str):
    return client.post(
        "/api/wallets/exchange",
        json={
            "source_wallet_id": source_wallet_id,
            "target_wallet_id": target_wallet_id,
            "amount": amount,
        },
    )
