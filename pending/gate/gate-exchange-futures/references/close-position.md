# Gate Futures Close Position — Scenarios & Prompt Examples

Gate futures close-position scenarios and expected behavior.

## Position query (dual vs single mode)

**In dual mode**, `get_futures_position(settle, contract)` fails (API returns an array). Use **`list_futures_positions(settle, holding=true)`** or **`get_futures_dual_mode_position(settle, contract)`** when account is in dual mode (`get_futures_accounts` → `position_mode === "dual"` or `in_dual_mode === true`). In single mode use **`get_futures_position(settle, contract)`**.

## Scenario 1: Close all (one-click)

**Context**: User wants to close all positions regardless of size.

**Prompt Examples**:
- "Close all"
- "One-click close"
- "Close all positions"
- "close all positions"

**Expected Behavior**:
1. Call `list_futures_positions(settle="usdt")` to get all positions.
2. Show position list and confirm: "Confirm close all positions?"
3. After confirm, for each contract with position: call `create_futures_order(settle="usdt", contract=..., size=opposite size, reduce_only=true, ...)` market close (negative size to close long, positive to close short; tif="ioc", price="0").
4. Query `list_futures_positions` again to verify no (or negligible) position left.
5. Output close result with realized PnL.

**Response Template**:
```
Confirm close all positions? Current positions:
- BTC_USDT long 5 contracts, unrealised PnL +$200

(After user confirms)

All positions closed.

| Contract   | Side | Size | Fill price | Realised PnL |
|------------|------|------|------------|--------------|
| BTC_USDT   | Long | 5    | $52,000    | +$200        |

No open positions.
```

---

## Scenario 2: Partial close (specified size)

**Context**: User wants to close part of the position and keep the rest.

**Prompt Examples**:
- "Close 2 contracts"
- "Close 3 BTC contracts"
- "Reduce 1 contract"
- "Partial close, close 2 long"

**Expected Behavior**:
1. Query current position to verify sufficient size.
2. Compute close size (negative for long, positive for short).
3. Call `create_futures_order(size=-2, reduce_only=true, tif="ioc")` (or equivalent).
4. Verify remaining position.

**Response Template**:
```
Partial close done.

| Item        | Value        |
|-------------|--------------|
| Contract    | BTC_USDT     |
| Closed size | 2 contracts |
| Fill price  | $52,000      |
| Remaining   | Long 3       |

Close done; 3 long contracts remaining.
```

---

## Scenario 3: Close half

**Context**: User wants to close half of the position.

**Prompt Examples**:
- "Close half"
- "Close half of position"
- "Reduce 50%"

**Expected Behavior**:
1. Query position: size = 10.
2. Half: close_size = 5.
3. Call `create_futures_order(size=-5, reduce_only=true)`.
4. Verify remaining = 5.

**Response Template**:
```
Half closed.

| Item      | Before | After   |
|-----------|--------|---------|
| Size      | 10     | 5       |
| Side      | Long   | Long    |
| Fill price| -      | $52,000 |

Close done; 50% position remaining.
```

---

## Scenario 4: Reverse (long to short)

**Context**: User is long and wants to reverse to short.

**Prompt Examples**:
- "Reverse"
- "Reverse to short"
- "Long to short"
- "Close long open short"

**Expected Behavior**:
1. Query position via **position query** (dual: `list_futures_positions` or `get_futures_dual_mode_position`; single: `get_futures_position`): long +5.
2. Show reverse plan and ask user to confirm (include estimated liq/margin).
3. After confirm: first `create_futures_order(settle, contract, size="-5", reduce_only=true, price="0", tif="ioc")` to close long, then `create_futures_order(..., size="-5", price="0", tif="ioc")` to open 5 short (no reduce_only).
4. Verify new position via **position query** (same as above): short -5.

**Response Template**:
```
Reverse done.

| Item   | Before | After   |
|--------|--------|---------|
| Side   | Long   | Short   |
| Size   | 5      | 5       |
| Avg    | $50,000| $52,000 |

Reversed from long to short.
```

---

## Scenario 5: Reverse (short to long)

**Context**: User is short and wants to reverse to long.

**Prompt Examples**:
- "Reverse to long"
- "Short to long"
- "Close short open long"

**Expected Behavior**:
1. Query position via **position query** (dual: `list_futures_positions` or `get_futures_dual_mode_position`; single: `get_futures_position`): short -3.
2. Show reverse plan; after confirm: first `create_futures_order(..., size="3", reduce_only=true, price="0", tif="ioc")` to close short, then `create_futures_order(..., size="3", price="0", tif="ioc")` to open 3 long.
3. Verify new position: long +3.

**Response Template**:
```
Reverse done.

| Item | Before | After |
|------|--------|-------|
| Side | Short  | Long  |
| Size | 3      | 3     |

Reversed from short to long.
```

---

## Scenario 6: Reverse with different size

**Context**: User wants to reverse but new size differs from current.

**Prompt Examples**:
- "Reverse to short 3" (current long 5)
- "Close long, open 2 short"

**Expected Behavior**:
1. Query position: long +5.
2. Show plan (close 5 long → open 3 short), confirm, then: close all long with reduce_only, then open 3 short.
3. Verify position: short -3.

**Response Template**:
```
Reverse done.

| Item | Before | After |
|------|--------|-------|
| Side | Long   | Short |
| Size | 5      | 3     |

Reversed to short 3 (all 5 long closed).
```

---

## Scenario 7: Query then choose close action

**Context**: User wants to close but has not specified how.

**Prompt Examples**:
- "Help me close"
- "I want to close"
- "Close position"

**Expected Behavior**:
1. Query current position.
2. Show position and ask user to choose action.
3. Execute based on choice.

**Response Template** (query phase):
```
Current position:

| Contract   | Side | Size | Entry   | Mark    | Unrealised PnL |
|------------|------|------|---------|---------|----------------|
| BTC_USDT   | Long | 5    | $50,000 | $52,000 | +$200          |

Choose:
1. **Close all** — close all 5
2. **Partial** — specify size, e.g. "Close 2"
3. **Reverse** — close long, open short

Reply with option or exact action.
```

---

## Scenario 8: No position to close

**Context**: User asks to close but has no position.

**Prompt Examples**:
- "Close BTC position"

**Expected Behavior**:
1. Query position: size = 0.
2. Inform user there is no position to close.

**Response Template**:
```
No BTC_USDT position to close.

To open, you can say:
- "BTC_USDT long 1 contract, market"
- "BTC_USDT short 1 contract, limit 50000"
```

---

## Scenario 9: Close size exceeds position

**Context**: User wants to close more than current size.

**Prompt Examples**:
- "Close 10" (only 5 contracts)

**Expected Behavior**:
1. Query position: size = 5.
2. Detect 10 > 5, suggest alternatives.
3. Wait for user decision.

**Response Template**:
```
You have only 5 long contracts; cannot close 10.

Choose:
1. Close all — close all 5
2. Different size — enter 1–5

Reply with your choice.
```

---

## Scenario 10: Close all for one contract

**Context**: User wants to close all positions for a specific contract.

**Prompt Examples**:
- "Close BTC position"
- "Close all ETH"
- "close BTC position"

**Expected Behavior**:
1. Query position for that contract.
2. Close all for that contract.
3. Verify and report.

**Response Template**:
```
BTC_USDT position closed.

| Item         | Value          |
|--------------|----------------|
| Contract     | BTC_USDT       |
| Previous     | Long 5         |
| Fill price   | $52,000        |
| Realised PnL | +$200          |

BTC_USDT position cleared.
```

---

## Scenario 11: Close all across multiple contracts

**Context**: User has positions in several contracts and wants to close all.

**Prompt Examples**:
- "Close all positions"
- "Close all contracts"

**Expected Behavior**:
1. Query all positions.
2. Show all and confirm.
3. Close each contract.

**Response Template**:
```
Confirm close all positions? Current:

| Contract   | Side | Size | Unrealised PnL |
|------------|------|------|----------------|
| BTC_USDT   | Long | 5    | +$200          |
| ETH_USDT   | Short| 10   | -$50           |

(After user confirms)

All positions closed.

Closed 2 contracts.
Total realised PnL: +$150
```
