# quant

Quantitative analysis: run indicator scripts against K-line data

Subcommands: run Example: longbridge quant run TSLA.US --start 2024-01-01 --end 2024-12-31 --script "..." Example: cat script.pine | longbridge quant run TSLA.US --start 2024-01-01 --end 2024-12-31

Usage: longbridge quant [OPTIONS] <COMMAND>

Commands:
  run   Run a quant indicator script against historical K-line data on the server
  help  Print this message or the help of the given subcommand(s)

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

---

## `quant run` — run an indicator script

```
Run a quant indicator script against historical K-line data on the server

Executes the script server-side and returns the computed indicator/plot values as JSON. The script language is compatible with `PineScript` V6 syntax (minor exceptions may apply).

Periods: 1m  5m  15m  30m  1h  day  week  month  year

Script source (--script takes priority over stdin): --script TEXT   inline script text stdin           cat script.pine | longbridge quant run TSLA.US ...

The optional --input flag accepts a JSON array matching the order of input.*() calls in the script, e.g. --input '[14,2.0]'

Example: longbridge quant run TSLA.US --start 2024-01-01 --end 2024-12-31 --script "..." Example: cat script.pine | longbridge quant run TSLA.US --start 2024-01-01 --end 2024-12-31 Example: longbridge quant run 700.HK --period 1h --start 2024-01-01 --end 2024-06-30 --script "..." --input '[14]' Example: longbridge quant run TSLA.US --start 2024-01-01 --end 2024-12-31 --script "..." --format json Example: longbridge quant run 700.HK --period 1m --start "2024-01-02 09:30" --end "2024-01-02 16:00" --script "..."

Usage: longbridge quant run [OPTIONS] --start <START> --end <END> <SYMBOL>

Arguments:
  <SYMBOL>
          Symbol in <CODE>.<MARKET> format, e.g. TSLA.US 700.HK

Options:
      --period <PERIOD>
          K-line period: 1m 5m 15m 30m 1h day week month year (default: day)
          
          [default: day]

      --start <START>
          Start date/datetime for the K-line range (YYYY-MM-DD or "YYYY-MM-DD HH:MM")

      --end <END>
          End date/datetime for the K-line range (YYYY-MM-DD or "YYYY-MM-DD HH:MM")

      --script <SCRIPT>
          Script text. Omit to read from stdin (e.g. echo "..." | longbridge quant run ...)

      --input <INPUT>
          Script input values as a JSON array, e.g. '[14,2.0]' Must match the order of input.*() calls in the script

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

## Usage patterns

```bash
# Run an inline script against a symbol
longbridge quant run TSLA.US --start 2024-01-01 --end 2024-12-31 --script "..."

# Pipe a script file
cat my_strategy.pine | longbridge quant run NVDA.US --start 2024-01-01 --end 2024-12-31

# Always add --format json for AI agent processing
longbridge quant run TSLA.US --start 2024-01-01 --end 2024-12-31 --script "..." --format json
```

## Notes

- Script language: Pine Script-compatible indicator syntax
- Run `longbridge quant run --help` for all current flags and script syntax
- Use `longbridge kline` to preview the underlying OHLCV data first
