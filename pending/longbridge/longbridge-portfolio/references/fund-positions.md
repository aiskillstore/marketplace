# fund-positions

```
Current fund (mutual fund) positions across all sub-accounts

Returns: symbol, name, `current_net_asset_value`, `cost_net_asset_value`, currency, `holding_units`.

Usage: longbridge fund-positions [OPTIONS]

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
longbridge fund-positions --format json

# See all options
longbridge fund-positions --help
```
