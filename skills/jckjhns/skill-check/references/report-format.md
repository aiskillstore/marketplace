# Report Format

## Contents

- [Report collapsing rules](#report-collapsing-rules) — always include, conditional sections, depth-specific visibility, minimal example
- [Full section reference](#full-section-reference)
  - [1. Header](#1-header)
  - [2. Summary card](#2-summary-card)
  - [3. File manifest](#3-file-manifest)
  - [4. Test results — Passed](#4-test-results--passed)
  - [5. Security findings](#5-security-findings)
  - [6. Eval regression results](#6-eval-regression-results)
  - [7. Test results — Failed](#7-test-results--failed)
  - [8. Test results — Warnings](#8-test-results--warnings)
  - [9. Mock files used](#9-mock-files-used)
  - [10. Best practices review](#10-best-practices-review)
  - [11. Improvement suggestions](#11-improvement-suggestions)
  - [12. Depth note](#12-depth-note)
- [Output format](#output-format)

---

SkillCheck reports should be clear, scannable, and actionable. The format adapts based on
depth level and what was actually found — a Quick Check on a simple skill should be concise,
not a 12-section skeleton full of "N/A" and "No findings."

---

## Report collapsing rules

The full report has 12 possible sections, but most reports should use far fewer. The
principle: **only include a section if it has something to say.** Empty sections add noise
and make the report harder to scan.

### Always include (every report)
- **Header** — always present, identifies the run
- **Summary card** — always present, gives the verdict at a glance
- **Improvement suggestions** — always present (even passing skills have recommendations)
- **Depth note** — always present, tells the user what wasn't tested

### Include when they have content
- **File manifest** — include if the skill has more than just SKILL.md. Skip for minimal
  skills (SKILL.md only) since the manifest would be a single row.
- **Test results — Passed** — include if there are passed tests to report. For Quick Check
  on a minimal skill this might only be 3-4 lines, which is fine.
- **Security findings** — include only if something was flagged (Warning or above). If the
  security review was clean, a single line in the passed tests section is enough:
  "S9: Security review — clean, no issues found ✓"
- **Eval regression results** — include only at Standard+ depth AND when evals exist. If
  no evals directory was found, mention it in one line in improvement suggestions rather
  than giving it a whole empty section.
- **Test results — Failed** — include only if there are failures. If everything passed,
  this section doesn't exist.
- **Test results — Warnings** — include only if there are warnings.
- **Mock files used** — include only at Standard+ depth when mock files were generated.
- **Best practices review** — always include at any depth. Even a Quick Check runs best
  practices. But if every check passed, collapse to a one-liner:
  "Best Practices: 22/22 — all checks passed ✓"

### Depth-specific section visibility

| Section                 | Quick | Standard | Deep |
|-------------------------|-------|----------|------|
| Header                  | ✓     | ✓        | ✓    |
| Summary card            | ✓     | ✓        | ✓    |
| File manifest           | if >1 file | if >1 file | ✓ |
| Passed tests            | ✓     | ✓        | ✓    |
| Security findings       | if flagged | if flagged | if flagged |
| Eval regression         | —     | if evals exist | if evals exist |
| Failed tests            | if any | if any   | if any |
| Warnings                | if any | if any   | if any |
| Mock files used         | —     | if generated | ✓ |
| Best practices          | ✓     | ✓        | ✓    |
| Improvement suggestions | ✓     | ✓        | ✓    |
| Depth note              | ✓     | ✓        | ✓    |

### Example: Minimal Quick Check report

A Quick Check on a simple SKILL.md-only skill with no issues would collapse to roughly:

```
# SkillCheck Report: my-skill
**Depth:** Quick | **Tested:** 2026-04-29 | **Files:** 1

╔══════════════════════════════════════╗
║  Static Tests:    5/5 passed  ✓      ║
║  Best Practices: 14/22        ⚠      ║
╠══════════════════════════════════════╣
║  Overall:  HEALTHY                   ║
╚══════════════════════════════════════╝

## Passed tests
- S1: Frontmatter completeness ✓
- S2: Constraint consistency ✓
- S3: Path validation ✓
- S4: Security review — clean ✓
- S5: Reference coherence (N/A — no references) ✓

## Best Practices Review
Score: 14/22
[... only flagged items shown ...]
⚠ BP-10: Description assertiveness — could be more specific
⚠ BP-17: No input/output examples
⚠ BP-22: No evals directory

## Recommendations
1. Add more trigger phrases to the description
2. Add an input/output example
3. Consider adding evals for regression testing

Quick Check — structural and best practices analysis only. Run Standard
for functional testing.
```

That's 5 sections instead of 12. Clean, scannable, and still useful.

---

## Full section reference

The sections below define the format for each section when it IS included. Remember: skip
any section that has nothing to report.

### 1. Header

```
# SkillCheck Report: [skill-name]
**Depth:** Quick / Standard / Deep
**Tested:** [date]
**Skill path:** [path/to/skill]
**Files analyzed:** [count]
```

For Quick Checks on simple skills, condense to a single line:
```
# SkillCheck Report: [skill-name]
**Depth:** Quick | **Tested:** [date] | **Files:** [count]
```

### 2. Summary card

Present as a clear visual block. Only include categories that were actually tested:

```
╔══════════════════════════════════════════╗
║  SkillCheck Report: [skill-name]         ║
╠══════════════════════════════════════════╣
║  Static Tests:     8/8  passed   ✓       ║
║  Script Tests:     3/4  passed   ⚠       ║
║  I/O Tests:        5/6  passed   ⚠       ║
║  Workflow Tests:   4/4  passed   ✓       ║
║  Trigger Tests:    9/10 passed   ⚠       ║
║  Edge Cases:       6/8  passed   ⚠       ║
║  Cross-ref Tests:  3/3  passed   ✓       ║
║  Security Review:  1 warning     ⚠       ║
║  Eval Regression:  4/4  passed   ✓       ║
╠══════════════════════════════════════════╣
║  Overall:          41/46  (89.1%)        ║
║  Verdict:  MOSTLY HEALTHY                ║
╚══════════════════════════════════════════╝
```

For Quick Checks with few categories, a smaller card is fine:

```
╔══════════════════════════════════════╗
║  Static Tests:    5/5 passed  ✓      ║
║  Best Practices: 14/17        ⚠      ║
╠══════════════════════════════════════╣
║  Overall:  HEALTHY                   ║
╚══════════════════════════════════════╝
```

**Verdicts:**
- **HEALTHY** (100%) — All tests pass. Skill looks solid.
- **MOSTLY HEALTHY** (80-99%) — Minor issues. Works but has rough edges.
- **NEEDS ATTENTION** (50-79%) — Significant issues. May fail for some users.
- **CRITICAL** (<50%) — Major problems. Needs substantial rework.

Optionally, when the tone of the conversation is casual, you can add flavour text
after the verdict: "Natural 20 — ship it", "Passed with minor scratches",
"Failed the check", or "Critical fail — back to the workshop." Only do this if
the user seems receptive to it — don't force it in professional contexts.

Use the checkmark (✓) for categories at 100%, warning (⚠) for anything below.

### 3. File manifest

A quick reference of what was found in the skill directory. Skip for minimal skills
(SKILL.md only) where the manifest would be a single trivial row.

```
## Skill inventory

| File | Category | Status |
|------|----------|--------|
| SKILL.md | Core | ✓ Analyzed |
| scripts/build_chart.py | Script | ✓ Tested |
| references/api-guide.md | Reference | ✓ Referenced |
| assets/old_logo.png | Asset | ⚠ Orphaned |
```

### 4. Test results — Passed

Keep passed tests brief. A one-liner per test is fine:

```
## Passed tests

- **S1** File existence: All 7 referenced files present ✓
- **S2** Script syntax: scripts/build_chart.py valid Python ✓
- **S3** Dependencies: pandas, matplotlib, openpyxl all available ✓
- **IO1** Happy path: CSV → PPTX conversion produced valid 5-slide deck ✓
- **W1** Step ordering: All 4 steps in correct dependency order ✓
```

For reports with many passed tests (15+), group by category to keep it scannable rather
than listing every test individually.

### 5. Security findings

**Only include this section if the security review flagged something at Warning severity
or above.** A clean security review is reported as a single passed test in section 4.

Group by severity:

```
## Security findings

### Critical
None found ✓

### Warnings
- **SEC-W1**: `scripts/fetch_data.py` line 42 — downloads from a URL constructed
  from user input without validation. Consider using an allowlist of domains.

### Info
- **SEC-I1**: `scripts/build_chart.py` uses `subprocess.run()` — appears properly
  sanitized (arguments passed as list, no shell=True). No action needed.
```

If any Critical security findings exist, flag them at the top of the report with a
prominent banner:

```
⚠️  CRITICAL SECURITY FINDING — Review before distributing this skill
```

### 6. Eval regression results

**Only include at Standard+ depth, and only when evals exist.** If no evals directory
was found, don't create an empty section — mention it in recommendations instead.

```
## Eval regression

Found 4 existing test cases in evals/evals.json.

| Eval ID | Prompt (truncated)           | Assertions | Result |
|---------|------------------------------|------------|--------|
| 1       | "Generate a chart from..."   | 3/3 passed | ✓      |
| 2       | "Convert the CSV to..."      | 2/2 passed | ✓      |
| 3       | "Handle missing columns..."  | 1/2 passed | ⚠      |
| 4       | "Produce a summary..."       | 4/4 passed | ✓      |
```

If any eval failed, this is a significant finding — the skill has regressed from its
author's expectations. Detail which assertions failed and why.

### 7. Test results — Failed

**Only include if there are failures.** Give each failure its own detailed block:

```
## Failed tests

### ⚠ S4: Script error handling — scripts/build_chart.py

**What was tested:** Running the script with no arguments to check for graceful error handling.

**What happened:** The script threw an unhandled `IndexError` on line 23:
`IndexError: list index out of range`

**Why it matters:** If a user forgets to provide an input file, the skill will crash with
a confusing Python traceback instead of a helpful error message.

**Suggested fix:** Add argument validation at the top of the script:
```python
if len(sys.argv) < 2:
    print("Usage: build_chart.py <input.csv> [output.png]", file=sys.stderr)
    sys.exit(1)
```
```

### 8. Test results — Warnings

**Only include if there are warnings.** For things that didn't fail but are worth noting:

```
## Warnings

- **W-1**: `assets/old_logo.png` exists but is never referenced — orphaned file?
- **W-2**: The skill description is only 15 words — may not trigger reliably
- **W-3**: `scripts/build_chart.py` has no comments — maintainability concern
```

### 9. Mock files used

**Only include at Standard+ depth when mock files were generated.** Skip for Quick Check
(no mocks generated) or when the skill has no I/O contracts to test.

```
## Mock files generated

| File | Type | Purpose | Spec matched |
|------|------|---------|--------------|
| mock_sales.csv | CSV | Input for I/O test | columns: name, date, amount ✓ |
| mock_report.docx | DOCX | Input for conversion test | 3 sections, 1 table ✓ |
```

### 10. Best practices review

Always include, but adapt the format to the results:

**If all checks passed** — collapse to one line:
```
Best Practices: 22/22 — all checks passed ✓
```

**If some checks flagged** — show the score and only the flagged items (don't list every
passing check unless the user asks for the full breakdown):

```
## Best Practices Review

Score: 14/22

⚠ BP-7:  Reference file quality — references/api-guide.md is 420 lines with no TOC
⚠ BP-10: Description assertiveness — could list more trigger phrases
⚠ BP-13: Explain the why — 4 instances of MUST/ALWAYS without justification
```

**If the user asks for the full breakdown** or the score is below 17/22, show every check:

```
## Best Practices Review

Score: 15/22

✓ BP-1:  Name format — valid
✓ BP-2:  Description length — within limits
✓ BP-3:  Portability fields (N/A)
✓ BP-4:  Standard directory layout
✓ BP-5:  SKILL.md under 500 lines (287 lines)
✓ BP-6:  Progressive disclosure — references used appropriately
⚠ BP-7:  Reference file quality — references/api-guide.md is 420 lines with no TOC
...
```

Mark checks as N/A when they don't apply. N/A checks count as passed.

### 11. Improvement suggestions

Always include. Prioritized, actionable list:

```
## Recommendations

### Critical (will break for users)
1. Add argument validation to `scripts/build_chart.py` — currently crashes on missing input

### Important (reduces quality)
2. Add error handling for malformed CSV input — skill silently produces empty output
3. Improve skill description — current 15-word description may fail to trigger

### Nice to have (polish)
4. Remove orphaned `assets/old_logo.png`
5. Add inline comments to `scripts/build_chart.py`
6. Consider adding example input/output files to help users understand expectations
```

If there are no Critical or Important items, collapse those headers:

```
## Recommendations

No critical or important issues found.

### Nice to have (polish)
1. Consider adding evals for regression testing
2. Remove orphaned `assets/old_logo.png`
```

### 12. Depth note

Always end with context about what level of testing was done. Keep it to one or two lines:

**Quick Check:**
> "Quick Check — structural, security, and best practices analysis only. Run **Standard**
> for functional testing or **Deep** for edge-case coverage."

**Standard Check:**
> "Standard Check — scripts and happy-path I/O tested. Run **Deep** for edge cases,
> stress testing, and triggering analysis."

**Deep Check:**
> "Deep Check — all aspects tested including edge cases, error recovery, and triggering."

---

## Output format

Present the report directly in the conversation. If the user is likely to want a downloadable
version, also save it as a markdown file to the outputs directory:

```
/mnt/user-data/outputs/skillcheck-[skill-name]-report.md
```
