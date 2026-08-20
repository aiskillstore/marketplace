# Unregistered-user role selection + routing (Steps 2 + 5)

> Loaded from `ai-guide.md` Step 1 ONLY when the user is logged in but `agent get-my-agents` returns NO OKX.AI identity. Registered users never load this file.

## Step 2 — Role selection page

**Free zone (1–5 sentences, agent's own words):** answer whatever the user actually asked about OKX.AI, then segue naturally into the menu.

**Fixed zone:** render **Variant A** from [`intro.md`](./intro.md) in the user's language; substitute `{okx_ai_site}`. Then **stop and wait** for the user to reply `1` / `2` / `3` (handled in Step 5 below).

## Step 5 — Routing after role pick

When the user replies `1` / `2` / `3`:

Render the matching wait-state line from [`intro.md`](./intro.md), then load the registration playbook below and follow it to completion. The wait-state lines live in [`intro.md`](./intro.md) (authoritative — render that exact text, do not retype a variant here):

| Pick | Wait-state line (from `intro.md`) | Then load |
|---|---|---|
| `1` (User) | `Registering your User identity, hang tight... ⏳` | [`../../okx-ai/references/identity-register.md`](../../okx-ai/references/identity-register.md) (register flow — pass role `User`) |
| `2` (ASP) | `Registering your ASP identity, hang tight... ⏳` | [`../../okx-ai/references/identity-register.md`](../../okx-ai/references/identity-register.md) (register flow — pass role `ASP`) |
| `3` (Evaluator) | `Registering your Evaluator identity, hang tight... ⏳` | [`../../okx-ai/references/identity-register.md`](../../okx-ai/references/identity-register.md) (register flow — pass role `Evaluator`; → then evaluator staking, owned by that flow) |

If the user's reply is NOT exactly `1` / `2` / `3`: map an unambiguous role word to its number (`user` / `User` / `用户` / `Buyer` / `Client` / `买家` / `买方` → 1; `ASP` / `Provider` / `服务商` / `Seller` / `卖家` / `卖方` → 2; `evaluator` / `Evaluator` / `评审员` / `仲裁者` / `评估者` / `arbiter` → 3). If it is still ambiguous, empty, multiple roles, or unrelated, re-render the three options from Variant A and ask the user to reply `1` / `2` / `3`. NEVER guess a role or invent a fourth path.
<!-- retention: 仲裁者 / 评估者 / arbiter are kept as input aliases for role recognition; do not delete them or reduce their occurrences. 评审员 is the current term. -->

> When the reply names the Evaluator role with a legacy word (仲裁者 / 仲裁员 / 评估者 / arbiter / Arbitrator), apply the Legacy role words rename-prompt rule in [`../../okx-ai/references/identity-invariants.md`](../../okx-ai/references/identity-invariants.md) before routing — recognize it as Evaluator and do not restate the old word.

Consent + post-success comm-init are handled inside the registration playbook; login was already confirmed in Step 1 (the playbook still re-checks defensively). This skill does not duplicate them.
