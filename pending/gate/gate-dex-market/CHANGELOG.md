# Changelog

All notable changes to `gate-dex-market` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2026.3.6-1] - 2026-03-06

### Added

- 7 public market data query tools (all require no authentication)
  - `market_get_kline` — K-line data
  - `market_get_tx_stats` — On-chain transaction statistics
  - `market_get_pair_liquidity` — Trading pair liquidity
  - `token_get_coin_info` — Token details
  - `token_ranking` — Token rankings
  - `token_get_coins_range_by_created_at` — New token discovery
  - `token_get_risk_info` — Security risk audit
- 5 workflows (A–E): market data, token details, rankings, security audit, new token discovery
- MCP Server remote HTTP connection check (mandatory Step 0)
- Skill routing: post-action guidance within market tools
- Display standards: price precision, address truncation, time formatting
- Security rules: read-only, objective display, no investment advice
