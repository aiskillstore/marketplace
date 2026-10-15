# Bootstrap workspace context from a domain

The prescriptive, automatable version of Phase 1 of [`lifecycle.md`](lifecycle.md). Use this when the user wants to **seed an empty (or thin) context repo from public data**, starting from nothing more than their company's domain. The recipe enriches the company via aiArk + builtwith + enrichCrm + theirStack, scrapes public sources in parallel sub-agents, and writes one file per atomic concept through `cargo-ai context runtime write` — skipping any domain that already has content.

Output: a populated `global/`, `icp/`, `persona/`, `client/`, `proof/`, `signal/` (and where evidence supports it, `alternative/`, `objection/`, `insight/`) — enough that a fresh agent session can hold a coherent conversation about the company. Phase 2 (call-driven refinement) is deliberately out of scope here — see the "What this recipe does NOT do" section.

**Trigger phrases:**
- *"Set up my workspace context from acme.com."*
- *"Bootstrap the context repo — my domain is acme.com."*
- *"Fill in the ICP and personas from our website."*
- *"My workspace is empty, just use our domain to populate everything."*

## What this recipe exercises

- `cargo-ai context runtime browse` / `graph get` for the idempotency check.
- Domain-keyed enrichments (`aiArk.enrichCompany`, `builtwith.getDomainSummary`, `enrichCrm.getFunding`) for the factual spine.
- Parallel sub-agents for public-source scraping (website, careers, blog, news, review sites).
- The driving agent's native LLM to synthesize each digest into typed markdown matching the per-domain template (no `cargo-ai orchestration action execute` double-hop — that pattern is for workflow node graphs, not for an agent already in the loop).
- `cargo-ai context runtime write` to commit one file per concept.

## Required inputs

Before executing, the agent needs:
1. **`domain`** (required) — canonical domain (`acme.com`), no protocol, no path.
2. **`companyName`** (optional) — falls back to whatever `aiArk.enrichCompany` returns for the domain.
3. **`depth`** (optional, default `standard`) — `minimal` (global + 1 icp + 2 personas), `standard` (full domain coverage), `deep` (also scrapes G2/Capterra/Reddit/HN for objections + alternatives).

If `domain` is missing, ask **once** and stop. Don't guess from the user's email — workspace domain and user email often diverge.

## Recipe

### Step 1 — Confirm the target workspace

Each Cargo workspace maps to one company. `runtime write` pushes immediately. Wrong workspace = polluted repo for someone else.

```bash
cargo-ai whoami
# → user.email, workspace.uuid, workspace.name
```

Read back `workspace.name` to the user and confirm it matches the company the `domain` belongs to. **Stop and ask** if the name is generic (`"Main"`, `"Test"`, a person's name, an internal codename) — workspace names are user-set and frequently don't match the customer-facing brand.

**Non-interactive mode** (server-side trigger from signup, scheduled job, etc.): skip the read-back if `domain` was passed in at session start *and* `workspace.uuid` was pinned at login. The capture point at signup is the authority — don't add a blocking question that breaks the automation.

### Step 2 — Idempotency check (the "if not exists" part)

Inventory what's already in the repo so we only fill gaps, never overwrite:

```bash
cargo-ai context runtime browse > /tmp/ctx-browse.json
cargo-ai context graph get > /tmp/ctx-graph.json

# Count entries per domain (excluding _template.md)
jq -r '.files[] | select(.path | test("^[^/]+/[^_].*\\.md$")) | (.path | split("/")[0])' /tmp/ctx-browse.json \
  | sort | uniq -c
```

Build a skip-list: any domain (`global/`, `icp/`, etc.) with ≥ 2 non-template entries is considered "already seeded" — leave it alone. **Print the skip-list to the user** before any writes so they see what wasn't touched and can override.

For domains that exist but are thin (1 entry), still write *new* files into them, but never `runtime edit` an existing file in bootstrap mode. Edits are for the refresh phase (see [Phase 2](lifecycle.md#phase-2--refresh-from-real-calls)), not bootstrap.

### Step 3 — Enrich the seed (factual spine)

Run these in parallel — they give you the factual scaffolding (industry, headcount, tech stack, funding) every downstream synthesis step will cite. All three key on the **domain**, so there is no id-resolution step:

```bash
DOMAIN=acme.com

# Parallel enrichments — same domain, three different signal families
for pair in "aiArk:enrichCompany" "builtwith:getDomainSummary" "enrichCrm:getFunding"; do
  slug="${pair%%:*}"; action="${pair##*:}"
  cargo-ai orchestration action execute \
    --action "$(jq -nc --arg i "$slug" --arg a "$action" \
                  '{kind:"connector",integrationSlug:$i,actionSlug:$a}')" \
    --data "{\"domain\":\"$DOMAIN\"}" \
    --wait-until-finished > /tmp/enrich-$action.json &
done
wait
```

Total: ~1.01 credits (`aiArk.enrichCompany` 0.01, `builtwith.getDomainSummary` free, `enrichCrm.getFunding` 1). Drop the funding call and the whole spine costs a hundredth of a credit.

If every call comes back empty, fall back to website scraping only (Step 4) — note in every written file's `## Source` section that firmographics were unavailable.

### Step 4 — Scrape public sources in parallel sub-agents

Spawn one sub-agent per source. Each returns a **structured digest** (key claims + source URL), never raw HTML. Suggested fan-out:

| Sub-agent | Source URLs | Lands in |
|---|---|---|
| Website core | `https://<domain>`, `/about`, `/product`, `/pricing`, `/customers` | `global/positioning`, `global/narrative`, `global/mission`, `global/pricing`, `client/...` |
| Careers | `/careers`, `/jobs`, LinkedIn jobs | `persona/...`, `signal/hiring-intent-...` |
| Blog & launches | `/blog`, `/changelog`, `/news` | `insight/...`, `proof/...` |
| News & funding | Google News, Crunchbase summary | `signal/funding-...`, `proof/...` |
| Reviews *(depth=deep only)* | G2, Capterra | `objection/...`, `alternative/...` |
| Communities *(depth=deep only)* | Reddit, HN search | `objection/...`, `insight/...` |

For each digest, require a `source_url` per claim. **Skip anything you cannot source** — a thin context beats a fabricated one.

### Step 5 — Synthesize and write per domain

For each domain you intend to populate, read the template first so frontmatter (`title`, `description`) and section structure are valid. Missing `title` or `description` **breaks the knowledge graph**.

```bash
# Always read the template first
cargo-ai context runtime read --path global/_template.md
cargo-ai context runtime read --path persona/_template.md
cargo-ai context runtime read --path icp/_template.md
cargo-ai context runtime read --path client/_template.md
cargo-ai context runtime read --path proof/_template.md
cargo-ai context runtime read --path signal/_template.md
```

Then synthesize one markdown file per atomic concept **directly** — the agent running this recipe is already an LLM, so don't double-hop through `cargo-ai orchestration action execute` to call Anthropic / OpenAI. That pattern is for batch synthesis inside a workflow node graph (Play/Tool); here, the agent has the digest in context and can produce the file body itself.

For each domain, the agent should:

1. Read the template (already done above) and the relevant digest from Step 4.
2. Produce one complete markdown body per concept, including frontmatter (`title` + `description`, both required), section structure from the template, and source URLs cited in `## Source` or `## Day-to-day`.
3. Write each file with `cargo-ai context runtime write`. **One concept per file** — if you're tempted to write two `## Persona` headings into one file, split into two files instead.

Example for `persona/` (after the agent has drafted `vp-engineering.md` from the careers digest):

```bash
cargo-ai context runtime write \
  --path persona/vp-engineering.md \
  --content "$(cat <<'EOF'
---
title: VP of Engineering
description: Senior engineering leader at 50-500 person SaaS companies, owns platform reliability and developer productivity.
---

## Role
- Title: VP of Engineering
- Seniority: Executive
- Function: Engineering
- Reports to: CTO or CEO

## KPIs
- ...

## Source
- https://acme.com/careers/vp-engineering
EOF
)"
```

### Step 6 — Verify and report

Re-run the graph to confirm the writes landed and surface any orphan cross-refs:

```bash
cargo-ai context graph get > /tmp/ctx-graph-after.json

# Node delta
echo "Before: $(jq '.nodes | length' /tmp/ctx-graph.json)"
echo "After:  $(jq '.nodes | length' /tmp/ctx-graph-after.json)"

# Orphans (nodes referenced but not authored)
jq -r '.edges[] | select(.target.exists == false) | "\(.source.path) → \(.target.path)"' /tmp/ctx-graph-after.json
```

Report to the user:
- Files written, grouped by domain.
- Domains skipped (from Step 2).
- Orphan cross-refs (these usually mean the synthesis referenced a `persona/x` that wasn't actually written — either author the missing file or rewrite the reference).

## Credit budget

| Step | Cost per call | Calls (depth=standard) | Subtotal |
|---|---|---|---|
| aiArk.enrichCompany | 0.01 | 1 | 0.01 |
| builtwith.getDomainSummary | 0 | 1 | 0 |
| enrichCrm.getFunding | 1 | 1 | 1 |
| Public-source scrapes (sub-agents) | 0 (agent LLM tokens, not Cargo credits) | 4–6 | 0 |
| Synthesis (agent native) | 0 (agent LLM tokens, not Cargo credits) | 6–8 | 0 |
| context runtime write | 0 | 15–30 files | 0 |
| **Total (standard)** | | | **~1 Cargo credit** |
| **Total (deep)** adds review-site + community sub-agents | | | **~1 Cargo credit** |

Bootstrap is one-shot per workspace. Re-running is a no-op for already-seeded domains thanks to Step 2's skip-list.

## Action shape

`{"kind":"connector","integrationSlug":"<slug>","actionSlug":"<slug>"}`. **No `connectorUuid` in `config`.**

## Output deliverable

A summary the agent presents to the user:

```
Context repo bootstrapped from acme.com:

Written (24 files):
  global/         3 files  (positioning, narrative, pricing)
  icp/            2 files  (mid-market-saas, enterprise-fintech)
  persona/        4 files  (vp-eng, head-of-data, cto, vp-product)
  client/         5 files  (3 enterprise, 2 mid-market)
  proof/          7 files  (4 metrics, 3 quotes)
  signal/         3 files  (hiring-intent-data-eng, series-c-funding, snowflake-adoption)

Skipped (already had content):
  alternative/, objection/, insight/

Orphan refs: none.

Next steps:
  - Open a fresh agent session so the seeded files load clean.
  - Refine from real sales calls — see Phase 2 of lifecycle.md.
```

## What this recipe does NOT do

- **No refinement from sales calls.** That's [Phase 2 of `lifecycle.md`](lifecycle.md#phase-2--refresh-from-real-calls) — deliberately human-in-the-loop. Auto-promoting call-derived claims into context produces plausible-sounding but shallow ICPs.
- **No `runtime edit` on existing files.** Bootstrap is additive only. Edits belong to the refresh phase.
- **No invention.** If a claim has no `source_url`, drop it. Thin context is recoverable; fabricated context erodes trust in everything downstream.
- **No promotion past the repetition threshold.** See [authoring rules of thumb](../conventions.md#authoring-rules-of-thumb). Bootstrap claims come from public sources, which count as one source — note the URL in the file body, don't promote to a confident assertion.

## When stuck — file a workspace report

If `context runtime write` fails repeatedly, the workspace has no context repo configured, or a template has changed shape and the writes no longer match, file via:

```bash
cargo-ai workspaceManagement report create \
  --title "bootstrap-from-domain: <one-line summary>" \
  --description "<exact command(s) tried, errorMessage, domain attempted, workspace.uuid>"
```

See [`../../../cargo-workspace-management/SKILL.md`](../../../cargo-workspace-management/SKILL.md).
