# max-qty

```
Estimate maximum buy or sell quantity given current account balance

Returns: `cash_max_qty` (cash only), `margin_max_qty` (with margin financing). Example: longbridge max-qty TSLA.US --side buy --price 250

Usage: longbridge max-qty [OPTIONS] --side <SIDE> <SYMBOL>

Arguments:
  <SYMBOL>
          Symbol in <CODE>.<MARKET> format

Options:
      --side <SIDE>
          Order side: buy | sell  (case-insensitive, REQUIRED)

      --price <PRICE>
          Limit price as a decimal string, e.g. 250.00 (required for LO orders)

      --order-type <ORDER_TYPE>
          Order type: LO | MO | ELO | ALO  (case-insensitive, default: LO)
          
          [default: LO]

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
longbridge max-qty --format json

# See all options
longbridge max-qty --help
```
