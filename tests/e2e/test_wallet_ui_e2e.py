from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.ui_helpers import (
    create_wallet_via_ui,
    open_wallet,
    wallet_balance_locator,
    wallet_status_locator,
)


@pytest.mark.e2e
def test_create_wallet_dkk_shows_active_and_zero(page: Page, e2e_base_url: str):
    # Arrange
    wallet_id = create_wallet_via_ui(page, e2e_base_url, "DKK")

    # Assert
    wallet_row = page.locator("#walletList tr", has=page.get_by_role("link", name=wallet_id))
    expect(wallet_row).to_contain_text("DKK")
    expect(wallet_row).to_contain_text("0.00")
    expect(wallet_row).to_contain_text("ACTIVE")


@pytest.mark.e2e
def test_deposit_updates_balance_and_shows_deposit_transaction(page: Page, e2e_base_url: str):
    # Arrange
    wallet_id = create_wallet_via_ui(page, e2e_base_url, "DKK")
    open_wallet(page, e2e_base_url, wallet_id)

    # Act
    deposit_form = page.locator("#depositForm")
    deposit_form.get_by_label("Amount").fill("100.00")
    deposit_form.get_by_role("button", name="Deposit").click()

    # Assert
    expect(wallet_balance_locator(page)).to_have_text("100.00")

    tx_container = page.locator("#transactions")
    expect(tx_container).to_contain_text("DEPOSIT")
    expect(tx_container).to_contain_text("COMPLETED")
    expect(tx_container).to_contain_text("100.00 DKK")


@pytest.mark.e2e
def test_withdraw_insufficient_funds_shows_error_balance_unchanged_and_failed_tx(page: Page, e2e_base_url: str):
    # Arrange
    wallet_id = create_wallet_via_ui(page, e2e_base_url, "DKK")
    open_wallet(page, e2e_base_url, wallet_id)

    # Arrange (seed balance via UI)
    deposit_form = page.locator("#depositForm")
    deposit_form.get_by_label("Amount").fill("50.00")
    deposit_form.get_by_role("button", name="Deposit").click()
    expect(wallet_balance_locator(page)).to_have_text("50.00")

    # Act
    withdraw_form = page.locator("#withdrawForm")
    withdraw_form.get_by_label("Amount").fill("999.00")
    withdraw_form.get_by_role("button", name="Withdraw").click()

    # Assert
    expect(wallet_balance_locator(page)).to_have_text("50.00")

    tx_container = page.locator("#transactions")
    expect(tx_container).to_contain_text("WITHDRAWAL")
    expect(tx_container).to_contain_text("FAILED")
    expect(tx_container).to_contain_text("INSUFFICIENT_FUNDS")


@pytest.mark.e2e
def test_exchange_dkk_to_usd_updates_balances_and_shows_exchange_tx(page: Page, e2e_base_url: str):
    # Arrange
    dkk_wallet_id = create_wallet_via_ui(page, e2e_base_url, "DKK")
    usd_wallet_id = create_wallet_via_ui(page, e2e_base_url, "USD")

    # Arrange (fund DKK wallet via UI)
    open_wallet(page, e2e_base_url, dkk_wallet_id)
    deposit_form = page.locator("#depositForm")
    deposit_form.get_by_label("Amount").fill("20.00")
    deposit_form.get_by_role("button", name="Deposit").click()
    expect(wallet_balance_locator(page)).to_have_text("20.00")

    # Act
    page.goto(f"{e2e_base_url}/exchange.html")

    # Select wallets by value (wallet id).
    page.locator("#sourceWallet").select_option(dkk_wallet_id)
    page.locator("#targetWallet").select_option(usd_wallet_id)
    page.get_by_label("Amount").fill("10.00")
    page.get_by_role("button", name="Exchange").click()

    # Assert
    result = page.locator("#exchangeResult")
    expect(result).to_contain_text("EXCHANGE")
    expect(result).to_contain_text("COMPLETED")

    # Deterministic FX assertions (requires EXCHANGE_API_URL pointing at the local FX stub).
    # Stub rate: USD=2.0
    expect(result).to_contain_text("10.00")
    expect(result).to_contain_text("Credited: 20.00 USD")


@pytest.mark.e2e
def test_freeze_blocks_deposit_and_unfreeze_allows_deposit_again(page: Page, e2e_base_url: str):
    # Arrange
    wallet_id = create_wallet_via_ui(page, e2e_base_url, "DKK")
    open_wallet(page, e2e_base_url, wallet_id)

    # Act
    page.locator("[data-testid='freeze-btn']").click()

    # Assert
    expect(wallet_status_locator(page)).to_contain_text("FROZEN")

    # Act
    deposit_form = page.locator("#depositForm")
    deposit_form.get_by_label("Amount").fill("1.00")
    deposit_form.get_by_role("button", name="Deposit").click()

    # Assert
    expect(wallet_balance_locator(page)).to_have_text("0.00")

    tx_container = page.locator("#transactions")
    expect(tx_container).to_contain_text("DEPOSIT")
    expect(tx_container).to_contain_text("FAILED")
    expect(tx_container).to_contain_text("INVALID_WALLET_STATE")

    # Act
    page.locator("[data-testid='unfreeze-btn']").click()

    # Assert
    expect(wallet_status_locator(page)).to_contain_text("ACTIVE")

    # Act
    deposit_form.get_by_label("Amount").fill("1.00")
    deposit_form.get_by_role("button", name="Deposit").click()

    # Assert
    expect(wallet_balance_locator(page)).to_have_text("1.00")

