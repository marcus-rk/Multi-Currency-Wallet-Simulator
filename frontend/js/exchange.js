/**
 * Exchange page controller.
 *
 * Uses API endpoints:
 * - GET  /api/wallets
 * - POST /api/wallets/exchange
 */

import { fetchJson, formatError, ApiError } from "./api.js";
import { clearFeedback, setError, setLoading, setStatus, escapeHtml, renderTable, formatDecimal } from "./ui.js";

const els = {
  loading: document.getElementById("loading"),
  status: document.getElementById("statusBox"),
  error: document.getElementById("errorBox"),
  source: document.getElementById("sourceWallet"),
  target: document.getElementById("targetWallet"),
  amount: document.getElementById("exchangeAmount"),
  form: document.getElementById("exchangeForm"),
  result: document.getElementById("exchangeResult"),
};

function walletLabel(wallet) {
  return `${wallet.id} (${wallet.currency} ${formatDecimal(wallet.balance, 2)})`;
}

function populateWalletSelect(selectEl, wallets) {
  selectEl.innerHTML = wallets
    .map((w) => `<option value="${escapeHtml(w.id)}">${escapeHtml(walletLabel(w))}</option>`)
    .join("");
}

function walletStatusPill(status) {
  const s = String(status || "");
  if (s === "ACTIVE") return `<span class=\"pill pill--success\">${escapeHtml(s)}</span>`;
  if (s === "FROZEN") return `<span class=\"pill pill--warning\">${escapeHtml(s)}</span>`;
  if (s === "CLOSED") return `<span class=\"pill pill--neutral\">${escapeHtml(s)}</span>`;
  return `<span class=\"pill pill--neutral\">${escapeHtml(s)}</span>`;
}

function txTypePill(type) {
  const t = String(type || "");
  return `<span class=\"pill pill--neutral\">${escapeHtml(t)}</span>`;
}

function txStatusPill(status) {
  const s = String(status || "");
  if (s === "COMPLETED") return `<span class=\"pill pill--success\">${escapeHtml(s)}</span>`;
  if (s === "FAILED") return `<span class=\"pill pill--error\">${escapeHtml(s)}</span>`;
  return `<span class=\"pill pill--neutral\">${escapeHtml(s)}</span>`;
}

function renderWalletSummary(wallet, title) {
  return `
    <h3>${escapeHtml(title)}</h3>
    <dl class="kv">
      <div class="kv__row"><dt>ID</dt><dd><code class="mono">${escapeHtml(wallet.id)}</code></dd></div>
      <div class="kv__row"><dt>Currency</dt><dd>${escapeHtml(wallet.currency)}</dd></div>
      <div class="kv__row"><dt>Balance</dt><dd>${escapeHtml(formatDecimal(wallet.balance, 2))}</dd></div>
      <div class="kv__row"><dt>Status</dt><dd>${walletStatusPill(wallet.status)}</dd></div>
    </dl>
  `;
}

function renderTransaction(tx) {
  if (!tx) return "";

  const rows = [tx];
  return renderTable({
    columns: [
      { header: "Type", cell: (t) => txTypePill(t.type) },
      {
        header: "Amount",
        cell: (t) => {
          const base = `${formatDecimal(t.amount, 2)} ${t.currency}`;
          const credited = t.credited_amount && t.credited_currency ? `${formatDecimal(t.credited_amount, 2)} ${t.credited_currency}` : "";
          return credited
            ? `${escapeHtml(base)}<div class=\"muted\">Credited: ${escapeHtml(credited)}</div>`
            : escapeHtml(base);
        },
      },
      { header: "Status", cell: (t) => txStatusPill(t.status) },
      { header: "Time", cell: (t) => `<span class=\"mono\">${escapeHtml(t.created_at)}</span>` },
      { header: "Error", cell: (t) => (t.error_code ? `<code class=\"mono\">${escapeHtml(t.error_code)}</code>` : "") },
    ],
    rows,
  });
}

async function loadWallets() {
  clearFeedback({ loadingEl: els.loading, statusEl: els.status, errorEl: els.error });
  setLoading(els.loading, true, "Loading wallets...");

  try {
    const wallets = await fetchJson("/api/wallets");
    populateWalletSelect(els.source, wallets);
    populateWalletSelect(els.target, wallets);

    if (wallets.length >= 2) {
      els.target.selectedIndex = 1;
    }

    els.result.innerHTML = wallets.length === 0 ? "<p>Create wallets first.</p>" : "";
  } catch (err) {
    setError(els.error, formatError(err));
  } finally {
    setLoading(els.loading, false);
  }
}

async function onExchangeSubmit(event) {
  event.preventDefault();
  clearFeedback({ loadingEl: els.loading, statusEl: els.status, errorEl: els.error });

  const source_wallet_id = els.source.value;
  const target_wallet_id = els.target.value;
  const amount = els.amount.value;

  setLoading(els.loading, true, "Exchanging...");

  try {
    const response = await fetchJson("/api/wallets/exchange", {
      method: "POST",
      body: { source_wallet_id, target_wallet_id, amount },
    });

    const tx = response.transaction;
    if (tx && tx.error_code) {
      setError(els.error, `${tx.error_code} (HTTP 422)`);
    } else {
      setStatus(els.status, "Exchange completed");
    }

    els.result.innerHTML =
      renderWalletSummary(response.source_wallet, "Source wallet") +
      renderWalletSummary(response.target_wallet, "Target wallet") +
      `<h3>Transaction</h3>` +
      renderTransaction(tx);

    await loadWallets();
  } catch (err) {
    setError(els.error, formatError(err));

    if (err instanceof ApiError && err.status === 422 && err.data) {
      const tx = err.data.transaction;
      els.result.innerHTML =
        renderWalletSummary(err.data.source_wallet, "Source wallet") +
        renderWalletSummary(err.data.target_wallet, "Target wallet") +
        `<h3>Transaction</h3>` +
        renderTransaction(tx);
      await loadWallets();
    }
  } finally {
    setLoading(els.loading, false);
  }
}

function init() {
  els.form.addEventListener("submit", onExchangeSubmit);
  loadWallets();
}

init();
