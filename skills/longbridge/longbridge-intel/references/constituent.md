# constituent

```
Index or ETF constituent stocks

For an index, lists its member stocks. US index symbols require a leading dot (e.g. .DJI.US, .SPX.US, .IXIC.US); HK indexes use the plain code (e.g. HSI.HK). For a US ETF, fetches full holdings from SEC EDGAR (N-PORT) by default, falling back to the platform asset-allocation summary when SEC data is unavailable (e.g. UIT funds like SPY, or very new tickers). For non-US ETFs the platform asset-allocation breakdown is used. --sort/--order are ignored for ETFs since the data is already weight-ranked.

Example: longbridge constituent HSI.HK Example: longbridge constituent .SPX.US --sort market-cap --order asc Example: longbridge constituent HSI.HK --limit 20 --sort change Example: longbridge constituent IVV.US --limit 0   (full SEC holdings)

Usage: longbridge constituent [OPTIONS] <SYMBOL>

Arguments:
  <SYMBOL>
          Index or ETF symbol in <CODE>.<MARKET> format (e.g. HSI.HK, .SPX.US, IVV.US)

Options:
      --limit <LIMIT>
          Number of results to return (0 = all, for ETF SEC holdings)
          
          [default: 50]

      --sort <SORT>
          Sort indicator
          
          [default: change]
          [possible values: change, price, turnover, inflow, turnover-rate, market-cap]

      --order <ORDER>
          Sort order
          
          [default: desc]
          [possible values: desc, asc]

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
longbridge constituent --format json

# See all options
longbridge constituent --help
```
