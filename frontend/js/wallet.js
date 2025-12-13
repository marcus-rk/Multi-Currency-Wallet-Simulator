/**
 * Wallet page controller.
 *
 * Uses API endpoints:
 * - GET  /api/wallets/:id
 * - GET  /api/wallets/:id/transactions
 * - POST /api/wallets/:id/deposit
 * - POST /api/wallets/:id/withdraw
 * - POST /api/wallets/:id/freeze
 * - POST /api/wallets/:id/unfreeze
 * - POST /api/wallets/:id/close
 */

import { SUPPORTED_CURRENCIES } from "./config.js";
import { fetchJson, formatError, ApiError } from "./api.js";
import { clearFeedback, setError, setLoading, setStatus, escapeHtml, renderTable, formatDecimal } from "./ui.js";

const uiElements = {
  loading: document.getElementById("loading"),
  status: document.getElementById("statusBox"),
  error: document.getElementById("errorBox"),
  walletInfo: document.getElementById("walletInfo"),
  transactions: document.getElementById("transactions"),
  refreshButton: document.getElementById("refreshWallet"),
  depositForm: document.getElementById("depositForm"),
  withdrawForm: document.getElementById("withdrawForm"),
  depositCurrency: document.getElementById("depositCurrency"),
  withdrawCurrency: document.getElementById("withdrawCurrency"),
  depositAmount: document.getElementById("depositAmount"),
  withdrawAmount: document.getElementById("withdrawAmount"),
  freezeButton: document.getElementById("freezeWallet"),
  unfreezeButton: document.getElementById("unfreezeWallet"),
  closeButton: document.getElementById("closeWallet"),
};

function getWalletId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

function populateCurrencySelect(selectEl, selectedValue) {
  selectEl.innerHTML = SUPPORTED_CURRENCIES.map((c) => {
    const selected = c === selectedValue ? " selected" : "";
    return `<option value="${escapeHtml(c)}"${selected}>${escapeHtml(c)}</option>`;
  }).join("");
}

function walletStatusPill(status) {
  const s = String(status || "");
  if (s === "ACTIVE") return `<span class="pill pill--success">${escapeHtml(s)}</span>`;
  if (s === "FROZEN") return `<span class="pill pill--frozen">${escapeHtml(s)}</span>`;
  if (s === "CLOSED") return `<span class="pill pill--closed">${escapeHtml(s)}</span>`;
  return `<span class="pill pill--neutral">${escapeHtml(s)}</span>`;
}

function txTypePill(type) {
  const t = String(type || "");
  return `<span class="pill pill--neutral">${escapeHtml(t)}</span>`;
}

function txStatusPill(status) {
  const s = String(status || "");
  if (s === "COMPLETED") return `<span class="pill pill--success">${escapeHtml(s)}</span>`;
  if (s === "FAILED") return `<span class="pill pill--error">${escapeHtml(s)}</span>`;
  return `<span class="pill pill--neutral">${escapeHtml(s)}</span>`;
}

function renderWalletInfo(wallet) {
  return `
    <dl class="kv">
      <div class="kv__row"><dt>ID</dt><dd><code class="mono">${escapeHtml(wallet.id)}</code></dd></div>
      <div class="kv__row"><dt>Currency</dt><dd>${escapeHtml(wallet.currency)}</dd></div>
      <div class="kv__row"><dt>Balance</dt><dd>${escapeHtml(formatDecimal(wallet.balance, 2))}</dd></div>
      <div class="kv__row"><dt>Status</dt><dd data-testid="wallet-status">${walletStatusPill(wallet.status)}</dd></div>
      <div class="kv__row"><dt>Updated</dt><dd><span class="mono">${escapeHtml(wallet.updated_at)}</span></dd></div>
    </dl>
  `;
}

function renderTransactions(transactions) {
  if (!transactions || transactions.length === 0) {
    return "<p>No transactions.</p>";
  }

  return renderTable({
    columns: [
      { header: "Type", cell: (t) => txTypePill(t.type) },
      {
        header: "Amount",
        cell: (t) => {
          const base = `${formatDecimal(t.amount, 2)} ${t.currency}`;
          const credited = t.credited_amount && t.credited_currency ? `${formatDecimal(t.credited_amount, 2)} ${t.credited_currency}` : "";
          return credited
            ? `${escapeHtml(base)}<div class="muted">Credited: ${escapeHtml(credited)}</div>`
            : escapeHtml(base);
        },
      },
      { header: "Status", cell: (t) => txStatusPill(t.status) },
      { header: "Time", cell: (t) => `<span class="mono">${escapeHtml(t.created_at)}</span>` },
      { header: "Error", cell: (t) => (t.error_code ? `<code class="mono">${escapeHtml(t.error_code)}</code>` : "") },
    ],
    rows: transactions,
  });
}

async function loadWalletAndTransactions(walletId) {
  clearFeedback({ loadingEl: uiElements.loading, statusEl: uiElements.status, errorEl: uiElements.error });
  setLoading(uiElements.loading, true, "Loading wallet...");

  try {
    const [wallet, transactions] = await Promise.all([
      fetchJson(`/api/wallets/${encodeURIComponent(walletId)}`),
      fetchJson(`/api/wallets/${encodeURIComponent(walletId)}/transactions`),
    ]);

    document.title = `Wallet ${wallet.id}`;
    uiElements.walletInfo.innerHTML = renderWalletInfo(wallet);
    uiElements.transactions.innerHTML = renderTransactions(transactions);

    populateCurrencySelect(uiElements.depositCurrency, wallet.currency);
    populateCurrencySelect(uiElements.withdrawCurrency, wallet.currency);
  } catch (err) {
    setError(uiElements.error, formatError(err));
    uiElements.walletInfo.innerHTML = "";
    uiElements.transactions.innerHTML = "";
  } finally {
    setLoading(uiElements.loading, false);
  }
}

async function runWalletOperation({ walletId, kind, amount, currency }) {
  clearFeedback({ loadingEl: uiElements.loading, statusEl: uiElements.status, errorEl: uiElements.error });
  setLoading(uiElements.loading, true, `${kind}...`);

  try {
    const response = await fetchJson(`/api/wallets/${encodeURIComponent(walletId)}/${kind}`, {
      method: "POST",
      body: { amount, currency },
    });

    const tx = response.transaction;
    if (tx && tx.error_code) {
      setError(uiElements.error, `${tx.error_code} (HTTP 422)`);
    } else {
      setStatus(uiElements.status, `${kind} completed`);
    }

    await loadWalletAndTransactions(walletId);
  } catch (err) {
    setError(uiElements.error, formatError(err));

    // For 422 responses, backend sends useful JSON (wallet + transaction)
    if (err instanceof ApiError && err.status === 422 && err.data && err.data.transaction) {
      const tx = err.data.transaction;
      setError(uiElements.error, `${tx.error_code || "Operation failed"} (HTTP 422)`);
      await loadWalletAndTransactions(walletId);
    }
  } finally {
    setLoading(uiElements.loading, false);
  }
}

async function runWalletLifecycle({ walletId, action }) {
  clearFeedback({ loadingEl: uiElements.loading, statusEl: uiElements.status, errorEl: uiElements.error });
  setLoading(uiElements.loading, true, `${action}...`);

  try {
    await fetchJson(`/api/wallets/${encodeURIComponent(walletId)}/${action}`, {
      method: "POST",
    });
    setStatus(uiElements.status, `${action} completed`);
    await loadWalletAndTransactions(walletId);
  } catch (err) {
    setError(uiElements.error, formatError(err));
    await loadWalletAndTransactions(walletId);
  } finally {
    setLoading(uiElements.loading, false);
  }
}

function init() {
  const walletId = getWalletId();
  if (!walletId) {
    setError(uiElements.error, "Missing wallet id in query string (?id=...)");
    return;
  }

  uiElements.refreshButton.addEventListener("click", () => loadWalletAndTransactions(walletId));

  uiElements.freezeButton.addEventListener("click", () => runWalletLifecycle({ walletId, action: "freeze" }));
  uiElements.unfreezeButton.addEventListener("click", () => runWalletLifecycle({ walletId, action: "unfreeze" }));
  uiElements.closeButton.addEventListener("click", () => runWalletLifecycle({ walletId, action: "close" }));

  uiElements.depositForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await runWalletOperation({
      walletId,
      kind: "deposit",
      amount: uiElements.depositAmount.value,
      currency: uiElements.depositCurrency.value,
    });
    uiElements.depositForm.reset();
  });

  uiElements.withdrawForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await runWalletOperation({
      walletId,
      kind: "withdraw",
      amount: uiElements.withdrawAmount.value,
      currency: uiElements.withdrawCurrency.value,
    });
    uiElements.withdrawForm.reset();
  });

  loadWalletAndTransactions(walletId);
}

init();
