# Gate Futures Open Position — Scenarios & Prompt Examples

Gate futures open-position scenarios and expected behavior.

## Unit Conversion

When the user does not specify size in **contracts**, convert to **contracts** before placing the order:

| User unit | Conversion | Notes |
|-----------|------------|-------|
| **U (USDT notional)** | contracts = u ÷ mark_price ÷ quanto_multiplier | No leverage or cross: `size_contracts = u / mark_price / quanto_multiplier` |
| **U (USDT notional) + leverage** | contracts = u × leverage ÷ mark_price ÷ quanto_multiplier | With leverage: `size_contracts = u * leverage / mark_price / quanto_multiplier` |
| **Base (e.g. BTC, ETH)** | contracts = base_amount ÷ quanto_multiplier | `size_contracts = base_amount / quanto_multiplier` |

- **Data source**: Call `get_futures_contract(settle, contract)` for `mark_price`, `quanto_multiplier`.
- **Precision**: Resulting contracts must satisfy contract `order_size_min` and size precision; if below minimum, prompt the user.

## Position and leverage query (dual vs single mode)

**Tool `get_position` does not exist.** Use the following by account mode (from **`get_futures_accounts(settle)`** → **`position_mode`** or **`in_dual_mode`**):

- **Dual mode** (`position_mode === "dual"` or `in_dual_mode === true`): use **`list_futures_positions(settle, holding=true)`** or **`get_futures_dual_mode_position(settle, contract)`** for position/leverage. Do **not** use `get_futures_position` in dual mode (API returns an array and causes parse error).
- **Single mode**: use **`get_futures_position(settle, contract)`** for position/leverage.

Same rule for **margin mode** (`pos_margin_mode`): get it from the position returned by the above query.

## Pre-Order Confirmation

**Before opening**, show the **final order summary** and only call `create_futures_order` after user confirmation.

- **Leverage**: Query current leverage for **contract + side** via the **position query** above (dual: `list_futures_positions` or `get_futures_dual_mode_position`; single: `get_futures_position`).
- **Summary**: Contract, side (long/short), size (contracts), price (limit or “market”), margin mode (cross/isolated), **leverage**, estimated margin and liquidation price; for market orders also mention slippage risk. **Do not** add text about mark price, limit protection, or suggesting to adjust price.
- **Confirmation**: *“Please confirm the above and reply ‘confirm’ to place the order.”* Only after the user confirms (e.g. “confirm”, “yes”, “place”) execute the order.

## Margin Mode Switch API (update_futures_dual_comp_position_cross_mode)

**Switch margin mode only when the user explicitly requests it**: switch to isolated only when user asks for isolated (e.g. "isolated", "逐仓"); switch to cross only when user asks for cross (e.g. "cross", "全仓"). **If the user does not specify margin mode, do not switch — place the order in the current margin mode.**

When switching cross/isolated margin, call MCP **`update_futures_dual_comp_position_cross_mode`** with **`settle`**, **`contract`**, **`mode`**:

- **`mode`**: `"CROSS"` = cross margin, `"ISOLATED"` = isolated margin (required; do not use a `cross` boolean).
- **`settle`**: Settlement currency, e.g. `"usdt"`.
- **`contract`**: Contract name, e.g. `"BTC_USDT"`.

Example: cross `update_futures_dual_comp_position_cross_mode(settle="usdt", contract="BTC_USDT", mode="CROSS")`; isolated `update_futures_dual_comp_position_cross_mode(settle="usdt", contract="BTC_USDT", mode="ISOLATED")`.

## Leverage Before Order

If the **user specifies leverage** and it **differs from current** for that contract/side, **first** set leverage, **then** call `create_futures_order`. Use **`update_futures_dual_mode_position_leverage(settle, contract, leverage)`** in dual mode; **`update_futures_position_leverage(settle, contract, leverage)`** in single mode. Do not use `update_futures_position_leverage` in dual mode (API returns array and causes parse error). *Note:* In dual mode, `update_futures_dual_mode_position_leverage` may return an MCP parse error (e.g. "expected record, received array") even when leverage was set successfully; if the call was made, proceed to place the order.

## Margin Mode vs Position Mode

**Switch to isolated only when the user explicitly requests isolated; switch to cross only when the user explicitly requests cross.** If the user does not specify margin mode, **do not switch — place the order in the current margin mode.**

When **target margin mode** is explicitly requested and **differs from** the **current margin mode** of the existing position for that contract, check **position mode** first:

- **Position mode**: Call MCP **`get_futures_accounts(settle)`**. From **`position_mode`**: `single` = single position mode, `dual` = dual (hedge) position mode.
- **Margin mode**: From **position** — use the **position query** per dual/single mode above and read `pos_margin_mode` (cross/isolated).

**Branch logic** (target margin mode ≠ current position margin mode and contract already has a position):

| position_mode | Position mode | Behavior | Prompt |
|---------------|---------------|----------|--------|
| `single` | Single position | Do not interrupt | Prompt: "You already have a {currency} position; switching margin mode will apply to this position too. Continue?" (e.g. currency from contract: BTC_USDT → BTC). After user confirms, switch and continue opening. |
| `dual` | Dual position | **Interrupt** | Prompt: "Please close the position first, then open a new one." Do not switch margin mode or place the order. |

## Scenario 1: Limit order open long (cross margin)

**Context**: User wants to open long on BTC_USDT at a limit price, cross margin.

**Prompt Examples**:
- "Open long 1 contract BTC_USDT at 65000"
- "BTC_USDT perpetual, cross margin, long 1 contract at 65000"
- "limit buy 1 BTC_USDT futures at 65000"

**Expected Behavior**:
1. Fetch contract via `get_futures_contract(settle="usdt", contract="BTC_USDT")`
2. Switch to cross via `update_futures_dual_comp_position_cross_mode(settle="usdt", contract="BTC_USDT", mode="CROSS")`
3. Query leverage via **position query** (dual: `list_futures_positions` or `get_futures_dual_mode_position`; single: `get_futures_position`) for contract + long side
4. **Show final order summary** (contract, side, size, price, mode, **leverage**, estimated liq/margin), ask user to confirm
5. After confirm, place order via `create_futures_order(settle="usdt", contract="BTC_USDT", size="1", price="65000", tif="gtc")`
6. Verify position via **position query** (dual: `list_futures_positions(holding=true)` or `get_futures_dual_mode_position`; single: `get_futures_position`)
7. Output open result

**Response Template**:
```
Order placed.

Order ID: 123456789
Contract: BTC_USDT
Side: long (buy)
Size: 1 contract
Price: 65000 USDT
Status: open (resting)
Mode: cross
Leverage: 10x (from position query)
```

---

## Scenario 2: Market order open short isolated 10x

**Context**: User wants to open short at market, isolated margin, 10x leverage.

**Prompt Examples**:
- "Market short 2 contracts ETH_USDT, isolated 10x"
- "ETH_USDT isolated 10x, market short 2"
- "market sell 2 ETH_USDT futures with 10x leverage"

**Expected Behavior**:
1. Fetch contract via `get_futures_contract(settle="usdt", contract="ETH_USDT")`
2. Switch to isolated via `update_futures_dual_comp_position_cross_mode(settle="usdt", contract="ETH_USDT", mode="ISOLATED")`
3. Set leverage via **`update_futures_dual_mode_position_leverage`** (dual) or **`update_futures_position_leverage`** (single): `(settle="usdt", contract="ETH_USDT", leverage="10")`
4. **Show final order summary** (contract, side, size, market, mode, leverage, estimated liq/margin), ask user to confirm
5. After confirm, place market order via `create_futures_order(settle="usdt", contract="ETH_USDT", size="-2", price="0", tif="ioc")`
6. Verify position via **position query** (dual: `list_futures_positions(holding=true)` or `get_futures_dual_mode_position`; single: `get_futures_position`)
7. Output fill and position info

**Response Template**:
```
Market short filled.

Order ID: 123456790
Contract: ETH_USDT
Side: short (sell)
Size: 2 contracts
Avg fill: 3500.50 USDT
Status: finished
Mode: isolated 10x

Current position:
- Size: -2 contracts
- Entry: 3500.50
- Liq price: 3850.00
```

---

## Scenario 3: FOK order (fill or kill)

**Context**: User wants FOK so the order either fills completely or is cancelled.

**Prompt Examples**:
- "FOK limit buy 1 BTC_USDT at 65000"
- "BTC_USDT FOK, long 1 at 65000"
- "fill or kill buy 1 BTC_USDT at 65000"

**Expected Behavior**:
1. Fetch contract via `get_futures_contract(settle="usdt", contract="BTC_USDT")`
2. Place FOK via `create_futures_order(settle="usdt", contract="BTC_USDT", size="1", price="65000", tif="fok")`
3. If depth insufficient, return ORDER_FOK error
4. If success, output full fill result

**Error Case Response**:
```
FOK order did not fill.

Reason: Insufficient depth to fill entirely.
Suggestions:
1. Reduce size
2. Adjust price
3. Use GTC or IOC instead
```

---

## Scenario 4: Price outside limit protection

**Context**: User’s price is too far from market and hits exchange limit protection.

**Prompt Examples**:
- "BTC_USDT long at 100000" (market ~65000)

**Expected Behavior**:
1. Do **not** pre-compute valid range from contract `order_price_deviate` (actual limit depends on risk_limit_tier and may differ).
2. Place order; if API returns **PRICE_TOO_DEVIATED**, extract the **valid price range from the error message** and show it to the user.
3. Suggest user adjust price within that range.

**Response Template** (after receiving PRICE_TOO_DEVIATED):
```
Order failed: price outside limit protection.

Your price: 100000 USDT
Valid range (from exchange): [min] - [max] USDT

Suggestion: Adjust price within the range above.
```

---

## Scenario 5: Insufficient balance

**Context**: Account margin is insufficient for the requested position.

**Prompt Examples**:
- "Open long 100 contracts BTC_USDT" (insufficient balance)

**Expected Behavior**:
1. Fetch contract via `get_futures_contract(settle="usdt", contract="BTC_USDT")`
2. Place order → receive BALANCE_NOT_ENOUGH
3. Output balance warning and suggestions

**Response Template**:
```
Order failed: insufficient margin.

Required margin: 6500 USDT
Available: 1000 USDT

Suggestions:
1. Reduce size
2. Add USDT
3. Increase leverage (e.g. from 10x to 20x)
```

---

## Scenario 6: Mode switch failed (position not empty)

**Context**: User tries to switch cross/isolated while having an open position; switch is rejected.

**Prompt Examples**:
- "Switch to cross" (currently isolated with position)
- "Cross margin long BTC_USDT" (currently isolated with position)

**Expected Behavior**:
1. Call `update_futures_dual_comp_position_cross_mode(settle="usdt", contract="BTC_USDT", mode="CROSS")`
2. Receive POSITION_HOLDING (or similar; API returns this for mode switch with position)
3. Query position via **position query** (dual: `list_futures_positions` or `get_futures_dual_mode_position`; single: `get_futures_position`)
4. Output failure and current position

**Response Template**:
```
Mode switch failed: position not empty.

Current position: BTC_USDT long 5 contracts
Current mode: isolated 10x

Suggestion: Close the position first, then switch margin mode.
```

---

## Scenario 6b: Dual position — switch margin mode (interrupt)

**Context**: User wants to open in a different margin mode than current position, and account is **dual position** mode.

**Expected Behavior**:
1. During open flow, detect target margin mode ≠ current `pos_margin_mode` and contract has a position.
2. Call `get_futures_accounts(settle="usdt")`; if `position_mode === "dual"`.
3. **Interrupt**: do not call `update_futures_dual_comp_position_cross_mode`, do not place order.
4. Output: *"Please close the position first, then open a new one."*

**Response Template**:
```
In dual position mode you cannot switch this contract’s margin mode while a position exists.

Please close the position first, then open a new one.
```

---

## Scenario 6c: Single position — switch margin mode (confirm then continue)

**Context**: User wants to open in a different margin mode; account is **single position** mode.

**Expected Behavior**:
1. Detect target margin mode ≠ current `pos_margin_mode` and contract has a position.
2. Call `get_futures_accounts(settle="usdt")`; if `position_mode === "single"`.
3. **Do not interrupt**. Prompt: *"You already have a {currency} position; switching margin mode will apply to this position too. Continue?"* (e.g. BTC_USDT → "You already have a BTC position...").
4. After user confirms, call `update_futures_dual_comp_position_cross_mode(settle, contract, mode="ISOLATED" or "CROSS")`, then continue leverage and place order.

**Response Template** (before confirm):
```
You already have a BTC position; switching margin mode will apply to this position too. Continue?
```

---

## Scenario 7: POC (Post Only) order

**Context**: User wants to post as Maker only; if the order would take liquidity it should be cancelled.

**Prompt Examples**:
- "POC limit buy 1 BTC_USDT at 64000"
- "Maker only, BTC_USDT long 1 at 64000"
- "post only buy 1 BTC_USDT at 64000"

**Expected Behavior**:
1. Fetch contract via `get_futures_contract(settle="usdt", contract="BTC_USDT")`
2. Place POC via `create_futures_order(settle="usdt", contract="BTC_USDT", size="1", price="64000", tif="poc")`
3. If order would immediately match, return ORDER_POC (or similar)
4. If resting as Maker, output success

**Response Template**:
```
Order placed (Post Only).

Order ID: 123456791
Contract: BTC_USDT
Side: long (buy)
Size: 1 contract
Price: 64000 USDT
Status: open
Role: Maker

Note: This order will only fill as Maker (maker fee).
```

---

## Scenario 8: Open by U (USDT notional)

**Context**: User specifies size in USDT (U); convert to contracts then open.

**Prompt Examples**:
- "BTC_USDT long 1000U"
- "Market short 500 U ETH_USDT"
- "Long 2000 USDT notional BTC"

**Expected Behavior**:
1. Fetch contract via `get_futures_contract(settle="usdt", contract="BTC_USDT")` for `mark_price`, `quanto_multiplier`.
2. Compute contracts: no leverage → contracts = u ÷ mark_price ÷ quanto_multiplier; **with leverage** → contracts = u × leverage ÷ mark_price ÷ quanto_multiplier (respect precision and `order_size_min`).
3. If contracts < order_size_min, prompt "Notional converts to below minimum size."
4. Proceed with open flow (mode switch, leverage, `create_futures_order`) using the computed size.
5. Report can show both "~xxx U" and "yy contracts".
