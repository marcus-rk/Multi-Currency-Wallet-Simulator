from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from ..enums import Currency, WalletStatus


@dataclass
class Wallet:
    '''
    Domain model representing a Wallet.
    - **id**: str, identifier of the wallet
    - **currency**: Currency, currency of the wallet
    - **balance**: Decimal, current balance of the wallet
    - **status**: WalletStatus, status of the wallet (ACTIVE, INACTIVE)
    - **created_at**: datetime, timestamp when the wallet was created
    - **updated_at**: datetime, timestamp when the wallet was last updated
    '''
    id: str
    currency: Currency
    balance: Decimal
    status: WalletStatus
    created_at: datetime
    updated_at: datetime

    def is_active(self) -> bool:
        return self.status is WalletStatus.ACTIVE
