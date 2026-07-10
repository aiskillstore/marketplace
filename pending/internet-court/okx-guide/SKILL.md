---
name: okx-guide
description: >-
  Onchain OS onboarding and guide hub for first-time use, product introductions, OKX.AI, and
  customer-support intents. Classifies requests and routes them through the Intent Routing
  table. Use for questions about what Onchain OS is, what it can do, getting started,
  tutorials, onboarding, first-time setup, and introductions; for OKX.AI explanations and
  role-registration routing across User, ASP, and Evaluator roles, including spelling and
  language variants; and for Help Center, customer service, complaints, feedback, bug reports,
  FAQs, or user-guide requests. Do not use for direct on-chain actions such as swaps, wallet,
  balance, or token operations, or for Agent task lifecycle actions such as publish, accept,
  deliver, or dispute; those have dedicated skills.
license: MIT
metadata:
  author: okx
  version: "4.2.1"
  homepage: "https://web3.okx.com"
---

# Onchain OS — Guide Hub (Onboarding · OKX.AI · Support)

The single entry point for onboarding, OKX.AI onboarding, and customer-support intents. Classify the user's intent, load the matching reference file, and follow it to completion. Each reference file is self-contained (it carries its own flow steps and acceptance criteria).

## Pre-flight Checks

**MUST**: Run the shared preflight **only for the onboarding flow** (§1 → `references/how-to-play.md`): read `../okx-agentic-wallet/_shared/preflight.md`; if that file does not exist, read `_shared/preflight.md` instead.

- **OKX.AI** (§2 → `references/ai-guide.md`): do **NOT** run the shared preflight here. `ai-guide.md` does its own login/identity check via `onchainos wallet status`, and the registration playbooks run their own preflight. (This matches the pre-merge standalone behavior and avoids an extra CLI round-trip.)
- **Support** (§3 → `references/ai-support.md`): conversation-layer only (no CLI) — no preflight.

## Intent Routing

Match the user's intent to a row, then read the Reference file(s) **before** responding and follow them exactly.

| User Intent | Reference |
|---|---|
| First-time / "what is onchainos" / "what can it do" / how to use / how to play / getting started / tutorial / "I just installed" / "now what" / "where do I start" / "I'm new" / welcome banner + numbered-pick routing | [`references/how-to-play.md`](./references/how-to-play.md) |
| OKX.AI — "what is OKX.AI" / "how to use OKX.AI" / "OKX.AI quick start" (any spelling variant) / register a role (User / ASP / Evaluator) / platform detection / registered-user home | [`references/ai-guide.md`](./references/ai-guide.md) |
| Customer support / talk to a human / customer service / file a complaint / give feedback / report a bug or system error / Help Center / FAQ / user guide / "something is broken" | [`references/ai-support.md`](./references/ai-support.md) |

## Disambiguation

**MUST**: When an opener could match more than one row, prefer the more specific intent:

- The subject is explicitly **OKX.AI** (any spelling / spacing / casing / typo variant) → **ai-guide.md**, even when phrased as onboarding ("how do I play OKX.AI").
- Generic **Onchain OS** onboarding, or a blank "now what / where do I start / I'm new" with no product named → **how-to-play.md**.
- Intent to reach a **human / complaint / feedback / bug / FAQ / help docs** → **ai-support.md**.
