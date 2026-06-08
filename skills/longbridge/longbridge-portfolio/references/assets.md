# assets

```
Account asset overview — net assets, cash, buy power, margins, and per-currency breakdown

Returns: currency, `net_assets`, `total_cash`, `buy_power`, `max_finance_amount`, `remaining_finance_amount`, `init_margin`, `maintenance_margin`, `margin_call`, `risk_level`, and a `cash_infos` array with per-currency available/frozen/settling/withdrawable amounts. Example: longbridge assets Example: longbridge assets --currency HKD

Usage: longbridge assets [OPTIONS]

Options:
      --currency <CURRENCY>
          Filter by currency (e.g. USD HKD CNY SGD)
          
          [default: USD]

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
longbridge assets --format json

# See all options
longbridge assets --help
```
