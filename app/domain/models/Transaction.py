from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from .Literals import TransactionType, TransactionStatus, Currency

@dataclass
class Transaction:
    id: str
    type: TransactionType
    source_wallet_id: Optional[str]
    target_wallet_id: Optional[str]
    amount: Decimal
    credited_amount: Optional[Decimal]
    currency: Currency
    status: TransactionStatus
    error_code: Optional[str]
    timestamp: datetime
