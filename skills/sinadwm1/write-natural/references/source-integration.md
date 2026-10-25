# Integrate sources without importing their errors

## Contents

1. Traceability and reading scope
2. Decision hierarchy
3. Reconciled conflicts
4. Source roles and tool boundaries
5. Maintenance and attribution

## Traceability and reading scope

This skill integrates the supplied 112-record research corpus: D01–D40, A01–A25, Q01–Q40 and R01–R07. The source catalog preserves the original record; the newer source reviews state what was actually read, exact extraction/section locators, access limits, findings, decisions, rule IDs and final integration paths. The archived dossier is an input, not proof of a new full-text review.

Read `evidence/source-reviews.json` for the detailed record and `evidence/coverage.json` for the coverage index. Use `source-analysis.md` to inspect dispositions as prose. A local extracted-text line locator is bound to the named snapshot/hash, not an immutable line number at the publisher. Transient full-text downloads are not redistributed with this package.

“Accounted for” means every source has an explicit, substantive decision. It does not mean every source is equally reliable, every line of an inaccessible supplement was read, or every instruction was adopted. Preserve partial/abstract-only/blocked status. Do not turn an access failure into a supporting factual source.

## Decision hierarchy

Apply applicable user and host instructions first. For writing decisions, preserve factual fidelity and required attribution/disclosure. Respect the destination's actual rules and the author's voice within those constraints. Use current primary guidance for current product or platform claims. Treat research results at their tested model, language, sample and task scope. Treat editorial conventions and public skills as revisable heuristics.

Use four dispositions:

- `adopt`: retain a sound rule within its documented scope.
- `adapt`: retain the useful idea with conditions, exceptions, a different implementation, or a narrower claim.
- `context_only`: retain a mechanism, limitation, example or question; it does not become a runtime mandate.
- `reject`: record an unsupported, obsolete, conflicting or harmful inference so it is not silently reintroduced.

Keep attributions separate from endorsements. An author or organization cited in this package did not author, certify, or endorse this skill.

## Reconciled conflicts

These integration rules are original synthesis. Follow the per-source ledger for precise scope and evidence.

| Conflict | Integration decision |
|---|---|
| Absolute bans on adverbs, passive voice and triads versus meaning and genre | Use contextual review; retain meaningful uncertainty, legitimate passive constructions and actual three-part results. |
| Removing connectors versus preserving argument | Keep relationships such as cause, condition and contrast even if the connector adds no new noun. |
| Changing “one of the most popular” into “the most popular” | Reject claim strengthening, including in a published style example. |
| Generic character scrubbing versus Persian orthography and bidi | Preserve legitimate U+200C ZWNJ and necessary direction mechanisms; never blanket-delete invisible characters. |
| Artificial sentence variation versus natural rhythm | Let the content determine cadence; no randomness, error insertion or numerical rhythm quotas. |
| “Personalize” versus missing experience | Use supplied/verified experience or explicit fiction; invent no biography, interview, test or customer. |
| AI-detector score as a proxy for quality | Reject the proxy; evaluate fidelity, usefulness, reasoning and language independently. |
| High laboratory detection rates versus distribution shift | Retain both results within their own conditions; promise neither universal failure nor universal success. |
| Multilingual announcement versus evaluated language list | Inspect the final evaluated languages; Arabic/Urdu/English coverage does not validate Persian. |
| Vendor support page versus independent performance evidence | Treat feature support as documentation, accuracy as a separate empirical question. |
| Academic paper-writing skill versus missing research | Never invent methods, results, references or reporting-checklist items. |
| Fixed SEO word floors, keyword densities and E-E-A-T “scores” | Reject unsupported universal formulas; follow people-first usefulness and current primary platform guidance. |
| Retired testing tool in a public SEO skill | Do not recommend it as current; verify tool status before use. |
| Unsupported percentage lifts in a copywriting skill | Do not reuse the number as evidence or a promise. |
| Covert customer recording suggested in a tutorial | Do not adopt it; use authorized research materials and consent-based collection. |
| Training/logit-level methods versus Markdown instructions | Explain them as research/tool options requiring separate capabilities; do not pretend a prompt reproduces them. |
| Fluency or a high overall score versus factual accuracy | Apply critical integrity gates independently; style cannot compensate for false claims. |
| Better wording versus better outcomes | Measure the task's real outcome when authorized; a preference rating does not establish sales or impact. |

## Source roles and tool boundaries

Public skills supply procedural patterns: genre routing, small-scope editing, evidence collection, repeated focused review and protection of writer voice. Linters supply repeatable local checks and useful warning designs. Papers supply findings and limits, not universal writing commandments. Standards supply genre-specific reporting needs, not missing data. User discussions supply experiences and candidate failure modes, not population statistics.

The included scripts are original, dependency-free implementations. They do not embed third-party linters, research models, vendor APIs or watermark detectors. Optional external tools are described in `tools-and-evidence.md`; do not install or call them merely because they appear in the research.

## Maintenance and attribution

Keep the reviewed date with changing claims. Recheck current official product support, rollout, access, scoring and platform policies when a current answer requires it. Retain historical results at their original dates; do not overwrite an old benchmark with a new vendor version name.

Source-derived summaries and original examples are used instead of wholesale copies of public skills or papers. Preserve the specific license/attribution notes in the source reviews. Public availability is not a redistribution license, and a repository's main license need not cover every imported dataset or rule set. If adding third-party code or substantial copied text later, verify its exact version/license and include the required notice before distribution.

The skill's effectiveness beyond the recorded checks remains an empirical question. Use the validation scope and realistic cases in `validation.md`; do not turn a successful package check into an accuracy or undetectability claim.
