# statement

```
Download and export account statements (daily/monthly)

Without a subcommand, lists available statements (equivalent to `statement list`). Example: longbridge statement Example: longbridge statement --type monthly Example: longbridge statement export --file-key KEY --section `equity_holdings`

Usage: longbridge statement [OPTIONS] [COMMAND]

Commands:
  list    List available statements for an account
  export  Export statement sections as CSV files or markdown
  help    Print this message or the help of the given subcommand(s)

Options:
      --type <STATEMENT_TYPE>
          Statement type: daily (default) | monthly
          
          [default: daily]

      --start-date <START_DATE>
          Start date (YYYY-MM-DD, e.g. 2026-01-21). Defaults to 30 days ago

      --limit <LIMIT>
          Number of records to return. Defaults to 30 for daily, 12 for monthly

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
longbridge statement --format json

# See all options
longbridge statement --help
```
