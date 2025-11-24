from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .enums import Currency, WalletStatus

@dataclass
class Wallet:
    id: str
    currency: Currency
    balance: Decimal
    status: WalletStatus
    created_at: datetime
    updated_at: datetime
