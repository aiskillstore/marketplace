# Creation Handoff

## Result

- Skill: `qiaomu-campus-resume` 1.5.0
- Job: use a one-question-at-a-time evidence interview or an uploaded resume to collect and confirm student job-search facts, then generate one role-appropriate, locally validated HTML/PDF resume.
- Local status: installed in the canonical Agent Skills directory.
- Publication: https://github.com/joeseesun/qiaomu-campus-resume, release v1.5.0; the post-release clean-install result is reported externally after the tag exists.
- Rollback: private local backup retained outside the public package.

## Reference skills studied

- [alirezarezvani/claude-skills: grill-me](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/grill-me/skills/grill-me): skills.sh showed 1K installs on 2026-08-04. Learned one-question cadence, recommendation attachment, depth-first branches and dependency order; applied in `references/intake-and-interview.md`.
- [mattpocock/skills: grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me): canonical upstream concept; repository had 201,786 stars on 2026-08-04. Learned relentless narrowing; adapted to supportive student evidence coaching.
- [addyosmani/agent-skills: interview-me](https://github.com/addyosmani/agent-skills/tree/main/skills/interview-me): repository had 81,485 stars on 2026-08-04. Learned correctable hypotheses, concise restatement and explicit confirmation; applied in the per-turn format and generation gate.
- Existing visual references remain [tw93/kami](https://github.com/tw93/kami) and [mmmlllnnn/ResumeCollection](https://github.com/mmmlllnnn/ResumeCollection), with assets excluded and only layout mechanisms adapted.

The mutable signals above measure adoption or repository attention, not user ratings or skill quality. Rating evidence was unavailable.

## Absorbed and rejected

- Keep: one question per turn, a concrete current judgment, depth-first branch resolution, periodic restatement and explicit confirmation.
- Adapt: generic design decisions become student evidence loops—context, personal ownership, action, result, proof and interview explainability.
- Reject: hostile tone, batched forms, arbitrary 95% confidence, codebase-specific companion tools, photos, sidebars, rounded cards and interview-outcome promises.
- Invent: local `interview-ledger.json`, deterministic readiness checker, two-evidence-loop minimum, skill-to-evidence linking, unresolved-fact blocking, sensitive-field rejection and one-PDF default.

## Advantages and highlights

- **Design advantage**: each question must close a specific resume evidence gap, so the dialogue does not become a generic career questionnaire.
- **Design advantage**: users can say “skip,” “unknown,” “stop,” or request a draft; the skill reports missing facts instead of filling them with model inference.
- **Validated advantage**: deterministic readiness checks cover target, contact, education, two evidence loops, linked skills, blocking uncertainties, explicit confirmation and sensitive-field rejection.
- **Validated advantage**: package validation and 15 unit tests pass locally; trigger evaluation includes dialogue requests and the adjacent mock-interview exclusion.
- **Hypothesis**: one-question dialogue may be easier for students and surface stronger stories than a giant form, but live student completion, recruiter blind review, named ATS parsing and employment outcomes remain `missing evidence`.

## Verification and limits

- `assess_interview.py` passes the confirmed fixture and rejects missing confirmation, one-evidence-only and sensitive-field variants.
- The existing renderer, six optional themes and six ResumeCollection reference presets remain intact; batch output is now explicit opt-in rather than the default.
- Existing typography/PDF evidence remains valid for renderer 1.4; the v1.5 change does not alter PDF layout code.
- Deliberately excluded: third-party upload, account access, job submission, mock interview, academic CV, executive resume, portfolio website and cover-letter workflows.
- Missing evidence: live multi-turn student evaluation, provider-backed baseline comparison, recruiter blind review, cross-platform ATS upload tests and employment outcomes.
