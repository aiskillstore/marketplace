# Design Summary

- Skill tier: complex
- Trigger surface: release prep, release checklist, rollout coordination, rollback planning
- Deterministic content: checklist stages, migration prompts, packet sections, and stakeholder message scaffolds
- Flexible content: risk commentary, go/no-go judgment, and escalation notes
- Package choice: `SKILL.md`, `agents/interface.yaml`, `manifest.json`, `references/`, `scripts/`, `evals/`, `input/`, `outputs/`
- Boundary rule: use for release packet creation and readiness review, not for general project planning or one-off announcements
- Validation goal: the generated packet must contain release scope, migration notes, rollout plan, rollback triggers, stakeholder communication, and an explicit decision block
