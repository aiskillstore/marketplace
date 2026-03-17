---
name: grimoire-polymarket
description: Queries Polymarket market data and CLOB state, and manages CLOB orders via the Grimoire venue CLI wrapper backed by the official Polymarket CLI.
---

# Grimoire Polymarket Skill

Use this skill for Polymarket market discovery, CLOB market data, and order-management operations through the `polymarket` venue adapter.

Preferred invocations:

- `grimoire venue polymarket ...`
- `npx -y @grimoirelabs/cli venue polymarket ...` (no-install)
- `bun run packages/cli/src/index.ts venue polymarket ...` (repo-local)
- `grimoire-polymarket ...` (direct binary from `@grimoirelabs/venues`)

Recommended preflight:

- `grimoire venue doctor --adapter polymarket --json`
- `grimoire venue polymarket info --format json`

## Commands

Canonical agent commands:

- `grimoire venue polymarket info [--format <auto|json|table>]`
- `grimoire venue polymarket search-markets [--query <text>] [--slug <slug|url>] [--question <text>] [--event <text>] [--tag <text>] [--category <text>] [--league <text>] [--sport <text>] [--open-only <true|false>] [--active-only <true|false>] [--ignore-end-date <true|false>] [--tradable-only <true|false>] [--all-pages <true|false>] [--max-pages <n>] [--stop-after-empty-pages <n>] [--limit <n>] [--format <auto|json|table>]`

Allowed passthrough groups (official CLI surface, restricted by wrapper policy):

- `markets` (`list|get|search|tags`)
- `events` (`list|get|tags`)
- `tags` (`list|get|related|related-tags`)
- `series` (`list|get`)
- `sports` (`list|market-types|teams`)
- `clob` (book/prices/markets/orders/trades/etc.)
- `data` (positions/value/leaderboards/etc.)
- `status`

Blocked groups in this wrapper (intentionally not exposed for agents):

- `wallet`
- `bridge`
- `approve`
- `ctf`
- `setup`
- `upgrade`
- `shell`

Legacy compatibility aliases are still supported (`market`, `book`, `midpoint`, `spread`, `price`, `last-trade-price`, `tick-size`, `neg-risk`, `fee-rate`, `price-history`, `order`, `trades`, `open-orders`, `balance-allowance`, `closed-only-mode`, `server-time`) but should not be used for new agent flows.

## Examples

```bash
# Wrapper/health
grimoire venue polymarket info --format json
grimoire venue polymarket status --format json

# Canonical discovery
grimoire venue polymarket search-markets --query bitcoin --active-only true --open-only true --format json
grimoire venue polymarket search-markets --category sports --league "la liga" --active-only true --open-only true --format json

# Official passthrough discovery/data
grimoire venue polymarket markets list --limit 25 --format json
grimoire venue polymarket markets search "atleti" --limit 25 --format json
grimoire venue polymarket events list --limit 25 --format json
grimoire venue polymarket clob book <token_id> --format json
grimoire venue polymarket clob midpoint <token_id> --format json
grimoire venue polymarket clob price <token_id> --side buy --format json

# Authenticated order-management reads
grimoire venue polymarket clob order <order_id> --format json
grimoire venue polymarket clob trades --market <condition_id> --format json
grimoire venue polymarket clob orders --market <condition_id> --format json
grimoire venue polymarket clob balance --asset-type conditional --token <token_id> --format json
```

## Runtime Configuration

Adapter/runtime auth (for spell execution and authenticated CLOB operations):

- required: `POLYMARKET_PRIVATE_KEY`
- optional API creds: `POLYMARKET_API_KEY`, `POLYMARKET_API_SECRET`, `POLYMARKET_API_PASSPHRASE`
- optional derive toggle (default true): `POLYMARKET_DERIVE_API_KEY=true|false`
- optional signature routing: `POLYMARKET_SIGNATURE_TYPE` (`0` EOA, `1` POLY_PROXY, `2` GNOSIS_SAFE), `POLYMARKET_FUNDER`

Venue CLI backend:

- Official binary required: `polymarket`
- Install: `brew tap Polymarket/polymarket-cli && brew install polymarket`
- Optional path override: `POLYMARKET_OFFICIAL_CLI=/custom/path/polymarket`

## Adapter Notes

- Adapter name: `polymarket`
- Execution type: `offchain`
- Supported chain metadata: `137` (Polygon)
- Action type: `custom`
- Supported custom ops: `order`, `cancel_order`, `cancel_orders`, `cancel_all`, `heartbeat`

Order argument aliases accepted:

- token: `token_id` or `tokenID` or `tokenId` or `coin`
- amount: `size` or `amount`
- side: `BUY`/`SELL`
- order type: `GTC`/`GTD`/`FOK`/`FAK`
- extra compatibility aliases: `arg0..arg5`, `reduce_only`

Order type routing:

- `GTC`/`GTD` -> limit order path (`createAndPostOrder`)
- `FOK`/`FAK` -> market order path (`createAndPostMarketOrder`)

## Notes

- Prefer `--format json` for agent and automation workflows.
- `search-markets` is the agent-oriented normalized discovery command; passthrough `markets search` is thinner and closer to official behavior.
- Keep prompts/tooling on this CLI surface; do not call Polymarket HTTP APIs directly from advisory tools.
