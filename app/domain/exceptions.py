class WalletNotFoundError(Exception):
    """Raised when a wallet is not found."""


class InvalidAmountError(Exception):
    """Raised when an amount is invalid (e.g. negative or non-numeric)."""


class InvalidCurrencyError(Exception):
    """Raised when a currency is invalid or unsupported."""


class InsufficientFundsError(Exception):
    """Raised when a wallet has insufficient funds for a transaction."""


class WalletStateError(Exception):
    """Raised when a wallet is in an invalid state (e.g. CLOSED or FROZEN)."""


class ExchangeRateServiceError(Exception):
    """Raised when the external exchange rate service fails."""
