# Eval Schema Reference

SkillCheck consumes the same `evals.json` schema that the skill-creator produces. This
reference documents the exact format SkillCheck expects and how it processes each field
during testing.

---

## evals.json

Located at `evals/evals.json` within the skill directory. This is the primary eval file
that SkillCheck looks for.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Convert this CSV to a presentation with one slide per row",
      "expected_output": "A .pptx file with a title slide and one content slide per data row",
      "files": ["evals/files/sample_data.csv"],
      "expectations": [
        "Output is a valid .pptx file",
        "First slide is a title slide",
        "Number of content slides matches number of CSV rows",
        "Each slide contains the data from its corresponding row"
      ]
    },
    {
      "id": 2,
      "prompt": "Generate a chart from the sales data",
      "expected_output": "A PNG chart showing sales over time",
      "files": ["evals/files/sales.csv"],
      "expectations": [
        "Output is a valid PNG image",
        "Chart has labeled axes",
        "X-axis represents time periods",
        "Y-axis represents sales values"
      ]
    }
  ]
}
```

### Field reference

**Top level:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skill_name` | string | Yes | Must match the skill's `name` in SKILL.md frontmatter. SkillCheck validates this. |
| `evals` | array | Yes | List of eval objects. Must contain at least one. |

**Each eval object:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique identifier. SkillCheck uses this to label results (ER-1, ER-2, etc.). |
| `prompt` | string | Yes | The task prompt to execute — what a real user would type. This is what SkillCheck feeds to the skill during regression testing. |
| `expected_output` | string | Yes | Human-readable description of what success looks like. Used for qualitative assessment when expectations are too vague or absent. |
| `files` | array of strings | No | Input files required for this eval, as paths relative to the skill root. SkillCheck checks these files exist before running the eval. If missing, the eval is skipped with an error. |
| `expectations` | array of strings | No | Verifiable statements about the output. Each should be a concrete, assessable claim. SkillCheck evaluates these as assertions. |

---

## How SkillCheck processes evals

### Step 1: Validation

Before running any evals, SkillCheck validates the file:

1. **Schema check** — Is it valid JSON? Does it have `skill_name` and `evals`?
2. **Name match** — Does `skill_name` match the SKILL.md frontmatter `name`?
3. **ID uniqueness** — Are all eval IDs unique?
4. **Required fields** — Does every eval have `id`, `prompt`, and `expected_output`?
5. **File existence** — For each eval with `files`, do the referenced files actually exist
   at the specified paths relative to the skill root?

Any validation failure is reported but doesn't prevent other valid evals from running.

### Step 2: Execution

For each eval, SkillCheck:

1. Sets up the test environment — copies any referenced input files to the workspace
2. Reads the skill's SKILL.md (simulating what Claude would see when the skill triggers)
3. Executes the `prompt` as if a user typed it, following the skill's instructions
4. Saves all outputs to `skillcheck-workspace/eval-regression/eval-<id>/`

### Step 3: Assertion checking

For each expectation string, SkillCheck determines the best way to verify it:

**Programmatic checks** (preferred when possible):
- "Output is a valid .pptx file" → Check file exists and is parseable
- "Number of content slides matches number of CSV rows" → Count slides, count rows, compare
- "File is saved to /mnt/user-data/outputs/" → Check path
- "Output contains the string 'Summary'" → Search file content

**Inspection-based checks** (when programmatic isn't feasible):
- "Chart has labeled axes" → Render/open the image and evaluate visually
- "Each slide contains the data from its corresponding row" → Parse slides and compare
- "The tone is professional" → Subjective assessment with reasoning

For each assertion, SkillCheck records:
- `text`: The expectation string
- `passed`: boolean
- `evidence`: What was observed that supports the pass/fail judgment

This matches the `grading.json` format from the skill-creator ecosystem.

### Step 4: Reporting

Results appear in the "Eval Regression" section of the report. See `references/report-format.md`
section 6 for the exact format.

---

## Input files

Eval input files should be stored in `evals/files/` within the skill directory:

```
my-skill/
├── evals/
│   ├── evals.json
│   └── files/
│       ├── sample_data.csv
│       ├── test_document.docx
│       └── example_input.json
```

File paths in `evals.json` are relative to the skill root, so `evals/files/sample_data.csv`
resolves to `<skill-root>/evals/files/sample_data.csv`.

SkillCheck supports any file type Claude can work with as eval input: CSV, JSON, TXT, MD,
HTML, XML, XLSX, DOCX, PPTX, PDF, PNG, JPG, WEBP, GIF, SVG, ZIP, and code files.

---

## Writing good expectations

Expectations are the most important part of an eval — they determine what SkillCheck actually
checks. Good expectations are:

**Specific and verifiable:**
- Good: "Output is a valid .pptx file with exactly 5 slides"
- Bad: "Output is a nice presentation"

**Independent:**
- Good: Each expectation tests one thing
- Bad: "Output is a valid PDF and contains a table with 3 columns and a chart"

**Covering different aspects:**
- Output format (is it the right file type?)
- Output structure (does it have the right sections/slides/columns?)
- Output content (does it contain the expected data?)
- Output location (is it saved to the right place?)
- Error handling (does it fail gracefully on bad input?)

**Example of a well-written eval:**

```json
{
  "id": 3,
  "prompt": "Convert the markdown report into a Word document with a table of contents",
  "expected_output": "A .docx file with table of contents, all sections preserved, and consistent formatting",
  "files": ["evals/files/quarterly_report.md"],
  "expectations": [
    "Output is a valid .docx file",
    "Document contains a table of contents",
    "All markdown headings are preserved as document headings",
    "All markdown tables are converted to Word tables",
    "File is saved to /mnt/user-data/outputs/",
    "Document has consistent font and heading styles throughout"
  ]
}
```

---

## Compatibility with skill-creator

SkillCheck's eval format is identical to what skill-creator produces. This means:

- Evals created during skill development work as-is for SkillCheck regression testing
- SkillCheck-generated evals (when it outputs its own evals.json — see task 3 TODO) use the
  same format, so they're compatible with skill-creator's benchmarking tools
- The grading output format (`text`, `passed`, `evidence`) matches what skill-creator's
  eval-viewer expects

If a skill was built with skill-creator, its evals should "just work" with SkillCheck.
If they don't, that's a bug in SkillCheck.
