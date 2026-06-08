# portfolio

```
Portfolio overview — total assets, P/L, intraday P/L, holdings, and cash breakdown

Fetches live quotes, FX rates, and account balance concurrently, then computes all P/L figures in USD.

Returns: overview (`total_asset`, `market_cap`, `total_cash`, `total_pl`, `total_today_pl`, `margin_call`, `risk_level`, `credit_limit`, currency), holdings table, and cash balances.

Without subcommand: shows full portfolio overview. Subcommands: short-margin Example: longbridge portfolio Example: longbridge portfolio short-margin

Usage: longbridge portfolio [OPTIONS] [COMMAND]

Commands:
  short-margin  Short-selling margin deposit details for the current account
  help          Print this message or the help of the given subcommand(s)

Options:
      --format <FORMAT>
          Output format: 'pretty' for human-readable, 'json' for AI agents and scripting
          
          [default: pretty]
          [possible values: table, json]

  -v, --verbose
          Print verbose request info (host, elapsed) to stderr, prefixed with `*` like curl -v

      --lang <LANG>
          Language for content fetched from longbridge.com: zh-CN or en. Defaults to system LANG env var, then en

  -h, --help
          Print help (see a summary with '-h')
```

## Usage

```bash
# Run with JSON output for AI agents
longbridge portfolio --format json

# See all options
longbridge portfolio --help
```
