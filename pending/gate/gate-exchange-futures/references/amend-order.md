# Gate Futures Amend Order — Scenarios & Prompt Examples

Gate futures amend-order scenarios and expected behavior.

## MCP tools and parameters

| Tool | Purpose | Required | Optional |
|------|---------|----------|----------|
| **amend_futures_order** | Amend one order | `settle`, `order_id` | `price`, `size`, `amend_text`, `text` |

- Only **open** orders can be amended; finished or cancelled orders will error.
- Before amending, you can call `get_futures_contract(settle, contract)` to check precision (`order_price_round`, `order_size_min`, etc.).

## Pre-amend confirmation

Before calling `amend_futures_order`, show **current order** and **new parameters**, then ask user to confirm. Example: *"Change price from 49000 to 50000. Confirm?"*

---

## Scenario 1: Change price only

**Context**: User has an open order and wants to change the limit price.

**Prompt Examples**:
- "Change order 94294117235059656 price to 50000"
- "Amend order 94294117235059656 price 50000"
- "amend order 94294117235059656 price to 50000"

**Expected Behavior**:
1. Parse order_id: `94294117235059656`, new_price: `50000`.
2. (Optional) Call `get_futures_order(settle="usdt", order_id="94294117235059656")` and `get_futures_contract` for precision.
3. Show before/after (current price → new price), ask confirm.
4. After confirm call `amend_futures_order(settle="usdt", order_id="94294117235059656", price="50000")`.
5. Verify response price, output success.

**Response Template**:
```
Order amended.

Order ID: 94294117235059656
Contract: BTC_USDT
Price: 49000 → 50000
Size: 1 (unchanged)
Status: open
```

---

## Scenario 2: Change size only

**Context**: User wants to change order size, keep price.

**Prompt Examples**:
- "Change order 94294117235059656 size to 10"
- "Amend order size to 10"
- "Order 94294117235059656 size to 10"

**Expected Behavior**:
1. Parse order_id and new_size: `10`.
2. (Optional) Get current order and contract precision.
3. Show before/after size, ask confirm.
4. Call `amend_futures_order(settle="usdt", order_id="94294117235059656", size="10")`.
5. Verify size, output success.

**Response Template**:
```
Order amended.

Order ID: 94294117235059656
Contract: BTC_USDT
Price: 50000 (unchanged)
Size: 5 → 10
Status: open
```

---

## Scenario 3: Change price and size

**Context**: User wants to change both price and size.

**Prompt Examples**:
- "Order 94294117235059656 price 51000 size 8"
- "Amend 94294117235059656 price 51000 size 8"
- "amend order 94294117235059656 price 51000 size 8"

**Expected Behavior**:
1. Parse order_id, new_price: `51000`, new_size: `8`.
2. (Optional) Get order and precision, show before/after, confirm.
3. Call `amend_futures_order(..., price="51000", size="8")`.
4. Verify response, output success.

**Response Template**:
```
Order amended.

Order ID: 94294117235059656
Contract: BTC_USDT
Price: 50000 → 51000
Size: 5 → 8
Status: open
```

---

## Scenario 4: Locate order by custom text then amend

**Context**: User used custom text (e.g. `t-my-order-001`) and wants to amend by that text. API may require numeric order_id; if user only gives text, resolve to order_id first.

**Prompt Examples**:
- "Change order t-my-order-001 price to 48000"
- "Amend t-my-order-001 price 48000"

**Expected Behavior**:
1. If only text given: call `list_futures_orders(settle="usdt", status="open")` and match by `text` to get `order_id`.
2. Show current order and new params, confirm.
3. Call `amend_futures_order(settle="usdt", order_id="<resolved_id>", price="48000")` (or pass text if API supports it).
4. Output success.

**Response Template**:
```
Order amended.

Custom text: t-my-order-001
Order ID: 94294117235059656
Price: 50000 → 48000
Status: open
```

---

## Scenario 5: Amend already filled order (fail)

**Context**: User tries to amend an order that is already filled.

**Prompt Examples**:
- "Amend order 94294117235059656 price to 50000" (order already filled)

**Expected Behavior**:
1. Call `amend_futures_order(...)`.
2. API returns ORDER_NOT_FOUND, ORDER_FINISHED or similar.
3. Output failure and possible reasons.

**Response Template**:
```
Amend failed.

Order ID: 94294117235059656
Reason: Order not found or already finished.

Possible reasons:
1. Order was fully filled
2. Order was cancelled
3. Wrong order ID
```

---

## Scenario 6: Price precision error

**Context**: User’s price does not match contract precision.

**Prompt Examples**:
- "Change order price to 50000.123456" (precision too fine)

**Expected Behavior**:
1. Call `get_futures_contract(settle="usdt", contract="BTC_USDT")` for `order_price_round`, validate before sending.
2. If invalid, suggest valid price (e.g. 50000.12); if still submitted, amend may return INVALID_PARAM_VALUE.
3. Output precision error and contract rules.

**Response Template**:
```
Amend failed.

Order ID: 94294117235059656
Input price: 50000.123456
Error: Price precision not allowed.

BTC_USDT price precision: 0.01
Suggested: 50000.12
```

---

## Scenario 7: No amend parameters given

**Context**: User says amend but does not specify what to change.

**Prompt Examples**:
- "Amend order 94294117235059656"

**Expected Behavior**:
1. Detect missing price and size.
2. Ask user what to change.

**Response Template**:
```
What do you want to change?

Order ID: 94294117235059656

You can change:
1. Price
2. Size

Example: "Change price to 50000" or "Change size to 10"
```

---

## Scenario 8: No order ID — list then amend

**Context**: User wants to amend but did not give order ID; list open orders first.

**Prompt Examples**:
- "Amend my order price"
- "Change my order" (no ID)

**Expected Behavior**:
1. Call `list_futures_orders(settle="usdt", status="open")` and show list.
2. Ask user to pick order (by number or contract+side) or to provide order ID.
3. Once order and new price/size are given, follow Scenario 1–3 (including confirm before amend).
