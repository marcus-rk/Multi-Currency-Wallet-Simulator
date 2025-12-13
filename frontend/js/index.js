/**
 * Wallet list (index) page controller.
 *
 * Uses API endpoints:
 * - GET  /api/wallets
 * - POST /api/wallets
 */

import { SUPPORTED_CURRENCIES } from "./config.js";
import { fetchJson, formatError, ApiError } from "./api.js";
import { clearFeedback, setError, setLoading, setStatus, escapeHtml, renderTable, formatDecimal } from "./ui.js";

const els = {
  loading: document.getElementById("loading"),
  status: document.getElementById("statusBox"),
  error: document.getElementById("errorBox"),
  currencySelect: document.getElementById("walletCurrency"),
  createForm: document.getElementById("createWalletForm"),
  walletList: document.getElementById("walletList"),
  refreshButton: document.getElementById("refreshWallets"),
};

function walletStatusPill(status) {
  const s = String(status || "");
  if (s === "ACTIVE") return `<span class="pill pill--success">${escapeHtml(s)}</span>`;
  if (s === "FROZEN") return `<span class="pill pill--frozen">${escapeHtml(s)}</span>`;
  if (s === "CLOSED") return `<span class="pill pill--closed">${escapeHtml(s)}</span>`;
  return `<span class="pill pill--neutral">${escapeHtml(s)}</span>`;
}

function populateCurrencySelect(selectEl) {
  selectEl.innerHTML = SUPPORTED_CURRENCIES.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
}

function renderWallets(wallets) {
  if (!wallets || wallets.length === 0) {
    return "<p>No wallets yet.</p>";
  }

  return renderTable({
    columns: [
      {
        header: "ID",
        cell: (w) => `<a href="/wallet.html?id=${encodeURIComponent(w.id)}">${escapeHtml(w.id)}</a>`,
      },
      { header: "Currency", cell: (w) => escapeHtml(w.currency) },
      { header: "Balance", cell: (w) => escapeHtml(formatDecimal(w.balance, 2)) },
      { header: "Status", cell: (w) => walletStatusPill(w.status) },
    ],
    rows: wallets,
  });
}

async function loadWallets() {
  clearFeedback({ loadingEl: els.loading, statusEl: els.status, errorEl: els.error });
  setLoading(els.loading, true, "Loading wallets...");

  try {
    const wallets = await fetchJson("/api/wallets");
    els.walletList.innerHTML = renderWallets(wallets);
  } catch (err) {
    setError(els.error, formatError(err));
    els.walletList.innerHTML = "";
  } finally {
    setLoading(els.loading, false);
  }
}

async function onCreateWalletSubmit(event) {
  event.preventDefault();
  clearFeedback({ loadingEl: els.loading, statusEl: els.status, errorEl: els.error });

  const currency = els.currencySelect.value;

  setLoading(els.loading, true, "Creating wallet...");
  try {
    const wallet = await fetchJson("/api/wallets", {
      method: "POST",
      body: { currency },
    });

    setStatus(els.status, `Created wallet ${wallet.id}`);
    await loadWallets();
  } catch (err) {
    setError(els.error, formatError(err));

    // If server still returned a JSON payload, surface it deterministically.
    if (err instanceof ApiError && err.data) {
      setStatus(els.status, JSON.stringify(err.data));
    }
  } finally {
    setLoading(els.loading, false);
  }
}

function init() {
  populateCurrencySelect(els.currencySelect);
  els.createForm.addEventListener("submit", onCreateWalletSubmit);
  els.refreshButton.addEventListener("click", loadWallets);
  loadWallets();
}

init();
