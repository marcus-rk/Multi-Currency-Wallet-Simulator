import { SUPPORTED_CURRENCIES } from "./config.js";
import { fetchJson, formatError, ApiError } from "./api.js";
import { clearFeedback, setError, setLoading, setStatus, escapeHtml, renderTable, formatDecimal } from "./ui.js";

const els = {
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

function renderWalletInfo(wallet) {
  return `
    <dl class="kv">
      <div><dt>ID</dt><dd>${escapeHtml(wallet.id)}</dd></div>
      <div><dt>Currency</dt><dd>${escapeHtml(wallet.currency)}</dd></div>
      <div><dt>Balance</dt><dd>${escapeHtml(formatDecimal(wallet.balance, 2))}</dd></div>
      <div><dt>Status</dt><dd>${escapeHtml(wallet.status)}</dd></div>
      <div><dt>Updated</dt><dd>${escapeHtml(wallet.updated_at)}</dd></div>
    </dl>
  `;
}

function renderTransactions(transactions) {
  if (!transactions || transactions.length === 0) {
    return "<p>No transactions.</p>";
  }

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
    rows: transactions,
  });
}

async function loadWalletAndTransactions(walletId) {
  clearFeedback({ loadingEl: els.loading, statusEl: els.status, errorEl: els.error });
  setLoading(els.loading, true, "Loading wallet...");

  try {
    const [wallet, transactions] = await Promise.all([
      fetchJson(`/api/wallets/${encodeURIComponent(walletId)}`),
      fetchJson(`/api/wallets/${encodeURIComponent(walletId)}/transactions`),
    ]);

    document.title = `Wallet ${wallet.id}`;
    els.walletInfo.innerHTML = renderWalletInfo(wallet);
    els.transactions.innerHTML = renderTransactions(transactions);

    populateCurrencySelect(els.depositCurrency, wallet.currency);
    populateCurrencySelect(els.withdrawCurrency, wallet.currency);
  } catch (err) {
    setError(els.error, formatError(err));
    els.walletInfo.innerHTML = "";
    els.transactions.innerHTML = "";
  } finally {
    setLoading(els.loading, false);
  }
}

async function runWalletOperation({ walletId, kind, amount, currency }) {
  clearFeedback({ loadingEl: els.loading, statusEl: els.status, errorEl: els.error });
  setLoading(els.loading, true, `${kind}...`);

  try {
    const response = await fetchJson(`/api/wallets/${encodeURIComponent(walletId)}/${kind}`, {
      method: "POST",
      body: { amount, currency },
    });

    const tx = response.transaction;
    if (tx && tx.error_code) {
      setError(els.error, `${tx.error_code} (HTTP 422)`);
    } else {
      setStatus(els.status, `${kind} completed`);
    }

    await loadWalletAndTransactions(walletId);
  } catch (err) {
    setError(els.error, formatError(err));

    // For 422 responses, backend sends useful JSON (wallet + transaction)
    if (err instanceof ApiError && err.status === 422 && err.data && err.data.transaction) {
      const tx = err.data.transaction;
      setError(els.error, `${tx.error_code || "Operation failed"} (HTTP 422)`);
      await loadWalletAndTransactions(walletId);
    }
  } finally {
    setLoading(els.loading, false);
  }
}

function init() {
  const walletId = getWalletId();
  if (!walletId) {
    setError(els.error, "Missing wallet id in query string (?id=...)");
    return;
  }

  els.refreshButton.addEventListener("click", () => loadWalletAndTransactions(walletId));

  els.depositForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await runWalletOperation({
      walletId,
      kind: "deposit",
      amount: els.depositAmount.value,
      currency: els.depositCurrency.value,
    });
    els.depositForm.reset();
  });

  els.withdrawForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await runWalletOperation({
      walletId,
      kind: "withdraw",
      amount: els.withdrawAmount.value,
      currency: els.withdrawCurrency.value,
    });
    els.withdrawForm.reset();
  });

  loadWalletAndTransactions(walletId);
}

init();
