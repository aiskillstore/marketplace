# Numerals, dates and claims

## Editorial rules

- **UE-NU001** *(warning)* — Dates in running prose use day–month–year, for example `9 November 2026`. A numeric `d/m/y` or `m/d/y` date in prose is reported, and so is the written month-first form (`March 5, 2026`), which the day-month-year order replaces. Full month names only: an abbreviated month is out of scope, a month-year reference (`March 2026`) and the correct day-month-year order never match. Dates in source code, data formats, URLs, `datetime` attributes and immutable references are masked first; the pattern stays intentionally conservative rather than guessing an intended locale, and dates are never rewritten by `--fix`.
- **UE-NU002** *(warning, fixable)* — Numeric ranges join with an en dash: `1990–2025`, not `1990-2025`.

## Agent review required

These three are reported as warnings in the `AGENT REVIEW REQUIRED` section. They are prompts for a reviewer, not verdicts, and never reach error severity.

- **UE-RE003** — A prose figure needs a hedge such as “approximately”, “at least” or “an estimated”, and should identify source and date.
- **UE-DI001** — A count must say what was counted and whether it is reported, estimated or total. The qualifying word must appear in the count's own sentence; a qualifier in the next sentence does not cover it. The counted-noun list is bounded — countries, refugees, children, cases, deaths, households and their peers — and a count of an unlisted noun is not reported.
- **UE-CL001** — A comparison may be aligning different reference periods. Check that the compared values share a reference year, and say “reported on or before” when values are carried forward.
- **UE-CL002**, **UE-CL003** *(with `--claims`)* — The claim register's own completeness rules: an entry with no recorded source or reference date, and a detected claim that is not recorded in the register. The check verifies that the bookkeeping happened, never that the claim is true (see the README's claim-evidence register section).

The checker does not calculate ratios, validate years against source rows, or prove that prose matches rendered data. Ordinal ranks are not counts; verify off-by-one boundaries yourself.
