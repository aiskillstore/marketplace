---
name: un-editorial-check
description: Reads user-visible copy the way a United Nations editor would — language, wording, tone, grammar, hate speech, spelling, terminology, dates, numbers, claims and register — and reports what fails. Use when reviewing web pages, dashboards, blog posts, page titles, meta descriptions, copy baked into JavaScript by a coding agent, or the text of a PDF document. Checks HTML, Markdown, plain text, rendered JavaScript string literals, PDF text and Word or OpenDocument document text only; it is not a code-quality, accessibility, security or SEO linter (those run only as explicit opt-in audits) and it does not judge whether a claim is true.
license: MIT
compatibility: Requires Node.js 18 or later and a host that can load the portable Agent Skills SKILL.md format.
metadata:
  version: "1.7.0"
  source-date: "2026-10-02"
---

# UN editorial check

Run the bundled Node.js CLI before offering editorial judgement. The CLI checks documented rules over extracted copy; it does not prove that prose is clear, neutral, accurate or adequately sourced.

Resolve `<skill-base>` from the directory containing this `SKILL.md`. All paths below are relative to that directory.

## Workflow

1. Run `node <skill-base>/bin/check.mjs <paths>`. Add `--report <path.pdf>` to write a current-to-should-be PDF of the same findings for the user.
2. Address error-severity findings (exit code `1`). Review warnings; do not suppress them merely to obtain exit code `0`.
3. Read the applicable files under [rules/](rules/): [spelling](rules/spelling.md), [terminology](rules/terminology.md), [numerals](rules/numerals.md), [register](rules/register.md), [diplomacy](rules/diplomacy.md), [hate speech](rules/hate-speech.md) and [grammar](rules/grammar.md). Do not restate or reinterpret them from memory.
4. Work through `AGENT REVIEW REQUIRED` findings: whether claims match evidence, figures are sourced and dated, citations are complete, comparisons use aligned years, and labels say what was counted.
5. Report deterministic findings separately from editorial judgement, following the five lanes: deterministic violations, heuristic editorial review, harmful or discriminatory review, diplomatic sensitivity, audits. Each finding carries its rule source, profile, confidence, limitation and recommended human action; keep those fields intact in whatever you hand back.

`--stdin` reads one document from standard input as plain-text prose under the synthetic name `<stdin>.txt`; `--fix` is refused beside it. `--claims <file>` verifies a committed claim register and `--claims-out <file>` writes one; the register rules (UE-CL002, UE-CL003) verify that bookkeeping happened, never that a claim is true. `--emit-corrected <file>` writes the recovered copy of exactly one PDF with the deterministic corrections applied, headed by a notice that it is recovered working text — take it from the report of the same run and read it against the source.

Verify an installation with `node <skill-base>/bin/check.mjs --self-test` (bundled corpus, exact expected findings). `--init` writes a starter `.un-editorial.json` with a host and CI snippet, and `--baseline <path>` records an established corpus so only new findings fail.

## What is checked, and what is not

Only classified user-visible copy is checked: prose in HTML text nodes and attributes that carry copy, Markdown, plain text, JavaScript string literals that have render evidence (an assignment to a render target, a template or concatenation used as copy, a sentence-like literal), and the text recovered from a PDF. Comments, code, identifiers, URLs and cited titles are masked before any rule runs. Quoted and block-quoted material is classified with its context rather than silently dropped: where the harmful or discriminatory review applies, it is reported separately as quoted or reported content.

A PDF (`.pdf`), document containers (`.docx`, `.odt`) and an http(s) page named with `--url` are supported for reading. A retrieved page is checked under its URL as the name; an error status, a response that is neither HTML nor plain text, and a body over 4 MiB are refusals with exit `2`, and audits stay local to files on disk. It is a rendered page, not a source: the tool recovers the text and reports findings in it, but it cannot tell a quotation from a paragraph, so **every unit of PDF copy is treated as `authored`** and quoted material inside a PDF is screened rather than left alone. `line` addresses a visual line reconstructed from text positioning, counted continuously across the document, and is not a source line; a finding carries `pdfPage` in the JSON and SARIF output. Scanned or image-only documents, encrypted documents, and documents whose fonts have no recoverable encoding are refused with exit `2` and a reason — never reported as clean, and never partially read. Do not describe a refused PDF as checked, and do not offer OCR: the tool does not perform it. `--fix` refuses a PDF and every document container, so take those corrections from the report rather than from an applied rewrite. A `.docx` or `.odt` body is recovered paragraph by paragraph: `line` addresses the recovered paragraph in document order, text boxes, headers, footers, footnotes, endnotes and comments are never read, and a tracked deletion is excluded because struck copy is not user-visible. An encrypted document, a misnamed file and a container with no recoverable body text are refused with exit `2` and a reason — never reported as clean.

Code quality, accessibility, security and SEO findings are **audits**, not editorial rules. They run only when asked for with `--profile publishing`, `--profile accessibility` or `--profile security`, they are reported in their own section, and they never change the exit code.

`--report <path.pdf>` writes the review as a PDF and `--report <path.html>` as a single self-contained HTML page; both record the pre-fix state, carry every finding's rule source, profile, confidence, limitation and recommended action, and state that they are not verification of facts, legal opinion or United Nations endorsement. An extension the tool does not render is a refusal, not a silent fall-back.

`--glossary <file>` reports the reader's own terminology: a term on their `forbiddenTerms` list that appears in the copy, and a term on their `requiredTerms` list that appears nowhere in a scanned file. Report those findings as the reader's house terminology and never as a United Nations rule, do not record them in [rules/sources.json](rules/sources.json), and note that they are audit-lane and never move the exit code. `--fix` never rewrites a glossary term.

`--watch` re-scans on change for one person editing, resolves no exit code, and exits `130` on interrupt. Do not use it in continuous integration.

## Boundaries

Never use `--fix` without showing the user the target files first. `--fix` prints a `(proposed)` diff and writes nothing; `--fix --apply` writes and labels results `(applied)`. It is limited to deterministic replacements (British spelling, `per cent`, en-dash ranges, `the United States`, a doubled word, a space before punctuation and a missing space between sentences) in `.md`, `.markdown` and `.txt` files, and it refuses symbolic links, hard-linked files, PDFs and anything that is not a regular file. Review every resulting diff. It does not rewrite dates, terminology, claims or exclamation marks.

Exit codes: `0` no error-severity editorial findings, `1` error-severity editorial findings, `2` usage, configuration, scan or write failure. Audits never move the exit code. A run with no findings prints `No findings under the enabled, documented local rules.` — that is the whole meaning of a clean result, and it is the only clean wording to report to the user.

Configuration comes from [config/default.json](config/default.json) plus an optional project `.un-editorial.json`, or `--config <file>`. A `--profile` value is either a built-in audit name (`publishing`, `accessibility`, `security`), a bundled profile name (`un-secretariat-document`, `un-v1`, `un-geneva-web`, `generic-british-english`) or a path to an organisation profile JSON file merged over the bundled baseline in [config/profiles/un-v1.json](config/profiles/un-v1.json). Do not invent undocumented configuration keys; the maintained index of rule IDs is [rules/catalogue.json](rules/catalogue.json).

Suppress a single known-good case inside the copy span it belongs to, and record the reason in version control: `<!-- ue:ignore UE-SP001 -->`, `<!-- ue:ignore UE-SP* -->` or `<!-- ue:ignore all -->`. A suppression applies to its own paragraph only.

When `baseOrigin` is configured, canonical URLs are checked against its scheme, hostname and effective port. SRI results certify declaration syntax and required attributes, not whether a digest matches downloaded content.
