
# Onchain OS — How to Play (Entry Router)

The first-time / "I don't know what to do" entry point. Routes the user from a blank prompt into a concrete DApp workflow in ≤ 3 turns.

> **Pre-flight:** already run by the `okx-guide` hub (`SKILL.md` §Pre-flight Checks) before this flow is loaded — do NOT run it again here.

## Authoring Pattern — Free Zone vs Fixed Zone

Most user-facing copy in this flow is split into two parts:

- **Free zone** — the agent answers the user's actual question or acknowledgement first, in 1–5 sentences, contextually woven. No fixed copy. The user shouldn't feel like they hit a script.
- **Fixed zone** — the canonical English template block (welcome banner, login options, API Key heads-up). At runtime:
  - Render all natural-language prose in the user's language.
  - **Quoted reply words inside prose (e.g. `"login"`) MUST translate with their sentence.** Leaving an English quoted word inside otherwise-translated Chinese / Japanese / etc. prose is a translation bug — the quotes do NOT make the word a literal trigger.
  - Keep literal: emojis, `{placeholders}`, `1–N`, code identifiers / commands / URLs, markdown structure.

This applies to: **Welcome Banner**, **Login Method Choice**, and **API Key Login** Step 1 heads-up.

**MUST**: **Bridging is mandatory.** End the free zone with a transitional half-sentence (e.g. "let me drop the menu" / "here's where to start ↓") — never with a hard period followed by an unrelated fixed-zone line. Self-check before emitting: read the free-zone tail + first fixed-zone line as a single unit; if they feel like two separate posts pasted together, rewrite the free-zone tail.

## Status Check

**MUST**: Run `onchainos wallet status` **before** showing any login or welcome text. Use the `loggedIn` field to branch.

```
onchainos wallet status
```

- `loggedIn: false` → render the **logged-out** Welcome Banner.
- `loggedIn: true`  → render the **logged-in** Welcome Banner.

---

# Welcome Banner

**MUST**: Render the banner from `welcome.md` — it covers placeholders (`{evm_address}` / `{solana_address}` / `{balance}` from `wallet balance`; geoblock variant from `wallet geoblock`), the template, and pick routing (Step 4). Variant A = 4 picks (Polymarket allowed); Variant B = 3 picks (Polymarket geoblocked). Numbered picks are interpreted strictly against the currently-rendered menu (digit-routing contract per welcome.md §4). Never fabricate addresses or balance. If `wallet balance` fails despite `loggedIn: true` (stale session — refresh token expired), prompt the user to log in again per welcome.md §2.2 instead of rendering a partial banner.

---

# Login Method Choice

Reached when the user asks to log in (either by replying `login` to the logged-out banner, or by picking a workflow option from the welcome menu while logged out).

**Free zone (1–5 sentences, agent's own words):** answer whatever the user actually asked / acknowledged. If they came from a workflow pick, briefly explain that login unlocks that workflow. Then segue naturally into the fixed-zone choice below.

**Fixed zone — render the template below in the user's language**:

```
Welcome to Agentic Wallet — the Onchain OS wallet built for agents. Pick a login method:

1. 📧 Email (recommended — 30 seconds)
2. 🔑 API Key (already an OKX developer? Fastest path)

Reply 1 or 2 ↓
```

If the user replies `1` or "email" → **Email Login**.
If the user replies `2` or "API Key" → **API Key Login**.

## Email Login

Handled by `okx-agentic-wallet` skill's Authentication section. Steps:

1. Ask for email → `onchainos wallet login <email> --locale <locale>`
2. Ask for OTP code → `onchainos wallet verify <code>`
3. On success → **Post-login routing** below.

## API Key Login

Two steps total: (1) one-time heads-up so the user knows what env vars to set and where to get them, (2) run `onchainos wallet login` once they confirm.

### Step 1 — Heads-up (one-shot, fixed zone)

**Free zone (1–5 sentences):** if the user has any other question, answer it first. Then segue naturally into the heads-up.

**Fixed zone — render the template below in the user's language**:

```
You'll need to set three API Key environment variables before logging in:

1. `OKX_API_KEY` — API Key
2. `OKX_SECRET_KEY` — Secret Key
3. `OKX_PASSPHRASE` — Passphrase

You can find these at https://web3.okx.com/onchainos/dev-portal.

**Attention ⚠️:** Do not paste credentials into the chat — follow the dev-portal instructions and set them locally.
```

Then **stop and wait** for the user to confirm they're ready (e.g. "done / ok / ready").

### Step 2 — Login

Once the user confirms, run:

```
onchainos wallet login
```

On success → **Post-login routing** below. On login failure, surface the error and ask the user to verify their env vars (do NOT re-show the heads-up — they already saw it).

**NEVER**:
- Do NOT accept API Key / Secret / Passphrase inline in chat. If the user pastes credentials in chat: do NOT echo, do NOT use the values, ask them to delete the message + rotate the keys + set the env vars locally instead.
- Do NOT walk the user through generating keys, opening URLs, creating `.env` files, editing `.gitignore`, or any other multi-step setup. The heads-up is one-shot — they handle their own local setup.
- Do NOT ask the user to paste the browser URL or any callback back to the CLI. The dev-portal is read-only.

## Post-login routing

After login completes successfully:

- If the user came from picking the **OKX.AI option** (Reply `1`) while logged out: automatically load `ai-guide.md` and follow it. Do NOT re-render the welcome banner.
- If the user came from picking the **Daily brief** option (option `4` in Variant A / option `3` in Variant B) while logged out: automatically load `~/.onchainos/workflows/daily-brief.md` and follow it. Do NOT re-render the welcome banner.
- If the user came from picking any other **workflow pick** while logged out: automatically load the corresponding workflow file (`~/.onchainos/workflows/<file>.md`) and follow it. Do NOT re-render the welcome banner.
- If the user came from replying `login` (or equivalent) to the logged-out banner: render the **logged-in** Welcome Banner so they see their addresses + balance.

---

# Free-form fallback

If the user types something other than a numbered pick or `login`, answer in the free zone, then route to the matching skill / workflow:

| Intent | Route to |
|---|---|
| meme sniping / pump.fun / new launches, or follow smart money / KOL / whale | `okx-dex` (or load `smart-money-signals.md`) |
| yield / earn / stake / DeFi | `okx-defi` |
| login (free-form, not as a banner reply) | this skill's **Login Method Choice** |
| named DApp + action verb (Aave / Hyperliquid / etc.) | `okx-dapp-discovery` |

---

## Acceptance Criteria

1. **Banner variant matches auth state** — `loggedIn: false` renders the logged-out variant (no addresses); `loggedIn: true` renders the logged-in variant (addresses + balance).
2. **Skill picks load without login gate** — Polymarket (option 2 in Variant A) and USDC APY (option 3 in A / option 2 in B) load even when logged out; each loaded skill handles its own auth.
3. **OKX.AI (Reply 1) and Daily brief (option 4 in A / option 3 in B) gate on login** — when logged out, route through Login Method Choice first, then auto-resume the chosen target (`ai-guide.md` or `daily-brief.md`) WITHOUT re-rendering the welcome banner. Smart-money / new-token intents are no longer numbered picks but remain reachable via the free-form fallback table (`okx-dex`).
4. **Turn budget** — ≤ 3 turns end-to-end for a new user; ≤ 2 turns for a returning user picking a workflow + login.
5. **Disclaimer placement** — the disclaimer is the final segment of every rendered banner (both variants, both auth states).
6. **Stale-session fallback** — when `wallet status` returns `loggedIn: true` but `wallet balance` fails (e.g. expired refresh token) or lacks the address / balance fields, the flow prompts re-login (routes to Login Method Choice) instead of rendering a partial or fabricated logged-in banner; after re-login it renders the logged-in banner.

