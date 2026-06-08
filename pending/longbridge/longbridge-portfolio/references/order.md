# order

```
Order management: list, detail, buy, sell, cancel, replace, executions

Without a subcommand, lists today's orders (or historical with --history). Example: longbridge order Example: longbridge order --history --start 2024-01-01 --symbol TSLA.US Example: longbridge order detail 20240101-123456789 Example: longbridge order buy TSLA.US 100 --price 250.00 Example: longbridge order sell TSLA.US 100 --price 260.00 Example: longbridge order cancel 20240101-123456789 Example: longbridge order replace 20240101-123456789 --qty 200 --price 255.00 Example: longbridge order executions --history --start 2024-01-01

Usage: longbridge order [OPTIONS] [COMMAND]

Commands:
  detail      Full detail for a single order including charges and history
  executions  Today's trade executions (fills), or historical with --history
  buy         Submit a buy order (prompts for confirmation)
  sell        Submit a sell order (prompts for confirmation)
  cancel      Cancel a pending order (prompts for confirmation)
  replace     Modify quantity or price of a pending order (prompts for confirmation)
  help        Print this message or the help of the given subcommand(s)

Options:
      --history
          Return historical orders instead of today's (list mode only)

      --start <START>
          Filter start date (YYYY-MM-DD)

      --end <END>
          Filter end date (YYYY-MM-DD)

      --symbol <SYMBOL>
          Filter by symbol (e.g. TSLA.US)

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
longbridge order --format json

# See all options
longbridge order --help
```

> ⚠️ **Mutating command** — `order buy`, `order sell`, `order cancel`, `order replace` modify account state. Always present a preview to the user and wait for explicit confirmation before executing.
