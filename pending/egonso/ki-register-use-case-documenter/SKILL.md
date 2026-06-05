---
name: ki-register-use-case-documenter
description: Document AI use cases for EU AI Act governance, inspect code or interview users, then validate and submit confirmed manifests to KI-Register.
metadata:
  homepage: https://kiregister.com/developers/agent-kit
  openclaw:
    homepage: https://kiregister.com/developers/agent-kit
    requires:
      anyBins:
        - node
    primaryEnv: KI_REGISTER_API_KEY
---

# KI-Register Use Case Documenter

Use this skill when an AI application, process, or workflow should become a structured KI-Register use case for EU AI Act-oriented governance, audit preparation, procurement, supplier requests, or internal review.

The operating principle is simple: document first, validate the manifest, get explicit human confirmation, then submit to KI-Register when API credentials are available.

## Primary outputs

- `docs/agent-workflows/<slug>/manifest.json`
- `docs/agent-workflows/<slug>/README.md`

The manifest is the canonical machine-readable source. The README is the human-readable review surface for operators, legal, compliance, product, and engineering teams.

## Setup and account flow

1. If the Agent Kit repository is present, use its CLI from the package root: `node ./bin/studio-agent.mjs`.
2. If the Agent Kit is vendored inside another repo as `agent-kit/`, use: `node ./agent-kit/bin/studio-agent.mjs`.
3. If no local onboarding exists, run `studio-agent onboard` or `node ./bin/studio-agent.mjs onboard`.
4. If the user does not have a KI-Register account or API key, send them to `https://kiregister.com/developers/agent-kit` or directly to `https://kiregister.com/settings/agent-kit`. They should sign in or create an account, create or choose the target register, create one scoped Agent Kit API key, and copy the generated command.
5. Keep `KI_REGISTER_API_KEY` in the environment or a local secret store. Do not write API keys into Git, manifests, README files, logs, screenshots, or skill files.

## Capture modes

Use the smallest mode that can produce a defensible use case record:

- **Codebase inspection**: When the user points at a repo, inspect README files, app routes, API routes, config, prompts, workflows, scripts, tests, and docs. Infer only facts that are supported by local evidence. Mark unclear areas as missing and ask targeted follow-up questions.
- **Stakeholder interview**: When the process is not visible from files, ask one sharp question at a time. Cover purpose, owner, systems, data, decision influence, human checkpoints, risks, controls, and artifacts.
- **Low-friction capture**: When enough context is already known, run `studio-agent capture` with flags or an input JSON file, then let the CLI ask only for missing required fields.

## Required coverage

Capture at least:

- documentation type: `application`, `process`, or `workflow`
- title, purpose, and owner role
- systems in execution order
- usage contexts and data categories
- decision influence
- trigger events and process steps
- human checkpoints, risks, controls, and artifacts

Useful EU AI Act-oriented review questions:

- What is the intended purpose of the AI use case?
- Which humans can review, override, stop, or approve outputs?
- Which data categories enter the workflow?
- Does the AI prepare, assist, or automate a decision?
- Which logs, prompts, policies, SOPs, vendor docs, or review artifacts support the record?
- Which operational controls reduce known risks?

## Command workflow

Preferred commands:

```bash
node ./bin/studio-agent.mjs onboard
node ./bin/studio-agent.mjs capture
node ./bin/studio-agent.mjs interview
node ./bin/studio-agent.mjs validate ./docs/agent-workflows/<slug>/manifest.json
```

Submit after explicit confirmation:

```bash
export KI_REGISTER_API_KEY="akv1.<scopeId>.<keyId>.<secret>"
export KI_REGISTER_REGISTER_ID="reg_123"

node ./bin/studio-agent.mjs submit \
  ./docs/agent-workflows/<slug>/manifest.json \
  --endpoint "https://kiregister.com/api/agent-kit/submit"
```

The submit command must validate locally first. If the API key, register id, endpoint, or manifest is missing or invalid, stop and report the concrete blocker.

## Behavior expectations

- Prefer updating an existing workflow folder over creating duplicates for the same operational use case.
- Never submit an inferred manifest without showing the summary and getting explicit human confirmation.
- If the user asks for best-effort documentation from a codebase, create a draft with evidence-backed facts and clear unknowns.
- Keep the legal boundary clear: this supports structured governance documentation and review; it is not legal advice or a conformity assessment.
- Do not overclaim risk class. Use available facts and leave uncertain classification work for review.
- Keep secrets out of generated files. API keys belong in environment variables or secret stores.

## Repo rules

When working inside the KI-Register studio application repo:

- Before Firestore or schema changes, read `docs/DATA_MODEL_AND_QUERIES.md`.
- If the change affects rules, indexes, or deployment steps, also read `docs/manual_steps.md`.
- If routing is unclear, shortlist nearby docs with `docs/route-map.md` and the relevant sprint note before touching app surfaces.

## Portability

- The CLI is plain Node and does not require framework-specific runtimes.
- The canonical machine format is `manifest.json`.
- If an agent system has no skill loader, hand it this `SKILL.md` plus `../../schemas/studio-use-case.schema.json`, `../../examples/sample-use-case.json`, and `../../docs/direct-submission-to-ki-register.md`.
- Agents that support custom slash commands can map a shortcut to `studio-agent capture`.
- Outside the KI-Register studio repo, omit the repo-specific rules above and rely on the Agent Kit schema, sample manifest, CLI validation, and KI-Register API onboarding flow.
