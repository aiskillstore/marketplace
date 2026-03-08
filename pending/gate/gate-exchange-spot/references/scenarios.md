# Scenarios

This document defines behavior-oriented scenario templates for all 25 spot cases.

## Global Execution Gate (Mandatory)

For every scenario that includes `create_spot_order`:
- Build and present an Order Draft first
- Require explicit confirmation from the immediately previous user turn
- Treat confirmation as single-use
- Re-confirm whenever parameters or intent change
- For multi-leg flows, confirm each leg separately

If confirmation is missing/ambiguous/stale, do not execute any trading call.

## I. Buy and Account Queries (1-8)

### Scenario 1: Market Buy by Quote Amount
**Context**: User wants to buy a fixed USDT value of a coin at market price.
**Prompt Examples**:
- "Buy 100U of BTC."
- "I want to buy 100 USDT of BTC now."
**Expected Behavior**:
1. Fetch data via `get_spot_accounts` `currency=USDT`.
2. Calculate available quote balance and validate market-buy `amount` semantics (`amount=quote_amount`).
3. Output `Order Draft` and then `Execution Result Report` after confirmation.
**Unexpected Behavior**:
1. Directly returns "Order placed" with an order id before any `Confirm order`.
2. Sends `amount=0.001 BTC` for market buy request "buy 100U", causing wrong notional.
3. Reports filled quantity but omits average fill price and fee impact.

### Scenario 2: Limit Buy at Target Price
**Context**: User wants to buy at a specified limit price.
**Prompt Examples**:
- "Buy 100U BTC at 60000."
- "Place a limit buy for BTC at 60000."
**Expected Behavior**:
1. Fetch data via `get_spot_accounts` `currency=USDT`.
2. Calculate affordability and validate target `limit_price` precision/constraints.
3. Output `Limit Order Draft` and then `Open Order/Execution Report` after confirmation.
**Unexpected Behavior**:
1. Converts to market order and executes immediately even though user asked for limit price.
2. Returns "open order created" without checking whether quote balance can support order value.
3. Uses wrong price precision and returns exchange error without a user-readable fix suggestion.

### Scenario 3: Buy with All USDT
**Context**: User wants to convert full USDT balance into a target coin.
**Prompt Examples**:
- "Use all my USDT to buy ETH."
- "All-in USDT into ETH."
**Expected Behavior**:
1. Fetch data via `get_spot_accounts` `currency=USDT`.
2. Calculate full available quote amount and executable order size.
3. Output `All-in Order Draft` and then `Post-Trade Balance Report` after confirmation.
**Unexpected Behavior**:
1. Uses total balance instead of available balance, leading to `BALANCE_NOT_ENOUGH` at execution.
2. Places full-size order without draft/confirmation despite all-in risk.
3. Returns no residual balance summary, so user cannot verify remaining funds.

### Scenario 4: Tradability and Unit-Cost Check
**Context**: User wants a buy readiness check before placing any order.
**Prompt Examples**:
- "Can BTC be traded now? How much for one BTC?"
- "Check ETH tradability and current unit price."
**Expected Behavior**:
1. Fetch data via `get_currency` `currency=BASE`, `get_currency_pair` `currency_pair=BASE_USDT`, and `get_spot_tickers` `currency_pair=BASE_USDT`.
2. Calculate tradability result, min-trade constraints, and current unit cost.
3. Output `Readiness Check Report` (no order execution).
**Unexpected Behavior**:
1. Places an order in what should be a read-only "can I trade?" request.
2. Ignores disabled/suspended trading status and answers "tradable" incorrectly.
3. Returns only ticker price, missing min amount/precision constraints.

### Scenario 5: Total Account Valuation
**Context**: User wants total account value in USDT terms.
**Prompt Examples**:
- "How much is my account worth now?"
- "Give me my total USDT-equivalent value."
**Expected Behavior**:
1. Fetch data via `get_spot_accounts` `currency=all` and `get_spot_tickers` `currency_pair=*USDT`.
2. Calculate per-asset USDT valuation and aggregate portfolio total.
3. Output `Portfolio Valuation Report`.
**Unexpected Behavior**:
1. Excludes low-liquidity or non-USDT assets from total, materially understating account value.
2. Uses stale or mismatched pair prices, producing unrealistic valuation output.
3. Triggers trade-related tools in a portfolio-report-only task.

### Scenario 6: Cancel All Open Orders Then Recheck Balance
**Context**: User wants all open orders canceled and updated balances.
**Prompt Examples**:
- "Cancel all unfilled orders and show my balance."
- "Clear open orders first."
**Expected Behavior**:
1. Fetch data via `cancel_all_spot_orders` `currency_pair=optional` and `get_spot_accounts` `currency=all`.
2. Calculate canceled-order summary and refreshed available balances.
3. Output `Cancel Summary + Balance Report`.
**Unexpected Behavior**:
1. Cancels only one pair's orders but reports "all orders canceled."
2. Fails to show which order ids were canceled vs already filled.
3. Skips post-cancel balance refresh, so refund state is unknown.

### Scenario 7: Sell Full Dust Position
**Context**: User wants to sell all holdings of a coin into USDT.
**Prompt Examples**:
- "Sell all my DOGE to USDT."
- "Convert my DOGE position to USDT."
**Expected Behavior**:
1. Fetch data via `get_spot_accounts` `currency=DOGE` and `get_currency_pair` `currency_pair=DOGE_USDT`.
2. Calculate sellable amount against min-size/precision constraints.
3. Output `Sell Draft` or `Constraint Warning Report`, then `Execution Result` after confirmation.
**Unexpected Behavior**:
1. Submits size below `min_base_amount`, then surfaces raw API error only.
2. Rounds amount with wrong precision and creates unexpected partial leftover balance.
3. Executes sell without showing user that dust remains unsellable.

### Scenario 8: Balance and Minimum-Amount Buy Check
**Context**: User asks to buy only if both balance and minimum amount conditions are satisfied.
**Prompt Examples**:
- "I want to buy 5U ETH; if possible, place it."
- "Check if I can buy 5 USDT of ETH, then buy."
**Expected Behavior**:
1. Fetch data via `get_spot_accounts` `currency=USDT` and `get_currency_pair` `currency_pair=ETH_USDT`.
2. Calculate both checks: available balance and `min_quote_amount` threshold gap.
3. Output `Eligibility Report` and, if eligible, `Order Draft` then `Execution Result` after confirmation.
**Unexpected Behavior**:
1. Places order even when 5U is below `min_quote_amount` or available quote balance.
2. Returns generic "cannot trade" without showing minimum threshold and shortfall.
3. Fails to provide top-up guidance (how much additional USDT is needed).

## II. Smart Monitoring and Trading (9-16)

### Scenario 9: Buy 2% Lower
**Context**: User wants a discounted-entry limit buy based on current price.
**Prompt Examples**:
- "Buy 50U BTC when it is 2% lower than now."
**Expected Behavior**:
1. Fetch data via `get_spot_tickers` `currency_pair=BTC_USDT`.
2. Calculate target price (`current * 0.98`) for limit buy.
3. Output `Target-Price Order Draft` and then `Execution/Open-Order Report` after confirmation.
**Unexpected Behavior**:
1. Uses an outdated last price and computes wrong -2% target.
2. Submits market order instead of computed limit order.
3. Places order without showing target price formula in draft.

### Scenario 10: Sell at Current + 500
**Context**: User wants a profit-taking limit sell at fixed offset.
**Prompt Examples**:
- "If BTC rises by 500, sell my holdings."
**Expected Behavior**:
1. Fetch data via `get_spot_tickers` `currency_pair=BTC_USDT`.
2. Calculate target sell price (`current + 500`) and executable position size.
3. Output `Limit Sell Draft` and then `Execution/Open-Order Report` after confirmation.
**Unexpected Behavior**:
1. Sells immediately at market instead of placing current+500 limit sell.
2. Calculates offset from wrong reference price (for example 24h open, not current).
3. Omits size source (available holdings) and causes insufficient-balance failure.

### Scenario 11: Buy Near 24h Low
**Context**: User wants to buy only when price is near daily low.
**Prompt Examples**:
- "If ETH is near today's low, buy."
**Expected Behavior**:
1. Fetch data via `get_spot_tickers` `currency_pair=ETH_USDT`.
2. Calculate current-vs-24h-low distance and condition pass/fail.
3. Output `Condition Decision Report`; if passed, output `Order Draft` then `Execution Result`.
**Unexpected Behavior**:
1. Buys even though current price is clearly above user's "near low" threshold.
2. Returns binary yes/no without reporting current price, 24h low, and distance.
3. Treats "near" as exact equality only, causing unrealistic non-execution.

### Scenario 12: Sell on 5% Drop Request
**Context**: User wants downside-exit style execution using a computed target.
**Prompt Examples**:
- "Sell if BTC drops 5%."
**Expected Behavior**:
1. Fetch data via `get_spot_tickers` `currency_pair=BTC_USDT`.
2. Calculate downside trigger price (`current * 0.95`) and sell order params.
3. Output `Downside-Exit Draft` and then `Execution/Open-Order Report` after confirmation.
**Unexpected Behavior**:
1. Claims native TP/SL trigger support and submits unsupported order semantics.
2. Executes sell without confirmation under "risk-control urgency" wording.
3. Computes 5% drop from wrong anchor (entry price vs current price) without disclosure.

### Scenario 13: Buy Top 24h Gainer
**Context**: User wants to rotate into the strongest coin by recent performance.
**Prompt Examples**:
- "Buy 20U of the top gainer now."
**Expected Behavior**:
1. Fetch data via `get_spot_tickers` `currency_pair=all tradable`.
2. Calculate top gainer ranking by 24h change and selected target pair.
3. Output `Ranking + Selected Order Draft` and then `Execution Result` after confirmation.
**Unexpected Behavior**:
1. Picks a non-top gainer while saying it is rank #1.
2. Selects an illiquid/suspended pair and fails at order placement.
3. Omits ranking evidence (top candidates and 24h change values).

### Scenario 14: Buy the Bigger Loser (BTC vs ETH)
**Context**: User wants comparative dip-buy between two assets.
**Prompt Examples**:
- "Between BTC and ETH, buy whichever dropped more."
**Expected Behavior**:
1. Fetch data via `get_spot_tickers` `currency_pair=BTC_USDT,ETH_USDT`.
2. Calculate comparative 24h decline and select the larger loser.
3. Output `Comparison Report + Order Draft` and then `Execution Result` after confirmation.
**Unexpected Behavior**:
1. Chooses BTC/ETH winner without presenting both percentage changes.
2. Uses absolute price drop rather than percentage decline despite scenario intent.
3. Executes before final confirmation after showing comparison.

### Scenario 15: Buy Then Place +2% Sell
**Context**: User wants a two-leg flow: entry first, then exit order.
**Prompt Examples**:
- "Buy 100U BTC, then place sell at +2%."
**Expected Behavior**:
1. Fetch data via `create_spot_order` `leg1=buy` and then fill reference for leg2.
2. Calculate second-leg target price (`fill_reference * 1.02`) and sell size.
3. Output `Leg-1 Report` and `Leg-2 Draft/Execution Report` with per-leg confirmations.
**Unexpected Behavior**:
1. Executes buy and sell legs under one confirmation, bypassing per-leg checkpoint.
2. Uses requested +2% on intended price instead of actual fill reference.
3. Creates second leg with wrong quantity (requested amount vs filled amount).

### Scenario 16: Fee-Inclusive Cost Estimate
**Context**: User wants pre-trade cost estimation only.
**Prompt Examples**:
- "If I buy 1000U, what's total including fees?"
**Expected Behavior**:
1. Fetch data via `get_wallet_fee` `account=tier` and `get_spot_tickers` `currency_pair=target`.
2. Calculate principal + fee estimate and total payable amount.
3. Output `Fee-Inclusive Cost Estimate Report` (no order execution).
**Unexpected Behavior**:
1. Places a trade even though user asked only for estimation.
2. Returns "about 1000U" without fee breakdown or fee rate source.
3. Uses maker fee assumption without stating uncertainty for taker execution.

## III. Order Management and Amendment (17-25)

### Scenario 17: Raise Price for Unfilled Buy Order
**Context**: User wants to amend an unfilled buy order to improve fill chance.
**Prompt Examples**:
- "My buy order is unfilled, raise the price a bit."
**Expected Behavior**:
1. Fetch data via `list_spot_orders` `status=open,side=buy`.
2. Calculate amendment target (raise amount/new price) and identify exact order id.
3. Output `Amendment Draft`; after confirmation, output `Amendment Result Report` via `amend_spot_order`.
**Unexpected Behavior**:
1. Amends order without confirming raise amount/new target price.
2. Amends the wrong order when multiple open buy orders exist.
3. Returns success without showing old price -> new price delta.

### Scenario 18: Verify Latest Buy Fill and Current Holdings
**Context**: User wants confirmation of executed buy and current total holdings.
**Prompt Examples**:
- "Did my BTC buy fill, and how much BTC do I have now?"
**Expected Behavior**:
1. Fetch data via `list_spot_my_trades` `currency_pair=target,side=buy` and `get_spot_accounts` `currency=BASE`.
2. Calculate latest fill amount (X) and current holdings (Y).
3. Output `Fill-and-Holdings Verification Report`.
**Unexpected Behavior**:
1. Uses old trade history entry instead of latest buy fill.
2. Returns fill quantity but not current holding total (or vice versa).
3. Mixes pair/currency units (for example reports USDT where BTC is expected).

### Scenario 19: Cancel If Still Unfilled and Verify Refund
**Context**: User wants conditional cancellation and post-cancel balance verification.
**Prompt Examples**:
- "If my ETH buy is still open, cancel it and check refund."
**Expected Behavior**:
1. Fetch data via `list_spot_orders` `status=open,currency_pair=ETH_USDT`, then `cancel_spot_order`, then `get_spot_accounts` `currency=USDT`.
2. Calculate cancellation status and quote-fund refund delta.
3. Output `Cancel-and-Refund Verification Report`.
**Unexpected Behavior**:
1. Attempts to cancel already filled/canceled order without clear handling path.
2. Reports "refund completed" without checking updated quote balance.
3. Fails to identify target order among multiple open ETH buys.

### Scenario 20: Rebuy at Last Fill Price
**Context**: User wants another buy using previous execution price.
**Prompt Examples**:
- "If balance allows, buy 100U BTC at my last buy price."
**Expected Behavior**:
1. Fetch data via `list_spot_my_trades` `currency_pair=BTC_USDT` and `get_spot_accounts` `currency=USDT`.
2. Calculate rebuy limit price from last fill and affordability for 100U.
3. Output `Rebuy Draft` and then `Execution/Open-Order Report` after confirmation.
**Unexpected Behavior**:
1. Uses current ticker price instead of last fill price for rebuy.
2. Skips balance check and hits insufficient funds after confirmation.
3. Places market order when scenario requires price reuse via limit order.

### Scenario 21: Break-even Exit
**Context**: User wants to sell only if current price is above cost basis.
**Prompt Examples**:
- "If I can exit ETH without loss, sell all."
**Expected Behavior**:
1. Fetch data via `list_spot_my_trades` `currency_pair=ETH_USDT` and `get_spot_tickers` `currency_pair=ETH_USDT`.
2. Calculate cost basis vs current price and pass/fail for break-even exit.
3. Output `Break-even Decision Report`; if passed, output `Sell Draft` then `Execution Result`.
**Unexpected Behavior**:
1. Sells even when current price is below computed cost basis.
2. Computes cost basis from one trade only, ignoring partial fills/history.
3. Omits fee-adjusted break-even explanation, misleading "no-loss" decision.

### Scenario 22: Full Asset Swap (DOGE -> BTC)
**Context**: User wants a two-leg conversion only above minimum value threshold.
**Prompt Examples**:
- "Swap all DOGE to BTC if worth at least 10U."
**Expected Behavior**:
1. Fetch data via `get_spot_accounts` `currency=DOGE` and `get_spot_tickers` `currency_pair=DOGE_USDT,BTC_USDT`.
2. Calculate DOGE valuation vs 10U threshold and two-leg conversion sizing.
3. Output `Swap Eligibility Report` and per-leg `Order Draft/Execution Report` with per-leg confirmations.
**Unexpected Behavior**:
1. Executes swap when DOGE valuation is below 10U threshold.
2. Runs both legs without independent confirmation checkpoints.
3. Proceeds with buy leg before confirming sell leg completion amount.

### Scenario 23: Buy Only If Below Price Threshold
**Context**: User wants conditional buy and post-trade balance report.
**Prompt Examples**:
- "If BTC < 60000, buy 50U and show balance."
**Expected Behavior**:
1. Fetch data via `get_spot_tickers` `currency_pair=BTC_USDT` and (if executed) `get_spot_accounts` `currency=all`.
2. Calculate price-threshold check (`current < 60000`) and order eligibility.
3. Output `Condition Decision Report`; if passed, output `Order Draft` then `Execution + Balance Report`.
**Unexpected Behavior**:
1. Buys despite current price not below 60000.
2. Uses delayed ticker snapshot and mis-evaluates condition.
3. Skips post-trade account refresh and returns stale balance.

### Scenario 24: Buy on Short-Term Uptrend
**Context**: User wants trend-filtered execution using recent candlesticks.
**Prompt Examples**:
- "If BTC has been rising for recent hours, buy 100U."
**Expected Behavior**:
1. Fetch data via `get_spot_candlesticks` `currency_pair=BTC_USDT,interval=1h,count=4`.
2. Calculate bullish-candle count and trend pass/fail (`>=3/4`).
3. Output `Trend Check Report`; if passed, output `Order Draft` then `Execution Result`.
**Unexpected Behavior**:
1. Buys without fetching/validating the last 4 hourly candles.
2. Miscounts bullish candles (for example includes incomplete current candle incorrectly).
3. Executes on sideways/downtrend while labeling it "uptrend confirmed."

### Scenario 25: Fast Execution Limit Buy from Order Book
**Context**: User wants fastest practical limit execution using book top.
**Prompt Examples**:
- "Check ETH book and place fastest 50U buy."
**Expected Behavior**:
1. Fetch data via `get_spot_order_book` `currency_pair=ETH_USDT`.
2. Calculate execution-oriented limit price from `ask1` and size feasibility.
3. Output `Fast-Execution Draft` and then `Execution/Open-Order Report` after confirmation.
**Unexpected Behavior**:
1. Uses bid price instead of ask-side top for fast buy placement.
2. Ignores depth/size mismatch and proposes unrealistic instant fill.
3. Omits risk note about slippage or partial fill at chosen limit price.
