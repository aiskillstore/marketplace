# Recoup Music-Company Anatomy (lead with this)

This OS is always a **music company / independent label**, one **org = one git repo**, backed by the
Recoup API as system of record. Scaffold this concrete tree first; the universal anatomy below is the
general pattern it instantiates.

```
{label-repo}/                       # one org/label = one git repo
├── CLAUDE.md / AGENTS.md           # the brain (filing rules, auto-manage loop, never-stale, DB-is-SoR)
├── README.md                       # human entry point: the map + the compounding loop
├── .env.example                    # documents RECOUP_API_KEY|RECOUP_ACCESS_TOKEN, RECOUP_ORG_ID, RECOUP_API_URL
├── .gitignore                      # ignores .env + local secrets (shared repo — never commit creds)
├── .agents/skills -> ../plugin/skills
│
│   # CORE — the loops actively maintain these:
├── artists/                        # the roster (mirrors the live Recoup account; one folder per SIGNED artist)
│   └── {artist-slug}/
│       ├── RECOUP.md               #   identity + per-artist brain — frontmatter artistName/artistSlug/artistId(=account_id)
│       └── releases/               #   the release lifecycle lives here, per artist (stage tracked in RELEASE.md)
│           ├── {release-slug}/RELEASE.md
│           └── top-tracks.md
├── knowledge/                      # compounding: settled answers — faqs / insights / decisions / sops
├── library/                        # compounding: instruments — release checklist, splits sheet, pitch/EPK templates, scripts
├── work/                           # one-off / ad-hoc, dated, by project
├── artifacts/dashboard.html        # regenerated outputs — live roster + release-calendar snapshot
├── plugin/                         # the in-place {label-slug}-os plugin (label-specific glue + the organs)
├── operations/                     # meta: health.md · improvements.md · routines.md · sync.md (the DB<->repo contract)
│
│   # OPTIONAL — add a folder only when the label has real material for it:
├── content/                        #   the caption/graphic/video flywheel (recoup-content-*)
├── deals/                          #   catalog acquisitions / underwriting (recoup-catalog-*) — not the roster's own songs
├── contacts/                       #   industry network: managers, A&R, press, curators (recoup-research-find-contacts)
├── proof/                          #   press, chart milestones, playlist adds, testimonials
├── business/                       #   splits, royalties, contracts, finance, metrics
├── prospects/                      #   A&R funnel — unsigned demos/candidates (no account_id yet)
└── reference/                      #   the label bible: brand guidelines, genre canon
```

**No top-level `pipeline/` or `releases/`.** Release flow lives under each artist
(`artists/{slug}/releases/`, stage tracked in `RELEASE.md`); a cross-roster release calendar is a
*dashboard* (`artifacts/dashboard.html`), not a folder. Unsigned candidates go in `prospects/`.

**Empty roster?** If the org has **0 artists**, don't scaffold an empty `artists/` — hand off to
`recoup-roster-onboard` first (it gathers the label's roster and fans `recoup-roster-add-artist` out
across parallel subagents), then build around the result.

**System-of-record split (write it into `operations/sync.md`):** the Recoup API/DB owns structured
entities (roster, socials, metrics, releases-as-records, billing); this repo owns the unstructured
brain. Entity creation is **API-first** — onboard artists via `recoup-roster-add-artist`, then the
folder follows; never `mkdir` a roster. For research/content/release/song/catalog work, call the
`recoup-*` skills rather than authoring duplicates into `plugin/skills/`.

---

# Universal Workspace-OS Anatomy

Every workspace OS, regardless of domain, is built from the same skeleton — but **scaffold lean**.
Create the small **core** set the loops actively maintain; add an **optional** top-level folder only
when the domain has real material for it now (when unsure, leave it out — it's one `mkdir` to add
later). Rename folders to the domain's language, and keep every **top-level folder name a single
lowercase word** (`operations`, not `operating-system`). The split that matters most: **compounding**
(assets that get better every use) vs **flowing** (instances moving through stages).

```
{workspace}/
├── README.md                 # human entry point: the map + the compounding loop
├── CLAUDE.md                 # the brain: filing rules, auto-manage loop, never-stale contract
├── AGENTS.md                 # symlink -> CLAUDE.md (same brain for any agent runner)
├── .agents/
│   └── skills -> ../plugin/skills
│
├── reference/                # OPTIONAL canon, read-mostly: source docs, specs, brand guides
│   └── principles.md         # distilled 1-page cheat sheet of how this domain works
│
├── library/                  # COMPOUNDING: blank instruments you fill in or run (templates, scripts, checklists)
├── knowledge/                # COMPOUNDING: settled answers you read back (never-answer-twice)
│   ├── faqs/                 #   canonical answers
│   ├── insights/             #   mined explanations / lessons
│   ├── decisions/            #   decision log (what we chose + why) — fuels compound learning
│   └── sops/                 #   written procedures we follow
│
├── {pipeline}/               # FLOWING: staged work (deals / tickets / releases / submissions)
│   ├── _board.md             #   snapshot of the funnel
│   └── 01-…/ 02-…/ …         #   numbered stages for sort order
├── {entities}/               # FLOWING: the core unit's records (clients / artists / features…)
│   └── _TEMPLATE/            #   copyable lifecycle skeleton + dashboard README
│
├── work/                     # CORE: non-recurring / one-off work, grouped by project, dated
│   └── {project}/YYYY-MM-DD-…/ #  e.g. work/acme/2026-06-22-pricing/ (no project? date at the root)
│
├── artifacts/                # CORE: finalized RECURRING outputs (dashboard, reports, exports) kept current
│   └── dashboard.html        #   live snapshot (HTML, not md) — regenerated by the auto-manage loop
│
├── proof/                    # OPTIONAL: outcomes/credibility (case studies, results, testimonials)
├── content/                  # OPTIONAL flywheel: raw -> ideas -> drafts -> published
├── business/                 # OPTIONAL back office: legal, finance, metrics (as relevant)
│
├── plugin/                   # COMPOUNDING capabilities, packaged in place as an installable plugin
│   ├── .claude-plugin/
│   │   └── plugin.json       #   Claude manifest (name defaults to {DOMAIN_SLUG}-os)
│   ├── .codex-plugin/
│   │   └── plugin.json       #   Codex manifest (skills: ./skills/)
│   ├── skills/               #   one folder per skill (SKILL.md)
│   │   ├── RESOLVER.md         #   OPTIONAL trigger->skill table (add once skills outgrow descriptions)
│   │   ├── {domain}-intake/    #   the auto-manage orchestrator (ingest anything end to end)
│   │   ├── {domain}-doctor/    #   read-only health check — the verification surface
│   │   ├── {domain}-janitor/   #   run doctor, then reconcile + de-stale (scheduled)
│   │   ├── {domain}-learn/     #   compound-learning capture (domain knowledge)
│   │   ├── {domain}-reflect/   #   improve the OS itself (system knowledge)
│   │   └── {domain}-skillify/  #   promote proven repeatable work into a skill
│   └── README.md             #   what the plugin is + how to install
│
└── operations/               # META: how the OS runs (not its outputs)
    ├── health.md             #   latest {domain}-doctor report (score + punch list)
    ├── improvements.md       #   self-improvement ledger ({domain}-reflect)
    ├── routines.md           #   cadences (daily/weekly/periodic)
    └── sync.md               #   how the filesystem maps to any external system of record (CRM, etc.)
```

## library/ vs knowledge/ vs work/ vs artifacts/
- **library/** = blank **instruments you reuse** — templates, scripts, checklists, boilerplate. If
  you'd *use* it to produce something, it's library (a proposal template, a release checklist).
- **knowledge/** = **settled answers you read back** — faqs, insights, decisions, sops. If you'd
  *consult* it to decide or recall, it's knowledge (why we picked a vendor; how we close a deal).
- **work/** = **non-recurring output** — a one-off deliverable or scratch build, grouped by project
  (`work/{project}/YYYY-MM-DD-…/`), so the root never sprouts a `catalog-builder/`-style folder.
- **artifacts/** = **finalized recurring output you keep current** — the dashboard, a weekly report,
  a recurring export. Produced again and again, not once.
- Rule of thumb: a deliverable's reusable skeleton → `library/`; the lesson learned making it →
  `knowledge/`; a one-time build → `work/{project}/`; an output you regenerate on a cadence →
  `artifacts/`. If the *process* will repeat, don't leave it as a doc — skillify it into `plugin/`.

## The feedback organs (what makes the OS self-managing)
- **doctor** (`plugin/skills/{domain}-doctor`) — read-only verification surface; scores the workspace
  and writes a punch list to `operations/health.md`. "Consistent" = a clean doctor run, not a feeling.
- **janitor** — runs the doctor, then fixes what's safe. Remediation, gated on the doctor.
- **reflect** (`plugin/skills/{domain}-reflect`) — improves the *system* (skills, routing, checks,
  templates) into `operations/improvements.md`; the 50/50 budget.
- **resolver** — routing. Each skill's `description` routes it while the pack is small; graduate to an
  explicit `plugin/skills/RESOLVER.md` (trigger -> skill) once descriptions overlap. The doctor's
  reachability check flags any **dark** skill (built but unreachable).

## Domain mappings (core unit -> flowing folders)
| Domain | Pipeline (flowing) | Entities (flowing) | Compounding highlights |
|---|---|---|---|
| Consulting | leads -> qualifying -> discovery -> proposal -> negotiation -> won/lost | clients/ | proposals, pricing, proof |
| Product management | backlog -> discovery -> in-progress -> shipped | features/ or releases/ | PRD templates, specs, decision log |
| Record label | demos -> A&R -> signed -> production -> release -> promo | artists/ | release checklists, splits, assets |
| Research | questions -> lit-review -> experiment -> analysis -> writeup | studies/ | protocols, datasets, findings |
| Agency / creative | brief -> pitch -> production -> delivery | accounts/ | brand kits, asset library, case studies |
| Personal / founder | ideas -> exploring -> building -> launched | projects/ | playbooks, lessons, network |

## Rules
- **Top-level folder names are one lowercase word** — `operations` (not `operating-system`),
  `knowledge` (not `knowledge-base`), `business` (not `business-ops`). When you rename a folder to the
  domain's language, keep it a single word (`clients/`, `releases/`, `experiments/`). Skill folders
  inside `plugin/skills/` are the exception: they stay kebab-case per the Agent Skills spec. Hidden
  agent config directories (`.agents/`) are compatibility adapters, not workspace taxonomy.
- **Don't over-scaffold the root.** Build the core (flowing `{pipeline}/` + `{entities}/`,
  `knowledge/`, `library/`, `work/`, `artifacts/`, `plugin/`, `operations/`); add an optional folder
  (`reference/`, `proof/`, `content/`, `business/`) only when the domain has real material for it now.
  Core folders may start empty because the loops fill them; optional folders should not. Over-prepare
  *inside* folders (subfolders + stubs), never as a wide row of empty top-level dirs.
- **One-off work never earns a top-level folder.** Ad-hoc or task-specific work (building a catalog,
  a one-time analysis) goes in `work/{project}/YYYY-MM-DD-…/` — never a new root directory like
  `catalog-builder/`. A finalized output you *regenerate* (the dashboard, a recurring report) goes in
  `artifacts/`; a one-time output stays in `work/`.
- **If work will repeat or needs maintaining, skillify it.** After finishing a task, ask: *will this
  be done again, need upkeep, or prevent a failure from recurring?* If yes, stage a draft under
  `work/YYYY-MM-DD-skillify-{name}/`, verify it with the strongest domain-appropriate check, ask for
  approval, then move it into `plugin/skills/` and repackage instead of leaving a one-off folder
  behind.
- **Name plugins `{DOMAIN_SLUG}-os` by default.** Use the same kebab-case name in
  `plugin/.claude-plugin/plugin.json` and `plugin/.codex-plugin/plugin.json`.
- **The packaged plugin is a transient artifact, not taxonomy.** The `{DOMAIN_SLUG}-os.plugin` zip is a
  release output delivered outside the workspace (via `/tmp`), never a top-level `outputs/` folder —
  `plugin/skills/` is the source of truth. After any in-place skill/manifest change, re-zip and stamp
  `operations/.packaged-version` so `{domain}-doctor`'s package-freshness check can tell the installable
  artifact apart from a stale one.
- **Expose skills once for Cursor/Codex.** Use `.agents/skills -> ../plugin/skills` as the shared
  project-skill adapter. Do not also create `.cursor/skills` unless the user explicitly wants a
  Cursor-only mirror, because duplicate discovery can surface the same skill twice.
- **Consistency is evidence-gated.** `{domain}-doctor` (read-only) is the verification surface — it
  scores the workspace into `operations/health.md`; the janitor and the build report are gated on it.
  Keep it report-only (a doctor that edits is a cage) and its checks behavioral contracts, not a wall
  of distrust validators.
- **Compound the system, not only its contents.** When friction recurs, `{domain}-reflect` turns it
  into a skill / routing row / doctor check / template / rule in `operations/improvements.md` — spend
  ~half the effort on the machinery (50/50). Only on observed repetition, never generic advice.
- Numbered stage prefixes (`01-`, `02-`) for workflow sort order.
- Every entity folder keeps a current `README.md` dashboard (status, owner, value/stakes, next action).
- If an external system of record exists (CRM, issue tracker), it owns *state*; the filesystem owns
  *artifacts*. Document the mapping in `operations/sync.md`.
- Keep the root clean: source/reference material lives under `reference/`, not at the root.
