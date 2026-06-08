# topic

```
Community discussion topics

Without subcommand: lists topics for a symbol. Subcommands: list  detail  mine  create  replies  create-reply  search Example: longbridge topic TSLA.US Example: longbridge topic list TSLA.US Example: longbridge topic detail 6993508780031016960 Example: longbridge topic create --body "Bullish on TSLA today" Example: longbridge topic search TSLA

Usage: longbridge topic [OPTIONS] [SYMBOL] [COMMAND]

Commands:
  detail        Get full details of a community topic by its ID
  mine          Topics created by the authenticated user
  create        Publish a new community discussion topic
  replies       List replies for a community topic (paginated)
  create-reply  Post a reply to a community topic
  search        Search community topics by keyword
  help          Print this message or the help of the given subcommand(s)

Arguments:
  [SYMBOL]
          Symbol in <CODE>.<MARKET> format (e.g. TSLA.US 700.HK). Omit when using a subcommand

Options:
      --count <COUNT>
          Maximum number of topics to show (default: 20)
          
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
longbridge topic --format json

# See all options
longbridge topic --help
```
