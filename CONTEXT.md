# Multi-Currency Wallet Simulator

A single-user simulator of wallets that each hold money in one currency, with deposits, withdrawals, exchanges between wallets and wallet lifecycle changes. Built as a playground for software testing techniques.

## Language

### Wallets

**Wallet**:
A store of money in exactly one currency, with a balance and a wallet status.
_Avoid_: Account, pocket

**Balance**:
The amount of money a wallet currently holds, in the wallet's currency. Never negative.
_Avoid_: Funds, total

**Wallet status**:
The lifecycle state of a wallet: ACTIVE, FROZEN or CLOSED. Only an ACTIVE wallet accepts money operations.
_Avoid_: State, inactive

**Freeze / Unfreeze / Close**:
The status changes that move a wallet between ACTIVE, FROZEN and CLOSED. CLOSED is final.
_Avoid_: Lock, delete, deactivate

### Money

**Currency**:
One of the supported ISO 4217 currencies: DKK, EUR or USD.

**Minor unit**:
The smallest unit of a currency, such as one øre or one cent. All supported currencies have two decimal places.
_Avoid_: Cent (when speaking generally), subunit

**Amount**:
A positive quantity of money in a given currency, as requested in an operation.
_Avoid_: Value, sum

### Operations and transactions

**Operation**:
A request to change money in wallets: a deposit, a withdrawal or an exchange.
_Avoid_: Action, command

**Deposit**:
An operation that adds an amount to one wallet.
_Avoid_: Top-up, credit

**Withdrawal**:
An operation that removes an amount from one wallet.
_Avoid_: Debit, payout

**Exchange**:
An operation that moves an amount out of a source wallet and credits the converted amount to a target wallet in another currency.
_Avoid_: Transfer, conversion

**Exchange rate**:
How many units of the target currency one unit of the source currency buys. Exactly 1 when both currencies are the same.
_Avoid_: FX rate, price

**Credited amount**:
The amount added to the target wallet in an exchange: the amount times the exchange rate, rounded once, half up, to the target currency's minor unit.
_Avoid_: Converted amount, result

**Transaction**:
The permanent record of one operation or status change, with its outcome. A transaction is never edited after it is written.
_Avoid_: Log entry, history item

**Transaction status**:
The outcome recorded on a transaction: COMPLETED when the operation was applied in full, FAILED when it was rejected and no balance changed.
_Avoid_: Result, state

**Error code**:
The machine-readable reason a transaction failed or a request was rejected, such as INSUFFICIENT_FUNDS or INVALID_AMOUNT.
_Avoid_: Error message, reason
