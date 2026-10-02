# Show-and-tell / builder post

Facts to keep intact: version 1.1.0, published 28 September 2026, zero npm dependencies, 43 rules, five output lanes. Recommended placement: a builder forum, a repository Show & Tell thread, or a project update post.

---

**Show and tell: `un-editorial-check` — an editorial pre-screen for United Nations style English copy, with nothing to install**

I built `un-editorial-check` for a recurring problem: agent-written and human-written copy that reads fine but quietly breaks an organisation's editorial rules, and reviewers who catch it only at the end.

What it is:

- A single Node.js CLI plus an Agent Skill. No dependencies, no network calls, runs offline on Node.js 18 or newer.
- 43 documented rules over spelling, terminology, dates, numbers, register, contested claims and wording, each with its source and retrieval date recorded in `rules/sources.json`.
- Extraction first: only HTML text nodes and copy-bearing attributes, Markdown paragraphs, plain-text blocks and rendered JavaScript strings reach a rule. Comments, code, identifiers, URLs and cited titles never do.

Design decisions I would defend in review:

- Report first. A finding identifies a review requirement; it does not establish the truth of a claim.
- Five output lanes, so a heuristic warning, a diplomatic sensitivity and a security audit never masquerade as the same thing.
- `--fix` is opt-in, previews as a diff, and refuses anything beyond a short deterministic allow-list. Terminology, claims, dates, political wording, quotations, harmful wording and sources are never rewritten.
- The clean run prints one sentence and nothing more: `No findings under the enabled, documented local rules.`

Not a code linter, not a fact-checker, not an approval. It pre-screens copy against documented local rules and says what those rules found.

```sh
npx -y un-editorial-check statement.md --report review.pdf
```

https://github.com/ahaomar/un-editorial-check
