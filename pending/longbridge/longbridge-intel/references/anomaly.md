# anomaly

```
Quote anomalies / unusual market movements

Example: longbridge anomaly --market HK Example: longbridge anomaly --market US --symbol TSLA.US

Usage: longbridge anomaly [OPTIONS]

Options:
      --market <MARKET>
          Market: HK | US | CN | SG
          
          [default: HK]

      --symbol <SYMBOL>
          Filter to a specific symbol

      --count <COUNT>
          Number of results (max 100)
          
          [default: 50]

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
longbridge anomaly --format json

# See all options
longbridge anomaly --help
```
