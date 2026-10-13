# Context repo lifecycle

The repeatable playbook for keeping a workspace's context repo healthy over time. Two phases: a one-time **bootstrap** from public sources (delegated to the [`bootstrap-from-domain.md`](bootstrap-from-domain.md) recipe), then a **refresh loop** driven by sales-call analysis (this doc's focus). Use this when standing up a new workspace, or as a periodic rehydration. Recommended cadence: every 2–4 weeks.

The phases are deliberately separated. Bootstrapping from public data gets you to a baseline fast; call-driven refinement is where the quality lives. Step 2 (turning a single call into context edits) cannot be safely automated end-to-end — keep a human in the loop on every edit.

## Before you start — confirm the target workspace

Each Cargo workspace maps to one company. `runtime write` and `runtime edit` push to **that workspace's** context repo immediately, so the first thing to do is confirm you're pointed at the right one. This matters most for consultants and operators managing several client workspaces.

```bash
cargo-ai whoami
# → user.email, workspace.uuid, workspace.name
```

Read back the `workspace.name` to the human and confirm it matches the company you intend to harden context for. **If the name is generic or ambiguous** — `"Main"`, `"Test"`, a person's name, an internal codename, anything that doesn't unambiguously identify the company — stop and ask: "What's the company name and canonical domain (e.g. `acme.com`)?" Workspace names are user-set and frequently don't match the customer-facing brand; the domain is the disambiguator. If you logged in without pinning a workspace, re-login with the right one:

```bash
cargo-ai login --oauth --workspace-uuid <uuid>
# or, non-interactive:
cargo-ai login --token <workspace-scoped-token>
```

If you're working across multiple clients in one session, prefix the workspace name in your notes for every claim you record — it's easy to attribute a Phase 2 insight to the wrong company otherwise.

## Phase 1 — Bootstrap from public sources

For the automatable seed step, use [`bootstrap-from-domain.md`](bootstrap-from-domain.md). It takes a domain, inventories existing files via `runtime browse` + `graph get` so it only fills gaps, enriches via aiArk + builtwith + enrichCrm, scrapes public sources in parallel sub-agents, and writes one file per atomic concept through `context runtime write`.

Once the bootstrap commit lands, open a new agent session so the seeded files load clean (rather than mixed with scratch context from the bootstrap run), then continue with Phase 2.

## Phase 2 — Refresh from real calls

Goal: replace assumptions with evidence. Public sources tell you what the company *says*; calls tell you what prospects *do*.

### 1. Pull the last ~3 months of sales calls

Export transcripts from Gong / Chorus / Fathom / etc. Three months is a good default — long enough to see patterns, short enough that the language is current. For low-volume workspaces, take what you have.

While you're there, capture a **call volume estimate** (transcripts / quarter). It drives the repetition threshold in step 2b.

### 2. Analyze one call at a time, human in the loop

For each call:

1. Have an agent summarize the call against the existing context: which personas were on the call, which objections came up, which proof points were referenced or missed, which signals would have flagged this account.
2. The agent proposes edits — new `objection/...`, updated `persona/...` pains, additional `proof/...` quotes, etc.
3. A human approves each edit before it lands via `runtime write` or `runtime edit`.

Do **not** batch this. An agent processing 30 calls in a loop overweights the loudest objection and underweights nuance.

### 2b. Apply a repetition threshold

A single call's claim is anecdote. Before promoting a claim into context, require it to surface across multiple calls:

| Workspace volume | Threshold |
|---|---|
| Call-rich (≥ 50 transcripts / quarter) | **3 occurrences** before commit |
| Medium volume | **2 occurrences** |
| New / call-poor (< 10 transcripts) | **1 occurrence** — note the source in the file body |

Track candidates in a scratch doc (or draft `insight/` entries) until they cross the threshold. The threshold applies to *claims* — objections, pains, missed proof points. It does not apply to direct facts a call confirms (a customer name, a quote attributable to one named person, a competitor explicitly mentioned).

### 3. Validate by generating sequences

Before treating the context as production-ready, run permutations through the workspace's sequence-generating play or agent and read the outputs. Useful permutations:

- A persona + a play + an objection
- Two different personas with the same play
- A play with and without a specific proof point

If the generated sequences read like a different company between permutations, the context has internal contradictions. Find them by walking the knowledge graph for orphans and conflicting cross-refs — see `graph-queries.md` for queries that catch the common cases.

### 4. Push to production

`runtime write` and `runtime edit` already push to the default branch — there is no separate deploy step. "Push to production" here means flipping downstream agents and plays to read from the refreshed context. If your workspace pins a specific branch or commit, update the pin now.

### 5. Repeat every 2–4 weeks

Re-run Phase 2 on a cadence. Re-run Phase 1 only when something changes materially in public sources (rebrand, new pricing, new persona launch). On each refresh:

- Snapshot `cargo-ai context graph get` before and after, then diff to see what moved.
- Retire context not referenced in the last two cycles — staleness is the failure mode, not coverage gaps.

## What not to automate

Full automation of steps 2 / 2b does not reach acceptable quality in practice. The nuance lives in three decisions: which claim is worth committing, which file it belongs in, and whether an existing file should be edited or a new one created. Keep a human on each of those.
