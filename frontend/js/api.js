import { API_BASE_URL } from "./config.js";

export class ApiError extends Error {
  /** @param {{message: string, status: number, data?: any}} params */
  constructor({ message, status, data }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

function isJsonResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  return contentType.includes("application/json");
}

async function readResponseBody(response) {
  if (isJsonResponse(response)) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  try {
    return await response.text();
  } catch {
    return null;
  }
}

function buildErrorMessage(response, data) {
  if (data && typeof data === "object" && "error" in data) {
    const msg = String(data.error);
    return msg || `HTTP ${response.status}`;
  }
  return response.statusText || `HTTP ${response.status}`;
}

/**
 * fetchJson("/api/...", { method, body })
 * - `body` can be an object (will be JSON.stringified) or undefined.
 * - Throws ApiError for non-2xx responses, including parsed body when possible.
 */
export async function fetchJson(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;

  const method = (options.method || "GET").toUpperCase();
  const headers = new Headers(options.headers || {});
  headers.set("accept", "application/json");

  const init = {
    method,
    headers,
  };

  if (options.body !== undefined) {
    headers.set("content-type", "application/json");
    init.body = typeof options.body === "string" ? options.body : JSON.stringify(options.body);
  }

  const response = await fetch(url, init);
  const data = await readResponseBody(response);

  if (!response.ok) {
    throw new ApiError({
      message: buildErrorMessage(response, data),
      status: response.status,
      data,
    });
  }

  return data;
}

export function formatError(err) {
  if (err instanceof ApiError) {
    return `${err.message} (HTTP ${err.status})`;
  }
  if (err && typeof err === "object" && "message" in err) {
    return String(err.message);
  }
  return String(err);
}
