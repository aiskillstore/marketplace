# screener

```
Strategy screener — browse strategies, run filters, view indicator config

Workflow A — run a saved strategy: 1. `screener strategies` to list preset strategies and note the ID 2. `screener run <ID>` to execute it

Workflow B — custom filter: 1. `screener indicators` to discover available keys and value ranges 2. `screener filter KEY:MIN:MAX ... --market HK`

Example: longbridge screener strategies Example: longbridge screener run 42 Example: longbridge screener filter pettm:10:50 roe:5: --market HK Example: longbridge screener indicators

Usage: longbridge screener [OPTIONS] <COMMAND>

Commands:
  strategies  List stock-selection strategies and their filter conditions
  run         Run a saved strategy by its ID (from `screener strategies` output)
  filter      Filter stocks with custom indicator conditions
  indicators  List all available filter indicators with keys and value ranges
  help        Print this message or the help of the given subcommand(s)

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
longbridge screener --format json

# See all options
longbridge screener --help
```
