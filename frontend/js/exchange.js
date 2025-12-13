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

function renderWalletSummary(wallet, title) {
  return `
    <h3>${escapeHtml(title)}</h3>
    <dl class="kv">
      <div><dt>ID</dt><dd>${escapeHtml(wallet.id)}</dd></div>
      <div><dt>Currency</dt><dd>${escapeHtml(wallet.currency)}</dd></div>
      <div><dt>Balance</dt><dd>${escapeHtml(formatDecimal(wallet.balance, 2))}</dd></div>
      <div><dt>Status</dt><dd>${escapeHtml(wallet.status)}</dd></div>
    </dl>
  `;
}

function renderTransaction(tx) {
  if (!tx) return "";

  const rows = [tx];
  return renderTable({
    columns: [
      { header: "Type", cell: (t) => escapeHtml(t.type) },
      { header: "Amount", cell: (t) => escapeHtml(formatDecimal(t.amount, 2)) },
      { header: "Currency", cell: (t) => escapeHtml(t.currency) },
      { header: "Credited", cell: (t) => (t.credited_amount ? escapeHtml(formatDecimal(t.credited_amount, 2)) : "") },
      { header: "Credited currency", cell: (t) => (t.credited_currency ? escapeHtml(t.credited_currency) : "") },
      { header: "Status", cell: (t) => escapeHtml(t.status) },
      { header: "Error code", cell: (t) => (t.error_code ? escapeHtml(t.error_code) : "") },
      { header: "Created", cell: (t) => escapeHtml(t.created_at) },
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
