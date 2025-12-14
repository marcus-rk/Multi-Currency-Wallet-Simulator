"""Pure business rules.

Each function applies a single operation (deposit/withdraw/exchange/status-change)
to in-memory domain objects and returns updated state and/or derived outputs.
"""

from .apply_deposit import apply_deposit
from .apply_withdraw import apply_withdraw
from .apply_exchange import apply_exchange
from .apply_status_change import apply_status_change
