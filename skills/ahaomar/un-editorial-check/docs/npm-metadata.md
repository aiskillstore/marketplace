# npm metadata review

Field-by-field review of the published package record for `un-editorial-check`, as served by the npm registry for version 1.1.0. Every verdict below is stated against evidence that you can re-run yourself. The integration note at the end contains the exact paste-ready edits for `package.json` and `README.md`. This file is documentation only. It changes no metadata on its own.

## How to reproduce the evidence

```sh
npm view un-editorial-check --json
npm view un-editorial-check version description keywords homepage repository.url bugs.url
npm help package.json | less
```

The first command returns the full registry record. The second returns just the fields quoted below. The third opens npm's own documentation of the `package.json` fields that npm publishes.

## Verdict table

The middle column is the value for 1.1.0. Where the registry serves a field, it was read with `npm view` on 28 September 2026. Three fields below are marked *manifest only*: the registry does not serve them, so their values were read from `package.json` in the published tree and cannot be cross-checked against the registry.

| Field | Value for 1.1.0 | Verdict |
| --- | --- | --- |
| `name` | `un-editorial-check` | Correct. Matches the install and `npx` invocation documented in the README. |
| `version` | `1.1.0` | Correct. Matches `VERSION` and the six-anchor version set. |
| `description` | `Reads user-visible copy the way a UN editor would: language, wording, tone, spelling, terminology, dates, numbers, claims and register. Report-first, with a conservative opt-in fixer.` at 183 characters | Present, accurate and identical in the registry and in `package.json`. Change is optional, not corrective. See [Description](#description). |
| `keywords` | `un`, `editorial`, `editorial-standards`, `copy-check`, `linter`, `british-english`, `sarif`, `static-analysis`, `zero-dependency` at 9 entries | Present and accurate, but misses the formats and the agent-skill audience. See [Keywords](#keywords). |
| `homepage` | `https://github.com/ahaomar/un-editorial-check#readme` | Correct. Resolves to the repository README. No change proposed. |
| `repository` | `git+https://github.com/ahaomar/un-editorial-check.git` | Correct, in the normalised `git+https` form that npm documents. No change proposed. |
| `bugs` | `https://github.com/ahaomar/un-editorial-check/issues` | Correct. Points at the issue tracker. No change proposed. |
| `license` | `MIT` | Consistent with the repository licence file. No change proposed. |
| `files` — *manifest only* | `bin`, `lib`, `commands`, `rules`, `config`, `docs`, `scripts`, `agents`, `skills.sh.json`, `SKILL.md`, `README.md`, `USER-GUIDE.md`, `COMPATIBILITY.md`, `LICENSE`, `VERSION`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `MAINTAINING.md` | Correct, and worth stating precisely: `docs` is published, so every file under `docs/` ships in the npm tarball, while `templates` is absent and stays repository-only. Tests are excluded. No change proposed. |
| `engines` | `node` `>=18` | Correct, and matches the Node.js 18 requirement stated in the launch note and the README proposal. No change proposed. |
| `dependencies` — *manifest only* | absent | Correct by contract. The package ships zero npm dependencies. The registry omits the key entirely rather than reporting an empty object, which is consistent with no dependencies being declared. |
| `scripts` | `test`, `check:portability`, `check:syntax` | Correct. `npm run check:syntax` and `npm test` are the two commands integrators are asked to run, and `test` chains every suite including the documentation audits. |
| `templates` | absent from `files` | Correct and deliberate, with a consequence worth stating: `templates/` ships in the repository but not in the npm tarball, so `templates/social/**` is reachable from GitHub only. A consumer who installs from npm does not receive the social copy, the agent command templates or the pre-commit hook. The README already says the npm package ships the CLI itself and that `action.yml` and `templates/` are read from the repository. No change proposed. |
| `screenshots` | absent | Blocked, not missing by oversight. See [Screenshots](#screenshots). |

Registry and repository agree field by field for `name`, `version`, `description`, `keywords`, `homepage`, `repository`, `bugs` and `license`, checked with `npm view` against `package.json` on 28 September 2026. No drift, so no corrective edit is required before the next publish.

## Description

Recommendation: leave `description` unchanged. It is accurate, it matches `package.json` byte for byte, and it carries the phrase that describes the tool. The analysis below records why a rewrite was considered and why it does not earn its place.

Live value, verbatim:

```json
  "description": "Reads user-visible copy the way a UN editor would: language, wording, tone, spelling, terminology, dates, numbers, claims and register. Report-first, with a conservative opt-in fixer.",
```

What the live string does not contain: `rules`, `lint`, `pdf`, `sarif`, `dependency`. Those are the terms a searcher types, and `npm search` matches on the description. An alternative that adds them while staying under the live length, verbatim:

```json
  "description": "Reads user-visible copy the way a UN editor would: 43 rules, five review lanes, report-first, zero npm dependencies. Markdown, HTML, text, source and PDF in; PDF, JSON and SARIF out.",
```

Length check, verbatim:

```text
live description: 183 characters
alternative:      182 characters
longer option:    200 characters (enumeration kept, searchable terms added)
```

The trade-off is real and it is the reason this is not a recommendation. The alternative drops the element enumeration — language, wording, tone, spelling, terminology, dates, numbers, claims and register — which is the single most informative part of the current string for a human reader. Keeping the enumeration and adding the searchable terms lands at 200 characters, longer than what is there now. There is no string that is shorter, keeps the enumeration and adds the terms, so the choice is between three imperfect options rather than an upgrade. Pick the 182-character version only if search matching matters more to you than the enumeration.

Claim check for the alternative, in case you take it. Each assertion is traceable to a shipped artefact.

| Claim in the alternative | Where it is evidenced |
| --- | --- |
| 43 rules | `rules/catalogue.json`, where the `rules` array holds 43 entries |
| five review lanes | The lane set printed by `--help` and exercised by `tests/fixtures/lanes` |
| report-first | The report-before-write behaviour documented in `USER-GUIDE.md` |
| zero npm dependencies | The absent `dependencies` block in `package.json` |
| Markdown, HTML, text, source and PDF in | `SUPPORTED_EXTENSIONS` in `lib/extract.mjs`: `.md`, `.markdown`, `.txt`, `.html`, `.htm`, `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`, `.pdf` |
| PDF, JSON and SARIF out | `--report` for PDF, `--format json` and `--format sarif` in `--help` |
| PDF both in and out | Reading is the narrower of the two, and the string does not pretend otherwise: the limitations are listed in the note below and in `README.md` |

Note what the alternative does not claim. The tool does not read email as a distinct format; `.txt` covers that case, and no `.eml` extension is in `SUPPORTED_EXTENSIONS`.

As of 1.3.0 PDF is both read and written, so the string now lists it on both sides. Reading it is narrower than writing it, and the distinction is documented rather than blurred: a PDF is a rendered page, so the tool recovers its text and cannot tell a quotation from a paragraph, every unit is treated as authored copy, `line` addresses a visual line rather than a source line, and scanned documents, encrypted documents and documents whose fonts have no recoverable encoding are refused with exit `2` rather than read. The tool performs no optical character recognition and does not claim to.

## Keywords

Live keywords, verbatim:

```json
  "keywords": [
    "un",
    "editorial",
    "editorial-standards",
    "copy-check",
    "linter",
    "british-english",
    "sarif",
    "static-analysis",
    "zero-dependency"
  ],
```

Proposed keywords, verbatim:

```json
  "keywords": [
    "un",
    "editorial",
    "editorial-standards",
    "copy-check",
    "linter",
    "british-english",
    "sarif",
    "static-analysis",
    "zero-dependency",
    "united-nations",
    "cli",
    "agent-skill",
    "editorial-review",
    "neutral-language",
    "markdown",
    "html",
    "pdf-report",
    "writing-tools"
  ],
```

That is 9 entries live and 18 proposed, with every existing entry preserved and nothing renamed. This is the one change in this file that I recommend, because it costs nothing and closes four real gaps.

| Added keyword | Gap it closes |
| --- | --- |
| `un` is present, but `united-nations` is not | Searches for the spelled-out organisation name miss the package today |
| `cli` | The package is a command-line tool and the word does not appear anywhere in the set |
| `agent-skill`, `writing-tools` | The two audiences the package serves: agents that install skills, and people checking prose |
| `editorial-review`, `neutral-language` | The substance of the rule set, which the current set gestures at with `editorial-standards` alone |
| `markdown`, `html` | The formats the extractors accept, currently unrepresented |
| `pdf-report` | The `--report` output, currently unrepresented |

One correction to an earlier draft of this note. It claimed that npm caps `keywords` at 20 entries. npm's own `package.json` documentation says only that the field is an array of strings that helps discovery through `npm search`, and states no limit, so the cap claim has been removed rather than repeated. The proposal at 18 entries is comfortably short regardless.

## Screenshots

Verdict: the field cannot be filled honestly today, and adding an empty one would be worse than leaving it absent.

Evidence for the blocking facts, verbatim, each command with its real output:

```sh
npm help package.json | grep -i screenshots
```

```text
(no matches)
```

```sh
git ls-files | grep -iE '\.(png|jpe?g|gif|svg|webp)$'
```

```text
(no matches)
```

```sh
npm help package.json | grep -c screenshots
npm help package.json | grep -c devEngines
```

```text
0
1
```

Three facts, in order.

1. `npm help package.json` on the locally installed npm 11.19.0 returns zero matches for `screenshots` and one match for `devEngines`. The second match is the positive control: it proves the first result means the field is absent from the documentation rather than the documentation not being read. `devEngines` is a field npm does document.
2. The rendered npm documentation page at `https://docs.npmjs.com/cli/v11/configuring-npm/package-json` documents these fields: name, version, description, keywords, homepage, bugs, license, people fields, funding, files, exports, main, type, browser, bin, man, directories, repository, scripts, gypfile, config, dependencies, devDependencies, peerDependencies, bundleDependencies, optionalDependencies, overrides, engines, os, cpu, libc, devEngines, private, publishConfig, workspaces. `screenshots` is not among them. Reading the page as rendered returns a stable result across repeated fetches: `devEngines` and `funding` are present, `screenshots` is absent.
3. The repository tracks no image asset of any kind, so no URL could be pointed at without inventing one.

One trap when re-running fact 2. The docs site renders in the browser and serves a redirect shell to a plain HTTP client, so `curl` of that URL returns 162 bytes containing no field names at all: `curl -s <url> | grep -c devEngines` returns `0` even though the field is documented. Read the page as rendered, or use fact 1 as the reproducible check, rather than treating a curl result as evidence.

An earlier draft of this note attributed the field list to a specific patch version of the documentation. The URL serves the current v11 documentation and carries no version marker in its body, so no patch version is claimed here. Fact 1 remains the check to re-run, because it is the one that does not depend on a rendering client.

The practical alternatives, in order of preference.

1. Publish a terminal recording or a sample report image to the repository, for example under `docs/assets/`, then add the raw file URL.
2. Use the README image slot instead, which readers see without any metadata field at all.
3. Leave the field out until step 1 has happened.

Paste-ready block for the moment an asset exists. Do not apply it before then.

```json
  "screenshots": [
    "https://raw.githubusercontent.com/ahaomar/un-editorial-check/main/docs/assets/report-sample.png"
  ],
```

## Proposed README section

Status: complete and paste-ready. It resolves the collision an earlier draft of this note flagged rather than deferring it to you.

Insertion anchor, verbatim:

```text
insert immediately after the line 11 User Guide blockquote (the one beginning `> **For researchers, students and United Nations staff:**`), and immediately before the `## What it checks` heading
```

That places a first-time reader's path before the rule catalogue rather than after it, and it lands above the two prose sections that already state the product boundary. An earlier draft of this note named an anchor — a blockquote closing with `> **Full rule list ...**` — that does not exist in `README.md`; the anchor above is the real one, verified against the file. The line number is a convenience for locating the spot, not part of the instruction: re-read the two neighbouring lines if the file has moved.

Paste everything between the two rules below, in order.

---

## Quickstart

Node.js 18 or newer is the only requirement. `npx` fetches the package on first use, so nothing needs installing up front.

```sh
# 1. Check a file and write a PDF report beside it.
npx -y un-editorial-check statement.md --report un-editorial-review.pdf

# 2. Preview the automatic corrections as a diff. This writes nothing.
npx -y un-editorial-check statement.md --fix

# 3. Apply the corrections you approved in the preview, then run step 1 again.
npx -y un-editorial-check statement.md --fix --apply
```

The exit code is `0` when no error-severity editorial findings are present, `1` when there are, and `2` for a usage, configuration, scan or write failure. [Exit codes](#exit-codes) states what a clean run means. CI should treat `1` as a requested policy failure and `2` as a tool failure, and should not merge the two.

### What a scan actually outputs

Two summary lines, then findings grouped under one heading per lane.

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

Each finding occupies one line and carries its lane, its rule identifier, its position in the file and the action a human should take:

```text
  <file>:<line>:<col>  <ruleId>  [<lane>]  <what is wrong>.  → <recommended human action>.
```

Captured output is not reproduced here, because a scan of flawed copy prints the copy that triggered each rule. [docs/demo/README.md](docs/demo/README.md) runs the five lanes over a real statement, a real page and a real clean file, and gives the exact commands to regenerate every line of it.

### The five lanes in one glance

| Lane | What it holds | Default effect on the exit code |
|---|---|---|
| Deterministic violations | Rules that prove their own defect inside a documented boundary | Error severity fails the run with `1`; warnings do not |
| Heuristic editorial review | Judgement calls routed to `AGENT REVIEW REQUIRED` | Review severity by default; never fails unless configured to `error` |
| Harmful or discriminatory review | High-severity human review queue; never rewritten automatically | Error severity fails the run with `1` |
| Diplomatic sensitivity | Contested-status claims requiring diplomatic review | Warning by default; set `severities` to gate on it |
| Optional audits | Publishing, accessibility and security findings, requested with `--profile` | Never changes the exit code |

Quoted material is a context rather than a lane: a finding inside a quotation keeps its own lane and is reported separately, never blended into authored copy.

### More documentation

- [USER-GUIDE.md](USER-GUIDE.md) — the plain-language walkthrough with a copy-and-paste prompt
- [CHANGELOG.md](CHANGELOG.md) — every release from 0.2.0 to 1.1.0
- [docs/LAUNCH.md](docs/LAUNCH.md) — the 1.1.0 release announcement
- [docs/demo/README.md](docs/demo/README.md) — the five-lane demo and its reproduction commands
- [docs/MIGRATION.md](docs/MIGRATION.md) — what changed behaviour when, and the upgrade action for it
- [docs/CLAIM-EVIDENCE-AUDIT.md](docs/CLAIM-EVIDENCE-AUDIT.md) — each claim, its limitations and the suite that locks it
- [rules/catalogue.json](rules/catalogue.json) — the rule index with severity, confidence and guard notes

---

### How the earlier blocked part was resolved

An earlier draft of this note would not commit part 4, on the grounds that a captured run over `tests/fixtures/demo/statement.md` carries rule-violating text inside a fenced block. The scanner exempts fenced blocks from extraction, so such a block does pass `node bin/check.mjs --self-scan`. The draft treated a clean scan as insufficient evidence and stopped, leaving the section undelivered.

Resolving it was possible without either rule. The section above shows the report's **shape** — its summary lines, its lane headings in order, and the one-line finding format with placeholders — rather than a captured run. Placeholders carry no rule violation, so nothing in the block breaks a rule, and a reader learns the format without this file holding a copy of flawed copy. The concrete demonstration is one link away, in the demo, which is where the reproduction commands already live.

This is the same choice `docs/LAUNCH.md` and `docs/demo/README.md` make, and it is the reason the rule and the deliverable never actually collide.

### Verified properties of the section

Measured on a spliced copy of `README.md` with the section inserted at the anchor above, on 28 September 2026.

| Check | Result |
| --- | --- |
| `node bin/check.mjs --self-scan <spliced README>` | `0 errors, 0 warnings, 0 notes`, exit `0` |
| `npm test` on a copy carrying the spliced README | exit `0`, all suites green |
| `npm run check:portability` on the same copy | exit `0` |
| `node scripts/validate-portability.mjs` agent-mention check | unaffected, the section names no agent host |
| Exact clean-run sentence occurrences in `README.md` before | `2` |
| Exact clean-run sentence occurrences in the spliced copy after | `2` |

The last two rows are informational rather than a lock. No suite asserts a count for that sentence; `tests/audit-docs.mjs` asserts only that four surfaces — `README.md`, `SKILL.md`, `USER-GUIDE.md` and `commands/un-diplomatic-agent.md` — each contain it at least once. The section deliberately adds no occurrence, pointing at [Exit codes](#exit-codes) instead of repeating the string, so the README keeps the two it already had. An earlier draft of this note described a release check that expected `2`; no such check exists, and the claim has been corrected.

One formatting note. The section contains its own fenced blocks, so paste it as raw text between the two rules rather than copying it out of a rendered fence, and re-check fence balance afterwards.

## What the test suite covers, and what it does not

Stated plainly, because the files this task adds are only partly swept by `tests/audit-docs.mjs` and a reader should not assume otherwise.

| Check | Covers these new files | Does not cover |
| --- | --- | --- |
| Banned claim phrases | `docs/LAUNCH.md` and `docs/npm-metadata.md`, because the suite sweeps `docs/*.md` | `docs/demo/README.md`, all of `templates/social/**`, and `tests/fixtures/demo/**` |
| House style: no contractions, no question marks, British English, per cent kept inside code | none of them; the suite applies the style block to `USER-GUIDE.md` alone | all eight new prose files |
| Exact clean-run sentence present | none of them; the suite requires it on four named surfaces | — |
| Repository self-scan | `docs/LAUNCH.md`, `docs/demo/README.md` and `docs/npm-metadata.md`, which are outside `tests/fixtures/` | `tests/fixtures/demo/**`, which a directory scan skips |

`docs/demo/README.md` is not swept for banned phrases because `tests/audit-docs.mjs` lists `docs/*.md` with a non-recursive read, so it does not descend into `docs/demo/`. The three files under `tests/fixtures/demo/` are outside every documentation check by design, since they are the material that has to break rules.

The gap was closed by hand rather than by editing a suite this task does not own. Each new prose file was run through a checker replicating the `tests/audit-docs.mjs` style block verbatim — the same contraction pattern, the same question-mark and per-cent checks, and the same American-spelling list — and the banned-phrase sweep was run over the tracked files. Both are clean. A future change to `tests/audit-docs.mjs` that widens its file list would pick these files up automatically.

## Integrator verification

Run these in the worktree after applying the two edits above.

```sh
node bin/check.mjs --self-scan --quiet
npm run check:syntax
npm test
npm view un-editorial-check description keywords
```

Expected results, in order.

| Command | Expected |
| --- | --- |
| `node bin/check.mjs --self-scan --quiet` | exit 0, no errors reported |
| `npm run check:syntax` | exit 0 |
| `npm test` | exit 0, all suites green |
| `npm view ...` | unchanged until a new version is published, which is correct: registry values move only on publish |

The metadata edits take effect for consumers on the next publish. Nothing in this repository needs to change for the current 1.1.0 record to remain accurate, because every field except the two proposals above already reports the truth.
