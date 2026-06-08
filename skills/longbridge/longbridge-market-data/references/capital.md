# longbridge-capital-flow

Today's capital flow time-series and order-size distribution for a single security.

## Subcommands

> A single `capital` command handles both modes — distribution snapshot (default) and time-series (`--flow`). Run `longbridge capital --help` to confirm.

| CLI command                                        | Returns                                                                                |
| -------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `longbridge capital <SYMBOL> --format json`        | Cross-section snapshot: large / medium / small / super-large order buy & sell amounts. |
| `longbridge capital <SYMBOL> --flow --format json` | Today's main-capital net inflow / outflow time series.                                 |

**Single symbol per call.** Today's data only — no historical range.

## Workflow

1. Resolve a single symbol to `<CODE>.<MARKET>`.
2. Decide which mode: distribution snapshot (default), time-series (`--flow`), or both.
3. Call the Longbridge CLI directly (preferred) or fall back to MCP.
4. Summarise: net inflow direction (▲ / ▼), accumulated total, distribution skew. Cite Longbridge Securities.

## CLI

```bash
longbridge capital NVDA.US                  --format json     # snapshot
longbridge capital TSLA.US --flow           --format json     # time series
# Combined view → call both and merge in the LLM
```

## Output

The default snapshot returns a cross-section object; `--flow` returns a time-series array.

Field translations (LLM should map):

| Field (likely)           | 简体            | 繁體            | English                  |
| ------------------------ | --------------- | --------------- | ------------------------ |
| `large_in / large_out`   | 大单流入/流出   | 大單流入/流出   | Large order in/out       |
| `medium_in / medium_out` | 中单流入/流出   | 中單流入/流出   | Medium order in/out      |
| `small_in / small_out`   | 小单流入/流出   | 小單流入/流出   | Small order in/out       |
| `super_in / super_out`   | 超大单流入/流出 | 超大單流入/流出 | Super-large order in/out |

(Field names follow Longbridge JSON; LLM maps to the user's language.)

## Error handling

If `longbridge` is missing, fall back to MCP. Other stderr messages get relayed verbatim (auth issues → `longbridge auth login`; invalid symbol → re-check format).
