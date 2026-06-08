# longbridge-security-list

Catalog lookups: US overnight-eligible securities, and the HK broker_id → name dictionary.

## Subcommands

> Run `longbridge <subcommand> --help` to confirm the current flag spelling and defaults.

| CLI command                              | Returns                                                          |
| ---------------------------------------- | ---------------------------------------------------------------- |
| `longbridge security-list --format json` | US overnight-eligible securities `[{symbol, name_en, name_cn}]`. |
| `longbridge participants --format json`  | HK broker directory `[{broker_id, name_en, name_cn}]`.           |

> ⚠️ **Scope**: `security-list` only exposes the US Overnight category (full HK / A-share / SG catalogs are not available through this endpoint). The CLI returns `Error: Only US market is supported for security-list ...` if you pass `HK / CN / SG`. For non-US listed lookups, route the user to `longbridge-quote` for per-symbol queries.

## Usage rules

- For "how many" questions, reply with the array length; do **not** dump the full payload.
- For broker_id translation, find the matching row instead of dumping the whole directory.
- For "list all stocks" requests in non-US markets, ask the user to narrow scope (industry, name search) and route them to `longbridge-quote`.

## CLI

```bash
longbridge security-list      --format json
longbridge participants       --format json
```

## Output

- `security-list`: array of `{symbol, name_en, name_cn}` for US overnight-eligible names.
- `participants`: array of `{broker_id, name_en, name_cn}` for HK brokers.

## Error handling

If `longbridge` is missing, fall back to MCP. If stderr says _"Only US market is supported for security-list"_ on a non-US market query, explain the scope limit to the user and offer per-symbol lookup via `longbridge-quote`. Other stderr messages relay verbatim.
