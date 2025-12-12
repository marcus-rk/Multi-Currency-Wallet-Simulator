class WalletNotFoundError(Exception):
    """Raised when a wallet is not found."""
    pass

class InvalidAmountError(Exception):
    """Raised when an amount is invalid (e.g. negative or non-numeric)."""
    pass

class InvalidCurrencyError(Exception):
    """Raised when a currency is invalid or unsupported."""
    pass

class InsufficientFundsError(Exception):
    """Raised when a wallet has insufficient funds for a transaction."""
    pass

class WalletStateError(Exception):
    """Raised when a wallet is in an invalid state (e.g. CLOSED or FROZEN)."""
    pass
