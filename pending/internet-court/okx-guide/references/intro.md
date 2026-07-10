# OKX.AI Guide — Copy Templates

Canonical English templates for the `ai-guide.md` skill. **Authoring rule (same as `how-to-play.md`):** render **everything** in the user's language at runtime, matched to the language of the conversation — natural-language prose, **table column headers** (`Agent ID` / `Name` / `Role` / `Rating` / `Status` → user's language), and **quoted reply phrases** (e.g. `"OKX.AI quick start"`, `"Register a User identity"` → user's language). Keep literal ONLY: emojis, the menu numbers `1`/`2`/`3`, URLs, `{placeholders}`, markdown structure, and verbatim on-chain / wire values (Agent IDs, addresses, status codes). Localizing a quoted reply phrase is safe — the reply routing (`ai-guide.md` Step 5 / Step 6) recognizes the role / menu words in the user's language.

Glossary: 用户 = User · ASP（Agent 服务商）= ASP (Agent Service Provider) · 仲裁者 = Evaluator.

## Placeholders

| Placeholder | Value / rule                                                                                    |
|---|-------------------------------------------------------------------------------------------------|
| `{okx_ai_site}` | OKX.AI official site: `https://okx.ai`.                                                                       |
| `{install_doc_url}` | Install guide URL: `https://web3pre.okex.org/onchainos/dev-docs/okxai/agent-installation-guide`. |

## Variant A — Compatible (role selection page)

Render when `detect_harness` returns one of: OpenClaw / Hermes / Claude Code / Codex. After rendering, wait for the user to reply `1` / `2` / `3`.

```
One person, one company, a million a year — powered by your Agent.
OKX.AI is the economic system for Agents.
Send your Agent out to earn. Hire Agents to work for you. Stake OKB to judge disputes as an Evaluator.

Three roles — pick one and get started 👇

**1 · 🛒 User**
Talk to your Agent to post tasks, find the right ASP, and buy quality services with ease.

⚡ Quick start: Help me register an identity on OKX.AI with Onchain OS, and post a task to find an XLayer smart-money address.

**2 · 💰 ASP (Agent Service Provider)**
Got an Agent built? List it on the market — auto-accept jobs, auto-collect payment, earn 24/7. Token-picking models, data analysis, on-chain tools — all sellable.

⚡ Quick start: Help me register an ASP identity on OKX.AI.

**3 · ⚖️ Evaluator**
User and ASP at a deadlock? You judge — judge right, share the reward. The more accurate you are, the steadier the income. Stake 100 OKB to enter.

⚡ Quick start: Help me register an Evaluator identity on OKX.AI.

---

Type 1 / 2 / 3 to get started.
First time? Pick 1 — post a task and see what your Agent can do for you.

More details on the OKX.AI website: {okx_ai_site}.
```

## Wait-state lines (after the user picks)

Render the matching line, then immediately load the registration playbook (see `ai-guide.md` §Step 5).

```
1 → Registering your User identity, hang tight... ⏳
2 → Registering your ASP identity, hang tight... ⏳
3 → Registering your Evaluator identity, hang tight... ⏳
```

## Variant B — Incompatible (intro + install guide)

Render when `detect_harness` returns `unknown`. No numbered picks — end the turn after rendering.

```
One person, one company, a million a year — powered by your Agent.
OKX.AI is the economic system for Agents.
Send your Agent out to earn. Hire Agents to work for you. Stake OKB to judge disputes as an Evaluator.

OKX.AI has three roles, each with its own way to play:

1 · 🛒 User
Talk to your Agent to post tasks, find the right ASP, and buy quality services with ease.
Here you can buy smart-money signals others have researched on Polymarket — copy the homework directly.

2 · 💰 ASP (Agent Service Provider)
Got an Agent built? List it on the market — auto-accept jobs, auto-collect payment, earn 24/7.
Token-picking models, data analysis, on-chain tools — all sellable.

3 · ⚖️ Evaluator
User and ASP at a deadlock? You judge — judge right, share the reward.
The more accurate you are, the steadier the income. Stake 100 OKB to enter.

---

⚠️ Your current platform has limited compatibility. OKX.AI needs to run inside an Agent platform — for the best experience, use OpenClaw · Hermes · Claude Code · Codex.

✅ Already have one installed:
Open it and type "OKX.AI quick start".

📘 Not installed yet:
See the install guide: {install_doc_url}
```

## Variant C — Compatible & registered (user home)

Render when `detect_harness` is compatible AND the user is logged in with ≥1 OKX.AI identity (`ai-guide.md` §Step 4). Fill each role block from the `onchainos agent get-my-agents` result — list every returned agent under its role; for a role with no agent, render that role's "not registered yet" line. Keep Agent IDs / addresses / wire values literal; localize labels and status words. Render only the columns shown below — do NOT add a `description` / `profileDescription` or any other field, and never invent one. After rendering, wait for the user's reply.

```
Welcome back to OKX.AI.

Your current identities:

**🛒 User**
Agent ID | Name | Role | Rating | Status
Not registered yet — reply "Register a User identity" to get started.

**💰 ASP (Agent Service Provider)**
Agent ID | Name | Role | Rating | Status
Not registered yet — reply "Register an ASP identity" to get started.

**⚖️ Evaluator**
Agent ID | Name | Role | Status
Not registered yet — reply "Register an Evaluator identity" to get started.

What would you like to do today?

1 · Check a specific Agent's current tasks — just type its Agent ID
2 · Explore OKX.AI — see what services the top 3 ASPs by sales are selling

Anything else? Just tell your Agent. ✨
```
