# Deep Check

The most thorough level. Everything from Quick and Standard plus edge cases, malformed inputs,
stress testing, full end-to-end simulation, triggering analysis, and error recovery. Use this
when a skill is headed for wide distribution or when the user wants maximum confidence.

## What to run

### Everything from Quick and Standard

Run all Quick Check tests (static integrity, cross-reference consistency, security review,
best practices audit) and all Standard Check tests (eval regression, script execution,
happy-path I/O, workflow) first.

### Edge case inputs

For each declared input, generate additional mock files that probe boundaries.
See `references/mock-files.md` for type-specific edge cases. General categories:

1. **Empty input** — A valid file of the correct type but with no meaningful content.
   E.g., a CSV with headers but no rows, an empty JSON array, a blank .txt file.

2. **Minimal input** — The absolute smallest valid input. One row, one field, one word.

3. **Malformed input** — A file that claims to be the right type but is corrupted or wrong:
   - A .csv that's actually tab-separated
   - A .json with trailing commas or unquoted keys
   - A .xlsx that's actually a renamed .csv
   - A text file with mixed encodings

4. **Special characters** — Input containing unicode, emoji, RTL text, null bytes,
   extremely long strings, newlines in unexpected places.

5. **Large input** — Generate a realistically large file to check for performance issues:
   - CSV with 10,000 rows
   - JSON with deeply nested structures (10+ levels)
   - A very long markdown document

6. **Boundary values** — Dates at epoch boundaries, negative numbers where only positives
   are expected, numbers at the max/min of standard types.

For each edge case, verify:
- Does the skill crash or fail silently?
- Does it produce an error message that explains what went wrong?
- Does it produce garbled output without warning?
- Does it handle the case gracefully (ideal)?

### Full end-to-end workflow simulation

Simulate 3-5 realistic user prompts that exercise different aspects of the skill. These should
be the kind of thing a real user would type — complete with casual phrasing, implicit
assumptions, and varying levels of specificity.

For each prompt:
1. Set up the mock environment (upload mock files if needed)
2. Read the skill's SKILL.md
3. Follow the skill's instructions to accomplish the task
4. Capture all outputs
5. Evaluate: did the output match what the skill promised?

Include at least:
- One straightforward, "golden path" prompt
- One prompt that exercises conditional/branching logic
- One prompt that's slightly ambiguous or underspecified — real users rarely give
  perfectly precise instructions, so the skill needs to handle reasonable ambiguity
- One prompt that combines multiple features of the skill — features often work in
  isolation but break when composed together

### Triggering analysis

Generate 8-12 test queries:

**Should-trigger queries (4-6):**
- Direct, explicit request matching the skill's description
- Casual, indirect request where the skill is clearly the right fit
- Request using different terminology but same intent
- Request that's a sub-task of what the skill handles

**Should-not-trigger queries (4-6):**
- Near-miss: shares keywords but needs a different skill
- Adjacent domain: related topic but wrong tool for the job
- Ambiguous: could go either way, but another skill is better suited

For each query, reason about:
- Would the skill's description cause it to be selected?
- Are there any keywords that would cause false positives?
- Are there missing keywords that would cause false negatives?

### Error recovery testing

Deliberately break things and see how the skill handles it. Skills that work on the happy
path but crash on errors create a poor user experience — the user is left with a traceback
and no guidance on how to fix it.

1. **Missing tool** — What if a required tool (e.g., pip package) isn't installed?
2. **Permission errors** — What if the output directory isn't writable?
3. **Network failures** — If the skill depends on web resources, what if they're unavailable?
4. **Interrupted workflows** — What if the user interrupts partway through? Does the skill
   leave behind partial outputs or temp files that could confuse the next run?

### Script robustness

For each script, beyond what Standard already tested:

1. **Argument fuzzing** — Pass unexpected argument types, extra arguments, no arguments
2. **Concurrent safety** — If the script writes to a shared location, is there a race condition?
3. **Cleanup** — Does the script clean up temp files? Does it leave stale state? Leftover
   temp files can accumulate across runs and, in rare cases, cause subsequent runs to read
   stale data instead of generating fresh output.

## Expected test count

Typically 25-40 tests. Breakdown:
- Quick Check tests (static, cross-ref, security, best practices): 10-20
- Standard tests (eval regression, scripts, I/O): 8-12
- Edge case inputs: 4-8 (per declared input type)
- End-to-end simulations: 3-5
- Triggering analysis: 8-12
- Error recovery: 3-5
- Script robustness: 2-4 per script

## Report notes

Deep Check reports should be comprehensive. Include a section on "Testing coverage" that maps
which aspects of the skill were tested and which (if any) couldn't be tested and why.

If the skill passes Deep Check cleanly, it's ready for distribution. Say so in the report:
"This skill passed Deep Check with [N]% pass rate. It handles happy paths, edge cases, and
error conditions well and is ready for wider use."
