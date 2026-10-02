# npm package launch post

Facts to keep intact: version 1.1.0, published 28 September 2026, zero npm dependencies, MIT licence. Recommended placement: an npm or Node.js community channel, or the release description on the npm package page. Character counts per platform: run `node bin/check.mjs --preview <platform> <file>` with `x`, `linkedin`, `bluesky` or `mastodon`.

---

`un-editorial-check` 1.1.0 is on npm.

It is a zero-dependency Node.js CLI and Agent Skill that reads user-visible copy the way a United Nations editorial reviewer would — language, wording, tone, spelling, terminology, dates, numbers, claims and register — and reports what fails against 43 documented rules.

```sh
npx -y un-editorial-check statement.md --report review.pdf
```

What it gives you:

- Five lanes in every format: deterministic violations, heuristic editorial review, harmful or discriminatory review, diplomatic sensitivity, optional audits.
- Text, JSON, SARIF and PDF output, each finding carrying its rule source, profile, confidence, limitation and recommended human action.
- Exit codes `0` / `1` / `2`, and a clean run that says exactly one thing: `No findings under the enabled, documented local rules.`
- Report first: a finding identifies a review requirement. It does not establish the truth of a claim, and it does not change your file. `--fix` is opt-in, previewed as a diff and limited to deterministic corrections.

Node.js 18 or newer, MIT licence, no dependencies, no network calls.

https://www.npmjs.com/package/un-editorial-check
https://github.com/ahaomar/un-editorial-check
