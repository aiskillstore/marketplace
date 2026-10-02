# Migration guide

This guide lists every behaviour change in each release and what an existing user must do about it. Read only the sections for the features you use; nothing here is required to keep a plain report-only workflow running. The release notes are in [CHANGELOG.md](../CHANGELOG.md); every claim made here is tracked with its evidence in [CLAIM-EVIDENCE-AUDIT.md](CLAIM-EVIDENCE-AUDIT.md).

## Quick reference

| Version | Change | Migration action |
|---|---|---|
| 1.5.0 | The report's sections are re-ordered and renamed, section titles carry no numbers, an empty lane says it was checked, warnings are capped at twenty with the count withheld and the re-run command beside them, paths print relative to a scan root the report states, and both formats draw a severity mark and a category mark on every row | Re-key any parser that matched the old headings; read a capped section from the command it prints, or pass `--report-detail full`; a parser of report paths must resolve them against the `Root` row; JSON and SARIF are unchanged |
| 1.3.0 | `.pdf` is a supported input | Check any pipeline that enumerated the supported extensions, or that extracted PDF text itself before scanning |
| 1.3.0 | PDF and HTML reports group identical issues into one counted row, and carry a category legend and document header, footer and symbol; the terminal prints a category marker on each finding line and a legend of its own | Use `--report-detail full` for the previous report layout; JSON and SARIF are unchanged, and a parser of the terminal text needs the two additions noted below |
| 1.0.0 | The clean-run sentence changed wording | Update any grep, test or dashboard that matches the old sentence; exit codes are unchanged |
| Five output lanes replace the flat section list | Re-key text-report parsers; `--format json` and SARIF gain fields, existing fields stay |
| Heuristic findings are review severity by default | If you relied on them failing the build, set `severities` for those rules |
| The `-ize`/`-ise` spelling conflict family warns by default | Pick a bundled `--profile`, or set `severities` / `allowlist.spellings` |
| Terminology, claims, dates, political wording, quotations, harmful wording and sources are never rewritten by `--fix` | Rewrite those findings from the report's `Should be` column |
| `maternal mortality rate` is context-gated; the `women's work` pair is removed; the percentage sign is silent in running prose | Expect those findings to narrow or disappear; this is source evidence, not a broken rule |
| Contested-claim findings report as diplomatic review, not factual error | Set `severities` on `UE-DP001` if you want it to fail a run |
| New opt-ins: `--init`, `--self-test`, `--baseline`, GitHub Action, hook, templates | Optional; no existing flag changes behaviour |

## The report redesign (1.5.0)

**What changed.** Seven presentation changes to the PDF and the HTML report. None of them is a rule, a severity or a count: the scan finds what it found before, `--format json` and `--format sarif` are untouched by this release and by 1.4.0, and the exit code is untouched.

1. **The sections are re-ordered and renamed, and both formats read the same plan.** `Summary`, then `Categories`, then the findings under `Harmful / Discriminatory Content`, `Diplomatic Sensitivity`, `Editorial Errors`, `Editorial Warnings`, `Agent Review Required`, `Audit Findings`, then `Quoted material`, `Priority Recommendations` and `Sources`. The PDF previously drew one `Issues` heading for every authored finding, and the HTML report used its own lane titles (`Deterministic violations`, `Heuristic editorial review`, `Harmful-discriminatory review`, `Diplomatic sensitivity`, `Optional audits`); the deterministic lane is now split by severity into `Editorial Errors` and `Editorial Warnings`. `Priority Recommendations` is new, and is derived only from counts this scan produced. `--report-detail full` keeps one heading per file, `Findings by file`.
2. **The separate heuristic review queue is gone.** `Review queue (heuristic findings)` was a second, shorter listing of findings already printed above it. `Agent Review Required` is that queue now, and carries every field the other sections do.
3. **Section titles carry no numbers.** A heading is its title, the lane it holds and the count beside it.
4. **A lane with nothing in it says so.** Its heading stays and the body reads that the lane was checked, so a clean lane cannot be mistaken for one that never ran.
5. **Warnings are capped in the body.** Under `grouped`, a section that would print more than twenty findings prints twenty, then `Showing 18 of 41 · 23 not listed above.` and the exact command that lists the rest. `Editorial Errors`, `Harmful / Discriminatory Content`, `Diplomatic Sensitivity` and `Audit Findings` are never capped, groups are never split at the boundary, and `--report-detail full` is never capped.
6. **Paths are relative to a scan root the report states.** The root — the common ancestor of the targets the scan was pointed at — appears once, as `Root` in `Summary`, and every path printed after it resolves against that root. Through 1.4.0 both formats printed absolute paths from the machine that ran the scan.
7. **Every row is drawn with its marks, and every row is the same row.** A severity mark, then the category's own mark beside its short code, then the position, the rule, the advice and all six provenance fields — in both formats and under both detail modes. The marks are drawn as vector paths, so nothing outside the file is fetched to draw them.

**What the redesign does not do.** It changes no finding, no severity, no lane count and no exit code. Grouping is still presentation only: `grouped` and `full` report the same numbers, and neither JSON nor SARIF takes `--report-detail`. The cap hides nothing from JSON or SARIF, which carry one result per finding whatever the report shows. The framing disclaimer, the endorsement boundary, the document symbol and the twelve-category legend are as they were; the legend has simply gained its own heading and its own drawn marks.

**What you must do.** If you parse the PDF or the HTML by section title, re-key to the names above — the old PDF headings `Issues`, `Review queue (heuristic findings)` and `Quoted material (<n>)`, and the old HTML lane titles, are all gone. If you resolve report paths, take `Root` from `Summary` and resolve against it; `--format json` and SARIF still carry absolute paths and need no change. If you want every finding in the body rather than twenty of them, pass `--report-detail full`, which is never capped. If a capped section's printed command matters to your readers, note that it is quoted for POSIX shells and names the package as the package names itself, so it assumes the tool is installed where it is run.

## PDF documents became a supported input (1.3.0)

**What changed.** `.pdf` moved into the supported-extension list. Before this release a PDF named on the command line was a refusal with exit `2` and a message telling you to extract the text yourself; now the tool recovers the text from the document's own bytes and screens it with the same rules as any other copy. Nothing else about reading a text file changed, and no rule was added: PDF support is a way of reading bytes, not a new check.

This is a behaviour change a pipeline will notice, in three specific ways.

1. **A file that used to be refused is now scanned.** If your job names a `.pdf` and expects exit `2`, it will now get a result — and possibly exit `1` if the copy has an error-severity finding. If a directory scan previously skipped PDFs silently, the file count in the run header and in the JSON `files` field will now include them.
2. **A refused PDF is a refusal, not a clean run.** A scanned or image-only document, an encrypted document, and a document whose fonts carry no recoverable encoding are all still refused with exit `2`, with the reason named on standard error and nothing on standard output. A run that refuses a PDF never prints the clean-run sentence for it. If your pipeline treats "exit `0`" as "checked", that assumption now holds more often and, where it previously covered a PDF that was never read, it no longer does.
3. **A PDF finding carries an extra field.** JSON and SARIF findings from a PDF include `pdfPage`, the 1-based page. The text output is unchanged: still `file:line:column`, where the line is a *visual* line reconstructed from the page layout rather than a line of a source file. Existing fields are untouched, so a consumer that ignores unknown keys needs no change.

**What you must do.** If your pipeline enumerated supported extensions to decide what to scan, add `.pdf` deliberately rather than by accident — decide whether you want a PDF screened in place, and if you previously extracted PDF text to a `.txt` and scanned that, you may now prefer the direct route. Keep the paste-the-text-into-a-`.txt` path for the documents that still refuse: it is the documented route for scanned, encrypted and undecodable-font PDFs, and it also gives a cleaner result, because a text file lets the tool classify quotations and the recovered PDF text cannot. Do not add a rule of your own that assumes `--fix` will rewrite a PDF: it refuses, as it refuses HTML, JavaScript and JSON.

## Grouped reports, the category legend and document furniture (1.3.0)

**What changed.** Three presentation features, none of them a rule, a severity or a count.

1. **Identical issues are grouped.** In the PDF and the HTML report, findings that are the same in every value the reader sees — rule, lane, severity, confidence, category, the matched text, the advice and the explanation — are drawn once as a single issue, with an `Occurrences` table listing each finding's own file, line and column, and a count shown when there is more than one. The previous layout, one block per finding, is `--report-detail full`. The default is the grouped layout, so an existing reader of the HTML or the PDF sees a different structure the first time it runs.
2. **A category legend.** The PDF, the HTML report and the terminal each state all twelve category markers with their text labels, and this scan's count against each. Every terminal finding line now also carries its marker and category between the rule id and the confidence, where before it carried only the rule id.
3. **Document furniture.** Both report formats carry a header reading `EDITORIAL REVIEW` with the report date, the targets and the version, a footer with the credit line and the page numbers, and a document symbol of the form `UE/<year>/<4 digits>`.

**What grouping does not do.** It is a rendering choice and nothing else. The severity counts, the lane counts and the process exit code are computed from the findings before either layout runs, so `grouped` and `full` cannot disagree about them. JSON and SARIF do not take the flag at all: they carry one result per finding, byte for byte as before. The document symbol is assigned by the tool from the date, the targets and the version as a stable reference for that one scan; it is registered nowhere and it is not a United Nations symbol number, so nothing should key on it as though it identified a document beyond this tool.

**What you must do.** If you parse the PDF or the HTML, either pass `--report-detail full` to keep reading the layout you have, or read the grouped layout: one issue per distinct finding, with occurrences listed under it. If you parse terminal output line by line, expect two additions — the marker and category after the rule id on a finding line, and a `categories:` line after `lanes:` — and note that neither appears on a clean run. If you consume `--format json` or SARIF, there is nothing to do.

## The clean-run sentence (1.0.0)

**What changed.** A run with no findings used to print `No editorial findings.` It now prints exactly:

```text
No findings under the enabled, documented local rules.
```

The same sentence now appears in the README, the skill instructions, the user guide and the `/un-diplomatic-agent` command template, and the PDF report states the same meaning.

**What you must do.** If a script, test or dashboard greps stdout for the old sentence, match the new one. Exit codes are unchanged: `0` still means no error-severity editorial findings, `1` still means at least one, `2` still means a tool or usage failure. Prefer exit codes or `--format json` over text matching.

## Five output lanes and heuristic severity

**What changed.** The report separates deterministic rule violations, heuristic editorial review, harmful or discriminatory review, diplomatic sensitivity and optional audits. Every finding carries its rule source, profile, confidence, limitation and recommended human action, in the text, JSON, SARIF and PDF outputs. Heuristic findings flip to review severity by default: they no longer move the exit code unless the organisation configures them to `error`.

**What you must do.**

- If you parse the text report by section heading, re-key to the lane headings. The stable interfaces remain the exit codes and `--format json`.
- JSON and SARIF consumers keep every existing field (`file`, `line`, `column`, `ruleId`, `category`, `severity`, `confidence`, `scope`, `message`, `suggestion`, `current`, `proposed`, `audit`) and gain the lane, source, profile, limitation and action fields.
- If a heuristic rule used to fail your build as an error, pin it in `.un-editorial.json`:

```json
{
  "severities": { "UE-RE004": "error" }
}
```

## Spelling conflicts between profiles

**What changed.** The `-ize`/`-ise` conflict family — words such as `organization` — is no longer a blanket error. Under the default run it is a profile-selection warning: the message names the profile choice instead of calling a form wrong, does not fail the run and is not rewritten by `--fix`. `--profile un-secretariat-document` (alias `un-v1`) and `--profile un-geneva-web` are silent on the family because the United Nations spelling list itself prints the `-ize` forms. `--profile generic-british-english` reports the family as errors because that profile chooses `-ise`. Only `analyse`, `catalyse`, `paralyse` and `practise` remain errors under every profile.

**What you must do.** Choose one deliberately:

```sh
# pin the United Nations secretariat baseline
node bin/check.mjs content --profile un-secretariat-document

# or pin British -ise preferences
node bin/check.mjs content --profile generic-british-english
```

Alternatively keep the default warning, silence specific words with `allowlist.spellings`, or pin severities in `.un-editorial.json`. If CI must be red or green on spelling, do not rely on the default: set the severity explicitly.

## The `--fix` set shrank

**What changed.** `--fix` applies only safe, deterministic, reversible replacements: British spelling outside the profile-dependent conflict family, en-dash ranges, a doubled word, a space before punctuation and a missing space between sentences. Terminology (`per cent`, `the United States` included), claims, dates, political wording, quotations, harmful wording and sources are never rewritten by `--fix`.

**What you must do.** If a pipeline used `--fix --apply` to apply terminology or spelling-conflict corrections, take those from the report's `Should be` column instead — the approval-gated command template already does this. Review every `--fix` diff as before; the files it accepts (`.txt`, `.md`, `.markdown`) and its refusals are unchanged.

## Terminology rules reworked against sources

**What changed.**

- `maternal mortality rate` is reported only where the printed statistic is the per-100 000-live-births figure, and only for review — the rate and the ratio are different measures.
- The unsourced `women's work` replacement pair is removed; the sourced pair `handicapped` → `persons with disabilities` stays.
- The percentage sign is silent in running prose (the live United Nations guidance permits either form in running text); the spelling `percent` becomes `per cent`.
- The shared source note that cited a dead `editorial.un.org` address and contradicted the percentage guidance was corrected alongside these rules.

**What you must do.** Treat vanished findings as source-backed removals, not regressions — the evidence and retrieval dates are in `rules/sources.json`. If you still want a house rule that the guide does not carry, express it in a profile (`terminology.forbidden`) with your own source.

## Contested claims require diplomatic review

**What changed.** `UE-DP001` reports a bare territorial-status claim as requiring diplomatic review in the diplomatic sensitivity lane, symmetrically for every party to the claim, instead of standing as a factual error.

**What you must do.** If a build gate relied on exit `1` from `UE-DP001`, set its severity explicitly in `.un-editorial.json`:

```json
{
  "severities": { "UE-DP001": "error" }
}
```

## New opt-ins (no migration required)

- `--init` writes a starter `.un-editorial.json` plus a host and CI snippet.
- `--self-test` runs a bundled corpus and asserts the exact expected findings — use it after every upgrade.
- `--baseline <path>` records the findings of a run; later runs fail only on findings that are not in the baseline.
- A GitHub Action (`action.yml`), a pre-commit hook snippet and agent command templates for Claude Code, Codex, OpenCode and Cursor ship with the package.
- Report previews cut deterministically at a platform-specific length and mark the cut, so nothing is ever truncated silently.

## Configuration compatibility

Every documented `.un-editorial.json` key keeps its meaning and precedence (`ignoredPaths`, `allowlist`, `severities`, `rules`, `spellingReview`, `baseOrigin`, `renderTargets`). The configuration file still wins over a profile on a shared key. Unknown keys, unknown rule IDs and malformed values still fail closed with exit `2` — a stale key is reported, never ignored. Profile files gain the `spellingConflicts` key; a profile that names a non-existent spelling key fails with exit `2`.

## What did not change

- Exit codes `0` / `1` / `2`, and audits never moving the exit code.
- Report-first operation: a finding identifies a review requirement; it does not establish truth.
- Zero npm dependencies and offline-deterministic operation.
- `--fix` remains opt-in, prose-only and diff-previewed; symbolic links, hard links and non-regular files remain refused, and a PDF is now refused by that gate as well.
- Inline suppression syntax (`ue:ignore`) and its span rules.
- The approval-gated `/un-diplomatic-agent` flow.
- The rule catalogue: PDF support adds no rule. It is a way of reading bytes, and the same documented rules run over the recovered text.

## Suggested upgrade steps

1. Read the release notes for the version you are moving to in [CHANGELOG.md](../CHANGELOG.md).
2. Update the installed skill (`npx skills update un-editorial-check`) or reinstall as described in the README.
3. Run `un-editorial-check --self-test` (or `npm test` in a checkout) to verify the installation.
4. Apply the sections above that match your setup, then re-run your pipeline once and compare the lane output with your expectations.
5. Keep your existing `.un-editorial.json`; adjust only the severities and profile choices you deliberately want to change.
