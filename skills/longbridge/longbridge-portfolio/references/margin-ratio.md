# margin-ratio

```
Margin ratio requirements for a symbol

Returns: `im_factor` (initial), `mm_factor` (maintenance), `fm_factor` (forced liquidation). Example: longbridge margin-ratio TSLA.US

Usage: longbridge margin-ratio [OPTIONS] <SYMBOL>

Arguments:
  <SYMBOL>
          Symbol in <CODE>.<MARKET> format

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
longbridge margin-ratio --format json

# See all options
longbridge margin-ratio --help
```
