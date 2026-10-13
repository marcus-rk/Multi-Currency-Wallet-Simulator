# SRS addendum

Rules added or changed after SRS v2.1 (`docs/SRS/`). The SRS PDFs are exam deliverables and stay unchanged; where this file and the SRS disagree, this file wins. Section numbers refer to SRS v2.1.

## 3.1.3 Balances

Balances and amounts are stored exactly, as whole minor units of their currency. See [ADR-0004](adr/0004-money-as-integer-minor-units.md).

## 3.3.1 to 3.3.4 Amounts in deposits, withdrawals and exchanges

The SRS requires an amount to be numeric and greater than zero. In addition, an amount is rejected when it:

- has more decimal places than its currency's minor unit allows (more than 2 for DKK, EUR and USD), for example `1.234`;
- is not finite (`NaN`, `Infinity`);
- is greater than `1000000000.00`.

Such a request is malformed. It is rejected with HTTP 400 and error code `INVALID_AMOUNT` before any operation starts, and no transaction is recorded. The credited amount of an exchange is still rounded once, half up, to two decimals, as section 3.3.4 requires.

## 3.3, 3.3.5 and 4.1 Atomic operations and failed transactions

An operation is applied in one database transaction: either every balance change and its COMPLETED transaction are saved, or nothing is. When an operation is rejected, its balance changes are rolled back first and the FAILED transaction is then recorded on its own. See [ADR-0005](adr/0005-one-transaction-per-operation.md).

## 4.2 Error responses

Every error response has the SRS body, `{"error": "<ERROR_CODE>", "message": "<English text>"}`. The status codes deviate from the SRS on purpose: 400 malformed request, 404 wallet not found, 409 status change not allowed, 422 operation rejected, 502 exchange rate unavailable, 500 unexpected error. See [ADR-0003](adr/0003-error-response-contract.md).
