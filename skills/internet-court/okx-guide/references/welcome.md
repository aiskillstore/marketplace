# Welcome Banner

Two variants by auth state. Both share the same 5-segment structure:

1. **3-line header** — value proposition (same in both auth states).
2. **Address block** — logged-in only (EVM, Solana, USD balance).
3. **OKX.AI featured block** — "Today's highlight" value prop + dedicated CTA `Reply 1`.
4. **Secondary numbered menu** — "Other things you might like" (3 picks in Variant A, 2 picks in Variant B).
5. **Bottom disclaimer** — final non-blank line of every render.

Variant A (`polymarket_available = true`) has **4 picks total**: `1` = OKX.AI featured CTA, `2` = Polymarket, `3` = USDC APY, `4` = Daily brief.
Variant B (`polymarket_available = false`) has **3 picks total**: `1` = OKX.AI featured CTA, `2` = USDC APY, `3` = Daily brief.

- **Logged-out** — no addresses, no balance.
- **Logged-in** — addresses + balance shown, no QR codes.

## Step 1 — Free zone (conditional)

**Skip the free zone entirely when the opener is one the banner already answers.** The banner header is "Hi, welcome to Onchain OS." + 3 value-prop sentences explaining what Onchain OS is and how it works. Repeating that in a free zone above is pure duplication.

Specifically:

| User opener | Free zone? |
|---|---|
| "what is onchainos / how do I play / how to use / what can it do / introduce yourself / tutorial / getting started" | **Skip.** Go straight to the banner. |
| "I just installed it, now what" / "where do I start" / "I'm new" | 1 short sentence acknowledging, then bridge. |
| User asked an unrelated concrete question alongside | 1–3 sentences answering it, then bridge. |

**Bridging (only when a free zone is present)**: end with a transitional half-sentence (e.g. "let me drop the menu" / "here's where to start ↓") — NOT a hard period followed by the banner's first line. Self-check: read free-zone tail + first banner line as one unit; if they feel like two separate posts pasted together, rewrite the tail. If they restate what the banner already says, **delete the free zone entirely**.

## Step 2 — Prepare placeholders (run BEFORE rendering)

### 2.1 Auth state

Already known from `onchainos wallet status` (run earlier). Pick the right banner variant:
- `loggedIn: true` → **logged-in** variant.
- `loggedIn: false` → **logged-out** variant.

### 2.2 Addresses + balance (logged-in variant only)

Pull `evmAddress`, `solAddress`, and the total USD balance from the `onchainos wallet balance` response. Never fabricate.

**MUST**: **Stale-session fallback.** `wallet status` can report `loggedIn: true` from cached credentials while the session's refresh token has already expired — in that case `wallet balance` fails (e.g. `{"ok": false, "error": "Refresh token expired. Log in again."}`) or comes back without the address / balance fields. When the balance call fails or is missing those fields: do **NOT** render the logged-in banner and do **NOT** show partial or fabricated data. Tell the user their session has expired and they need to log in again, then route to **Login Method Choice** in `how-to-play.md`. After re-login completes, resume per **Post-login routing** (render the logged-in Welcome Banner with the now-valid addresses + balance).

> **Do NOT call `onchainos wallet qrcode`** — QR codes are not part of the banner anymore. The CLI subcommand still exists for direct use, but the welcome flow no longer renders QR block art.

### 2.3 Polymarket geoblock check (fail-closed)

Polymarket is restricted in some jurisdictions (e.g. United States). Probe geo before deciding whether to render Variant A or Variant B:

```bash
onchainos wallet geoblock
```

Expected stdout (exit 0):

```json
{"blocked":false}
```

Set `polymarket_available` strictly:

- Exit 0 AND stdout parses to JSON AND `blocked === false` → `polymarket_available = true`.
- **Any other outcome** — non-zero exit, JSON parse error, missing/non-boolean `blocked`, or `blocked === true` — → `polymarket_available = false`.

This is **fail-closed**. Do not warn or surface the geoblock decision — silently switch to the geoblocked menu variant.

## Step 3 — Render the banner

The template below is canonical English. Render in the user's language at runtime per the global translation rule in `how-to-play.md → Authoring Pattern`.

Output as plain text (no `>` blockquote prefix, no surrounding fence). Render order top-to-bottom: header → (logged-in only: address block) → OKX.AI featured block → secondary numbered menu → trailer → disclaimer.

The fenced blocks below are templates inside this spec doc — emit only the text inside, not the fences.

### 3.1 Header — same in both variants

```
Hi, welcome to Onchain OS.
I'm your on-chain AI sidekick — just talk to me to trade, check markets, and chase trends.
Wallet, trading, market data, payments — all in one place, ready out of the box —
no more juggling a dozen DApps, re-connecting wallets, or reviewing signatures every time.
```

### 3.2 Address block — logged-in variant only

```
Your Agentic Wallet addresses:

EVM: {evm_address}
Solana: {solana_address}

Balance: ${balance}
```

### 3.3 OKX.AI featured block — same in both variants

This is the **primary featured segment**, rendered above the secondary numbered menu. It is NOT itself one of the numbered picks; the dedicated CTA is the literal `Reply 1`.

```
✨ Today's highlight — OKX.AI

Ever thought about doing business with an Agent?

Post tasks and buy services — let other people's Agents do the work for you.
Or put your own Agent to work selling services 24/7, earning while you kick back.
One person, with a fleet of Agents, is a whole company.

Reply 1 to see how OKX.AI works →
```

### 3.4 Secondary menu — Variant A (`polymarket_available = true`, 3 numbered picks)

```
Other things you might like:
🔥 2 · Polymarket — top 3 markets worth watching today, I'll handpick them
💰 3 · Don't let your USDC sit idle — let's find the best APY right now
☕ 4 · One coffee's time to digest today's on-chain market
```

### 3.5 Secondary menu — Variant B (`polymarket_available = false`, 2 numbered picks, no Polymarket)

```
Other things you might like:
💰 2 · Don't let your USDC sit idle — let's find the best APY right now
☕ 3 · One coffee's time to digest today's on-chain market
```

### 3.6 Trailer

**Logged-out**:

```
Which one? Just reply with 1–N 👆
```

**Logged-in**:

```
Which one? Just reply with 1–N 👇
```

Replace `N` with `4` for Variant A or `3` for Variant B.

### 3.7 Disclaimer — always at the bottom, both variants

This is the **final non-blank line of every render** (both variants, both auth states).

```
**Attention ⚠️:** AI analysis is for reference only, trade with caution.
```

## Step 4 — Pick handling

**Digit-routing contract (locked):** numbered picks are interpreted strictly against the **currently-rendered menu**. A user who types "2" in Variant B is routed to the description at slot 2 of Variant B (USDC APY) — NOT to Polymarket (slot 2 of Variant A). The numbers are display indices, not stable canonical IDs. This applies to every numbered slot across both variants.

Route by pick **description** (not the raw number — the number shifts between variants).

| Reply | Variant | Description | Login gate? | Target |
|---|---|---|---|---|
| `1` | A + B | OKX.AI featured | **Yes** (logged-out → Login Method Choice → resume) | `ai-guide.md` |
| `2` | A | 🔥 Polymarket Top 3 | No | invoke `okx-dapp-discovery` (it routes to / installs `polymarket-plugin`) |
| `2` | B | 💰 USDC APY | No | invoke `okx-defi` |
| `3` | A | 💰 USDC APY | No | invoke `okx-defi` |
| `3` | B | ☕ Daily on-chain brief | **Yes** (logged-out → Login Method Choice → resume) | `~/.onchainos/workflows/daily-brief.md` |
| `4` | A | ☕ Daily on-chain brief | **Yes** (logged-out → Login Method Choice → resume) | `~/.onchainos/workflows/daily-brief.md` |

### 4.1 Reply `1` — OKX.AI featured (login-gated, both variants)

OKX.AI is the primary featured option. Auth handling:

- **Logged-in user**: load `ai-guide.md` directly. One-line bridge ("Handing off to OKX.AI — meet your Agent.").
- **Logged-out user**:
  1. One-line bridging copy ("OKX.AI needs a wallet logged in — I'll walk you through login first, then we'll pick this up right after.").
  2. Route to **Login Method Choice** in `how-to-play.md`.
  3. Remember the original pick. After login completes, **automatically resume** by loading `ai-guide.md` — do NOT re-render the welcome banner, do NOT ask the user to re-state.

### 4.2 Reply `2` / Reply `3` (Variant A) — skill picks, no login gate

The skill itself handles auth where it needs it. Don't pre-block on login.

- **🔥 Polymarket** (Variant A reply `2`): invoke `okx-dapp-discovery` skill. One-line bridge ("Handing off Polymarket to dapp-discovery."). Don't pre-explain or pre-route.
- **💰 USDC APY** (Variant A reply `3`, Variant B reply `2`): invoke `okx-defi` skill, passing the user's intent ("find best USDC APY").

### 4.3 Daily brief — login-gated (Variant A reply `4`, Variant B reply `3`)

Daily brief assumes an authenticated wallet (most CLI commands inside need login).

- **Logged-in user**: load `~/.onchainos/workflows/daily-brief.md` directly and follow it.
- **Logged-out user**:
  1. One-line bridging copy ("This one needs the wallet logged in — I'll walk you through login first, then we'll pick this up right after.").
  2. Route to **Login Method Choice** in `how-to-play.md`.
  3. Remember the original pick. After login completes, **automatically resume** by loading `daily-brief.md` — do NOT re-render the welcome banner, do NOT ask the user to re-state. (Symmetric with the OKX.AI path.)

### 4.4 "login" reply (logged-out only)

When a logged-out user replies `login` (or similar), route to **Login Method Choice** in `how-to-play.md`. After login completes, render the **logged-in** Welcome Banner so the user sees their addresses + balance. Do NOT auto-load any pick target in this branch — the user asked to log in, not to run a specific pick.

### 4.5 Free-form text (any state)

Anything else (not a numbered pick, not `login`, not a hidden-pick keyword): answer in free zone, then route via the fallback table in `how-to-play.md → Free-form fallback`. Notably:

- Free-text **"smart money"** / whale tracking intent, or **"new tokens"** / fresh on-chain launches intent → route to `okx-dex`.

These two descriptions are NOT in the numbered menu anymore, but the free-text fallback in `how-to-play.md` still routes them correctly.

### 4.6 User names a hidden pick (e.g. types "polymarket" when Variant B is rendered)

The user picked a description that isn't on the rendered menu (most common: Polymarket when geoblock returned anything other than `blocked:false`).

**Do NOT** echo the reason it's hidden. **Do NOT** say "region", "blocked", "geo", "your country", "jurisdiction", "restricted", or anything else that lets the user reverse-engineer the geoblock outcome.

Use a neutral redirect that keeps them on the visible menu:

```
That one isn't available here right now — anything else from the menu work for you? Reply 1–3 👇
```

(Variant B's pick count is 3; if Variant A ever reaches this branch, replace `3` with `4`.) If the user keeps pressing, repeat the redirect; do not negotiate or explain beyond "not available right now".

### 4.7 Login abandonment — any login-gated route

If a user picks a login-gated option (Reply `1` OKX.AI in either variant; Reply `4` Daily brief in Variant A; Reply `3` Daily brief in Variant B) and then **abandons the Login Method Choice flow** (does not complete login), the flow stops at Login Method Choice. The originally-picked target (`ai-guide.md` or `daily-brief.md`) is **NOT auto-resumed**, and the welcome banner is **NOT re-rendered**. Surface the abandonment as a clean exit; if the user later re-engages, treat the new turn as a fresh request.

### 4.8 Downstream-skill load failure

The banner shape (variant, pick count, numbering) is **fixed at render time** based on the Step 2 placeholders. If a downstream skill load fails after the user picks (e.g. `okx-defi` not installed, `ai-guide.md` not found, `daily-brief.md` missing), surface the failure after the pick — the banner is **NOT** retroactively re-rendered, and the digit-to-description mapping does NOT change. If the user retries, route them through whatever standard error/fallback path the failed skill defines, NOT through a fresh banner.

## Canonical render terminator

The disclaimer below is the **final non-blank line** of every rendered banner (both variants, both auth states). Nothing renders after it.

**Attention ⚠️:** AI analysis is for reference only, trade with caution.
