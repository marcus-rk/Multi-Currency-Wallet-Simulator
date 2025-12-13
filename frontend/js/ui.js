/**
 * UI helper utilities.
 *
 * Small, framework-free helpers for:
 * - feedback banners (loading/status/error)
 * - HTML escaping
 * - deterministic decimal formatting
 * - simple table rendering
 */

const loadingTimers = new WeakMap();
const LOADING_DELAY_MS = 150;

export function setLoading(loadingEl, isLoading, text = "") {
  if (!loadingEl) return;

  const existingTimer = loadingTimers.get(loadingEl);
  if (existingTimer) {
    clearTimeout(existingTimer);
    loadingTimers.delete(loadingEl);
  }

  if (!isLoading) {
    loadingEl.textContent = "";
    loadingEl.hidden = true;
    return;
  }

  const message = text || "Loading...";

  // Keep hidden until we decide to show it (prevents empty-line flicker).
  loadingEl.textContent = "";
  loadingEl.hidden = true;

  // Avoid UI flicker on fast requests by only showing the text if loading
  // lasts longer than a short threshold.
  const timer = setTimeout(() => {
    loadingEl.hidden = false;
    loadingEl.textContent = message;
    loadingTimers.delete(loadingEl);
  }, LOADING_DELAY_MS);

  loadingTimers.set(loadingEl, timer);
}

export function setStatus(statusEl, message) {
  if (!statusEl) return;
  const text = message || "";
  statusEl.textContent = text;
  statusEl.hidden = text.trim() === "";
}

export function setError(errorEl, message) {
  if (!errorEl) return;
  const text = message || "";
  errorEl.textContent = text;
  errorEl.hidden = text.trim() === "";
}

export function clearFeedback({ loadingEl, statusEl, errorEl }) {
  setLoading(loadingEl, false);
  setStatus(statusEl, "");
  setError(errorEl, "");
}

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function pad2(n) {
  return String(n).padStart(2, "0");
}

/**
 * Format an ISO-8601 timestamp into a compact local datetime string.
 * Example: 2025-12-13T16:59:05.379579+00:00 -> 2025-12-13 17:59 (depending on local timezone)
 */
export function formatDateTimeCompact(value) {
  if (value === null || value === undefined) return "";
  const raw = String(value).trim();
  if (raw === "") return "";

  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return raw;

  const yyyy = d.getFullYear();
  const mm = pad2(d.getMonth() + 1);
  const dd = pad2(d.getDate());
  const hh = pad2(d.getHours());
  const min = pad2(d.getMinutes());
  return `${yyyy}-${mm}-${dd} ${hh}:${min}`;
}

function stripLeadingZeros(s) {
  const stripped = s.replace(/^0+(?=\d)/, "");
  return stripped === "" ? "0" : stripped;
}

/**
 * Deterministic decimal formatter for values coming from the API as strings
 * (Python Decimal serialized with str()).
 *
 * - No floating point math (avoids weird precision artifacts).
 * - Rounds half-up at the requested decimals.
 */
export function formatDecimal(value, decimals = 2) {
  if (value === null || value === undefined) return "";

  const raw = String(value).trim();
  if (raw === "") return "";

  // Basic fast-path for already-short values
  // (still route through rounding for consistency)

  let sign = "";
  let s = raw;
  if (s.startsWith("-")) {
    sign = "-";
    s = s.slice(1);
  } else if (s.startsWith("+")) {
    s = s.slice(1);
  }

  // We do not expect scientific notation from the backend; fall back to Number()
  // only if needed (keeps UI functional without throwing).
  if (/[eE]/.test(s)) {
    const num = Number(raw);
    if (!Number.isFinite(num)) return raw;
    return new Intl.NumberFormat(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  }

  const parts = s.split(".");
  const intPartRaw = parts[0] ?? "0";
  const fracPartRaw = parts[1] ?? "";

  const intPart = stripLeadingZeros(intPartRaw.replace(/\D/g, "") || "0");
  const fracPart = fracPartRaw.replace(/\D/g, "");

  if (decimals <= 0) {
    const roundDigit = fracPart.length > 0 ? fracPart[0] : "0";
    let intDigits = intPart.split("");
    if (roundDigit >= "5") {
      // carry into integer
      let i = intDigits.length - 1;
      while (i >= 0) {
        const d = intDigits[i].charCodeAt(0) - 48;
        if (d < 9) {
          intDigits[i] = String(d + 1);
          break;
        }
        intDigits[i] = "0";
        i -= 1;
      }
      if (i < 0) intDigits.unshift("1");
    }
    return `${sign}${intDigits.join("")}`;
  }

  const needed = decimals + 1; // include rounding digit
  const paddedFrac = (fracPart + "0".repeat(needed)).slice(0, needed);
  const keep = paddedFrac.slice(0, decimals);
  const roundDigit = paddedFrac[decimals];

  let fracDigits = keep.split("");
  let intDigits = intPart.split("");

  if (roundDigit >= "5") {
    // carry through fractional digits
    let i = fracDigits.length - 1;
    while (i >= 0) {
      const d = fracDigits[i].charCodeAt(0) - 48;
      if (d < 9) {
        fracDigits[i] = String(d + 1);
        break;
      }
      fracDigits[i] = "0";
      i -= 1;
    }

    // carry into integer if needed
    if (i < 0) {
      let j = intDigits.length - 1;
      while (j >= 0) {
        const d = intDigits[j].charCodeAt(0) - 48;
        if (d < 9) {
          intDigits[j] = String(d + 1);
          break;
        }
        intDigits[j] = "0";
        j -= 1;
      }
      if (j < 0) intDigits.unshift("1");
    }
  }

  return `${sign}${intDigits.join("")}.${fracDigits.join("")}`;
}

export function formatMoney(amount, currency, decimals = 2) {
  const formatted = formatDecimal(amount, decimals);
  return currency ? `${formatted} ${currency}` : formatted;
}

export function renderTable({ columns, rows }) {
  const thead = `<thead><tr>${columns.map((c) => `<th scope=\"col\">${escapeHtml(c.header)}</th>`).join("")}</tr></thead>`;
  const tbody = `<tbody>${rows
    .map((row) => `<tr>${columns.map((c) => `<td>${c.cell(row) ?? ""}</td>`).join("")}</tr>`)
    .join("")}</tbody>`;
  return `<table class=\"table\">${thead}${tbody}</table>`;
}
