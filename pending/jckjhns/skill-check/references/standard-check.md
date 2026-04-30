# Standard Check

The default depth level. Includes everything from Quick Check plus actual script execution,
happy-path I/O contract validation, existing eval regression, and basic workflow testing. This is
the sweet spot for most skills — catches real functional problems without spending ages on edge
cases.

## What to run

### Everything from Quick Check

Run all static integrity tests, SKILL.md quality checks, cross-reference consistency,
security review, and best practices audit first. They're fast and give you a foundation
before moving into execution.

**Important:** If the security review found any Critical severity issues in scripts, warn the
user before proceeding with execution-based tests. The scripts you're about to run may contain
the flagged patterns. Ask: "The Quick Check found critical security issues in [script]. Do you
want me to proceed with executing it, or should we address the security findings first?"

### Existing eval regression

If the skill has an `evals/` directory with test cases, run them before your own generated tests.
These represent the skill author's own expectations and are the most authoritative measure of
whether the skill works. See `references/eval-schema.md` for the exact format and how each
field is processed.

1. **Validate the eval file** — Check the schema, name match, ID uniqueness, required fields,
   and input file existence. Report any validation errors but continue with valid evals.

2. **Run each eval** — For each test case:
   - Set up any required input files (if the eval references files, check if they exist in
     the evals directory or need to be created)
   - Read the skill's SKILL.md
   - Follow the skill's instructions to accomplish the eval prompt
   - Save outputs to a workspace directory: `skillcheck-workspace/eval-regression/eval-<id>/`

3. **Check assertions** — If the eval defines assertions, verify each one:
   - Programmatic assertions (file exists, contains string, matches regex) — run as code
   - Descriptive assertions ("output should be a valid PDF") — evaluate by inspection
   - Record pass/fail for each assertion with evidence

4. **Report results** — Even if all evals pass, report what was tested. If any fail, this is
   a significant finding — the skill no longer passes its own tests, which suggests a regression
   was introduced.

**If no evals directory exists**, skip this section and note in the report: "No existing eval
set found. Consider adding evals/evals.json with test cases for future regression testing."
Also, in the improvement suggestions section, include 2-3 starter test case prompts based
on the skill's I/O contracts. For example:

> No evals found. Here are some test cases you could save to `evals/evals.json`:
> 1. "Convert this CSV to JSON format" (tests the primary happy path)
> 2. "Convert this CSV to XML" (tests unsupported format handling)
> 3. "Convert this file" with no CSV provided (tests missing input handling)

This gives the user a concrete starting point without SkillCheck formally owning the evals.

### Script execution tests

For each script in the skill's `scripts/` directory:

1. **Identify expected arguments** — Read how SKILL.md invokes the script. Note the arguments,
   flags, and any piped input. Cross-reference with the argument mismatches found during
   Quick Check — if a mismatch was flagged, use the *script's* expected arguments (not
   SKILL.md's incorrect invocation) to test the script itself. Note the mismatch in the report.

2. **Generate minimal mock input** — Create the simplest valid input the script needs.
   See `references/mock-files.md` for how to generate mock files per type.

3. **Run with mock input** — Execute the script and capture stdout, stderr, and exit code:
   ```bash
   python3 scripts/build_chart.py --input mock_data.csv --output /tmp/test_output.png 2>&1
   echo "Exit code: $?"
   ```

4. **Verify output** — Check that:
   - The script exited with code 0 (or expected non-zero for error cases)
   - Expected output files were created
   - Output files are non-empty and parseable (e.g., valid PNG, valid JSON)

5. **Missing argument test** — Run the script without required arguments. It should fail
   gracefully (exit non-zero with a helpful message), not crash with an unhandled exception.
   Users will inevitably forget inputs, and a cryptic traceback makes the skill look broken
   even when the fix is simple.

### I/O contract tests (happy path)

For each declared input/output pair in the skill:

1. **Generate a realistic mock input file** using `references/mock-files.md`. The mock should
   match the exact specification in the SKILL.md — correct file type, expected columns/fields,
   realistic sample data.

2. **Simulate the workflow** — Read the skill's SKILL.md, then follow its instructions as if
   you were Claude receiving the test prompt. Use the mock input file.

3. **Verify the output**:
   - Was the output file created?
   - Is it the correct file type?
   - Is it non-empty and well-formed?
   - Does it contain the expected structure (sections, slides, columns, etc.)?
   - Is it in the correct output location?

### Basic workflow tests

1. **Step completability** — For each step in the skill's workflow, verify the tools and
   resources it depends on are available. A skill that requires a tool not present in the
   environment will fail at runtime with no workaround. For example, if step 3 says
   "run the Python script", verify Python is available and the script exists.

2. **Step ordering** — Check that no step depends on output from a later step. Out-of-order
   dependencies cause silent failures where a step receives empty or missing input because
   its prerequisite hasn't run yet.

3. **Conditional coverage** — If the skill has branching logic, test at least the primary
   (most common) branch. Untested branches often contain stale instructions that were never
   updated when the rest of the skill changed.

## Expected test count

Typically 15-25 tests. Breakdown:
- Quick Check tests (static, cross-ref, security, best practices): 10-20
- Eval regression: 1 per existing eval (0 if none exist)
- Script execution: 2-3 per script
- I/O contracts: 1-2 per declared input/output pair
- Workflow: 2-4

## What to skip

- Edge case and malformed inputs (that's Deep)
- Stress testing with large files (that's Deep)
- Triggering analysis (that's Deep)
- Multiple variants per input type (that's Deep)
- Error recovery testing (that's Deep)

## Report notes

Standard Check reports should note which input/output contracts were tested, which existing
evals were re-run (and whether they passed), and which edge cases were skipped.

If existing evals failed, highlight this prominently — it means the skill has regressed from
what the author originally verified.

End with: "This was a Standard Check. Run Deep for edge cases, stress testing, and triggering
analysis."
