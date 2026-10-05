# NestJS Feature Audit Report Template

Keep the four category headings exactly as written and in order. Do not remove empty categories.

```markdown
# Feature Audit: <feature>

- Verdict: complete | incomplete | blocked | not verifiable
- Revision: `<branch>@<commit>`; clean | dirty
- Freshness: verified against `<remote>/<branch>@<sha>` | local snapshot accepted by user
- Roadmap: `<docs/path.md:line>` | user-provided roadmap
- Scope: <modules, paths, contracts, environments>
- Conversation context: used with source | unavailable | not needed

## ✅ Implemented

### IMP-001 — <roadmap item>

- Requirement: `<roadmap path:line>` — <normalized target>
- Observed: verified
- Evidence: `<source/test/config path:line>` and `<command/result or runtime observation>`
- Impact: <outcome now satisfied>
- Next proof: <remaining acceptance or regression check; `none` only when fully proven>

## ❌ Missing/Not Implemented

### MISS-001 — <roadmap item>

- Requirement: `<roadmap path:line>` — <normalized target>
- Observed: absent | partial
- Evidence: <searches and expected integration points checked>
- Impact: <unsatisfied roadmap outcome>
- Next proof: <artifact or check that would prove implementation>

## ⚠️ Legacy Code

### LEG-001 — <legacy path that must migrate>

- Requirement: `<roadmap or standard path:line>` — <migration target>
- Observed: superseded implementation remains active
- Evidence: `<legacy path:line>` and `<target path or missing replacement>`
- Impact: <compatibility, duplication, maintenance, or cutover effect>
- Next proof: <migration/cutover/removal evidence>

## 🛑 Bugs & Blockers

### BLOCK-001 — <bug or blocker>

- Requirement: `<roadmap path:line>` — <affected target>
- Observed: broken | blocked | not verifiable
- Evidence: <failure, reproduction, missing prerequisite, or unavailable gate>
- Impact: <incorrect behavior or prevented milestone>
- Exit evidence: <exact result that clears this entry>
```

When a category is empty, write:

```text
None found in the audited evidence.
```

## Verdict rules

- **complete:** every in-scope roadmap item is implemented and all required acceptance evidence is verified.
- **incomplete:** one or more roadmap items are absent, partial, or still on a required legacy path.
- **blocked:** a distinct prerequisite prevents the next required outcome or reliable audit completion.
- **not verifiable:** the roadmap passed the gate, but available evidence cannot support a trustworthy overall state.

Do not use a percentage unless the roadmap itself provides weights. Counts may summarize entries but cannot replace the evidence contract.
