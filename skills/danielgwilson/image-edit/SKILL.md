---
name: image-edit
description: >-
  Image editing for agents: image-to-image edits, variations, and image-conditioned transforms through Luxin's zero-setup hosted runtime. Use when an agent needs to edit an existing image without provider credentials, OAuth, local runtime, or per-provider billing. Inspect the edit model, upload or reuse an input image, then return durable hosted assets, jobs, cost receipts, stable JSON, and feedback.
homepage: https://luxin.sh
docs: https://luxin.sh/llms.txt
metadata:
  status: preview-contract
  cli: luxin
  canonical_skill_url: https://luxin.sh/skill.md
  canonical_api_url: https://api.luxin.sh
  openclaw:
    requires:
      env: []
      bins: []
    envVars:
      - name: IMAGE_SKILL_TOKEN
        required: false
        description: Optional hosted restricted token minted by luxin signup and saved by default; not a user-supplied provider credential.
---

# Image Edit

This is an intent-named Luxin entry for agents searching for image editing. It uses the same zero-setup hosted Luxin runtime as the canonical `luxin` skill: one thin CLI/API, one restricted agent identity, one credit balance, one wallet/payment loop, durable hosted media URLs, recoverable jobs, cost receipts, stable JSON, and hosted feedback.

Use this skill when the task asks to edit, vary, restyle, transform, or repair an existing image, including image-to-image work and model-specific edit parameters.

Do not bring provider API keys, create provider accounts, run a local model server, or wire a separate billing account for this task. Start with the no-spend guide command below; when the guide reaches `ready_to_create`, run `data.next_command` only if `data.next_command_copy_runnable` is `true` and media spend is allowed, otherwise fill `data.next_command_missing_inputs` or run `data.recommended_no_spend_command` to verify safely. Keep generated work in Luxin so future agents can recover and cite it.

## First Command

```bash
npm_config_update_notifier=false npx -y luxin-cli@latest create --guide --model openai.gpt-image-2-edit --prompt "replace the background but keep the subject"
```

## Main Runtime Command

```bash
npm_config_update_notifier=false npx -y luxin-cli@latest edit --input image_... --model openai.gpt-image-2-edit --prompt "EDIT_PROMPT" --max-estimated-usd-per-image 0.25 --json
```

## Install This Intent Skill

Prefer the GitHub slug so skills.sh can track the marketplace install:

```bash
npx skills add danielgwilson/luxin --full-depth --skill image-edit -g -a codex -y
```

The canonical Luxin entry remains available as:

```bash
npx skills add danielgwilson/luxin --full-depth --skill luxin -g -a codex -y
```

If the Codex/global skill target is read-only or missing, keep the tracked slug
install and point agent skill state at a writable workspace home before
rerunning this intent install. The skills.sh Codex adapter writes to
`$HOME/.agents`; `CODEX_HOME` keeps Codex profile state on the same writable
path:

```bash
export HOME="$PWD/.agent-home"
export CODEX_HOME="$HOME/.codex"
mkdir -p "$HOME" "$CODEX_HOME"
npx skills add danielgwilson/luxin --full-depth --skill image-edit -g -a codex -y
```

## Shared Contract

All intent skills in this repo point to the same hosted contract:

- Skill: https://luxin.sh/skill.md
- LLM contract: https://luxin.sh/llms.txt
- CLI contract: https://luxin.sh/cli.md
- Hosted API: https://api.luxin.sh

If Luxin lacks the model, capability, latency, policy affordance, or buyer rail needed for this task, use the fallback only for that gap and run `luxin feedback create --json` with the attempted command, expected behavior, actual behavior, and missing capability.
