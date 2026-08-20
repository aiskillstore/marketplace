# OKX.AI Trading Hackathon — Core (gates, output rules, reading order)

> Scope: everything the hackathon activity enforces regardless of which question the user asked.
> The step-by-step flow and CLI/MCP reference live in [`hackathon-registration.md`](hackathon-registration.md);
> standalone questions in [`hackathon-faq.md`](hackathon-faq.md). Skill-wide rules (pre-flight,
> wrong-skill guard, activity routing, language, secrets) live in `../SKILL.md`.

Enter one of the user's **existing** Trading ASP agents in the OKX.AI trading hackathon. Wraps the
`onchainos hackathon` CLI command group / `hackathon_register` MCP tool.

This activity never creates an agent identity — it only signs up an ASP that already exists
(`../SKILL.md` §Wrong-skill guard).

## Mandatory reading order

**Before producing ANY user-facing message about hackathon registration, you MUST first read the
matching file below.** Do NOT improvise the format. Do NOT shorten or reorder the fixed templates in
`hackathon-registration.md` — they are product-mandated copy.

| User intent | Reference file |
|---|---|
| "register my agent / ASP for the hackathon", actively walking through registration | [hackathon-registration.md](hackathon-registration.md) — Step 1-4 flow + CLI/MCP reference |
| Standalone question about eligibility, funding, account types, errors, or "can I do X" — not mid-registration | [hackathon-faq.md](hackathon-faq.md) |

If the intent maps to neither, ask which they meant — do **not** invent a freeform format.

`onchainos hackathon --help` lists the subcommands and `onchainos hackathon register --help` its
flags; **learn exact syntax from the CLI, not from memory** (`../SKILL.md` §Command Index). The flag table, return fields, and CLI-side error list live in
[hackathon-registration.md](hackathon-registration.md).

## Gates & execution checklist (registration flow)

Copy this checklist and tick as you go. **Steps 1-4 map 1:1 onto `hackathon-registration.md`** —
their content is there, not duplicated here. **Gates A/B/C** bracket the flow and exist only here,
because its steps cannot state them.

- [ ] **Gate A — Pre-flight** (**BLOCKING**) — `../SKILL.md` §Pre-flight Checks runs before the first `onchainos` command this session, ASP listing included
- [ ] **Gate B — Read-before-write** (**BLOCKING**) — `hackathon-registration.md` is loaded before the first user-facing message
- [ ] **Step 1 — Pick the Trading ASP** (**REQUIRED**)
  - [ ] 1a. Projection printed `{"error": …}`, died with a `jq:` error, or returned `listed:0` while `total > 0` → apply Step 1's Fallback; **none** of these means "no agents"
  - [ ] 1b. The terminal no-ASP template is output only when `M` is 0 **and** 1a has been ruled out
  - [ ] 1c. The submitted `agent_id` comes from this run's list output — never recalled, guessed, inferred, or reconstructed from the user's wording. This is where the id came **from**; whether it may be shown is §Output Rules
  - [ ] 1d. Three ASP preconditions confirmed — **MUST** have the user's own `1` before Step 3; never answer that prompt for them
- [ ] **Step 2 — Choose the competition account** (**REQUIRED**) — `web3` or `cefi`; `cefi` also needs the UID
- [ ] **Step 3 — Submit** — only once 1d and Step 2 both hold a real user reply
- [ ] **Step 4 — Report the result** (**REQUIRED**) — branch on `errorCode`
- [ ] **Gate C — Send-gate** (**BLOCKING**) — §Pre-Delivery Checklist runs before every message

## Output Rules

- Identify the hackathon EXCLUSIVELY by name ("OKX.AI Trading Hackathon") — **never** by its internal activity id, in any format. The CLI does not return that id; do not source it from anywhere else.
- The agent id MAY appear exactly once: in the numbered ASP-selection list ([hackathon-registration.md](hackathon-registration.md) Step 1), so ASPs sharing a name can be told apart. Any later message that refers to the chosen agent at all — confirmation, failure, a follow-up answer — names it **by name only**. The success template names no agent; do not add one back.
- The OKX UID is a user identifier: the CLI never returns it, and when you echo the executed command you **MUST** mask it (`--uid <hidden>`). Never paste a raw UID into the conversation.
- Registration receives value, so there is no confirm-to-spend (`CliConfirming`) gate.
- The JWT is injected by the client layer from the keychain. **NEVER**: log it, print it, or pass it in a flag — leaking it would let an attacker act as the user. The flow creates no new secrets.

## Pre-Delivery Checklist

Runs before every user-facing message — the `hackathon-registration.md` MUSTs that are easy to skip
after a long response. The items already stated above are **anchored, not restated**: verify them at
their own rows.

- [ ] On failure: the branch matches `errorCode`, not the wording of `error` — and `hackathon_service_unavailable` never blames the ASP's eligibility
- [ ] Fixed templates rendered in the user's language, structure unchanged, tutorial URL kept byte-for-byte as a link
- [ ] §Gates 1a-1d still hold for this message — Fallback ruled out, no-ASP branch earned, `agent_id` from this run's list, the user's own `1`
- [ ] §Output Rules holds — activity id never shown, agent-id displayed at most once, UID masked
