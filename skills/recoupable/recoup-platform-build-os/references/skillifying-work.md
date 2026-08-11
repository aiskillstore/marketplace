# Skillifying Work

Skillifying is the promotion path from **work that succeeded once** to **a durable capability the
workspace can reuse**. It is domain-agnostic: a technical workspace may produce scripts and tests; a
marketing workspace may produce a repeatable brief, checklist, examples, and review rubric. The point
is the same: the next agent should not rediscover the process from scratch.

## When to skillify
- Skillify when a task will repeat, must be maintained, or a failure should become structurally hard
  to repeat.
- Do **not** skillify one-off output. Put it in `work/{project}/YYYY-MM-DD-…/`, capture any reusable
  lesson in `knowledge/`, and stop.
- Ask after meaningful work: **"Will this be done again or need upkeep?"** If yes, offer to
  skillify it.

## Promotion loop
1. **Prove provenance.** Start from a real completed task, artifact, conversation, or failure. If you
   cannot identify the accepted result and the steps that produced it, do not synthesize a skill from
   vibes.
2. **Name the capability.** Choose a short kebab-case name and 3-5 concrete trigger phrases the user
   is likely to say.
3. **Extract the invariant process.** Keep the parts that repeat. Remove chat fragments, false starts,
   and one-off details.
4. **Separate judgment from exact work.** The `SKILL.md` carries the process and decision rules.
   Deterministic or mechanical work belongs in `scripts/`, `assets/`, or templates, with checks where
   practical.
5. **Stage before publishing.** Draft in a dated `work/YYYY-MM-DD-skillify-{name}/` folder first.
   Never leave a half-working skill in `plugin/skills/`.
6. **Verify for the domain.** Use the strongest cheap proof available:
   - code/script skill: unit test or smoke command against a fixture/sample;
   - document/process skill: run it against a sample prompt or prior artifact and compare to the
     accepted result;
   - review/quality skill: write 2-3 scenario prompts or a rubric and confirm the skill catches the
     important failure.
7. **Ask before committing.** Show the proposed name, triggers, verification result, and destination.
   Only move the staged skill into `plugin/skills/{name}/` after approval.
8. **Repackage and register.** Re-zip `plugin/`, update any plugin README/index, and note the new skill
   in `artifacts/dashboard.html` or `operations/routines.md` if it changes how the OS is run.

## Minimum skillified bundle
- `plugin/skills/{name}/SKILL.md` with valid frontmatter and trigger-rich description.
- Supporting `scripts/`, `assets/`, or `references/` only when they remove real repetition.
- A verification note in the staging folder or `SKILL.md` describing how it was tested.
- A durable learning in `knowledge/` when the skill came from a failure or important decision.
