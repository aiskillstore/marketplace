# Example Run: Standard Check on "csv-to-chart"

## Contents

- [The skill under test](#the-skill-under-test)
- [Phase 1: Discover](#phase-1-discover)
- [Phase 2: Test](#phase-2-test) — Test plan, Execution
- [Phase 3: Report](#phase-3-report) — Security findings, Eval regression, Failed tests, Warnings, Best practices, Mock files, Recommendations

---

This is a complete worked example of SkillCheck running a Standard Check on a fictional
skill called `csv-to-chart`. The skill converts CSV data into chart images. It has a few
issues baked in to show how SkillCheck catches and reports them.

---

## The skill under test

Here's the directory structure of `csv-to-chart`:

```
csv-to-chart/
├── SKILL.md
├── scripts/
│   └── generate_chart.py
├── references/
│   └── chart-styles.md
├── assets/
│   └── company_logo.png
└── evals/
    ├── evals.json
    └── files/
        └── sample_sales.csv
```

And here's the SKILL.md:

```yaml
---
name: csv-chart
description: >
  Generates charts from CSV data. Use when the user wants to visualize CSV data
  as a bar chart, line chart, or pie chart.
---
```

```markdown
# CSV to Chart

Generate professional charts from CSV files.

## Workflow

1. Read the user's CSV file from /mnt/user-data/uploads/
2. Identify the columns to plot (ask the user if ambiguous)
3. Read references/chart-styles.md for styling guidelines
4. Run the chart generation script:
   `python3 scripts/generate_chart.py --input <csv-path> --output <chart-path> --type <chart-type>`
5. Save the chart to /mnt/user-data/outputs/
6. ALWAYS add the company logo to the chart
7. NEVER use red as a primary chart color

## Supported chart types
- Bar chart (default)
- Line chart
- Pie chart
```

The script `generate_chart.py` accepts `--file` (not `--input`), `--out` (not `--output`),
and `--chart-type` (not `--type`). This mismatch is intentional for the example.

---

## Phase 1: Discover

SkillCheck reads the full directory and builds an inventory.

> **File manifest:**
>
> | File | Category | Purpose |
> |------|----------|---------|
> | SKILL.md | Core | Main instructions |
> | scripts/generate_chart.py | Script | Generates chart images from CSV data |
> | references/chart-styles.md | Reference | Styling guidelines for charts |
> | assets/company_logo.png | Asset | Company logo to overlay on charts |
> | evals/evals.json | Evals | 2 existing test cases |
> | evals/files/sample_sales.csv | Evals | Sample input for eval 1 |
>
> **What the skill claims to do:** Convert CSV data into bar, line, or pie charts with
> company branding and specific color rules.
>
> **Declared inputs:** CSV files from /mnt/user-data/uploads/
>
> **Declared outputs:** Chart images saved to /mnt/user-data/outputs/
>
> **Existing evals found:** Yes — 2 test cases in evals/evals.json
>
> **Immediate red flags:** The SKILL.md frontmatter says `name: csv-chart` but the
> directory is called `csv-to-chart` — not necessarily a problem but worth noting.

The user chose Standard depth (or didn't specify, so it defaulted).

---

## Phase 2: Test

SkillCheck extracts testable claims from the discovery findings, then builds a test plan.

**Script invocations found in SKILL.md:**
- `python3 scripts/generate_chart.py --input <csv-path> --output <chart-path> --type <chart-type>`

**Script's actual argument parser (from reading the code):**
- `--file` (required) — input CSV path
- `--out` (required) — output image path
- `--chart-type` (optional, default "bar") — one of bar, line, pie

**Cross-reference mismatch detected:**
- SKILL.md passes `--input` but script expects `--file`
- SKILL.md passes `--output` but script expects `--out`
- SKILL.md passes `--type` but script expects `--chart-type`

**I/O contracts:**
- Input: CSV file with plottable columns
- Output: Chart image (PNG implied by script), saved to /mnt/user-data/outputs/

**Constraints:**
- ALWAYS add company logo
- NEVER use red as primary color

**Existing evals:**
- Eval 1: "Create a bar chart from the sales data" (with sample_sales.csv)
- Eval 2: "Make a pie chart showing market share" (no input file)

---

### Test plan

SkillCheck presents the plan before executing:

> ## SkillCheck Test Plan: csv-chart
> ## Depth: Standard
>
> ### Static Tests (9 tests)
> - S1: File existence — all referenced files present
> - S2: Orphan detection — check for unreferenced files
> - S3: Script syntax — generate_chart.py parses as valid Python
> - S4: Dependencies — check imports (matplotlib, pandas, etc.)
> - S5: Frontmatter completeness — name and description present
> - S6: Constraint consistency — ALWAYS/NEVER rules don't contradict
> - S7: Cross-reference consistency — SKILL.md invocation vs script args
> - S8: Inter-file references — all referenced paths exist
> - S9: Security review — scan script for red flags
>
> ### Best Practices (22 checks)
> - BP-1 through BP-22 (see references/best-practices.md)
>
> ### Eval Regression (2 tests)
> - ER-1: "Create a bar chart from the sales data" (with sample_sales.csv)
> - ER-2: "Make a pie chart showing market share" (no input file)
>
> ### Script Execution (3 tests)
> - SE-1: Run generate_chart.py with mock CSV, verify output
> - SE-2: Run generate_chart.py without required args, check graceful failure
> - SE-3: Run generate_chart.py with correct args (using script's actual flags)
>
> ### I/O Contract Tests (2 tests)
> - IO-1: Happy path — provide CSV with plottable columns, expect PNG output
> - IO-2: Verify output lands in /mnt/user-data/outputs/
>
> ### Workflow Tests (3 tests)
> - W-1: Step completability — Python available, script exists, paths valid
> - W-2: Step ordering — no step depends on a later step's output
> - W-3: Conditional coverage — test the default (bar chart) branch
>
> **Total: 19 tests + 22 best practice checks**
>
> Want to add, remove, or tweak anything before I run these?

The user confirms, and SkillCheck proceeds.

### Execution

#### Static tests

```
S1: File existence                    PASS
    All 5 referenced files exist.

S2: Orphan detection                  PASS
    No orphaned files found.

S3: Script syntax                     PASS
    generate_chart.py parses as valid Python.

S4: Dependencies                      PASS
    matplotlib, pandas, Pillow all available.

S5: Frontmatter completeness          PASS
    name: "csv-chart", description: present (31 words).

S6: Constraint consistency            PASS
    2 constraints found (ALWAYS logo, NEVER red). No contradictions.

S7: Cross-reference consistency       FAIL
    SKILL.md invokes: --input, --output, --type
    Script expects:   --file, --out, --chart-type
    All three argument names are wrong.

S8: Inter-file references             PASS
    references/chart-styles.md exists, assets/company_logo.png exists.

S9: Security review                   PASS (clean)
    No critical or warning patterns found.
    Info: script uses subprocess for ImageMagick logo overlay — appears sanitized.
```

#### Best practices

```
BP-1:  Name format                          PASS
BP-2:  Description length                   PASS
BP-3:  Portability fields                   PASS    no env dependencies
BP-4:  Standard directory layout             PASS
BP-5:  SKILL.md line count (42 lines)        PASS
BP-6:  Progressive disclosure                PASS    references used for styling detail
BP-7:  Reference file quality                PASS    chart-styles.md is 85 lines, no TOC needed
BP-8:  Domain variant organization           N/A     single domain
BP-9:  Description completeness              WARN    no "when NOT to use" guidance
BP-10: Description assertiveness             WARN    very short, could list more trigger phrases
BP-11: Trigger info placement                PASS    no trigger info buried in body
BP-12: Imperative form                       PASS
BP-13: Explain the why                       WARN    "NEVER use red" — no explanation why
BP-14: Instruction clarity                   PASS
BP-15: Defaults over menus                   PASS
BP-16: Generality                            PASS
BP-17: Examples included                     WARN    no input/output examples in SKILL.md
BP-18: Gotchas section                       N/A     simple skill
BP-19: Context window efficiency             PASS    minimal, no bloat
BP-20: Script bundling                       PASS    chart generation is pre-built
BP-21: Error handling guidance               WARN    no guidance on what to do if script fails
BP-22: Eval set present                      PASS

Score: 17/22 (5 warnings, N/A counted as pass)
```

#### Eval regression

```
ER-1: "Create a bar chart from the sales data"     FAIL
      Eval has input file: evals/files/sample_sales.csv — file exists.
      Attempted to follow SKILL.md workflow.
      Step 4 failed: script invocation used --input (from SKILL.md) but
      script expects --file. Script exited with error:
      "unrecognized arguments: --input"

      Note: This failure is a consequence of the cross-reference mismatch
      found in S7. The skill's own eval cannot pass because SKILL.md tells
      Claude to use the wrong argument names.

ER-2: "Make a pie chart showing market share"       SKIP
      Eval references no input file, but the skill requires a CSV.
      eval_metadata says expected_output describes a pie chart, but no
      data is provided to chart. This eval appears incomplete — it needs
      a sample CSV in evals/files/ to be runnable.
```

#### Script execution

```
SE-1: Run with mock CSV (using SKILL.md's flags)    FAIL
      Same cross-reference issue as ER-1. Script rejects --input.

SE-2: Run without required args                     PASS
      Script prints: "Error: --file is required" and exits with code 1.
      Graceful failure with helpful message.

SE-3: Run with correct flags (--file, --out)         PASS
      Generated valid PNG chart (bar chart, 800x600).
      Output file is 45KB and parseable as PNG.
```

#### I/O contract tests

```
IO-1: Happy path (using script's actual flags)       PASS
      Provided mock CSV with columns: month, revenue, expenses.
      Script produced a valid bar chart PNG with labeled axes.

IO-2: Output location                                PASS
      Following the workflow (with corrected flags), output was
      saved to /mnt/user-data/outputs/chart.png as expected.
```

#### Workflow tests

```
W-1: Step completability                             PASS
     Python3 available, script exists, paths valid.

W-2: Step ordering                                   PASS
     No step depends on a later step's output.
     Step 3 (read styling) correctly comes before step 4 (generate).

W-3: Primary branch (bar chart)                      PASS
     Default bar chart generation works end-to-end.
```

---

## Phase 3: Report

```
╔════════════════════════════════════════════╗
║  SkillCheck Report: csv-chart              ║
╠════════════════════════════════════════════╣
║  Static Tests:     8/9   passed    ⚠       ║
║  Eval Regression:  0/1   passed    ⚠       ║
║  Script Tests:     2/3   passed    ⚠       ║
║  I/O Tests:        2/2   passed    ✓       ║
║  Workflow Tests:   3/3   passed    ✓       ║
╠════════════════════════════════════════════╣
║  Overall:          15/18  (83.3%)          ║
║  Verdict:  MOSTLY HEALTHY                  ║
╚════════════════════════════════════════════╝

Best Practices: 17/22 (5 warnings)
```

### Security findings

No critical or warning findings. One info-level note: `generate_chart.py` uses `subprocess`
for ImageMagick logo overlay — appears properly sanitized (arguments passed as list, no
shell=True).

### Eval regression

Found 2 existing test cases in evals/evals.json.

| Eval ID | Prompt (truncated)                    | Result |
|---------|---------------------------------------|--------|
| 1       | "Create a bar chart from the sales…"  | ⚠ FAIL |
| 2       | "Make a pie chart showing market…"    | SKIP   |

**ER-1 failed** because SKILL.md tells Claude to invoke the script with `--input`, `--output`,
`--type`, but the script expects `--file`, `--out`, `--chart-type`. This means the skill
cannot work as written — Claude will always pass the wrong flags.

**ER-2 was skipped** because the eval defines no input files, but the skill requires a CSV
to chart. This eval is incomplete.

### Failed tests

#### ⚠ S7: Cross-reference consistency

**What was tested:** Whether SKILL.md's script invocation matches what `generate_chart.py`
actually accepts.

**What happened:** All three argument names are wrong:
- SKILL.md uses `--input` → script expects `--file`
- SKILL.md uses `--output` → script expects `--out`
- SKILL.md uses `--type` → script expects `--chart-type`

**Why it matters:** This is a blocking issue. Every time Claude follows the SKILL.md
instructions to run the script, it will fail. The skill is non-functional as written.

**Suggested fix:** Update SKILL.md step 4 to:
```
python3 scripts/generate_chart.py --file <csv-path> --out <chart-path> --chart-type <chart-type>
```

#### ⚠ SE-1: Script execution with SKILL.md flags

**What was tested:** Running the script exactly as SKILL.md instructs.

**What happened:** Script rejected the arguments with "unrecognized arguments: --input"
and exited with code 2.

**Why it matters:** Same root cause as S7. Confirms the mismatch causes a real failure,
not just a cosmetic inconsistency.

**Suggested fix:** Same as S7 — fix the argument names in SKILL.md.

#### ⚠ ER-1: Eval regression — bar chart generation

**What was tested:** The skill author's own test case for bar chart generation.

**What happened:** Failed due to the same argument mismatch. The skill cannot pass its
own eval.

**Why it matters:** This is a regression (or the skill was never tested after the script
was last modified). The author's own expectations are unmet.

**Suggested fix:** Fix the argument names in SKILL.md (same root cause as S7 and SE-1).

### Warnings

- ER-2 was skipped because it has no input file — consider adding a sample CSV to
  evals/files/ so it can run.

### Best practices review

```
Score: 17/22

✓ BP-1:  Name format — valid
✓ BP-2:  Description length — within limits
✓ BP-3:  Portability fields (N/A)
✓ BP-4:  Standard directory layout
✓ BP-5:  SKILL.md under 500 lines (42 lines)
✓ BP-6:  Progressive disclosure
✓ BP-7:  Reference file quality
✓ BP-8:  Domain variant organization (N/A)
⚠ BP-9:  Description completeness — missing "when NOT to use" guidance
⚠ BP-10: Description assertiveness — consider adding trigger phrases like
         "plot my data", "visualize this spreadsheet", "graph these numbers"
✓ BP-11: Trigger info placement
✓ BP-12: Imperative form
⚠ BP-13: Explain the why — "NEVER use red as a primary chart color" has no
         explanation. Is it a brand guideline? An accessibility concern?
✓ BP-14: Instruction clarity
✓ BP-15: Defaults over menus
✓ BP-16: Generality
⚠ BP-17: Examples included — no input/output examples showing what a CSV
         should look like or what the resulting chart looks like
✓ BP-18: Gotchas section (N/A)
✓ BP-19: Context window efficiency
✓ BP-20: Script bundling
⚠ BP-21: Error handling guidance — no instruction for what Claude should do
         if the script fails or the CSV is malformed
✓ BP-22: Eval set present
```

### Mock files generated

| File | Type | Purpose | Spec matched |
|------|------|---------|--------------|
| mock_data.csv | CSV | Script and I/O testing | 3 columns (month, revenue, expenses), 10 rows ✓ |

### Recommendations

#### Critical (will break for users)
1. **Fix script argument names in SKILL.md** — The skill is currently non-functional
   because SKILL.md uses `--input`/`--output`/`--type` but the script expects
   `--file`/`--out`/`--chart-type`. This is the single highest priority fix.

#### Important (reduces quality)
2. **Add error handling guidance** — Tell Claude what to do if the script fails or the
   CSV doesn't have plottable numeric columns.
3. **Improve the skill description** — Add "when NOT to use" guidance and more trigger
   phrases to improve activation reliability.
4. **Fix eval 2** — Add a sample CSV file so the pie chart eval can actually run.
5. **Explain the "no red" constraint** — Why? Brand guidelines? Accessibility? Claude
   can apply the rule more intelligently if it understands the reasoning.

#### Nice to have (polish)
6. Add an input/output example to SKILL.md showing a sample CSV and the resulting chart.
7. Consider adding the name mismatch note — skill directory is `csv-to-chart` but
   frontmatter name is `csv-chart`.

---

This was a Standard Check. Run Deep for edge cases (malformed CSVs, huge datasets, empty
files), stress testing, and triggering analysis.
