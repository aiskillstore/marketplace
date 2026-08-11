# Authoring Skills (aligned to the Agent Skills spec)

Follows the official spec (agentskills.io/specification) and Anthropic's `skill-creator` guidance.

## Anatomy
```
skill-name/
├── SKILL.md          # required: YAML frontmatter + Markdown instructions
├── scripts/          # optional: executable code (deterministic/repetitive work)
├── references/       # optional: docs loaded into context on demand
└── assets/           # optional: TEMPLATES + resources used in output
```
Put document/config **templates in `assets/`** (not `references/`). Put guides/docs the agent reads
in `references/`. Keep file references **one level deep** from SKILL.md — avoid deep chains.

## Frontmatter (spec limits)
```
---
name: kebab-name            # <=64 chars; a-z 0-9 and hyphens; no leading/trailing/double hyphen; matches folder
description: what + when     # <=1024 chars; non-empty; what it does AND when to use it
metadata:                    # optional
  author: name
  version: "0.1.0"
# license, compatibility, allowed-tools are also optional
---
```

## Description = the trigger (make it a little "pushy")
The description is the primary triggering mechanism, and Claude tends to UNDER-trigger skills. Combat
that: state what it does AND explicit contexts, e.g. "...Make sure to use this skill whenever the user
mentions X, Y, or wants Z — even if they don't explicitly say 'X'." Third person, concrete keywords.
- Good: "Draft a release rollout plan for an upcoming single. Use whenever the user says 'plan the
  release', 'build a rollout', mentions a launch timeline, or a release moves to production."
- Weak: "Helps with releases."

## Body
- Imperative, verb-first ("Create the folder", not "You should create").
- **Explain the why** instead of heavy ALL-CAPS MUSTs — modern models follow reasoning better than rules.
- Keep SKILL.md under ~500 lines / <5000 tokens; move depth into `references/` with clear pointers.
- For a reference file over ~300 lines, add a table of contents.
- Include 1-2 input/output examples where useful.

## Validation gotchas (these actually break installs)
- **No angle brackets in `description`** — the loader reads `<...>` as XML tags and rejects it. Use
  `{placeholder}`.
- `name` matches the folder name and obeys the kebab rules above.
- Every skill folder has a `SKILL.md`; don't put loose non-skill folders inside a plugin's `skills/`.
- Validate structure with `skills-ref validate ./my-skill` if available.

## What to author for a new OS
Author every skill under the workspace `plugin/skills/` (the `plugin/` folder is the installable
plugin itself — see `packaging.md`). Expose those same skills to Cursor and Codex through the
workspace `.agents/skills` adapter; do not author a second copy there.
1. An **orchestrator**: `{domain}-intake` — the auto-manage loop as one trigger.
2. One skill per **recurring task** from the brief (work that repeats or needs upkeep — one-off builds
   stay in `work/`, not a throwaway skill).
3. A **doctor** (from `assets/doctor-SKILL.md.tmpl`) — read-only verification surface (health score +
   punch list to `operations/health.md`).
4. A **janitor** (from `assets/janitor-SKILL.md.tmpl`) — runs the doctor, then reconciles + fixes.
5. A **compound-learn** skill (from `assets/compound-learn-SKILL.md.tmpl`) — domain knowledge.
6. A **reflect** skill (from `assets/reflect-SKILL.md.tmpl`) — improves the OS itself into
   `operations/improvements.md` (the 50/50 budget).
7. A **skillify** skill (from `assets/skillify-SKILL.md.tmpl`) — promote proven repeatable work into
   staged, verified skills.
Prefix skills with the domain (e.g. `label-`, `pm-`) so they group together. Repackaging is just
re-zipping `plugin/`, so no separate packager skill is needed.

**Routing (graduated).** While the pack is small, each skill's `description` is the resolver — make it
trigger-rich and non-overlapping. Once skills multiply (descriptions overlap, or `{domain}-doctor`
flags reachability), add an explicit `plugin/skills/RESOLVER.md` (a trigger -> skill table) and keep it
honest. Either way, author a trigger for *every* skill so none goes **dark** (built but unreachable) —
that's what the doctor's reachability check catches.

## Plugin manifests and adapters
- Default the plugin name to `{DOMAIN_SLUG}-os` unless the user explicitly names it.
- Write both manifests with the same `"name"` and `"version"`:
  - `plugin/.claude-plugin/plugin.json`
  - `plugin/.codex-plugin/plugin.json`
- The Codex manifest must include `"skills": "./skills/"` because bundled skills live under
  `plugin/skills/`.
- Create `.agents/skills` as a symlink to `../plugin/skills`. Cursor and Codex both discover project
  skills there. Avoid also creating `.cursor/skills` by default to prevent duplicate skill discovery.

## Skillify proven work into a skill
Read `skillifying-work.md` when turning completed work into a new capability. The important idea is
general, not browser-specific: a successful one-off process becomes a skill only after it has evidence,
verification, and user approval.

1. Start from a proven result (accepted artifact, repeated task, or failure that should not recur).
2. Draft in `work/YYYY-MM-DD-skillify-{name}/`, not directly in `plugin/skills/`.
3. Extract the repeatable process and remove one-off chat/context.
4. Put exact/mechanical work into `scripts/`, `assets/`, or templates only when it removes real
   repetition. Keep judgment and decision rules in `SKILL.md`.
5. Verify with the strongest cheap check for the domain: a script test, a smoke command, a sample
   prompt replay, a fixture comparison, or a small review rubric.
6. Ask before publishing. Move the staged skill into `plugin/skills/{name}/` only after approval, then
   re-zip `plugin/`.

No half-working skills in `plugin/skills/`: staged and failed work is discarded or left under `work/`
as a draft, clearly not installed.

## Optional: rigor via the official skill-creator
Anthropic's `skill-creator` skill adds an eval/iterate loop: write 2-3 realistic test prompts, run
with-skill vs. baseline, review outputs, and optimize the description for triggering accuracy. Use it
when a skill is high-value and you want measured quality, not just vibes. It also ships
`scripts/package_skill.py` to produce the `.skill` file.
