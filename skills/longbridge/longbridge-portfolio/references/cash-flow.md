# cash-flow

```
Cash flow records (deposits, withdrawals, dividends, settlements)

Returns: `flow_name`, symbol, `business_type`, balance, currency, `business_time`, description. Defaults to last 30 days if no dates provided. Example: longbridge cash-flow --start 2024-01-01 --end 2024-03-31

Usage: longbridge cash-flow [OPTIONS]

Options:
      --start <START>
          Start date (YYYY-MM-DD), defaults to 30 days ago

      --end <END>
          End date (YYYY-MM-DD), defaults to today

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
longbridge cash-flow --format json

# See all options
longbridge cash-flow --help
```
