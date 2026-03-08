# Gate Futures Trading

## Overview

AI Agent skill for [Gate](https://www.gate.com) USDT perpetual futures. Supports **four operations only**: open position, close position, cancel order, amend order. No market monitoring or arbitrage scanning.

### Core Capabilities

| Module | Description | Example |
|--------|-------------|---------|
| **Open** | Limit/market open long or short, cross/isolated mode | "BTC_USDT long 100U, limit 65000" |
| **Close** | Full close, partial close, reverse position | "Close all BTC", "Reverse to short" |
| **Cancel** | Cancel single or batch orders | "Cancel all orders", "Cancel that buy order" |
| **Amend** | Change order price or size | "Change price to 60000" |

---

## Routing

Intent is routed by keywords to the corresponding reference:

| Intent | Keywords | Reference |
|--------|----------|-----------|
| Open position | long, short, buy, sell, open | `references/open-position.md` |
| Close position | close, close all, reverse | `references/close-position.md` |
| Cancel order | cancel, revoke | `references/cancel-order.md` |
| Amend order | amend, modify | `references/amend-order.md` |

---

## Quick Start

### Prerequisites

- Gate MCP configured and connected

### Example Prompts

```
# Open
"Open long 1 contract BTC_USDT at 65000"
"BTC_USDT long 100U, limit 65000"

# Close
"Close all BTC_USDT"
"Close half"

# Cancel
"Cancel all BTC_USDT orders"

# Amend
"Change that buy order price to 64000"
```

---

## File Structure

```
gate-futures/
├── README.md
├── SKILL.md
├── CHANGELOG.md
└── references/
    ├── open-position.md
    ├── close-position.md
    ├── cancel-order.md
    └── amend-order.md
```

---

## Security

- Uses Gate MCP tools only
- Open/close/cancel/amend require user confirmation before execution
- No credential handling or storage in this skill

## License

MIT
