# rank

```
LB popularity ranking lists (热度排行榜)

Returns stocks ranked by a composite heat score combining trading activity, media coverage, community discussion, and price volatility.

Run `rank` without --key to list all available tab keys (e.g. `ib_hot_all-us`). Then pass a key to `--key` to get the corresponding ranking.

Example: longbridge rank Example: longbridge rank --key ib_hot_all-us Example: longbridge rank --key ib_trade_heat-hk --count 20

Usage: longbridge rank [OPTIONS]

Options:
      --key <KEY>
          Ranking tab key (from `rank` with no --key). Omit to list available keys

      --market <MARKET>
          Market filter applied when listing (default: US)
          
          [default: US]

      --count <COUNT>
          Number of results (default: 20)
          
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
longbridge rank --format json

# See all options
longbridge rank --help
```
