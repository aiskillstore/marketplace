# un-editorial-check 1.1.0 — release announcement

**Published 28 September 2026 to [npm](https://www.npmjs.com/package/un-editorial-check) and [GitHub Releases](https://github.com/ahaomar/un-editorial-check/releases).**

`un-editorial-check` reads user-visible copy the way a United Nations editor would — language, wording, tone, spelling, terminology, dates, numbers, claims and register — and reports what fails. It is a zero-dependency Node.js command-line tool and an Agent Skill, it runs offline on your own machine, and it changes nothing unless you tell it to. Version 1.1.0 is the completion release: the report now separates five lanes, the clean-run wording is exact, and every claim the tool makes is recorded with the test that locks it.

## What shipped in 1.1.0

- **Five output lanes.** Text, JSON, SARIF and PDF output separate deterministic rule violations, heuristic editorial review, harmful or discriminatory review, diplomatic sensitivity and optional audits. Every finding carries its rule source, the profile it ran under, its confidence, the limitation that bounds it and the recommended human action.
- **An exact clean-run sentence.** A run with no findings prints `No findings under the enabled, documented local rules.` in the CLI, the README, the skill instructions, the user guide and the command template; the PDF states the same meaning.
- **Diplomatic claims are review, not verdicts.** A contested territorial-status statement is reported as requiring diplomatic review, symmetrically for every party to the claim, instead of standing as a factual error.
- **Heuristic findings are review severity by default.** They move a run to `AGENT REVIEW REQUIRED` and never fail it unless an organisation configures them to `error`.
- **A documentation truth-pass.** [docs/CLAIM-EVIDENCE-AUDIT.md](CLAIM-EVIDENCE-AUDIT.md) records each claim the documents make, its limitations and the suite that locks it, and [docs/MIGRATION.md](MIGRATION.md) gives the upgrade action for every behaviour change, keyed to the 1.0.0 release that introduced them.

Unchanged in 1.1.0: report-first operation, zero npm dependencies, the approval-gated `/un-diplomatic-agent` command and the exit-code contract.

## Three commands to try it

Node.js 18 or newer is the only requirement; `npx` fetches the tool on its first use.

```sh
# 1. Check a file and write a PDF report beside it.
npx -y un-editorial-check statement.md --report un-editorial-review.pdf

# 2. Preview the automatic corrections as a diff. This writes nothing.
npx -y un-editorial-check statement.md --fix

# 3. Apply the corrections you approved in the preview, then run step 1 again.
npx -y un-editorial-check statement.md --fix --apply
```

Nothing is written to your file before step 3, and step 3 is yours to run or not. `--fix` handles only deterministic replacements — British spelling outside the profile-dependent conflict family, en-dash ranges, a doubled word, a space before punctuation and a missing space between sentences. Terminology, claims, dates, political wording, quotations, harmful wording and sources are never rewritten by it.

Non-technical readers can use the copy-and-paste prompt in the [User Guide](../USER-GUIDE.md) instead of running commands by hand.

## What a scan actually outputs

The report opens with two summary lines: the scan's scope and its severity counts, then one lane-count line. Findings follow, grouped under a heading per lane, in this order.

```text
un-editorial-check <version> — scanned <n> file(s) — editorial: <e> errors, <w> warnings, <n> notes
lanes: deterministic <n> · heuristic-review <n> · harmful-discriminatory <n> · diplomacy <n> · audit <n> · quoted <n>

EDITORIAL ERRORS (<n>)          ← deterministic lane, by severity
EDITORIAL WARNINGS (<n>)
EDITORIAL NOTES (<n>)
AGENT REVIEW REQUIRED (<n>)     ← heuristic lane
HARMFUL-DISCRIMINATORY REVIEW (<n>)
DIPLOMATIC SENSITIVITY (<n>)
OPTIONAL AUDIT — <name> (<n>)   ← one per requested audit profile
```

Every finding occupies one line and carries its lane, its rule identifier, its position in the file, its confidence, and the action a human should take:

```text
  <file>:<line>:<col>  <ruleId>  [<lane>]  <what is wrong>.  → <recommended human action>.
```

A finding quoted out of a document is counted separately in the `quoted` lane count and keeps its own lane, so quoted text is never blended into authored copy.

Captured tool output is not reproduced in this file. A scan of deliberately flawed copy prints the copy that triggered each rule, so quoting a real run here would place rule-violating text in a tracked document. The full five-lane demonstration lives in [docs/demo/README.md](demo/README.md), which gives the exact commands to regenerate every line of it, and the deliberately flawed copy lives under `tests/fixtures/demo/` rather than under `docs/`. Run the commands to see the real report.

Add `--format json` or `--format sarif` for machine-readable output, and `--report review.pdf` for the current-to-should-be PDF.

## The five lanes in one glance

| Lane | What it holds | Default effect on the exit code |
|---|---|---|
| Deterministic violations | Rules that prove their own defect inside a documented boundary | Error severity fails the run with `1`; warnings do not |
| Heuristic editorial review | Judgement calls routed to `AGENT REVIEW REQUIRED` | Review severity by default; never fails unless configured to `error` |
| Harmful or discriminatory review | High-severity human review queue; never rewritten automatically | Error severity fails the run with `1` |
| Diplomatic sensitivity | Contested-status claims requiring diplomatic review | Warning by default; set `severities` to gate on it |
| Optional audits | Publishing, accessibility and security findings, requested with `--profile` | Never changes the exit code |

Quoted material is a context rather than a lane: a finding inside a quotation keeps its own lane and is reported separately, never blended into authored copy.

## The honest scope statement

- It pre-screens copy against documented local rules that ship with the package. A finding means a documented rule matched extracted copy; it does not establish the truth of a claim, and source accuracy, neutrality and year alignment stay with a human reader.
- It grants no approval. Sign-off belongs to the person responsible for the document: the tool writes nothing on its own, and the `/un-diplomatic-agent` flow stops at an explicit approval question before any change.
- It presents itself as neither verification of facts nor legal opinion nor institutional endorsement. The rules, their sources and their retrieval dates are published in [rules/sources.json](../rules/sources.json) so that a reader can re-check current guidance rather than trust a release.
- It is not a code-quality, accessibility, security or SEO linter. Those concerns run only as opt-in audits in their own section.

## What a clean run means

A run with no findings prints exactly one sentence:

```text
No findings under the enabled, documented local rules.
```

Nothing stronger follows from it. The tool checked the rules that were enabled and documented, and reported what those rules found.

## Where to read more

- [README.md](../README.md) — installation, CLI reference, all 43 rules, exit codes and documented limitations
- [USER-GUIDE.md](../USER-GUIDE.md) — the plain-language walkthrough with a copy-and-paste prompt
- [CHANGELOG.md](../CHANGELOG.md) — every release from 0.2.0 to 1.1.0
- [docs/MIGRATION.md](MIGRATION.md) — what changed behaviour when, and what an existing pipeline must do about it
- [docs/CLAIM-EVIDENCE-AUDIT.md](CLAIM-EVIDENCE-AUDIT.md) — each claim, its limitations and the test that locks it
- [docs/demo/README.md](demo/README.md) — the five-lane demo and its reproduction commands
- [rules/catalogue.json](../rules/catalogue.json) — the maintained rule index with severity, confidence and guard notes

---

Sections of this page may be reused verbatim as release notes or as a blog post. Keep the scope statement and the clean-run sentence intact when reusing them.
