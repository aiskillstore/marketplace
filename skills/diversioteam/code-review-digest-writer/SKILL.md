---
name: code-review-digest-writer
description: >
  Generates weekly code-review digest docs from PR review comments for any GitHub
  repository. If present, follows project-specific docs/review-digests/AGENTS.md
  guidelines. Use this to turn a date-bounded set of PR reviews into a structured
  markdown “newsletter” that captures themes, repeated issues, and concrete
  takeaways.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
---

# Code Review Digest Writer Skill

## When to Use This Skill

- You want a **weekly (or custom window) code-review digest** for the current
  repository or project, based on PR review comments.
- You have a **start date** and **end date** and want a markdown newsletter
  summarizing what was taught in PR review feedback in that period.
- You want to highlight **themes, repeated issues, and concrete best practices**
  rather than just listing PRs.

If the user does not provide both a start and end date, ask them to specify:
`YYYY-MM-DD` → `YYYY-MM-DD` before proceeding.

## Example Prompts

- “Generate a code review digest for this repo for 2025-02-01 → 2025-02-14.”
- “Create a weekly PR review digest for 2025-03-10 → 2025-03-17, using any existing digests as historical context.”
- “From 2025-04-01 to 2025-04-30, summarize what reviewers focused on in `owner/service-repo` and highlight repeated issues.”
- “Write a newsletter-style code review digest for this project for 2025-05-15 → 2025-05-29, tagging themes as [NEW] or [REPEAT].”

## Scope & Repositories

- Target repo: whichever project you want a digest for (typically the repo you
  currently have open in Claude Code).
- Ideally the repo contains `docs/review-digests/AGENTS.md` with
  project-specific digest guidelines. If not, fall back to the generic structure
  described in this Skill and any existing digest files.
- This Skill **must only modify docs** under:
  - `docs/review-digests/YYYY-MM-DD.md`
  where the date is the **end date** of the reporting window.
- Do **not** modify application code, tests, or configs in the target repo while
  this Skill is active. All changes should be within `docs/review-digests/`.
- If `docs/review-digests/` does not exist yet, create the directory before
  writing the digest file, so future digests can be added and past ones read.

## Required Local Tools & Assumptions

When using `Bash`, assume:

- `gh` (GitHub CLI) is installed and authenticated for the target repository
  (or for a default GitHub identity that can see it).
- Current working directory is the target repo root (or pass `--repo owner/name`
  explicitly to `gh` commands, if needed).

If `gh` is not available, gracefully fall back to:

- Summarizing based on locally available PR notes or docs, and
- Clearly stating in the digest that it was generated with partial data.

## High-Level Workflow

When asked to generate or update a digest, follow this workflow:

1. **Confirm time window**
   - Ensure you have `start_date` and `end_date` (inclusive).
   - Confirm with the user if there is any ambiguity.

2. **Load local digest guidelines**
   - If it exists, open `docs/review-digests/AGENTS.md` and read it carefully.
   - When present, treat that file as the **source of truth** for:
     - What the digest is.
     - Where it should be written.
     - Required structure and link style.
     - How to detect and label repeated issues.
   - If it does not exist, follow the layout described later in this Skill and
     use any existing digest files in `docs/review-digests/` as a reference.

3. **Inspect existing digests**
   - Ensure the `docs/review-digests/` directory exists:
     - If it does not, create it; in that case there will be no past digests yet.
   - Use `Glob` or `Bash` to list `docs/review-digests/*.md`.
   - Load at least the **last 3–4 digests** (if present).
   - Extract their **themes and repeated issues** (e.g., fixture reuse,
     blind-index invariants, Query() regression patterns, etc.).
   - You will use these to detect when issues are recurring.

4. **Fetch PR and review data for the window**
   - Use `Bash` with `gh` to query PRs whose:
     - `createdAt` is between `[start_date, end_date]`, OR
     - `closedAt` is between `[start_date, end_date]`.
   - Deduplicate PR numbers.
   - For each selected PR:
     - Fetch **top-level comments** (PR discussion).
     - Fetch **review-thread comments with code context** (via GraphQL).
   - Prefer comments from:
     - Human reviewers (`__typename == "User"`).
     - AI reviewers that contain substantial review content
       (e.g., Claude, Copilot PR reviewer).
   - Exclude noisy infrastructure/bot comments with no review content
     (e.g., `github-actions`, log-only bots, CI status updates).

5. **Cluster feedback into themes**
   - Read comments and diff context enough to understand:
     - What behavior or pattern was being discussed.
     - What best practice or correction was suggested.
   - Group comments across PRs into **themes**, such as:
     - Logging, Sentry, and performance instrumentation.
     - Tests, fixtures, and code structure.
     - Security, access control, and PII handling.
     - Domain-specific design and invariants for this repository.
     - Migrations & tooling.
     - Process and meta-patterns in reviews.

6. **Detect repeated issues**
   - For each current theme, compare it conceptually to themes you extracted
     from previous digests (step 3).
   - If the same pattern appears again (e.g., “use TypedDict instead of
     `dict[str, Any]` in payloads”, “avoid Django Ninja `Query()` constants”,
     “reuse shared fixtures instead of copy-paste”), treat it as a **repeated issue**.
   - Use labels:
     - `[NEW]` for themes that appear for the first time.
     - `[REPEAT]` for themes that have appeared in previous digests.

7. **Draft the digest file**
   - Target path: `docs/review-digests/END_DATE.md`
     - Example: period `2025-11-13` → `2025-11-27` → `docs/review-digests/2025-11-27.md`.
   - Follow the **layout described in `docs/review-digests/AGENTS.md`** and the
     most recent digest, including:
     - Title with repo and period.
     - **Overview** section with 3–6 bullets summarizing main themes.
     - Thematic sections (numbered) that group related feedback.
     - A closing section (e.g., “How to Use This Digest”).
   - Within each section:
     - Explain the practice in **plain language**.
     - Include 1–3 concrete, generalized examples.
     - Call out whether this is `[NEW]` or `[REPEAT]`.
     - Emphasize the “why” (business impact, correctness, safety, DX).

8. **Linking to PRs and comments**
   - In the body of the digest, use **reference-style links** only:
     - `[#2519 – Fix Teams Start Survey race condition][pr-2519]`
     - `Key comment: [Fixture reuse recommendation][c-2519-3]`
   - At the **bottom of the file**, define every link once:
     - `pr-<number>` for PRs.
     - `c-<number>-<n>` for specific review comments.
     - `ic-<number>-<n>` for issue comments, if needed.
   - Reuse identifiers consistently when the same comment is referenced in
     multiple sections.

9. **Respect tone and intent**
   - The digest is a **newsletter**, not a blame report.
   - Highlight:
     - What the team is learning.
     - Where we’re improving.
     - Where patterns are still repeating and need attention.
   - Make guidance actionable (e.g., “When adding a new CSV mapping endpoint,
     always run through the project’s PII and security checklist docs.”).

10. **Save and review**
   - Use `Edit` to create or update the digest file for `END_DATE`.
   - Re-open the file after writing to sanity-check:
     - Structure matches the prior digests.
     - Links resolve correctly and have definitions at the bottom.
     - `[NEW]` / `[REPEAT]` tags are applied consistently.
     - No accidental code changes occurred in the repo.

## Output Expectations

When this Skill is active and asked to generate a digest, your final output
should be:

- A **single markdown file** under `docs/review-digests/YYYY-MM-DD.md`.
- A short natural-language summary back to the user describing:
  - The period covered.
  - The main themes identified.
  - How many themes were `[REPEAT]` vs `[NEW]`.

If you were unable to access GitHub or some PRs, clearly note in the digest and
in your summary which data sources were missing and how that might limit the
digest.

## Severity / Emphasis Tags

Instead of issue severities, this Skill uses **learning/emphasis tags**:

- `[NEW]` – First time this theme appears in digests.
- `[REPEAT]` – Theme appeared in at least one prior digest.
- `[HIGH-IMPACT]` – Optional extra tag for themes with clear business impact
  (e.g., security invariants, multi-tenant correctness, high-risk migrations).

Use these tags sparingly and consistently; they should help readers prioritize
which lessons to internalize first.

## Compatibility Notes

This skill is designed to work with both **Claude Code** and **OpenAI Codex**.

For Codex users:
- Install via skill-installer with `--repo DiversioTeam/agent-skills-marketplace
  --path plugins/code-review-digest-writer/skills/code-review-digest-writer`.
- Use `$skill code-review-digest-writer` to invoke.

For Claude Code users:
- Install via `/plugin install code-review-digest-writer@diversiotech`.
- Use `/code-review-digest-writer:review-digest` to invoke.
