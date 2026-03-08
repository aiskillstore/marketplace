# Gate Futures Cancel Order — Scenarios & Prompt Examples

Gate futures cancel-order scenarios and expected behavior.

## Scenario 1: List orders then choose to cancel (recommended)

**Context**: User wants to cancel but does not know order ID; need to list open orders first.

**Prompt Examples**:
- "Cancel my order"
- "What open orders do I have"
- "Cancel order" (no ID)
- "Show my orders"

**Expected Behavior**:
1. Detect no order_id → query mode.
2. Call `list_futures_orders(settle="usdt", status="open")`.
3. Show order list with numbered options.
4. Wait for user selection.
5. Cancel based on selection.

**Response Template** (list phase):
```
You have 3 open orders:

| # | Contract   | Side | Size | Price | Left  | Time     |
|---|------------|------|------|-------|-------|----------|
| 1 | BTC_USDT   | Buy  | 1    | 50000 | 1     | 10:30:25 |
| 2 | BTC_USDT   | Sell | 2    | 80000 | 2     | 10:35:12 |
| 3 | ETH_USDT   | Buy  | 10   | 2800  | 10    | 11:02:45 |

Which order(s) do you want to cancel?
- Enter number(s), e.g. "1" or "1,2"
- Enter "all" to cancel all
```

---

## Scenario 2: Cancel by list number

**Context**: User selects by number from the list.

**Prompt Examples**:
- "Cancel #1"
- "1"
- "Cancel 1 and 3"
- "1,2"

**Expected Behavior**:
1. Parse selection (one or more numbers).
2. Map to order_id from the list.
3. Call `cancel_futures_order` for each.
4. Output result.

**Response Template**:
```
Order cancelled.

Cancelled #1:
- Order ID: 94294117235059656
- Contract: BTC_USDT
- Side: Buy
- Price: 50000
- Result: Cancelled
```

---

## Scenario 3: Cancel all orders (batch)

**Context**: User wants to cancel all open orders.

**Prompt Examples**:
- "Cancel all orders"
- "Cancel all"
- "Clear all orders"
- "All" (after seeing the list)

**Expected Behavior**:
1. Confirm: "Confirm cancel all orders?"
2. Call `list_futures_orders(settle="usdt", status="open")` to get contracts with orders; for each, call `cancel_all_futures_orders(settle="usdt", contract=...)` (required: `settle`, `contract`).
3. Output batch result.

**Response Template**:
```
Confirm cancel all orders? You have 3 open orders.

(After user confirms)

Batch cancel done.

| Order ID         | Contract   | Side | Price | Result    |
|------------------|------------|------|-------|-----------|
| 94294117235059656| BTC_USDT   | Buy  | 50000 | Cancelled |
| 94294117235059657| BTC_USDT   | Sell | 80000 | Cancelled |
| 94294117235059658| ETH_USDT   | Buy  | 2800  | Cancelled |

3 orders cancelled.
```

---

## Scenario 4: Cancel all for one contract

**Context**: User wants to cancel only orders for a specific contract.

**Prompt Examples**:
- "Cancel all BTC_USDT orders"
- "Cancel ETH contract orders"
- "Cancel all BTC orders"

**Expected Behavior**:
1. Parse contract: e.g. `BTC_USDT`.
2. Call `cancel_all_futures_orders(settle="usdt", contract="BTC_USDT")` (required: `settle`, `contract`; optional: `side`, `exclude_reduce_only`, `text`).
3. Output result for that contract.

**Response Template**:
```
All BTC_USDT orders cancelled:

| Order ID         | Side | Price | Result    |
|------------------|------|-------|-----------|
| 94294117235059656| Buy  | 50000 | Cancelled |
| 94294117235059657| Sell | 80000 | Cancelled |

2 orders cancelled.
```

---

## Scenario 5: Cancel by order ID

**Context**: User provides order ID directly.

**Prompt Examples**:
- "Cancel order 94294117235059656"
- "cancel order 94294117235059656"

**Expected Behavior**:
1. Parse order_id: `94294117235059656`.
2. Call `cancel_futures_order(settle="usdt", order_id="94294117235059656")`.
3. Verify `finish_as == "cancelled"`.
4. Output result.

**Response Template**:
```
Order cancelled.

Order ID: 94294117235059656
Contract: BTC_USDT
Side: Buy
Price: 50000
Status: finished
Result: Cancelled
```

---

## Scenario 6: Cancel by custom text

**Context**: User identified the order with custom text and wants to cancel by that text.

**Prompt Examples**:
- "Cancel order t-my-order-001"
- "Cancel t-my-order-001"

**Expected Behavior**:
1. Detect order_id starts with `t-`, treat as text.
2. Call `cancel_futures_order(settle="usdt", order_id="t-my-order-001")` (if API supports).
3. Output result.

**Response Template**:
```
Order cancelled.

Custom text: t-my-order-001
Order ID: 94294117235059656
Contract: BTC_USDT
Result: Cancelled
```

---

## Scenario 7: No open orders

**Context**: User wants to cancel but there are no open orders.

**Prompt Examples**:
- "Cancel my order"
- "Cancel all orders"

**Expected Behavior**:
1. Call `list_futures_orders(settle="usdt", status="open")`.
2. Get empty list.
3. Inform user.

**Response Template**:
```
No open orders to cancel.

To place an order you can say:
- "BTC_USDT long 1 contract, limit 50000"
```

---

## Scenario 8: Cancel already filled order (fail)

**Context**: User tries to cancel an order that is already filled.

**Prompt Examples**:
- "Cancel order 94294117235059656" (order already filled)

**Expected Behavior**:
1. Call `cancel_futures_order(settle="usdt", order_id="94294117235059656")`.
2. Receive ORDER_NOT_FOUND (or similar).
3. Output failure.

**Response Template**:
```
Cancel failed.

Order ID: 94294117235059656
Reason: Order not found or already finished.

Possible reasons:
1. Order was fully filled
2. Order was already cancelled
3. Wrong order ID

Check order history for status.
```

---

## Scenario 9: Cancel only bids or only asks

**Context**: User wants to cancel only buy or only sell orders.

**Prompt Examples**:
- "Cancel all buy orders"
- "Cancel all sell orders"
- "Cancel BTC buy orders"

**Expected Behavior**:
1. Parse side: `bid` (buy) or `ask` (sell).
2. For one contract use `cancel_all_futures_orders(settle="usdt", contract=..., side="bid")` (required: `settle`, `contract`; optional: `side`, `exclude_reduce_only`, `text`). For "all contracts one side" list then cancel per contract with side.
3. Output result.

**Response Template**:
```
All buy orders cancelled:

| Order ID         | Contract   | Price | Result    |
|------------------|------------|-------|-----------|
| 94294117235059656| BTC_USDT   | 50000 | Cancelled |
| 94294117235059658| ETH_USDT   | 2800  | Cancelled |

2 buy orders cancelled.
```
