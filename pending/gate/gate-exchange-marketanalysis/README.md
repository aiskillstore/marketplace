# gate-exchange-marketanalysis

## Overview

An AI Agent skill that provides market tape analysis on [Gate](https://www.gate.com), covering ten scenarios: liquidity, momentum, liquidation monitoring, funding rate arbitrage, basis (spot–futures) monitoring, manipulation risk, order book explanation, slippage simulation, K-line breakout/support–resistance, and liquidity with weekend vs weekday. All scenarios use a defined **MCP call order and output format** in `references/scenarios.md`.

---

### Core Capabilities

| Capability | Description | Example |
|------------|-------------|---------|
| **Liquidity analysis** | Order book depth, 24h vs 30d volume, slippage | "How is ETH liquidity?" |
| **Momentum** | Buy vs sell share, funding rate | "Is BTC more long or short in 24h?" |
| **Liquidation monitoring** | 1h liq vs baseline, squeeze, wicks | "Recent liquidations?" |
| **Funding arbitrage** | Rate + volume, spot–futures spread | "Any arbitrage opportunities?" |
| **Basis monitoring** | Spot–futures price, premium index | "What is the basis for BTC?" |
| **Manipulation risk** | Depth/volume ratio, large orders | "Is this coin easy to manipulate?" |
| **Order book explainer** | Bids/asks, spread, depth | "Explain the order book" |
| **Slippage simulation** | Market-order slippage vs best ask (pair + quote amount required) | "ADA_USDT slippage for $10K market buy?" |
| **K-line breakout / support–resistance** | Candlesticks + tickers; support/resistance; breakout momentum | "Does SOL/USDT show breakout signs? Analyze support and resistance." |
| **Liquidity + weekend vs weekday** | Order book + 90d candlesticks + tickers; weekend vs weekday volume/return | "Evaluate ETH liquidity and compare weekend vs weekday." |

> 📊 **Ten scenarios (Case 1–10):** Ask about liquidity, momentum, liquidation, arbitrage, basis, manipulation risk, order book, slippage simulation, K-line breakout/support–resistance, or liquidity vs weekend/weekday; the skill routes to the right case and follows `references/scenarios.md`.

---

## Architecture

```
Natural Language Input
    ↓
Intent Routing (Case 1–10, spot vs futures)
    ↓
Gate MCP Tools
    ├── get_spot_order_book / get_futures_order_book
    ├── get_spot_tickers / get_futures_tickers
    ├── get_spot_candlesticks / get_futures_candlesticks
    ├── get_spot_trades / get_futures_funding_rate
    ├── list_futures_liq_orders (when available)
    └── get_futures_premium_index
    ↓
Analysis & Judgment Logic
    ↓
Structured Report → Natural language response
```

**Sub-Modules:** `references/scenarios.md` — MCP call order, parameters, required fields, and report templates per case.

---

## Agent Use Cases

### 1. Liquidity check
> "How is ETH liquidity?"

Depth levels, 24h vs 30d volume, slippage; liquidity rating. For perpetual/contract, use futures order book and candlesticks/tickers.

### 2. Momentum (buy vs sell)
> "Is BTC more long or short in 24h, and is it sustainable?"

Trades → buy/sell share; tickers, candlesticks, order book top 10, funding rate for bias and sustainability.

### 3. Liquidation monitoring
> "Recent liquidations?"

Liquidation orders (if MCP provides), candlesticks, tickers; anomaly and squeeze labels.

### 4. Funding arbitrage scan
> "Any arbitrage opportunities?"

Screen by |rate| and volume; spot tickers and order book; exclude thin books.

### 5. Basis (spot–futures)
> "What is the basis for BTC?"

Spot and futures tickers, premium index; current vs history, widening/narrowing.

### 6. Manipulation risk
> "Is this coin easy to manipulate?"

Depth ratio (top 10 / 24h volume); large and consecutive same-side trades.

### 7. Order book explainer
> "Explain the order book"

Live order book (e.g. limit=10) + ticker; explain bids/asks, spread, depth.

### 8. Slippage simulation
> "ADA_USDT slippage for a $10K market buy?"

Requires pair and quote amount. Spot or futures: order book → tickers (futures: get_futures_contract first for quanto_multiplier). Walk ask ladder; report slippage vs best ask.

### 9. K-line breakout / support–resistance
> "Does SOL/USDT show signs of breaking out? Analyze support and resistance."

Candlesticks → tickers; derive support/resistance from OHLC; use 24h price and volume for momentum and breakout assessment.

### 10. Liquidity + weekend vs weekday
> "Evaluate ETH liquidity and compare weekend vs weekday."

Order book + 90d candlesticks + tickers (futures: get_futures_contract first). Split days into weekend vs weekday; compare volume and return.

---

## Quick Start

### Prerequisites

1. Gate MCP configured and connected (use the `gate-mcp-installer` skill if needed).
2. No extra dependencies.

### Example Prompts

```
# Liquidity
"How is ETH liquidity?"
"BTC perpetual depth"

# Momentum
"BTC 24h more long or short, sustainable?"

# Liquidation
"Recent liquidations?"

# Arbitrage
"Any funding rate arbitrage opportunities?"

# Basis
"What is the basis for ETH?"

# Manipulation
"Is PEPE easy to manipulate?"

# Order book
"Explain the order book with an example"

# Slippage simulation (pair + amount required)
"ADA_USDT contract slippage: if I market buy $20K, how much slippage?"

# K-line breakout / support–resistance
"Based on recent K-line, does SOL/USDT show breakout? Analyze support and resistance."

# Liquidity + weekend vs weekday
"Evaluate ETH contract liquidity and compare weekend vs weekday."
```

See `references/scenarios.md` for full MCP call order and report templates.

---

## File Structure

```
gate-exchange-marketanalysis/
├── README.md                          # This file
├── SKILL.md                           # Skill routing and instructions
├── CHANGELOG.md                       # Version history
└── references/
    ├── scenarios.md                   # MCP call order, judgment logic, report templates per case
    └── case-test-report.md            # Optional: simulation test summary
```

---

## Security

- No external scripts or executable code
- Uses Gate MCP tools only — no direct API calls
- No credential handling or storage
- Read-only market data analysis, no trading operations
- No file system writes
- No data collection, telemetry, or analytics

## License

MIT
