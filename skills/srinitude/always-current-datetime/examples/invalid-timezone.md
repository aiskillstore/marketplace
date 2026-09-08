# Invalid timezone

## Intent

Prove that an invalid configured timezone fails closed instead of producing a guessed date or time.

## Command

Run with the skill directory as the process working directory.

```bash
python3 scripts/current_anchor.py --timezone Not/A_Zone
```

## Real result

Exit code: `2`.

Stdout bytes: `0`.

Stderr:

```text
current_anchor_error: ZoneInfoNotFoundError: 'No time zone found with key Not/A_Zone'
```

## User-facing response

```text
temporal-anchor-unavailable: ZoneInfoNotFoundError: No time zone found with key Not/A_Zone. Retry after supplying a valid IANA timezone or restoring the local clock source.
```

Created files: none.

Verification: no success object or date-time prefix was emitted, and date-dependent or time-dependent work remained blocked.

## Recovery

Run the same direct-turn flow with a valid `--timezone` value, a valid `PROFILE_TIMEZONE`, or no configured value to use system-local time. A successful retry must acquire a new anchor rather than reuse this failed turn.
