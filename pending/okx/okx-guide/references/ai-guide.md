
# OKX.AI Guide

The OKX.AI onboarding entry. Introduces OKX.AI (the Agent economic system), detects whether the current runtime can run OKX.AI, and routes the user into one of the three identity-registration flows — or, on an incompatible platform, tells them how to get a compatible one.

## Scope & Boundary

This skill owns: OKX.AI intro + platform detection + login & identity detection (new vs returning user) + routing into registration. It does NOT:

- own the Onchain OS welcome banner — that is `how-to-play.md`.
- implement registration — delegated to `okx-ai` (see §Step 5).
- own the wallet-login flow — Step 1 only *checks* login via `wallet status` and hands off to `okx-agentic-wallet`'s existing login flow when needed; the registration playbooks also run their own preflight.

**NEVER**: Do NOT call `onchainos agent create` (or any registration / staking CLI) from this skill. Registration is always delegated to `okx-ai`. (Read-only `onchainos wallet status` and `onchainos agent get-my-agents` in Step 1 are allowed — they create nothing.)

## Step 0 — Platform detection

**MUST**: Run the detection function below and read its single-line output. `compatible` = output is NOT `unknown`.

```bash
detect_harness() {
  if [ "${CLAUDECODE:-}" = "1" ]; then
    echo "Claude Code"
  elif [ -n "${HERMES_INTERACTIVE:-}" ] || [ -n "${HERMES_SESSION_SOURCE:-}" ] \
    || [ -n "${HERMES_YOLO_MODE:-}" ] || [ -n "${HERMES_QUIET:-}" ]; then
    echo "Hermes"
  elif [ -n "${OPENCLAW_CLI:-}" ] || [ -n "${OPENCLAW_SHELL:-}" ]; then
    echo "OpenClaw"
  elif [ -n "${CODEX_THREAD_ID:-}" ] || [ -n "${CODEX_CI:-}" ]; then
    echo "Codex"
  else
    echo "unknown"
  fi
}
detect_harness
```

- Output ∈ {`Claude Code`, `Hermes`, `OpenClaw`, `Codex`} → **compatible** → Step 1.
- Output = `unknown` → **incompatible** → Step 3.

## Step 1 — Compatible: login + identity detection (routing gate)

Reached only when Step 0 is **compatible**. This step decides which page to show — by checking login **first**, identity **second**. The order is mandatory: `agent get-my-agents` requires a logged-in session, so never query identity before login is confirmed.

**MUST**:
1. **Login check** — run `onchainos wallet status` and read `loggedIn`.
   - `loggedIn: false` → user is not logged in. Do **not** query identity. Hand off to the existing wallet-login flow ([`../../okx-agentic-wallet/SKILL.md`](../../okx-agentic-wallet/SKILL.md) §login): prompt login, and on success resume here (re-run `wallet status`, then do the identity check).
   - `loggedIn: true` → continue to the identity check.
2. **Identity check** — run `onchainos agent get-my-agents`. It returns the logged-in user's own OKX.AI agents on XLayer (identified via JWT).
   - **Empty** (no agents) → user has no OKX.AI identity → **Step 2** (role selection page).
   - **≥1 agent** → user already has an identity → **Step 4** (registered user home).

The branch is decided **solely** by whether `agent get-my-agents` returns any agent — never show the role page (Step 2) to a user who already has an identity, nor the registered home (Step 4) to a user with none.

## Step 2 — Compatible & unregistered: role selection page

Reached from Step 1 when the user is logged in but has **no** OKX.AI identity. Render the role-selection page (Variant A) and route the `1`/`2`/`3` reply per [`unregistered-role-selection.md`](./unregistered-role-selection.md) (contains Step 2 page + Step 5 routing). Load it when this branch is hit.

## Step 3 — Incompatible: intro + install guide

Reached from Step 0 when the platform is **incompatible** (`unknown`). No login / identity check applies — OKX.AI cannot run here.

**Free zone (1–5 sentences):** answer the user's OKX.AI question, then segue.

**Fixed zone:** render **Variant B** from [`intro.md`](./intro.md) in the user's language; substitute `{install_doc_url}`. Do **not** offer numbered picks; end the turn.

## Step 4 — Compatible & registered: user home

Reached from Step 1 when the user is logged in and already has **≥1** OKX.AI identity. Render the registered-user home (Variant C, filled field-exact from the `agent get-my-agents` result) and handle its menu replies (Step 6: `1` + Agent ID → that Agent's current tasks; `2` → top ASPs; `Register a <role>` → register a missing role) per [`registered-home.md`](./registered-home.md). Load it when this branch is hit.

## Step 5 — Routing after role pick

Handled in [`unregistered-role-selection.md`](./unregistered-role-selection.md) alongside Step 2 (the `1`/`2`/`3` reply → wait-state line + registration playbook).

## Step 6 — Registered-home menu routing (from Step 4)

Handled in [`registered-home.md`](./registered-home.md) — covers `1` + Agent ID → `agent task-in-progress` with status mapping, `2` → top ASPs by sales via `agent search --query '按销量从高到低排序'`, and "Register a `<role>` identity" reroutes.

## Acceptance Criteria

1. `detect_harness` returns the right platform for each marker set; everything else → `unknown` → incompatible branch (Step 3).
2. Compatible branch (Step 1) checks login (`wallet status`) **before** identity (`agent get-my-agents`) — identity is never queried while logged out.
   - Not logged in → hand off to the existing wallet-login flow, then resume the check.
   - Logged in + no identity → role selection page (Step 2); replying `1` / `2` / `3` renders the right wait-state and loads the right registration playbook (Step 5).
   - Logged in + ≥1 identity → registered user home (Step 4), filled from the `agent get-my-agents` result; the home menu (Step 6) routes `1` + an Agent ID → that Agent's current tasks via `agent task-in-progress`, mapping each task's `status` to a label (e.g. `2` submitted = delivered/awaiting acceptance) rather than blanket-labeling everything "in progress" (with `code=3001` → "not your Agent, re-enter"), `2` → top ASPs by sales via `agent search --query '按销量从高到低排序'` (backend semantic sort-by-sales).
3. Incompatible branch (Step 3) shows the three-role intro (no picks) + install heads-up + `{install_doc_url}`; ends the turn.
4. `OKX.AI 快速开始` / `OKX.AI quick start` triggers this skill.
5. Fixed-zone copy renders in the user's language; emojis / numbers / URLs / placeholders stay literal.
6. Zero `onchainos agent create` calls in this skill (only read-only `wallet status` / `agent get-my-agents`); zero Rust changes.
