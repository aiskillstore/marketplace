---
name: skill-check
description: >
  Comprehensive testing and validation of Claude skills. Use this skill whenever the user wants to
  test, validate, audit, or quality-check a skill — whether they say "test my skill", "check this
  skill works", "validate my skill", "run skill-check", or anything similar. Also trigger when the
  user asks things like "does this skill handle edge cases?", "what's wrong with my skill?",
  "find problems in my skill", "is this skill secure?", "does my skill follow best practices?",
  or "how robust is this skill?". Even if they just say "check this" and point at a skill
  directory, use skill-check. This skill covers triggering tests, output quality tests, input/output
  contract validation, script execution checks, security review, best practices auditing, and
  multi-file skill analysis.
  Do NOT use for creating or editing skills (that's skill-creator) — skill-check is purely about
  testing and reporting on existing skills.
license: MIT
allowed-tools: Bash Read Write
---

# SkillCheck — Comprehensive Skill Testing

SkillCheck audits an entire skill directory, understands every moving part, and generates targeted
tests to verify the skill works as advertised. It doesn't just check "does it roughly work" — it
tests every aspect: triggering, input handling, output quality, script correctness, security,
best practices, and resource integrity.

---

## How it works

Three phases: **Discover → Test → Report.** Discovery is always required. Testing depth
depends on what the user wants. Reporting adapts to what was found.

| Depth         | What it covers                                                            |
|---------------|---------------------------------------------------------------------------|
| **Quick**     | Static analysis — structure, syntax, integrity, security, best practices  |
| **Standard**  | Static + script execution + happy-path I/O + eval regression              |
| **Deep**      | Everything — edge cases, mock files, e2e workflows, stress                |

If the user doesn't specify, default to **Standard** — it catches real functional problems
without the time investment of Deep. If they seem in a hurry, go **Quick**. If they mention
thoroughness, edge cases, or "test everything", go **Deep**.

For a worked example of a Standard Check from start to finish, see `references/example-run.md`.

---

## Gotchas

- The `evals.json` format must match the skill-creator schema exactly (see
  `references/eval-schema.md`). Don't invent a new format — compatibility with
  skill-creator's benchmarking tools is the whole point.
- Mock file generation for binary formats (DOCX, XLSX, PPTX, PDF, images) requires
  third-party Python packages that may not be installed. Always check availability
  before generating and fall back to text-based equivalents if installation fails.
  See `references/mock-files.md` for the dependency list.
- Cross-reference mismatches between SKILL.md and scripts are often the root cause
  of multiple downstream test failures (script execution fails, eval regression fails,
  I/O tests fail — all for the same reason). Identify and report the root cause
  rather than listing each symptom as a separate unrelated failure.
- Best practice scores are advisory and reported separately — do not add them to the
  main pass/fail verdict percentage. A skill can be functionally perfect but
  structurally messy, and the report should reflect that distinction.
- Security review runs before script execution for a reason — if Critical security
  issues are found in scripts, warn the user before executing them at Standard or
  Deep depth. Don't silently run code you've just flagged as dangerous.
- Incomplete skills (TODOs, stubs, placeholder text) need a progress report, not a
  wall of failures. It's easy to mechanically run the standard flow and produce 15
  failures that all say "this doesn't exist yet" — that's not useful. Read
  `references/incomplete-skills.md` and reframe.
- On Claude.ai without subagents, end-to-end tests run sequentially in shared context.
  This means earlier test results can influence later tests — an agent that just
  discovered a cross-reference bug might "know" to use the correct arguments on the
  next test. Keep this in mind when interpreting e2e results.
- The frontmatter `name` field must match the parent directory name per the Agent
  Skills spec. This is easy to miss because many platforms will still load the skill
  with a mismatch — but others won't, making it a silent portability bug.
- Report sections should be collapsed when empty — a Quick Check on a minimal skill
  should produce 5 sections, not a 12-section skeleton full of "N/A".
  See `references/report-format.md` for collapsing rules.

---

## Phase 1: Discover

Find the skill, scan it, understand what it contains, and decide how to test it.

### Find the skill

If the user gives a specific path, use it. If not, read `references/finding-the-skill.md`
to locate the skill from conversation context or common locations.

### Scan the directory

Read the entire skill directory, not just SKILL.md. Categorize every file:

| Category       | What to look for                                                       |
|----------------|------------------------------------------------------------------------|
| **Core**       | `SKILL.md` — the main instructions file                                |
| **Scripts**    | `scripts/` — executable code (Python, Bash, JS, etc.)                  |
| **References** | `references/` — documentation loaded into context as needed            |
| **Assets**     | `assets/` — templates, icons, fonts, images used in output             |
| **Examples**   | Any example input/output files, sample data                            |
| **Config**     | Package files, requirements, dependency lists                          |
| **Evals**      | `evals/` — existing test cases (if any)                                |

Record a manifest — you'll reference this throughout testing.

### Parse the SKILL.md

Extract from the frontmatter and body:

- **Name and description** — what it does and when it should trigger
- **Declared inputs** — file types, formats, schemas (pay close attention to explicitly
  named extensions, column names, data structures)
- **Declared outputs** — file types, formats, target paths, expected structures
- **Step-by-step workflows** — numbered or ordered procedures
- **Tool/dependency requirements** — libraries, CLIs, external tools
- **Conditional logic** — branching paths
- **Constraints and rules** — ALWAYS, NEVER, MUST directives
- **References to bundled files** — when to read other files in the skill
- **Script invocations** — exact commands including arguments and flags

### Analyze supporting files

For each non-SKILL.md file:

- **Scripts**: Read the code. Identify arguments, outputs, hardcoded paths, error handling,
  and dependencies. Pay special attention to argument parsing — you'll compare this against
  how SKILL.md invokes the script.
- **References**: Skim for structure and purpose. Note if SKILL.md actually references them.
- **Assets**: Note file types and whether they're referenced. Assets will be validated for
  integrity during testing — see `references/quick-check.md`.
- **Examples**: Identify as input examples, output examples, or both — gold for test generation.
- **Evals**: Read `evals.json` if present. See `references/eval-schema.md` for the format.

### Present findings

Show the user: the file manifest, what the skill claims to do, declared inputs/outputs,
immediate red flags, and whether evals were found.

**If the skill appears incomplete** (TODOs, placeholder text, missing referenced files,
stub scripts), read `references/incomplete-skills.md` and adjust your approach — reframe
as a progress report rather than a failure report.

Then ask which depth level they'd like (if they haven't already said).

---

## Phase 2: Test

Read the reference file for the chosen depth level. It defines exactly which tests to run,
in what order, and how to evaluate results:

- **Quick:** `references/quick-check.md` — static integrity, asset validation, SKILL.md
  quality, cross-reference consistency, multi-skill dependencies, security review, and
  22 best practice checks (`references/best-practices.md`)
- **Standard:** `references/standard-check.md` — everything in Quick, plus eval regression
  (`references/eval-schema.md`), script execution with mock inputs (`references/mock-files.md`),
  happy-path I/O contract validation, and workflow tests
- **Deep:** `references/deep-check.md` — everything in Standard, plus edge case inputs,
  end-to-end workflow simulation, triggering analysis, error recovery, and script robustness

### Test plan (Standard and Deep only)

For Standard and Deep checks, present the test plan to the user before executing — they may
know about domain-specific edge cases worth adding, or tests that aren't relevant. For Quick
checks on simple skills, skip straight to running the tests.

### Execution order

1. **Static tests first** — fast, free, and may reveal issues that make later tests
   pointless or unsafe (security problems, broken cross-references)
2. **Eval regression next** — the author's own tests are the most authoritative baseline
3. **Script tests** — run with mock inputs, verify outputs
4. **I/O contract tests** — generate mock files, run the skill, check results
5. **End-to-end tests last** — slowest and most context-heavy; earlier tests may have
   already uncovered the issues they'd find

For each test, record: test ID, what was tested, pass/fail, evidence, and notes. Evidence
is critical — it lets the user verify your judgment and makes the report actionable.

**On Claude.ai (no subagents):** Run tests sequentially. Save outputs to a workspace
directory so the user can inspect them after the report.

**With subagents:** Static tests first, then dynamic tests in parallel. Use independent
subagents for end-to-end tests — shared context lets earlier tests influence later ones,
masking issues that would appear in a fresh invocation.

---

## Phase 3: Report

Read `references/report-format.md` for the full template and collapsing rules. Key elements:

- **Summary card** with pass/fail counts and verdict (HEALTHY / MOSTLY HEALTHY /
  NEEDS ATTENTION / CRITICAL)
- **Failed test details** — what was tested, what happened, why it matters, suggested fix
- **Security findings** — dedicated section if anything flagged, prominent banner for
  Critical findings
- **Best practices score** — separate from the main verdict
- **Improvement suggestions** — prioritized: Critical → Important → Nice to have

Only include report sections that have content. See the collapsing rules in
`references/report-format.md` for which sections to skip at each depth level.
