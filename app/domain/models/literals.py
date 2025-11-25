from typing import Literal


# Transaction types and statuses
TransactionType = Literal["DEPOSIT", "WITHDRAWAL", "EXCHANGE"]
TransactionStatus = Literal["COMPLETED", "FAILED"]

# Transaction error codes
TransactionErrorCode = Literal[
    "INVALID_WALLET_STATE",
    "INVALID_AMOUNT",
    "UNSUPPORTED_CURRENCY",
    "INSUFFICIENT_FUNDS",
    "EXCHANGE_RATE_UNAVAILABLE",
]

# Wallet statuses and supported currencies
WalletStatus = Literal["ACTIVE", "FROZEN", "CLOSED"]
Currency = Literal["DKK", "EUR", "USD"]
