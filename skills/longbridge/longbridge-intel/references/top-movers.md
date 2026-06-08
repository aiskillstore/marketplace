# top-movers

```
Top stocks with abnormal price movements and correlated news

When a stock's price fluctuation exceeds its standard deviation over the past ~20 trading days, it is flagged as an abnormal change. The system then correlates related news to provide an interpretation of the move.

Different from `anomaly` (pure technical signals): `top-movers` pairs each alert with a reason summary, pinned news article, and industry tags.

Sort: hot (default) | time | change

Example: longbridge top-movers Example: longbridge top-movers --market HK Example: longbridge top-movers --market US --sort time --count 50

Usage: longbridge top-movers [OPTIONS]

Options:
      --market <MARKET>
          Market filter: HK | US | CN | SG (omit for all markets)

      --sort <SORT>
          Sort order: hot (default) | time | change
          
          [default: hot]
          [possible values: hot, time, change]

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
longbridge top-movers --format json

# See all options
longbridge top-movers --help
```
