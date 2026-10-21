# Model Gateway

Use this playbook for **S10–S16**, **S14b**, **C03**, **C06**, and **C07**. Parent skill: `SKILL.md` in this folder (or https://raw.githubusercontent.com/VectoreeAI/vectoree-skills/main/skills/vectoree/SKILL.md)

Need a project API key first (`scenarios/connect.md`). App inference uses OpenAI-compatible HTTP. Agent ops use the CLI. Do not mix them.

---

## Product models

Default for `ai chat` / `ai snippet` / Codex is `vectoree/auto`. Catalog ids otherwise come from `ai models search`, not from guessing OpenAI-only names.

| Model | Kind | Behavior |
|-------|------|----------|
| `vectoree/auto` | router | Default. Picks a cheap or available catalog model per request. Do not hardcode a vendor. Omit `--model`. |
| `deepseek/deepseek-v4-pro` | chat | Hot. Codex menu 2. |
| `qwen/qwen3-max` | chat | Hot. Codex menu 3. |
| `qwen/qwen-plus` | chat | Hot. Codex menu 4. |
| `z-ai/glm-5.2` | chat | Hot. Codex menu 5. |
| `qwen/qwen3.5-plus-02-15` | chat | Hot. Codex menu 6. |
| `qwen/qwen3-coder-flash` | chat | Hot. Codex menu 7. |
| `alibaba/wan-3.0` | video | Hot. Do not use with `ai chat` or Codex. |
| `alibaba/wan-2.7-t2v` | video | Hot. Do not use with `ai chat` or Codex. |
| `alibaba/happyhorse-1.1-t2v` | video | Hot. Do not use with `ai chat` or Codex. |
| `alibaba/wan-3.0-prime` | video | Hot. Do not use with `ai chat` or Codex. |

---

## S10: which models?

Catalog models expose `inputModality` and `outputModality`. Filter on **both** when the developer asks for TTS, STT, video, embeddings, etc. Do not guess slugs from OpenRouter names alone.

```bash
npx @vectoree/cli ai models list
npx @vectoree/cli ai models search deepseek
npx @vectoree/cli ai models get <model-id>

# filter by output modality (what the model produces)
npx @vectoree/cli ai models list --output-modality speech          # TTS
npx @vectoree/cli ai models list --output-modality transcription   # STT output
npx @vectoree/cli ai models list --output-modality video

# filter by input + output (STT: audio in → transcription out)
npx @vectoree/cli ai models list --input-modality audio --output-modality transcription

# combine search + modality
npx @vectoree/cli ai models search whisper --output-modality transcription
npx @vectoree/cli ai models search veo --output-modality video
```

Modality values mirror OpenRouter: `text`, `image`, `audio`, `speech`, `transcription`, `video`, `embeddings`, `rerank`, `file`. Pass `--json` when you need to parse. Comma-separate for AND filters (e.g. `--input-modality text,image`).

**Do not probe TTS/STT/video with `ai chat`.** That hits `/chat/completions` and fails with `GATEWAY_NO_AVAILABLE_CHANNEL`. Use the matching command (CLI ≥ 0.1.9):

```bash
npx @vectoree/cli ai speech "hello" --model qwen/qwen-audio-3.0-tts-flash
# omit --voice unless the developer named one; do not default to OpenAI "alloy"
npx @vectoree/cli ai transcribe --model <stt-id> --file clip.wav
npx @vectoree/cli ai image "a red apple" --model <image-id>
npx @vectoree/cli ai video "a cat walking" --model <video-id>
npx @vectoree/cli ai embed "hello" --model <embedding-id>
npx @vectoree/cli ai snippet --model <id>
```

Runtime paths: `POST /api/v1/audio/speech`, `/audio/transcriptions`, `/images`, `/videos` (async job, then poll), `/embeddings`.

---

## S12: ping

```bash
npx @vectoree/cli ai chat "ping"   # default: vectoree/auto
```

---

## S13: pick something cheap that works

```bash
npx @vectoree/cli ai chat "ping"   # default: vectoree/auto
```

---

## S11 / C03: AI chat page

```bash
npx @vectoree/cli ai models search deepseek
npx @vectoree/cli ai chat "ping"
npx @vectoree/cli ai snippet --model vectoree/auto --lang ts
```

Paste the snippet into a **server** route (API route or server action). The browser calls your server; your server calls Vectoree. Do not put `VECTOREE_API_KEY` in a client bundle.

```ts
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: `${process.env.VECTOREE_API_URL}/api/v1`,
  apiKey: process.env.VECTOREE_API_KEY,
});
```

Runtime path: `POST {VECTOREE_API_URL}/api/v1/chat/completions`. Fetch `docs get ai-integration-sdk` if you need more shapes; still call the Vectoree origin, not a third-party dashboard key.

Done when `ai chat` works and the page can send a message.

---

## S14: is the gateway up / how much did we spend?

```bash
npx @vectoree/cli ai status
```

Usage lives in Dashboard → Organization → Billing until `ai usage` exists. Do not invent a usage CLI.

## S14b: empty wallet / top-up

`402` with `BILLING_WALLET_NOT_ACTIVATED` or "Organization balance is insufficient" means the **org wallet** has no funds. The agent cannot charge a card.

1. Stop. Do not retry `ai chat` / Codex / `tools search`.
2. Send this URL to the human owner in the chat: `{VECTOREE_API_URL}/dashboard/organization/billing` (default `https://vectoree.ai/dashboard/organization/billing`).
3. Or open it: `npx @vectoree/cli billing open` (CLI ≥ 0.1.14). If that command is missing, open the URL in the browser yourself.

The 402 error body already includes this URL. Copy it if present.

---

## S15 / C06: migrate existing OpenAI calls

1. `npx @vectoree/cli current` and `ai status`.
2. Search the repo for `openai`, `baseURL`, `OPENAI_API_KEY`, `api.openai.com`.
3. `npx @vectoree/cli ai models search <vendor or name>` and pick a real catalog id (or `vectoree/auto`).
4. `npx @vectoree/cli ai snippet --lang ts` (or `python`) and apply:
   - `baseURL` → `{VECTOREE_API_URL}/api/v1`
   - `apiKey` → `VECTOREE_API_KEY`
   - `model` → the id from search
5. Probe with `ai chat "ping" --model <id>`.

Done when `baseURL` points at the project gateway and model ids come from search.

---

## S16 / C07: point Codex at Vectoree

This switches **Codex CLI** (and ChatGPT desktop, which shares `~/.codex`) to the Vectoree Model Gateway. It is not C01 (app backend). You still need a **project key** (`sk-ve-v1-…`) **or** an **employee key** (`ek-ve-v1-…`) — they are different credentials. Do not use the instance master key (`ik_`).

Human docs (copy-paste commands): https://docs.vectoree.ai/codex

**Human, interactive (preferred):** tell the user to paste one of these into their own terminal, or run them yourself if you have shell access and the user confirmed:

```bash
# macOS / Linux
bash <(curl -fsSL https://vectoree.ai/scripts/codex-vectoree-setup.sh)
```

```powershell
# Windows
irm https://vectoree.ai/scripts/codex-vectoree-setup.ps1 | iex
```

First menu: model slug (`1`–`7` / `c`) or `r` restore. Menu **1** is `vectoree/auto`. On install, the script asks how to get a key:

1. **Project key** — device-code browser login (same as `vectoree login --use-device-code`), pick a project, mint `sk-ve-v1-…`
2. **Employee key** — same login, pick an org with an active Employee AI seat, rotate `ek-ve-v1-…`
3. **Paste** an existing key

Optional env: `VECTOREE_API_KEY` (skips login), `VECTOREE_BASE_URL` (default `https://vectoree.ai/api/v1/`), `CODEX_HOME`. It also reuses `.vectoree/config.json` from a prior `vectoree link` when present.

**Agent, non-interactive:** do not replace the whole file (MCP servers and other keys must stay). Backup `~/.codex/config.toml` first, then set:

```toml
model = "vectoree/auto"
model_provider = "vectoree"
model_reasoning_effort = "high"

[model_providers.vectoree]
name = "Vectoree"
base_url = "https://vectoree.ai/api/v1/"
wire_api = "responses"
experimental_bearer_token = "sk-ve-v1-..."
```

`wire_api = "responses"` matches `POST /api/v1/responses`. Put the token from `.vectoree/config.json` or the user; never echo it.

Verify: Codex CLI startup banner shows `model: <slug>`. ChatGPT desktop model picker shows **Custom** (expected in API-provider mode; account history UI can look empty; local `~/.codex/sessions` are not deleted).

Restore: re-run the script, choose `r`, fully quit and reopen Codex / ChatGPT.

If Codex returns `BILLING_PRICE_NOT_CONFIGURED`, the slug is wrong or unpriced. `ai models search` / Dashboard Admin → Models. `*-latest` aliases often need the `~` prefix.
