# Contributing

Dittobot improves when real writing failures become small, repeatable tests.

## Where Changes Belong

- Put broad editing behavior in `SKILL.md` only when it should affect many tasks.
- Put concrete failure cases in `scripts/regression_100.py`.
- Put public philosophy and examples in `README.md`; put install, validation, lab-tooling, and release runbooks in the GitHub wiki.
- Put validation, install, and live-model tooling in `scripts/`.

If a change makes normal skill use more verbose without making Dittobot more reliable, it probably belongs in the harness instead of `SKILL.md`.

## Reporting Bad Rewrites

Use the "Bad rewrite" issue template when Dittobot:

- changes meaning;
- invents a fact, number, claim, citation, or customer;
- flattens the user's voice;
- misses the throughline in messy notes;
- asks an unnecessary clarifying question;
- adds wrappers, notes, or rationale when the rewrite should stand alone;
- violates a hard constraint such as word count or no dashes.

Redact private drafts, customer data, secrets, and anything that should not be public.

## Adding Regression Cases

Good regression cases include:

- source text with the bad pattern;
- expected rewritten behavior;
- protected facts and constraints;
- voice markers worth preserving;
- forbidden generic phrases, invented details, wrappers, or drift markers;
- a short reason the case belongs.

Prefer one sharp case over ten vague cases.

Use the lab scripts when a failure is hard to reason about:

```bash
python3 scripts/voice_probe.py samples/*.local.md
python3 scripts/audit.py --source-file source.txt --rewrite-file rewrite.txt --ledger-file profile.local.json
python3 scripts/case_lab.py --case-id new_case_01 --source-file source.txt --rewrite-file desired.txt --ledger-file profile.local.json
```

`voice_probe.py` extracts observable style signals from local samples. `audit.py` tells you which guardrails catch the bad output. `case_lab.py` prints a `Case(...)` skeleton you can review, redact, and paste into the harness.

## Validation

Before opening a pull request, run:

```bash
python3 scripts/validate_skill.py
python3 scripts/regression_100.py
python3 scripts/audit.py --source "I think notice may be due in 10 days." --rewrite "I think notice may be due in 10 days." --preserve-uncertainty --protected "10 days"
python3 scripts/case_lab.py --case-id sample_case_01 --source "rough but redacted source" --rewrite "clean but still redacted rewrite" --must "redacted"
python3 scripts/voice_probe.py --sample "This draft is not bad. It just apologizes for existing."
python3 -m py_compile scripts/*.py
```

For live smoke testing with an API key, keep cost bounded:

```bash
python3 scripts/live_eval.py --list-cases --prompt-mode source_only
python3 scripts/live_eval.py --prompt-mode source_only --limit 5
```

Do not commit `*.local.jsonl` transcripts.
Do not commit local profile cards, sample files, or ledgers; use `*.local.md` or `*.local.json`.
