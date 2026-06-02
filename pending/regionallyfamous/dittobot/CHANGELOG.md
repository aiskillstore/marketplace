# Changelog

## Unreleased

- Add portable repo validation and GitHub Actions checks.
- Add `scripts/audit.py` for model-free audits of arbitrary source/rewrite pairs.
- Add `scripts/case_lab.py` to turn redacted rewrite failures into regression-case skeletons.
- Add `scripts/voice_probe.py` for local, model-free voice-signal extraction from writing samples.
- Add `scripts/live_report.py` for summarizing local live-eval transcripts by model, prompt mode, family, error type, and usage.
- Add stable failure codes and buckets across audit/live-eval reporting.
- Add profile-contract self-tests for same-source/different-profile behavior, profile fact leakage, evidence phrase overuse, and boundary overrides.
- Add offline `live_eval.py --replay-jsonl` validation for saved raw-output transcripts.
- Save API-error transcript records when live eval fails before a model output.
- Add deterministic Codex plugin package builder and package verifier.
- Add Codex UI icon assets and wire them into skill and plugin metadata.
- Add `scripts/rewrite_report.py` for model-free rewrite provenance reports.
- Add `scripts/voice_profile.py` for compact, auditable voice profile contracts.
- Add `scripts/redact_case.py` and `scripts/failure_fixture.py` for privacy-first bad rewrite reports and fixture candidates.
- Add `scripts/scorecard.py` for deterministic release scorecards across fixtures, package health, skill budget, and optional live eval transcripts.
- Move operational runbooks into the GitHub wiki and refocus the README on the anti-slop argument and in-process examples.
- Add repo-only `scripts/public_copy_check.py` to keep README and repo-description copy sharp, voice-forward, and free of stiff marketing mush.
- Add mixed-emotional-stance guidance and contract tests for writing that is angry or sarcastic without losing hope, excitement, or restraint.
- Add `$skill-installer`-first install docs, a no-git terminal fallback installer, and a CI check for the one-line install path.
- Add a risograph README banner generated for Dittobot's voice-preserving editing metaphor.
- Add reusable fact-fence and voice-profile-card references.
- Add real `[[boundary: ...]]` ledger parsing.
- Add package-file manifest sharing between install drift checks and repo validation.
- Add stale-file detection for copied installs and stage copy installs before replacing the current skill.
- Add a progressive-disclosure word budget check for `SKILL.md`.
- Add optional live model smoke testing with safer API URL and transcript handling.
- Make live eval reporting track attempted, passed, not-run, and usage totals instead of counting stopped cases as passes.
- Make live-eval saved transcripts hash-only by default, with explicit raw source/output opt-ins.
- Add install drift checks for copied or symlinked skill installs.
- Strengthen voice-profile guidance, emotional anti-flattening, and format preservation.
- Harden deterministic fixture validation for protected facts, modality drift, causality drift, invented details, preambles, and no-dash constraints.
- Add thought-dump default fixtures, source-only live-eval prompts, clarifying-question guards, wrapper detection, ordered-term checks, artifact cleanup checks, and paragraph/bullet constraints.
- Add live-eval case listing, prompt printing, and prompt-mode filtering so source-only thought-dump defaults can be inspected without API calls.
- Add live-eval fail-fast/max-failure controls, hard API setup error stops, richer transcript hashes, and `--no-save-source`.
- Add claim-level regression checks for polarity, required claims, forbidden assertions, and uncertainty preservation.
- Add bad-rewrite and regression-case issue templates, pull request checklist, contributor guide, security/privacy guidance, and release checklist.

## 0.1.0

- Initial public Dittobot skill release.
