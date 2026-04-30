# Best Practices Review

## Contents

- [Spec Compliance](#spec-compliance) — BP-1: Name format, BP-2: Description length, BP-3: Portability fields
- [Structure & Organization](#structure--organization) — BP-4 through BP-8: Layout, line count, progressive disclosure, references, domain variants
- [Description Quality](#description-quality) — BP-9 through BP-11: Completeness, assertiveness, trigger placement
- [Writing Quality](#writing-quality) — BP-12 through BP-18: Imperative form, clarity, defaults, generality, examples, gotchas
- [Efficiency](#efficiency) — BP-19 through BP-20: Context window bloat, script bundling
- [Completeness](#completeness) — BP-21 through BP-22: Error handling, eval set
- [Scoring](#scoring)

---

This test evaluates a skill against established conventions from both the
[Agent Skills open standard](https://agentskills.io) and the skill authoring guide.
It's static analysis — reading files and checking patterns, no execution.

These checks cover two concerns: **spec compliance** (does the skill follow the open
standard so it works across platforms?) and **quality** (is it well-structured, efficient,
and clear?). Skills intended for public distribution should aim for full compliance on
both fronts. Internal skills can be more relaxed on quality checks but should still
follow the spec for portability.

The best practices review runs at **Quick Check** depth and above. It produces a mix of
pass/fail checks and advisory notes. Not every best practice is a hard rule — some are
strong recommendations where deviation might be intentional. The report should distinguish
between "this is wrong" and "this could be better."

---

## Spec Compliance

These checks validate against the Agent Skills open standard at agentskills.io. Failures
here mean the skill may not work correctly on non-Claude platforms or may fail validation
tools like `skills-ref validate`.

### BP-1: Name format

The `name` field must follow the spec's naming rules:
- 1-64 characters
- Lowercase letters, numbers, and hyphens only
- Must not start or end with a hyphen
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

**Check:** Validate the name against all five rules. The directory name match is
particularly important because some platforms use the directory name as the identifier,
and a mismatch causes the skill to silently fail to load.

**Severity:** Fail for any rule violation. These are hard requirements in the spec.

### BP-2: Description length

The `description` field must be 1-1024 characters per the spec.

**Check:** Measure the description length. Flag if over 1024 characters (spec violation)
or under 20 words (too vague to trigger reliably — not a spec violation but a quality
issue).

**Severity:** Fail if over 1024 chars. Warning if under 20 words.

### BP-3: Portability fields

The spec defines optional fields that improve cross-platform compatibility:
- `license` — important for publicly distributed skills so users know the terms
- `compatibility` — declares environment requirements (required tools, network access,
  platform-specific features) so platforms can warn users before activation

**Check:**
- If the skill appears intended for distribution (has a LICENSE file, is in a public
  repo, or the user mentions sharing it), flag if `license` is missing from frontmatter.
- If the skill depends on specific tools, packages, or platform features (detected from
  scripts imports, SKILL.md instructions, or declared dependencies), flag if
  `compatibility` is missing. For example, a skill that uses `python-docx` should
  declare `compatibility: Requires python-docx`.
- If the skill uses Claude-specific features (Claude.ai paths like `/mnt/skills/`,
  Claude-specific tools), flag with an info note that it may not be portable to
  other platforms without a `compatibility` declaration.

**Severity:** Advisory for missing `license`. Warning for missing `compatibility` when
environment requirements are detected.

---

## Structure & Organization

### BP-4: Standard directory layout

Skills should follow the conventional structure:

```
skill-name/
├── SKILL.md              (required)
├── scripts/              (executable code)
├── references/           (docs loaded into context as needed)
├── assets/               (templates, icons, fonts, images)
└── evals/                (test cases)
```

**Check:** Are executable scripts in `scripts/`? Are supplementary docs in `references/`?
Are templates and static files in `assets/`? Flag scripts at the root level, documentation
files mixed into `scripts/`, or other organizational oddities.

**Severity:** Advisory. A skill can work fine with non-standard layout, but it's harder
for others to navigate and maintain.

### BP-5: SKILL.md line count

The spec recommends keeping SKILL.md under 500 lines and 5000 tokens. This is the content
loaded into context every time the skill triggers — bloated instructions waste tokens on
every invocation.

**Check:** Count lines in SKILL.md. Flag if over 500, warn if over 400.

**If over 500:** Look for content that could be moved to reference files. Long examples,
detailed API documentation, format specifications, and edge-case handling are all candidates
for extraction into `references/`.

**Severity:** Warning at 400+, fail at 500+.

### BP-6: Progressive disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) — always in context (~100 tokens)
2. **SKILL.md body** — loaded when skill triggers (< 5000 tokens recommended)
3. **Bundled resources** — loaded on demand as needed

**Check:** Is the skill making good use of all three levels?
- Is heavy content (detailed specs, long examples, API docs) in reference files rather
  than crammed into SKILL.md?
- Does SKILL.md provide clear, conditional pointers for WHEN to read each reference file?
  (e.g., "Read references/aws.md if the user wants to deploy to AWS")
- Could any SKILL.md content be pushed down to a reference that's only read when relevant?

The spec emphasizes that conditional pointers are key — "Read X if Y happens" is far better
than "see references/ for details" because the agent may not know when to load it.

**Severity:** Advisory. But a skill that dumps everything into SKILL.md is wasting context
on every invocation.

### BP-7: Reference file quality

For reference files:
- Large reference files (>300 lines) should include a table of contents at the top so
  the agent can navigate without reading the entire file
- Each reference file should have a clear, singular purpose
- SKILL.md should explain when each reference should be read — vague pointers like
  "see references/ for more info" waste tokens because the agent might read everything
- Keep file references one level deep from SKILL.md (per spec). Avoid deeply nested
  reference chains where file A tells the agent to read file B which points to file C.

**Check:** Measure each reference file's length. Check for TOC in files over 300 lines.
Check that SKILL.md provides specific "when to read" guidance for each reference.
Check for nested reference chains.

**Severity:** Warning for missing TOC on large files. Advisory for vague pointers.
Warning for nested reference chains deeper than one level.

### BP-8: Domain variant organization

When a skill supports multiple domains, frameworks, or platforms, they should be organized
as separate reference files rather than all being in SKILL.md:

```
cloud-deploy/
├── SKILL.md (workflow + selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

The agent reads only the relevant reference file, saving context.

**Check:** Does the SKILL.md contain large blocks of domain-specific content that could be
split out? Look for repeated patterns like "If using X... [50 lines]. If using Y... [50 lines]."

**Severity:** Advisory. Only relevant for multi-domain skills.

---

## Description Quality

### BP-9: Description completeness

The description is the primary triggering mechanism. It must include:
- What the skill does
- Specific contexts and phrases that should trigger it
- When NOT to use it (to avoid false positives)

**Check:** Does the description cover all three? Flag if any are missing.

**Severity:** Warning for missing "what it does" or trigger contexts. Advisory for
missing negative guidance.

### BP-10: Description assertiveness

Agents tend to "undertrigger" skills — not using them when they'd be useful. Descriptions
should be somewhat "pushy": explicitly listing trigger phrases, file types, user intents,
and edge cases where the skill should still activate.

**Bad:** "How to build a dashboard to display data."
**Good:** "How to build a dashboard to display data. Use this skill whenever the user
mentions dashboards, data visualization, internal metrics, or wants to display any kind
of data, even if they don't explicitly ask for a 'dashboard.'"

**Check:** Is the description specific about when to trigger? Does it list concrete
examples of user phrases or contexts? Or is it a vague one-liner?

**Severity:** Warning. A weak description means the skill won't activate when it should.

### BP-11: Trigger info placement

All "when to use" information should be in the description frontmatter, not buried in the
SKILL.md body. The description is always in context; the body is only loaded after triggering.
Trigger guidance in the body has no effect — the triggering decision was already made.

**Check:** Scan the SKILL.md body for trigger-related content ("use this skill when",
"trigger this when", "activate when"). If found, flag that it should be in the description.

**Severity:** Warning. This is a functional issue.

---

## Writing Quality

### BP-12: Imperative form

Skill instructions should use the imperative form — direct commands.

**Good:** "Read the CSV file. Extract the header row. Generate a chart."
**Weak:** "The skill should read the CSV file. It would then extract the header row."
**Bad:** "You might want to consider reading the CSV file and possibly extracting headers."

**Check:** Sample 5-10 instruction sentences from the SKILL.md. Are most in imperative form?
Flag if the majority use passive voice, conditional language, or third-person descriptions.

**Severity:** Advisory. Imperative form is clearer and more reliably followed.

### BP-13: Explain the why

Instructions should explain WHY things matter rather than relying on heavy-handed
MUST/NEVER/ALWAYS directives. Understanding the reasoning behind a rule helps the agent
apply it intelligently in novel situations, rather than following it rigidly or ignoring it.

**Heavy-handed:** "ALWAYS use 12px font. NEVER use bullet points. MUST include a footer."
**Better:** "Use 12px font because the output is designed for print at A4 size, and smaller
fonts cause readability issues."

**Check:** Count MUST, NEVER, ALWAYS (case-insensitive, whole-word) in the SKILL.md. If the
density is high (more than 1 per 50 lines), check whether the surrounding text explains the
reasoning. Flag instances that lack justification.

**Severity:** Advisory. Skills with unexplained rigid rules tend to produce brittle outputs.

### BP-14: Instruction clarity

Instructions should be unambiguous. Vague phrases leave too much to interpretation.

**Vague phrases to flag:**
- "format it nicely" / "make it look good" / "use appropriate styling"
- "add relevant content" / "include useful information"
- "use a suitable structure" / "organize appropriately"
- "handle errors properly" / "deal with edge cases"

**Check:** Scan for vague instruction patterns. For each one found, note what a more
specific instruction would look like.

**Severity:** Advisory. Vague instructions are one of the top causes of inconsistent output.

### BP-15: Defaults over menus

When multiple tools or approaches could work, the skill should pick a default and mention
alternatives briefly — not present them as equal options. Choice overload causes the agent
to either pick randomly or waste time deliberating.

**Bad:** "You can use pypdf, pdfplumber, PyMuPDF, or pdf2image..."
**Good:** "Use pdfplumber for text extraction. For scanned PDFs requiring OCR, use
pdf2image with pytesseract instead."

**Check:** Look for patterns where the skill lists 3+ alternatives without indicating a
preferred choice. Common signals: "you can use X, Y, or Z", "options include", "choose
between".

**Severity:** Advisory. But clear defaults measurably improve output consistency.

### BP-16: Generality vs overfitting

Skills should be general enough to handle a range of inputs, not narrowly tailored to
specific examples. The spec recommends teaching *how to approach* a class of problems,
not *what to produce* for a specific instance.

**Check:** Look for signs of overfitting:
- Instructions that reference specific filenames, column names, or values from a single
  test case rather than general patterns
- Logic that only works for one specific input shape
- Examples treated as the only valid input rather than illustrations

**Severity:** Advisory. Flag if you notice it, but don't force the issue.

### BP-17: Examples included

Skills benefit from including input/output examples or output templates. The spec notes
that agents pattern-match well against concrete structures, making templates more reliable
than prose descriptions of expected format.

**Check:** Does the SKILL.md include at least one example of expected input → output?
Or an output format template?

**Severity:** Advisory for simple skills, warning for complex transformation skills.

### BP-18: Gotchas section

The open standard specifically recommends a "gotchas" section as the highest-value content
in many skills — concrete corrections to mistakes the agent would make without being told.
These aren't general advice but environment-specific facts that defy reasonable assumptions.

**Good gotchas:** "The users table uses soft deletes — queries must include
WHERE deleted_at IS NULL"
**Not gotchas:** "Handle errors appropriately" (too generic)

**Check:** Does the skill have domain-specific knowledge that would trip up an agent?
If the skill covers a complex domain (APIs, databases, specific tools), flag the absence
of a gotchas section. For simple skills, this check is N/A.

**Severity:** Advisory. Only relevant for domain-specific skills.

---

## Efficiency

### BP-19: Context window efficiency

Every token in SKILL.md is spent on every invocation. Content should earn its place.
The spec advises: "Would the agent get this wrong without this instruction?" If the
answer is no, cut it.

**Check for bloat:**
- Redundant instructions (the same thing said multiple ways)
- Explaining concepts the agent already knows (what a PDF is, how HTTP works)
- Overly long examples where a shorter one would teach the same thing
- Comments aimed at the skill author ("TODO", "FIXME", "we should revisit this")
- Placeholder content that was never filled in

**Severity:** Advisory. But context efficiency directly impacts cost and quality.

### BP-20: Script bundling

If a skill's workflow involves tasks that would require writing boilerplate code on every
invocation, those scripts should be pre-written and bundled in `scripts/`. The spec
recommends watching for patterns where the agent reinvents the same logic each run.

**Check:** Are there steps where the agent is told to write code from scratch that could
be a pre-built script? Look for patterns like "Write a Python script that..." or complex
data transformations described in prose.

**Severity:** Advisory. Only flag code that would be substantially the same on every run.

---

## Completeness

### BP-21: Error handling guidance

Skills should tell the agent what to do when things go wrong — missing files, bad input,
unavailable tools, unexpected formats.

**Check:** Does the SKILL.md mention any error cases? Does it provide fallback behavior?
For skills with scripts, does it explain what to do if a script fails?

**Severity:** Advisory for simple skills. Warning for skills with scripts or external
dependencies.

### BP-22: Eval set present

Skills benefit from having an `evals/` directory with test cases. This enables regression
testing and gives future maintainers a way to verify the skill still works.

**Check:** Does an `evals/` directory exist? Does it contain `evals.json` or equivalent?

**Severity:** Advisory. Not every skill needs formal evals, but their absence is worth
noting — especially for complex skills.

---

## Scoring

Best practices checks don't contribute to the main pass/fail percentage (they're advisory).
Instead, present them as a separate "Best Practices Score" in the report.

Spec compliance checks (BP-1 through BP-3) should be flagged more prominently than quality
checks — they affect whether the skill works on other platforms.

```
## Best Practices Review

Score: 19/22 checks passed

Spec Compliance:
✓ BP-1:  Name format — "csv-chart", matches directory, valid format
✓ BP-2:  Description length — 87 words (within limits)
⚠ BP-3:  Portability — uses python-docx but no compatibility field declared

Structure & Organization:
✓ BP-4:  Standard directory layout
✓ BP-5:  SKILL.md under 500 lines (287 lines)
✓ BP-6:  Progressive disclosure — references used appropriately
⚠ BP-7:  Reference file quality — references/api-guide.md is 420 lines with no TOC
✓ BP-8:  Domain variant organization (N/A — single domain)

Description Quality:
✓ BP-9:  Description completeness
⚠ BP-10: Description assertiveness — could list more trigger phrases
✓ BP-11: Trigger info placement

Writing Quality:
✓ BP-12: Imperative form
✓ BP-13: Explain the why
✓ BP-14: Instruction clarity
✓ BP-15: Defaults over menus (N/A — no multi-option patterns)
✓ BP-16: Generality
✓ BP-17: Examples included
✓ BP-18: Gotchas section (N/A — simple skill)

Efficiency:
✓ BP-19: Context window efficiency
✓ BP-20: Script bundling (N/A)

Completeness:
✓ BP-21: Error handling guidance
✓ BP-22: Eval set present
```

Mark checks as N/A when they don't apply. N/A checks count as passed.
