from __future__ import annotations

import re

"""UI-only helpers for Playwright E2E tests.

These helpers encapsulate common UI flows (create wallet, open wallet, locate
balance/status fields) so the test file can stay focused on the business
journeys.
"""

from playwright.sync_api import Locator, Page, expect


def create_wallet_via_ui(page: Page, base_url: str, currency: str) -> str:
    """Create a wallet via the index page and return the created wallet id.

    The UI shows transient status banners that may be cleared during refresh.
    To keep tests stable, the created wallet id is derived by diffing the wallet
    list before/after clicking "Create wallet".
    """

    page.goto(f"{base_url}/")

    # The index page triggers an initial refresh on load (GET /api/wallets).
    # Wait for the wallet list container to get content so we don't snapshot an
    # empty list and mis-diff later.
    wallet_list_container = page.locator("#walletList")
    expect(wallet_list_container).to_have_text(re.compile(r".*\S.*", re.DOTALL))

    wallet_links = page.locator("#walletList a")
    before_ids = set(wallet_links.all_inner_texts())
    before_count = wallet_links.count()

    page.get_by_label("Currency").select_option(currency)
    page.get_by_role("button", name="Create wallet").click()

    expect(wallet_links).to_have_count(before_count + 1)

    after_ids = set(wallet_links.all_inner_texts())
    created_ids = list(after_ids - before_ids)
    assert len(created_ids) == 1, f"Expected exactly one new wallet, got: {created_ids!r}"
    return created_ids[0]


def open_wallet(page: Page, base_url: str, wallet_id: str) -> None:
    """Navigate directly to a wallet page and wait for the page to be ready."""

    page.goto(f"{base_url}/wallet.html?id={wallet_id}")
    expect(page.get_by_role("heading", name="Wallet", exact=True)).to_be_visible()


def wallet_balance_locator(page: Page) -> Locator:
    """Locate the wallet balance field on the wallet page."""

    return page.locator("#walletInfo dt:has-text('Balance')").locator("xpath=following-sibling::dd[1]")


def wallet_status_locator(page: Page) -> Locator:
    """Locate the wallet status badge/text on the wallet page."""

    return page.locator("[data-testid='wallet-status']")
