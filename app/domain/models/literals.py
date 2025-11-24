from typing import Literal

# Transaction types and statuses
TransactionType = Literal["DEPOSIT", "WITHDRAWAL", "EXCHANGE"]
TransactionStatus = Literal["COMPLETED", "FAILED"]

# Wallet statuses and supported currencies
WalletStatus = Literal["ACTIVE", "FROZEN", "CLOSED"]
Currency = Literal["DKK", "EUR", "USD"]
