# filing

```
Regulatory filings for a symbol, or list/fetch filing content

Without subcommand: lists filings for a symbol. Subcommands: list  detail Example: longbridge filing AAPL.US Example: longbridge filing list AAPL.US Example: longbridge filing detail AAPL.US 580265529766123777

Usage: longbridge filing [OPTIONS] [SYMBOL] [COMMAND]

Commands:
  detail  Full Markdown content of a regulatory filing (HTML and TXT only)
  help    Print this message or the help of the given subcommand(s)

Arguments:
  [SYMBOL]
          Symbol in <CODE>.<MARKET> format (e.g. AAPL.US 700.HK). Omit when using a subcommand

Options:
      --count <COUNT>
          Maximum number of filings to show (default: 20)
          
          [default: 20]

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
longbridge filing --format json

# See all options
longbridge filing --help
```
