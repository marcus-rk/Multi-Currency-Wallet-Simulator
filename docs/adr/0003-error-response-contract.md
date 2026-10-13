---
status: accepted
---

# Error responses use the SRS body, with the current status codes

SRS section 4.2 specifies error bodies as `{"error": "<ERROR_CODE>", "message": "<English text>"}`, but the API returns `{"error": "<free text>"}`, and some errors (an unhandled exception outside the wallets blueprint, a malformed number) are not caught at all. Every error response now uses the SRS body, produced by one app-wide error handler. We keep the current status codes (404 not found, 409 invalid status change, 422 rejected operation, 502 exchange rate unavailable, 500 unexpected) instead of the SRS's 400 for every client error, because they say more precisely what went wrong and changing them would break the API a second time for no gain.

## Consequences

- This deviates from the SRS's status codes on purpose; `docs/srs-addendum.md` records the deviation next to the SRS section it changes.
- Clients and tests can rely on `error` being a code from a fixed list, and must not parse `message`.
