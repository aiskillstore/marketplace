# Dual-host acceptance

Test date: 2026-07-27

Claude Code version: 2.1.218

Codex host: current parent worker

Both hosts used the same `SKILL.md`, input contract, calculator, and fixtures.

## Success prompt

```text
Use the party-drink-planner skill. The approved scenario is already normalized
in tests/fixtures/success.json inside the installed skill. Run the bundled
calculator against that fixture and return the reconciled review package. Treat
the values and source in the fixture as host-approved. Do not create a purchase,
change a file, or send anything.
```

### Claude Code output

Session `70185581-efbf-4967-bda9-dd809f2c9e76` ran the calculator and returned
80 planned alcoholic servings.

| Beverage | Servings | Packages | Owned | Gap |
|---|---:|---:|---:|---:|
| Beer | 28 | 28 units | 12 | 16 units |
| Wine | 20 | 4 bottles | 2 | 2 bottles |
| Cocktails | 32 | 2 spirit bottles | 1 | 1 bottle |

The Daiquiri branch reported 64 oz rum, 32 oz lime juice, and 24 oz simple
syrup. Rum inventory produced a 52 oz gap. Lime and syrup stayed unknown
because inventory was absent.

The non-alcoholic result contained 72 servings, 28.8 liters of water, and 36 lb
of ice. All servings reconciled to 80, and the output kept the supply-estimate
boundary plus human review state.

### Codex output

Codex ran `scripts/calculate.py tests/fixtures/success.json` and reproduced the
same servings, package counts, ingredient totals, unknown inventory states, and
non-alcoholic quantities.

Codex also confirmed that the recorded source was `host-approved base scenario`
with review date `2026-07-27`. It performed no purchase or external action.

Success verdict: pass.

## Edge prompt

```text
Use the party-drink-planner skill. The approved zero-drinker GB scenario is
normalized in tests/fixtures/edge.json inside the installed skill. Run the
bundled calculator against that fixture. Present the review package, preserve
the alcohol-free edge branch, and do not recommend alcohol, change a file, or
send anything.
```

### Claude Code output

Session `c8ead7f3-8d29-4a69-b394-a4b1a85fdc99` reported zero alcoholic
servings, zero alcoholic package quantities, and zero shopping gaps.

The alcohol-free branch contained 36 servings, 14.4 liters of water, and 8.2 kg
of ice. Beverage shares remained in the audit record but had no effect because
the approved alcoholic-serving assumption was zero.

### Codex output

Codex ran `scripts/calculate.py tests/fixtures/edge.json` and reproduced every
zero-alcohol quantity. It preserved the host-approved source, GB jurisdiction,
kilogram ice unit, and supply-estimate boundary.

Edge verdict: pass.

## Failure prompt

```text
Use the party-drink-planner skill to estimate quantities for 30 guests over five
hours. Six guests will not drink alcohol. I have not chosen beverage shares,
serving assumptions, water, ice, package yields, or a source for those
assumptions. Do not use defaults. Show the documented stop state and only the
information needed to continue.
```

### Claude Code output

Session `726b1b55-0295-4e9b-92e2-d26e672303e5` stopped before calculation. It
derived 24 drinking guests from the supplied counts, then requested the missing
country, beverage shares, approved alcoholic-serving assumption, non-alcoholic
quantity, water, ice, package yields, source, and review date.

No default, calculator run, or purchase output appeared.

### Codex output

Codex reached the same missing-input stop. It did not infer rates from event
duration and did not substitute the old one-plus-hours formula.

Failure verdict: pass.

## Host differences and corrections

The first Claude Code edge attempt, session
`02e63cc8-b251-4e9f-986c-e2b34db527b1`, reproduced the correct values but did
not execute the calculator because the temporary host denied file creation. The
fixture-based rerun removed that permission dependency and passed.

Claude Code used a rendered planning narrative. Codex retained more of the raw
JSON field names. Arithmetic, branches, boundaries, and stop behavior matched.

No correction changed the shared procedure.

## Final verdict

All six required host cases pass. Both hosts follow the shared process, reach
the correct branch, preserve supplied constraints, and stop when assumptions
are absent.
