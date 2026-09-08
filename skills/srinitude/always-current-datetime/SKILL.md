---
name: always-current-datetime
description: 'Use when replying. Refresh current date and time.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Always current date and time

Use one fresh local clock anchor for every direct user turn. Apply it through `starting-point`, resolve relative dates and times without changing the user's words, and persist the current acquisition time in the visible reply.

## Which commands does this skill accept?

Treat an ordinary direct user message as `refresh`. These control words exist for inspection and testing.

| Command   | Result                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------- |
| `help`    | Show the trigger, clock fields, timezone order, visible prefixes, failure rule, and anchor state.       |
| `refresh` | Acquire one fresh anchor for the current direct turn, bind it to `starting-point`, and apply the reply. |

If a request matches neither command, use `refresh`. Do not ask the user to choose a command.

## When does it run?

Run before every reply to a direct user message, even when the message has no date or time words. A tool result, system event, or assistant continuation does not start a new clock acquisition. An exact mid-turn out-of-band user-message marker does.

## What is the per-turn contract?

Before interpreting or acting on the newest direct user message:

1. Load `starting-point` through the host's skill-loading capability.
2. Read this skill's concrete absolute directory from the host's load result.
3. Set that directory as the process runner's working directory and run the bundled script exactly once.
4. Parse the JSON and require every field in `references/eval-contract.md`.
5. Add the anchor to the private `starting-point` map as `as_of`.
6. Resolve temporal language before any date-sensitive or time-sensitive tool call.
7. Write the visible date-time prefix in the actual assistant response so session history stores it.

Run on macOS or Linux with that working directory:

```bash
python3 scripts/current_anchor.py
```

Run on Windows with that working directory:

```powershell
python scripts/current_anchor.py
```

Use `python` or `py -3` only when it is the installed interpreter. Do not use a skill-directory shell variable or guess an installation path. If the load result does not supply a concrete skill directory, report `temporal-anchor-unavailable: skill directory missing` and stop date-dependent or time-dependent work. Never pass a fabricated timestamp. Reuse an anchor only when its process result occurs after the newest direct user message.

The portable script accepts `--timezone <IANA-zone>`, then checks `PROFILE_TIMEZONE`, then uses system-local time. An explicit argument represents a profile configuration supplied by the host and wins over the environment.

If the command fails, returns invalid JSON, or omits a required field, stop date-dependent or time-dependent work and report `temporal-anchor-unavailable:` followed by the short error. Do not guess, reuse an earlier date or time, or fall back to the conversation-start timestamp.

## How is the anchor bound to starting-point?

Add this private structure without exposing the full outcome map:

```text
as_of: captured_at, date, time, weekday, timezone, zone_abbreviation, utc_offset, source
```

Apply it to:

- **Outcome:** Turn relative completion language into an exact date or date-time.
- **Proof:** Separate current observations from evidence gathered earlier.
- **Constraints:** Resolve deadlines, validity windows, and temporal bounds.
- **Starting path:** Distinguish actions available now from later actions.
- **Unknowns:** Keep ambiguous expressions unresolved until one concise question answers them.

## How is temporal language interpreted?

- Preserve the user's original words and authorship.
- Expose the resolved absolute date or date-time when a relative expression affects meaning or action.
- Keep past statements historical and future requests prospective.
- Convert date-sensitive and time-sensitive tool arguments to absolute values and include the timezone when the tool supports it.
- Treat `next Friday` and similar phrases as ambiguous when common conventions yield different dates. Show the candidate dates and ask one concise question.
- Do not ask when the conversation already establishes the convention.
- Reacquire after local midnight. Never infer rollover from elapsed conversation time.

## What is visible in the reply?

On the first assistant reply for a local date, and again when the local date changes, begin with:

```text
NOW: <weekday>, <full date> at <HH:MM:SS> | <zone abbreviation> | UTC<offset>
```

Begin every normal user-facing reply on that date with:

```text
[YYYY-MM-DD HH:MM:SS <zone abbreviation>] <result or question>
```

Inspect retained assistant messages to decide whether the daily header already appeared. When context compaction makes that uncertain, prefer a repeated current header over a missing or stale header. Prefix an interactive clarification question inside its question text. Do not prefix tool calls or internal notes.

The literal templates also live in `assets/response-prefixes.txt`. When clock acquisition fails, use the failure marker instead of a dated prefix.

## How does resume work?

After resume or context compaction, reacquire the clock before using any retained date or time. If this skill body is unavailable from retained context, reload it before acting. Stored date-time prefixes prove prior turns only.

## Which worked example should you read?

- Read `examples/help-command.md` for a complete `help` response.
- Read `examples/fresh-direct-turn.md` for one real UTC diagnostic, `as_of` binding, and both visible prefixes.
- Read `examples/invalid-timezone.md` for exit `2`, empty stdout, the failure marker, and recovery.

## Progressive disclosure

Read `references/eval-contract.md` and `evals/cases.json` before testing or changing this skill. Read `references/generation-contract.md` when changing the package structure or checking native-to-port lineage. Load `scripts/tests/` before changing script behavior and run those tests before implementation changes. Load the rest of `evals/` only when measuring activation, behavior, enrollment, or timing. Do not load these files on ordinary turns.

## Gotchas

- Do not skip the clock because the direct message has no date or time words.
- Do not treat tool output, a system event, or assistant continuation as a new direct user message.
- Do not call the clock after final reasoning or call it twice in one direct turn.
- Do not rewrite the user's temporal words after resolving them.
- Do not present older evidence as current proof.
- Do not silently choose one meaning for an ambiguous weekday phrase.
- Do not prefix tool calls or internal notes.
- Do not silently fall back after an invalid configured timezone.
- Do not put an unresolved skill-directory variable in the clock command.
- Do not claim prior-contract parity when either route misses a case.

## Limitations

The script cannot infer the user's intended timezone from prose. The host must supply an explicit IANA timezone through `--timezone` or `PROFILE_TIMEZONE` when system-local time is not the intended context. The skill can resolve dates and times and prepare absolute tool arguments, but a separate capability owns any real reminder, calendar, or deployment action.

## When is the turn ready?

The turn is ready only when the skill was loaded, one fresh clock call produced every required field after the newest direct message, `as_of` is bound to the private `starting-point` map, temporal language is resolved before date-sensitive or time-sensitive actions, and the actual user-facing response contains the required current date-time prefix. Any stale, missing, duplicate, or failed anchor leaves temporal work blocked.
