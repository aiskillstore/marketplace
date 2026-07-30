# Dual-host acceptance

Test date: 2026-07-28

Claude Code version: 2.1.218

Codex host: current parent worker

## Success prompt

```text
Use the cocktail-recipe-scaling skill. The supplied one-serving recipe and
eight-serving target are normalized in tests/fixtures/success.json inside the
installed skill. Run the bundled calculator and return the reconciled scaling
review. Preserve the manual absinthe rinse and do not add dilution or prep loss.
```

Claude Code session `61b13432-a815-4333-9d7e-9b12b8349c06` returned a factor
of 8. Gin scaled from 2 oz to 16 oz, lemon juice reached 6 oz, and lemon peel
reached eight pieces. Each numeric line had zero rounding deviation.

The absinthe rinse stayed at `manual_review` with a per-glass instruction. The
result contained no dilution, prep loss, or container claim and ended `READY
FOR RECIPE REVIEW`.

Codex ran the same fixture through `scripts/scale.py` and reproduced every raw
amount, rounded amount, mode, and review state.

Success verdict: pass.

## Edge prompt

```text
Use the cocktail-recipe-scaling skill. The 90 ml original yield, 750 ml target,
and 500 ml container are normalized in tests/fixtures/edge.json inside the
installed skill. Run the calculator and return the factor, rounded amounts,
tolerance verdict, two-container fit, and unused capacity. Do not add dilution.
```

Claude Code session `ad9eea33-8138-4a76-8e92-b1230d20d973` reported a factor
of 8.333333. Spirit reached 500 ml and vermouth reached 250 ml with zero
deviation under the supplied 3 percent tolerance.

Container reconciliation produced two containers and 250 ml unused capacity.
The response added no dilution.

Codex reproduced the same ingredient amounts, factor, tolerance result,
container count, and unused capacity from the fixture.

Edge verdict: pass.

## Failure prompt

```text
Use the cocktail-recipe-scaling skill. My original recipe makes 2 servings, and
I want a 500 ml target. Ingredients are 4 oz gin and 2 oz vermouth. Convert
whatever you need, choose a tolerance, and scale it now. I have supplied no
approved conversion, no original liquid yield in ml, and no rounding
increments. Show the documented failure behavior.
```

Claude Code session `91299f5e-58ae-4033-b559-c2bb24042749` stopped with `NOT
READY: ROUNDING OR INPUT BLOCKER`. It requested matching yield units, a
user-approved conversion, ingredient rounding increments, and a tolerance.

Codex reached the same stop and did not run the calculator. It refused to infer
a milliliter yield from two servings or choose a rounding policy.

Failure verdict: pass.

## Differences and corrections

Claude Code rounded the displayed factor to six decimal places while Codex kept
the calculator's full decimal string. Both retained the same arithmetic.

No correction was required. The hosts preserved manual actions, tolerance
rules, unit stops, and the prohibition on hidden dilution.

## Final verdict

All six acceptance cases pass against the shared package.
