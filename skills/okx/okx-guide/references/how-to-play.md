
# Onchain OS — How to Play (Entry Router)

The first-time / "I don't know what to do" entry point. Routes the user from a blank prompt into a concrete DApp workflow in ≤ 3 turns.

> **Pre-flight:** already run by the `okx-guide` hub (`SKILL.md` §Pre-flight Checks) before this flow is loaded — do NOT run it again here.

## Authoring Pattern — Free Zone vs Fixed Zone

Most user-facing copy in this flow is split into two parts:

- **Free zone** — the agent answers the user's actual question or acknowledgement first, in 1–5 sentences, contextually woven. No fixed copy. The user shouldn't feel like they hit a script.
- **Fixed zone** — the canonical English template block (welcome banner). At runtime:
  - Render all natural-language prose in the user's language.
  - **Quoted reply words inside prose (e.g. `"login"`) MUST translate with their sentence.** Leaving an English quoted word inside otherwise-translated Chinese / Japanese / etc. prose is a translation bug — the quotes do NOT make the word a literal trigger.
  - Keep literal: emojis, `{placeholders}`, `1–N`, code identifiers / commands / URLs, markdown structure.

This applies to the **Welcome Banner**.

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

# Login

Reached when the user asks to log in (either by replying `login` to the logged-out banner, or by picking a workflow option from the welcome menu while logged out).

**Free zone (1–5 sentences, agent's own words):** answer whatever the user actually asked / acknowledged. If they came from a workflow pick, briefly explain that login unlocks that workflow. Then start login.

For the login flow, follow the `okx-agentic-wallet` skill's **Authentication** section (run `onchainos wallet login`). On success → **Post-login routing** below.

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
| meme sniping / pump.fun / new launches, or follow smart money / KOL / whale | `okx-dex-market` (or load `smart-money-signals.md`) |
| yield / earn / stake / DeFi | `okx-defi` |
| login (free-form, not as a banner reply) | this skill's **Login** |
| named DApp + action verb (Aave / Hyperliquid / etc.) | `okx-dapp-discovery` |

---

## Acceptance Criteria

1. **Banner variant matches auth state** — `loggedIn: false` renders the logged-out variant (no addresses); `loggedIn: true` renders the logged-in variant (addresses + balance).
2. **Skill picks load without login gate** — Polymarket (option 2 in Variant A) and USDC APY (option 3 in A / option 2 in B) load even when logged out; each loaded skill handles its own auth.
3. **OKX.AI (Reply 1) and Daily brief (option 4 in A / option 3 in B) gate on login** — when logged out, route through Login first, then auto-resume the chosen target (`ai-guide.md` or `daily-brief.md`) WITHOUT re-rendering the welcome banner. Smart-money / new-token intents are no longer numbered picks but remain reachable via the free-form fallback table (`okx-dex-market`).
4. **Turn budget** — ≤ 3 turns end-to-end for a new user; ≤ 2 turns for a returning user picking a workflow + login.
5. **Disclaimer placement** — the disclaimer is the final segment of every rendered banner (both variants, both auth states).
6. **Stale-session fallback** — when `wallet status` returns `loggedIn: true` but `wallet balance` fails (e.g. expired refresh token) or lacks the address / balance fields, the flow prompts re-login (routes to Login) instead of rendering a partial or fabricated logged-in banner; after re-login it renders the logged-in banner.

