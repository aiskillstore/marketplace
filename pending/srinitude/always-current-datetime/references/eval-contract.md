# Evaluation contract

Owner and backlink: [`../SKILL.md`](../SKILL.md) through its progressive-disclosure section.

Load this file and [`../evals/cases.json`](../evals/cases.json) before testing or changing the skill.

## Clock schema

A successful clock call returns one JSON object with these fields:

- `captured_at`: ISO 8601 local timestamp with UTC offset
- `date`: ISO local date
- `time`: local time to seconds
- `weekday`: English weekday name
- `timezone`: configured IANA name or `system-local`
- `zone_abbreviation`: active local abbreviation
- `utc_offset`: signed `HH:MM`
- `source`: `argument`, `profile-environment`, or `system-local`
- `yesterday`: ISO date
- `tomorrow`: ISO date

Unknown or invalid configured timezones fail with a nonzero exit and an error on standard error. An empty profile timezone setting uses system-local time.

## Native behavior acceptance

Require all of these:

1. The script parses and stays within the code-shape limits.
2. A UTC run returns a valid internally consistent schema.
3. An invalid IANA timezone exits nonzero without a success object.
4. System-local fallback returns a valid offset and local date.
5. `SKILL.md` passes the repository skill loader and exposes every linked file.
6. All supported client manifests discover the canonical skill and load the runtime contract.
7. The trigger description stays concise and the Markdown limits pass.
8. A host that requires relevant-skill loading can discover this skill before a direct user reply.
9. `--timezone` overrides `PROFILE_TIMEZONE`, which overrides system-local time.
10. The clock command is relative to the supplied skill working directory and contains no unresolved skill-directory variable.
11. The visible per-turn prefix contains the acquired date, time to seconds, and zone abbreviation.

## Behavioral acceptance

Each case in `../evals/cases.json` declares required and forbidden behavior. Every case must pass. One missed clock call, stale anchor, duplicate call, prompt rewrite, wrong absolute date or time, missing stored date-time prefix, or fail-open fallback blocks behavioral parity.

Keep native, activation, behavior, enrollment, and whole-package statuses separate. A queued model evaluation is not a behavior PASS.

## Prior-contract comparison

Compare the same cases against the prior date-only contract. The skill may claim parity only when neither path misses a retained case. It may claim a benefit only for an observed axis such as a persisted acquisition time, fail-closed clock errors, or `starting-point` binding.
