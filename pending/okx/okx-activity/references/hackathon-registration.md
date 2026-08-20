# OKX.AI Trading Hackathon Registration — Flow & CLI Reference (`hackathon register`)

> **Precondition (BLOCKING):** [`hackathon-core.md`](hackathon-core.md) must already be loaded — it
> holds the gates, Output Rules, and Pre-Delivery Checklist that this flow's steps assume and do not
> restate. If you reached this file first, stop and read it now, then come back.
>
> Scope: the step-by-step registration flow and CLI/MCP reference for `hackathon register`. The hackathon's own gates, reading order, and output rules live in [`hackathon-core.md`](hackathon-core.md) — read that first; skill-wide rules (activity routing, pre-flight, wrong-skill guard, language) live in `../SKILL.md`.

## Flow

Wallet login is required. If not logged in, route via `../SKILL.md` §Pre-flight Checks, then resume at the step that failed.

### Step 1 — Pick the Trading ASP agent

1. List the user's agents (CLI only — there is no MCP tool for this call). Project the response down to the few fields this flow uses; the full rows carry `card[]` / `cells[]` render arrays this flow never reads, and they are ~35× larger:

```
onchainos agent get-my-agents --page-size 20 | jq -c 'if .ok == false then {error: .error} else ([(.data.list // [])[] | (.agentList // [.])[]] as $rows | {total: (.data.total // 0), listed: ($rows|length), asps: [$rows[] | select(.roleLabel == "ASP") | {agentId, name}]}) end'
```

   - **No** `--role` filter: the projection must keep every role so §2 can state the ASP-vs-other split, and the `select` above already applies the exact ASP rule.
   - Keep `(.agentList // [.])[]`. Agent rows arrive either directly under `.data.list[]` or nested under `.data.list[].agentList[]` (grouped by owner), and only the inner rows carry `roleLabel` on the nested shape — reading `.data.list[]` alone yields `asps: []` there, which looks exactly like having no ASP.
   - `--page-size 20` avoids the default page size of 5 silently truncating the list; if the user has more than 20 agents, paginate with `--page` rather than stopping at page 1 and guessing.
   - The `if .ok == false` guard and the `// []` / `// 0` defaults are load-bearing, not tidiness: the CLI's failure envelope is `{ok:false, error, errorCode?}` with **no `data` key**, so an unguarded `.data.list[]` turns every not-logged-in, expired-token, or 5xx response into a bare `jq: error … Cannot iterate over null` — indistinguishable from an empty list.
   - **Fallback** — three distinct cases, and **none** of them means "no agents". Never enter the terminal no-ASP branch on any of them:
     - The projection printed `{"error": …}` → that is the CLI's own failure envelope, not a listing. Surface that message and act on it (`not logged in` → `../SKILL.md` §Pre-flight Checks, then resume here); do not read it as an empty list.
     - `jq` is unavailable, or the command died with a `jq:` error → drop the pipe and apply §2 to the raw JSON.
     - `listed` is 0 while `total` is above 0 (the projection missed the shape) → apply §2 to the raw JSON; never read the empty result as "no agents".
2. Split the rows client-side by role: a row is ASP-eligible **only if `roleLabel` is exactly `"ASP"`**. Any other value (`"User"`, `"Evaluator"`, anything else) or a missing/absent `roleLabel` → **not eligible**. Never default a row into the ASP bucket. In the templates below, `N` is `listed` and `M` is the length of `asps` — never take `N` from `total`, which counts owner groups rather than agents on the nested shape and would make `N-M` wrong. Then present the summary line, followed by the ASP-only numbered list — one line per existing ASP with its **name and agent id** (shown here only, to disambiguate ASPs sharing a name — see `hackathon-core.md` §Output Rules). Numbering starts at **`1`**; there is **no option `0`** and no "create a new ASP" entry — this activity never creates an identity (`hackathon-core.md`), so creation is a tutorial pointer below the list, never a menu choice:

```
You have <N> agents in total, <M> of which are ASPs (the other <N-M> are Evaluator / User identities and cannot register).

Which ASP would you like to register for the OKX.AI Trading Hackathon?

1. <name> (ID: <agent_id>)
2. <name> (ID: <agent_id>)
...

Reply with a number.

Want a new trading ASP that meets the entry requirements instead? [See the tutorial](https://web3.okx.com/onchainos/dev-docs/okxai/a2a-subscription) to get started.
```

Keep `Reply with a number.` on its own line, as the last thing before the hint: it is the primary action, and folding the create hint into the same line buries it. The hint is a **separate trailing paragraph** — never a numbered row, never above the list.

Translate the whole message to the user's language; keep the numbered structure, and keep the URL byte-for-byte as a link. Do **not** add a guessed-eligibility hint next to any name (e.g. "this one looks like it qualifies") — the three preconditions are checked at registration and not inferable from a name.

**If `M` is 0** (no ASP, regardless of `N`): skip the list above — output this fixed template alone, then stop. This branch is terminal, so enter it **only** after Step 1's Fallback has ruled out all three of its cases — an error envelope, a missing or failed `jq`, and a shape mismatch.

```
You don’t have an ASP yet. Please create a trading ASP that meets the entry requirements first. [See the tutorial](https://web3.okx.com/onchainos/dev-docs/okxai/a2a-subscription) to get started.
```

For any language, translate the English above — keep the URL byte-for-byte, keep it a link, and add nothing: no account-switching suggestion, no precondition list, no menu.

3. If the reply is `0`, or the user says they want to create one instead of picking a number: do **not** treat it as invalid input and do **not** re-print the list. `0` was a menu option in an earlier version of this flow, so a returning user may still reply it out of habit — answer that intent directly, in one short message, with the create hint above (link included, translated to the user's language), then stop this flow. This activity never creates an identity (`hackathon-core.md`); an explicit "create one for me" is the `okx-ai` skill's job, so hand off there rather than doing it here.
4. Otherwise resolve the reply to the selected `agent_id`, and from here on identify the ASP **by name only** (`hackathon-core.md` §Output Rules).
   - If the user's original request already named an ASP (or gave an account type / UID) upfront, still run this list and match it against the name to get a real `agent_id` — never fabricate or guess an id. If the name matches more than one ASP, ask which one. Do not skip straight to the confirmation on a one-shot request; still show the list explicitly.
5. Before submitting, confirm the three ASP preconditions with the user (the check at registration is authoritative and rejects on failure — this pre-confirmation only avoids surprising the user with a rejection). Keep the ASP's name in the surrounding sentence, not inside the checklist:

```
Before I submit "<name>", please confirm it:

  ✓ is a trading-type ASP
  ✓ offers a subscription service
  ✓ offers a 3-day free trial

1. Confirm and submit

Reply 1 to proceed.
```

**MUST**: proceed only after the user replies `1`. Registration is irreversible — there is no list, update, status, or undo subcommand — so never answer this prompt on the user's behalf, and never treat a one-shot request that already named an ASP as having pre-answered it.

### Step 2 — Choose the competition account

Ask which account type to register, and include the funding reminder:

```
Which account should compete?

1. web3 — Use your current Agentic Wallet address.
2. cefi — Enter your OKX UID. For CeFi accounts, only USDT perpetual trading pairs will be counted. We recommend using a dedicated sub-account UID to avoid existing assets in your main account affecting the PnL% calculation.

Either way, fund the account with >300U-equivalent assets before trading begins.

Reply with a number.
```

- Reply `1` (web3) → `--account-type web3`. `--address` auto-resolves to the current wallet's X Layer address; do not ask for it.
- Reply `2` (cefi) → `--account-type cefi --uid <uid>`. Ask the user for their OKX UID. The X Layer `--address` is still submitted (auto-resolved), plus the `uid`. The USDT-perp scoring note and the dedicated-sub-account suggestion are **informational** — submit whichever UID the user gives, and do not ask them to prove it is a sub-account or refuse a main-account UID.
- The >300U funding requirement is a **reminder only** — the flow does NOT check the balance and does NOT gate on it.

### Step 3 — Submit

Call `hackathon_register` (MCP) or `onchainos hackathon register …` (CLI). See the reference below for flags.

### Step 4 — Report the result

**On success** — output the fixed template (translate to the user's language):

```
Registration received. We'll take a snapshot before the competition starts — please make sure beforehand:
1. Account balance: at least 300 USDT worth of assets;
2. Competing ASP: a trading subscription service. It will be recorded at snapshot and shown on the leaderboard.
Only signal returns from the snapshotted service will count. If you have several, the earliest-created one is used, and its signals are checked against your actual trades for consistency.
```

Output it verbatim (translated) — both numbered items and the closing paragraph, nothing dropped. Add nothing to it either: no agent name, no chain, no account type, no wallet address, no "good luck". Item 2 describes the ASP requirement generically on purpose — do not name the ASP that was just entered; the confirmation the user already replied to in Step 1 is what tells them which one it was. If they ask afterwards which agent was registered, answer then, by name and never by an internal id (`hackathon-core.md` §Output Rules).

**On failure** — two different outcomes. **MUST**: branch on the `errorCode` field, never on the wording of `error` — the wording can change without notice, while the code is the contract:

| `errorCode` | Meaning | What to say |
|---|---|---|
| `hackathon_registration_rejected` | The ASP was evaluated and refused. `error` carries the reason (e.g. not trading-type, no subscription, no 3-day trial). | **Translate `error` into the user's language** and show it as the reason — it is authoritative. Keep its condition and required action intact; do not soften, generalise, or swap in a different cause. Show it with nothing added: no line above it naming where it came from, no paraphrase below it — a paraphrase is where internal field identifiers leak into user text. |
| `hackathon_service_unavailable` | The request never reached the registration logic — connection error, timeout, 5xx, or an HTML error page. | Say the hackathon registration service is currently unavailable and suggest retrying shortly. **Never** tell the user their ASP failed the trading-type / subscription / trial checks — nothing was evaluated. |

Anything else (`invalid_input`, or a plain `{ok:false, error}` with no `errorCode`) is a CLI-side validation failure — see the error list at the end of this file.

If a `hackathon_registration_rejected` message says the activity is missing, closed, or ended, the hackathon this CLI build is pinned to is over — tell the user that and suggest upgrading `onchainos`. Do not present it as a problem with their ASP.

## CLI / MCP reference — `hackathon register`

**Requires wallet login.**

```
onchainos hackathon register --agent-id <id> --account-type <web3|cefi> [--address <addr>] [--uid <uid>]
```

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--agent-id` | Yes | — | Trading ASP agent id (from `agent get-my-agents`). |
| `--account-type` | Yes | — | Exactly `web3` or `cefi`, lowercase. Any other value — including a differently cased `CeFi` — is rejected on both the CLI and the MCP tool. |
| `--address` | No | wallet X Layer addr | EVM wallet address. Auto-resolved from the current wallet's X Layer address when omitted (both account types). |
| `--uid` | Conditional | — | OKX UID. **Required when `--account-type cefi`**, and **rejected when `--account-type web3`** — the request body carries no account-type field, so uid presence is the only signal the request carries. |

The activity id and chain index (X Layer, `196`) are **fixed internally** — no flag or param sets, overrides, or returns either. MCP tool `hackathon_register` mirrors the flags above (same `address` auto-resolve; no `activity_id` / `chain_index` params) and runs the **same validation**: both surfaces share one validator, so neither accepts anything the other rejects.

Success returns `{ "registered": true, "agentId", "accountType", "chainIndex", "address" }` — no `uid`; it is submitted and redacted in the audit log, never returned (masking rule: `hackathon-core.md` §Output Rules).

**CLI-side errors** (rejections and transport failures are handled in Step 4):
- `--uid is required for CeFi account registration` → collect the UID and retry.
- `--uid is only valid with --account-type cefi` → the user picked `web3` but a UID was passed; confirm which account they meant, then retry with one or the other.
- `invalid account type …` → `--account-type` was not exactly `web3` or `cefi`; re-send it lowercase.
- invalid `--address` for the chain → failed `validate_address_for_chain`; fix and retry.
- `--agent-id is required` / `contains control characters` / `is too long` → the id was blank or mangled; re-run Step 1 and take the id from the list rather than retyping it.
- `not logged in` → run `onchainos wallet login`, then retry.

A blank or whitespace-only `--uid` counts as **not supplied** — if the user replies empty when asked for their UID, ask again rather than submitting.
